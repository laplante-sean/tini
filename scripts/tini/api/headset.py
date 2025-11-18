from enum import Enum


class Headset(Enum):
    RIFT = "Rift"
    LAGUNA = "Rift S"
    MONTEREY = "Quest 1"
    HOLLYWOOD = "Quest 2"
    EUREKA = "Quest 3"
    SEACLIFF = "Quest Pro"
    GEARVR = "GearVR"
    PACIFIC = "Go"

    def to_section_id(self) -> str | None:
        """When retrieving applications from the app store, a "sectionId" must be provided."""
        match self:
            case Headset.RIFT | Headset.LAGUNA:  # Rift line
                return "1736210353282450"
            case (
                Headset.MONTEREY | Headset.HOLLYWOOD | Headset.EUREKA | Headset.SEACLIFF
            ):  # Quest line
                return "1888816384764129"
            case Headset.GEARVR | Headset.PACIFIC:
                return "174868819587665"
