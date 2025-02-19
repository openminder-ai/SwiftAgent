from enum import Enum


class RuntimeType(Enum):
    STANDARD = 0
    PERSISTENT = 1
    HOSTED = 2

    @classmethod
    def _missing_(cls, value: str) -> "RuntimeType":
        """Handle string inputs by converting them to enum members."""
        if isinstance(value, str):
            # Try to match the string (case-insensitive) to an enum name
            try:
                return cls[value.upper()]
            except KeyError:
                pass
        return None

    def is_hosted(self) -> bool:
        return self == RuntimeType.HOSTED

    def is_persistent(self) -> bool:
        return self == RuntimeType.PERSISTENT

    def is_standard(self) -> bool:
        return self == RuntimeType.STANDARD


class ClientConnectionMode(Enum):
    AGENT = 0
    SUITE = 1

    @classmethod
    def __missing__(cls, value: str) -> "ClientConnectionMode":
        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                pass

        return None
