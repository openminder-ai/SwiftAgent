from enum import Enum


class ApplicationType(Enum):
    STANDARD = 0
    PERSISTENT = 1
    HOSTED = 2

    def is_hosted(self) -> bool:
        return self == ApplicationType.HOSTED

    def is_persistent(self) -> bool:
        return self == ApplicationType.PERSISTENT

    def is_standard(self) -> bool:
        return self == ApplicationType.STANDARD
