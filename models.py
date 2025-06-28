from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float


@dataclass
class Tag:
    tag_name: str
    color: str
    locations: list[Location]