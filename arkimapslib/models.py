try:
    import pydantic.v1 as pydantic
except ImportError:
    import pydantic as pydantic  # type: ignore


class BaseDataModel(pydantic.BaseModel):
    """Stricter pydantic defaults for data models."""

    class Config:
        """Set up stricter pydantic Config."""

        validate_assignment = True
        extra = pydantic.Extra.forbid
