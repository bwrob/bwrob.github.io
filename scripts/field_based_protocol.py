"""Define protocols and data classes for  entities with name and ID attributes."""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, TypeVar, runtime_checkable

from attrs import define
from pydantic import BaseModel
from rich import print as rich_print


@runtime_checkable
class NameIdProtocol(Protocol):
    """Protocol for objects with a name and an ID number."""

    name: str
    id_number: int


@dataclass(slots=True)
class PetData:
    """Data class for storing pet information."""

    name: str
    id_number: int
    age: int
    animal_type: str


@define
class PersonalData:
    """Data class for storing personal information, including a pet."""

    name: str
    id_number: int
    age: int
    pet: PetData


class CarData(BaseModel):
    """Pydantic model for storing car information."""

    name: str
    id_number: int
    brand: str


WithNameId = TypeVar("WithNameId", bound=NameIdProtocol)


def filter_by_name(
    regex_condition: str,
    data_list: Sequence[WithNameId],
) -> Sequence[WithNameId]:
    """Filter a list of objects by the name attribute."""
    return [data for data in data_list if re.match(regex_condition, data.name)]


def filter_by_id(
    min_id: int,
    data_list: Sequence[WithNameId],
) -> Sequence[WithNameId]:
    """Filter list of objects by id."""
    return [data for data in data_list if data.id_number >= min_id]


list_of_pets = [
    PetData(name="Mittens", id_number=1, age=2, animal_type="cat"),
    PetData(name="Rex", id_number=2, age=3, animal_type="dog"),
    PetData(name="Matti", id_number=3, age=1, animal_type="dog"),
]

filtered_by_name = filter_by_name(r"^M", list_of_pets)
filtered_by_id = filter_by_id(2, list_of_pets)

rich_print(filtered_by_name, filtered_by_id)
