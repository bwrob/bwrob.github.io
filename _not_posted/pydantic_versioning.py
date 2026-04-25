import logging
import re
from typing import Any, ClassVar, Self

from pydantic import BaseModel, TypeAdapter, ValidationError
from pydantic._internal._model_construction import ModelMetaclass

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Custom exception for errors during schema migration."""


class VersionedModelMeta(ModelMetaclass):
    """Custom metaclass for Pydantic V2 models to manage schema versions and
    migrations.
    """

    _model_registry: ClassVar[dict[tuple[str, int], type["VersionedBaseModel"]]] = {}

    @staticmethod
    def _collect_migration_methods(
        attrs: dict[str, Any], schema_version: int, name: str
    ) -> dict[int, Any]:
        """Collects the 'update' migration method from class attributes.

        This method expects a staticmethod named 'update' that handles the
        migration from the immediately preceding version to the current
        schema_version.

        Args:
            attrs: The dictionary of class attributes.
            schema_version: The current schema version of the model.
            name: The name of the class.

        Returns:
            A dictionary mapping 'from_version' to the 'update' method,
            or an empty dictionary if 'update' is not found or does not
            match the expected signature.

        """
        migration_methods = {}
        update_method = attrs.get("update")
        if callable(update_method):
            # Assumes 'update' method handles migration from (current_version - 1)
            # to current_version.
            from_version = schema_version - 1
            if from_version >= 0:  # Ensure from_version is valid
                migration_methods[from_version] = update_method
            else:
                logger.warning(
                    "'update' method in %s is for schema_version %s, but no preceding version exists (from_version < 0). Skipping.",
                    name,
                    schema_version,
                )
        return migration_methods

    def __new__(
        mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any], **kwargs: Any
    ) -> type:
        """Creates a new class, injects versioning attributes, and registers
        the model.

        Args:
            name: The name of the class being created.
            bases: A tuple of base classes.
            attrs: A dictionary of attributes and methods for the new class.
            **kwargs: Arbitrary keyword arguments, including 'schema_version'.

        Returns:
            The newly created class.

        Raises:
            TypeError: If 'schema_version' is missing or invalid, or if a
                       duplicate model registration occurs.

        """
        schema_version = kwargs.pop("schema_version", None)

        if schema_version is None and any(
            isinstance(b, VersionedModelMeta) for b in bases
        ):
            msg = (
                f"Class {name} inheriting from VersionedBaseModel must define "
                "'schema_version' as a metaclass argument (e.g., class MyModel"
                "(VersionedBaseModel, schema_version=X):)"
            )
            raise TypeError(msg)

        if schema_version is not None:
            if not isinstance(schema_version, int) or schema_version < 1:
                msg = (
                    f"schema_version for {name} must be a positive integer, "
                    f"got {schema_version}"
                )
                raise TypeError(msg)

            attrs["_current_schema_version"] = schema_version

            match = re.match(r"(.+)V(\d+)$", name)
            family_name = match.group(1) if match else name
            attrs["_model_family_name"] = family_name

            attrs["_migration_methods"] = VersionedModelMeta._collect_migration_methods(
                attrs, schema_version, name
            )

        cls = super().__new__(mcs, name, bases, attrs, **kwargs)

        if schema_version is not None:
            registry_key = (cls._model_family_name, schema_version)
            if registry_key in mcs._model_registry:
                msg = (
                    f"Duplicate model registration: '{cls._model_family_name}' with "
                    f"schema_version {schema_version} already exists in the registry. "
                    "Schema versions must be unique per model name."
                )
                raise TypeError(msg)
            mcs._model_registry[registry_key] = cls

        return cls


class VersionedBaseModel(BaseModel, metaclass=VersionedModelMeta):
    """Base model for all versioned Pydantic models.

    Inherits from Pydantic's BaseModel and uses VersionedModelMeta to
    manage schema versions and migrations.
    """

    _current_schema_version: ClassVar[int]
    _model_family_name: ClassVar[str]
    _migration_methods: ClassVar[dict[int, Any]]

    class Config:
        extra = "forbid"
        protected_namespaces = ()

    @classmethod
    def _get_model_by_version(cls, version: int) -> type["VersionedBaseModel"]:
        """Retrieves a specific version of the model from the registry.

        Args:
            version: The schema version to retrieve.

        Returns:
            The Pydantic model class for the specified version.

        Raises:
            MigrationError: If the model for the specified version is not found.

        """
        model_class = VersionedModelMeta._model_registry.get(
            (cls._model_family_name, version)
        )
        if not model_class:
            msg = (
                f"Model '{cls._model_family_name}' with schema_version {version} "
                "not found in registry."
            )
            raise MigrationError(msg)
        return model_class

    @classmethod
    def _detect_version(cls, data: dict[str, Any]) -> int:
        """Implicitly determines the data's original schema version by
        attempting to validate against all known historical versions of this
        model family, from oldest to newest.

        Args:
            data: The raw incoming data dictionary.

        Returns:
            The detected schema version of the data.

        Raises:
            MigrationError: If no historical version successfully validates the
                            data.

        """
        model_family_name = cls._model_family_name
        model_versions_for_family = sorted(
            [
                v
                for (name, v) in VersionedModelMeta._model_registry
                if name == model_family_name
            ]
        )

        if not model_versions_for_family:
            msg = f"No versions registered for model family '{model_family_name}'."
            raise MigrationError(msg)

        detected_version = None
        for version in model_versions_for_family:
            model_to_try = VersionedModelMeta._model_registry[
                model_family_name, version
            ]
            try:
                TypeAdapter(model_to_try).validate_python(data)
                detected_version = version
                break
            except ValidationError:
                continue

        if detected_version is None:
            msg = (
                f"Could not implicitly detect schema version for data. "
                f"Data does not conform to any known version of '{model_family_name}'."
            )
            raise MigrationError(msg)
        return detected_version

    @classmethod
    def _migrate_and_validate(cls, raw_data: dict[str, Any]) -> "Self":
        """Loads and migrates raw data to the latest schema version of this
        model.

        Args:
            raw_data: The raw incoming data dictionary.

        Returns:
            An instance of the latest VersionedBaseModel with migrated data.

        Raises:
            ValueError: If the detected incoming_version is newer than the
                        target_version.
            NotImplementedError: If a required N -> N+1 migration step is
                                 missing.
            MigrationError: If any validation or migration step fails.

        """
        target_version = cls._current_schema_version
        current_data_payload = raw_data.copy()

        incoming_version = cls._detect_version(current_data_payload)
        logger.debug(
            f"Detected incoming data version: {incoming_version} for model "
            f"{cls.__name__}"
        )

        if incoming_version > target_version:
            msg = (
                f"Detected incoming data version ({incoming_version}) is newer than "
                f"the target model version ({target_version}). Forward migration "
                "only supported."
            )
            raise ValueError(msg)

        if incoming_version == target_version:
            logger.debug(
                "Data is already at target version %s. No migration needed.",
                target_version,
            )
            try:
                return cls.model_validate(current_data_payload)
            except ValidationError as e:
                msg = (
                    f"Final validation failed for data at target version "
                    f"{target_version}: {e}"
                )
                raise MigrationError(msg) from e

        logger.debug(
            "Starting iterative migration from v%s to v%s...",
            incoming_version,
            target_version,
        )

        for current_migration_version in range(incoming_version, target_version):
            next_version = current_migration_version + 1
            logger.debug(
                "Migrating from v%s to v%s...", current_migration_version, next_version
            )

            next_model_cls = cls._get_model_by_version(next_version)
            migration_method = next_model_cls._migration_methods.get(
                current_migration_version
            )

            if not migration_method:
                msg = (
                    f"Missing migration step: '{next_model_cls.__name__}' "
                    f"requires an 'update' method to migrate from v"
                    f"{current_migration_version} to v{next_version}."
                )
                raise NotImplementedError(msg)

            try:
                transformed_data = migration_method(current_data_payload)
                if not isinstance(transformed_data, dict):
                    msg = (
                        f"Migration method 'update' in {next_model_cls.__name__} "
                        "must return a dictionary."
                    )
                    raise TypeError(msg)

                current_data_payload = transformed_data

            except Exception as e:
                msg = (
                    f"Migration from v{current_migration_version} to v{next_version} "
                    f"failed for model {next_model_cls.__name__}: {e}"
                )
                raise MigrationError(msg) from e

            try:
                TypeAdapter(next_model_cls).validate_python(current_data_payload)
                logger.debug(
                    "Successfully migrated and validated to v%s.", next_version
                )
            except ValidationError as e:
                msg = (
                    f"Validation failed after migrating to v{next_version} "
                    f"for model {next_model_cls.__name__}: {e.errors()}"
                )
                raise MigrationError(msg) from e

        try:
            final_model = cls.model_validate(current_data_payload)
            logger.debug(
                "Successfully loaded and migrated data to final version %s.",
                target_version,
            )
            return final_model
        except ValidationError as e:
            msg = (
                f"Final validation against target model {cls.__name__} "
                f"(v{target_version}) failed: {e.errors()}"
            )
            raise MigrationError(msg) from e

    @classmethod
    def load(cls, raw_data: dict[str, Any]) -> "Self":
        """Public entry point for loading and migrating data.

        Args:
            raw_data: The raw incoming data dictionary.

        Returns:
            An instance of the latest VersionedBaseModel with migrated data.

        """
        return cls._migrate_and_validate(raw_data)
