"""Case-insensitive string enum implementation.

This module provides a `CaseInsensitiveStrEnum` class that extends the standard
`StrEnum` to support case-insensitive member lookup and ensure all member
values are lowercase.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Self, override


class CaseInsensitiveStrEnum(StrEnum):
    """A case-insensitive string enum.

    This class extends the `StrEnum` class to provide case-insensitive member lookup.
    It also provides a custom `_generate_next_value_` method that returns the
    lowercase version of the member name for use with `auto()`.
    """

    @classmethod
    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        """Implement the special hook that is called when a class is subclassed.

        It allows us to customize the class creation process without using metaclasses.
        """
        super().__init_subclass__(**kwargs)

        for member in cls:
            if not member.islower() or not member.value.islower():
                msg = f"Member '{member}' and value {member.value} must be lowercase."
                raise TypeError(msg)

    @override
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        """Return the lower-cased version of the member name.

        This method is overridden to ensure that when `auto()` is used to create
        enum members, their values are the lowercase version of their names.
        """
        return name.lower()

    @override
    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        """Provide case-insensitive member lookup.

        This method is called when a value is not found in the enum.
        It is overridden to perform a case-insensitive search for the member.
        """
        if not isinstance(value, str):
            return None

        value = value.lower()
        for member in cls:
            if member.name.lower() == value:
                return member

        return None
