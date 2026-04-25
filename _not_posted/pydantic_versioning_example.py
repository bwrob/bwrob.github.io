from scripts.pydantic_versioning import VersionedBaseModel


class UserV1(VersionedBaseModel, schema_version=1):
    """Represents User schema version 1."""

    id: str
    name: str

    @staticmethod
    def update(data: dict[str, Any]) -> dict[str, Any]:
        """Migrates data from version 0 to version 1.

        In this example, we assume v1 is the first version, so no actual
        transformation is needed.

        Args:
            data: The incoming data dictionary from version 0.

        Returns:
            The transformed data dictionary for version 1.

        """
        return data


class UserV2(VersionedBaseModel, schema_version=2):
    """Represents User schema version 2."""

    id: str
    full_name: str
    email: str

    @staticmethod
    def update(data: dict[str, Any]) -> dict[str, Any]:
        """Migrates data from version 1 to version 2.

        - Renames 'name' to 'full_name'.
        - Adds a default 'email' field.

        Args:
            data: The incoming data dictionary from version 1.

        Returns:
            The transformed data dictionary for version 2.

        """
        logger.debug("  Applying UserV2 migration (v1 -> v2). Data: %s", data)
        return {
            "id": data["id"],
            "full_name": data["name"],
            "email": f"{data['name'].lower().replace(' ', '.')}@example.com",
        }


class AddressV1(VersionedBaseModel, schema_version=1):
    """Represents Address schema version 1."""

    street: str
    city: str
    zip_code: str

    @staticmethod
    def update(data: dict[str, Any]) -> dict[str, Any]:
        """Migrates data from version 0 to version 1 for Address.

        Args:
            data: The incoming data dictionary from version 0.

        Returns:
            The transformed data dictionary for version 1.

        """
        return data


class UserV3(VersionedBaseModel, schema_version=3):
    """Represents User schema version 3."""

    id: str
    full_name: str
    email: str | None = None
    address: AddressV1 | None = None

    @staticmethod
    def update(data: dict[str, Any]) -> dict[str, Any]:
        """Migrates data from version 2 to version 3.

        - Makes 'email' optional.
        - Adds an optional 'address' field.

        Args:
            data: The incoming data dictionary from version 2.

        Returns:
            The transformed data dictionary for version 3.

        """
        logger.debug("  Applying UserV3 migration (v2 -> v3). Data: %s", data)
        return {
            "id": data["id"],
            "full_name": data["full_name"],
            "email": data.get("email"),
            "address": None,
        }


class AddressV2(VersionedBaseModel, schema_version=2):
    """Represents Address schema version 2."""

    street: str
    city: str
    zip_code: str
    country: str = "USA"

    @staticmethod
    def update(data: dict[str, Any]) -> dict[str, Any]:
        """Migrates Address data from version 1 to version 2.

        - Adds a default 'country' field.

        Args:
            data: The incoming data dictionary from version 1.

        Returns:
            The transformed data dictionary for version 2.

        """
        logger.debug("    Applying AddressV2 migration (v1 -> v2). Data: %s", data)
        transformed_data = data.copy()
        transformed_data["country"] = "USA"
        return transformed_data


class UserV4(VersionedBaseModel, schema_version=4):
    """Represents User schema version 4."""

    id: str
    full_name: str
    email: str | None = None
    address: AddressV2 | None = None

    @staticmethod
    def update(data: dict[str, Any]) -> dict[str, Any]:
        """Migrates data from version 3 to version 4.

        Handles nested Address migration by loading the nested address data
        into the AddressV2 model.

        Args:
            data: The incoming data dictionary from version 3.

        Returns:
            The transformed data dictionary for version 4.

        """
        logger.debug("  Applying UserV4 migration (v3 -> v4). Data: %s", data)
        transformed_data = data.copy()

        if "address" in transformed_data and transformed_data["address"] is not None:
            logger.debug("    Migrating nested Address...")
            migrated_address = AddressV2.load(transformed_data["address"])
            transformed_data["address"] = migrated_address.model_dump()
            logger.debug(
                f"    Nested Address migrated to: {transformed_data['address']}"
            )

        return transformed_data


class UserV5(VersionedBaseModel, schema_version=5):
    """Represents User schema version 5.

    Used to demonstrate a missing migration step from UserV4.
    """

    id: str
    full_name: str
    age: int
