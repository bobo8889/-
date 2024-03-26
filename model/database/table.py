from typing import Any, Dict


class BaseTable:
    __tablename__: str

    def get_attrs(self) -> Dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                result[key] = value
        return result

    def set_attrs(self, attrs: Dict[str, Any]) -> Any:
        for key, value in attrs.items():
            setattr(self, key, value)
        return self
