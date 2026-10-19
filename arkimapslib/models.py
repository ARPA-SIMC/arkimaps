import pydantic


class BaseDataModel(pydantic.BaseModel):
    """Stricter pydantic defaults for data models."""

    class Config:
        """Set up stricter pydantic Config."""

        validate_assignment = True
        extra = pydantic.Extra.forbid


__all__ = ["BaseDataModel", "pydantic"]
