# from __future__ import annotations

import datetime
from typing import Union


class ModelStep:
    """
    Identifies a step of a model, as a time span value and unit
    """

    __slots__ = ("_value",)

    _value: int

    def __init__(self, value: Union[int, str, "ModelStep"]):
        val, unit = self._parse_value(value)
        if unit != "h":
            raise ValueError(f"only 'h' currently supported as a time unit (found {unit!r})")
        self._value = val

    def __eq__(self, other):
        if isinstance(other, int):
            return self._value == other
        if isinstance(other, str):
            val, unit = self._parse_value(other)
            if unit != "h":
                raise ValueError(f"only 'h' currently supported as a time unit (found {unit!r})")
            return self._value == val
        if isinstance(other, ModelStep):
            return self._value == other._value
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, int):
            return self._value < other
        if isinstance(other, str):
            val, unit = self._parse_value(other)
            if unit != "h":
                raise ValueError(f"only 'h' currently supported as a time unit (found {unit!r})")
            return self._value < val
        if isinstance(other, ModelStep):
            return self._value < other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return f"{self._value}h"

    def __repr__(self) -> str:
        return f"ModelStep('{self._value}h')"

    def is_zero(self) -> bool:
        """Test if the step is zero, regardless of unit."""
        return self._value == 0

    def suffix(self) -> str:
        """
        Return a suffix that can be used in filenames to identify a step
        """
        return f"+{self._value:03d}"

    @staticmethod
    def _parse_value(value: Union[int, str, "ModelStep"]):
        """
        Parse a value (optionally with suffix) into a value and a unit
        """
        if isinstance(value, int):
            return value, "h"
        elif isinstance(value, ModelStep):
            return value._value, "h"
        elif isinstance(value, str):
            if len(value) < 2:
                raise ValueError(f"value {value!r} is too short to be a number plus unit suffix")
            return int(value[:-1]), value[-1]

        raise TypeError(f"value {value!r} is neither an int nor a str nor a ModelStep")

    @classmethod
    def from_grib1(cls, value: int, unit: int) -> "ModelStep":
        """
        Instantiate a ModelStep from a value and its GRIB1 unit
        """
        if unit == 0:  # minutes
            if value % 60 != 0:
                raise NotImplementedError(f"unsupported step {value} minutes")
            return cls(value // 60)
        if unit == 1:  # hours
            return cls(value)
        if unit == 2:  # days
            return cls(value * 24)
        if unit == 3:  # months
            raise NotImplementedError("unsupported step unit: months")
        if unit == 4:  # years
            raise NotImplementedError("unsupported step unit: years")
        if unit == 5:  # decades
            raise NotImplementedError("unsupported step unit: decades")
        if unit == 6:  # normals
            raise NotImplementedError("unsupported step unit: normals")
        if unit == 7:  # centuries
            raise NotImplementedError("unsupported step unit: centuries")
        if unit == 10:  # 3-hours
            return cls(value * 3)
        if unit == 11:  # 6-hours
            return cls(value * 6)
        if unit == 12:  # 12-hours
            return cls(value * 12)
        if unit == 254:  # seconds
            if value % 3600 != 0:
                raise NotImplementedError(f"unsupported step {value} seconds")
            return cls(value // 3600)
        raise ValueError(f"Unsupported GRIB time unit: {unit!r}")

    @classmethod
    def from_timedef(cls, value: int, unit: int) -> "ModelStep":
        """
        Instantiate a ModelStep from a value and its Timedef unit
        """
        if unit == 0:  # minutes
            if value % 60 != 0:
                raise NotImplementedError(f"unsupported step {value} minutes")
            return cls(value // 60)
        if unit == 1:  # hours
            return cls(value)
        if unit == 2:  # days
            return cls(value * 24)
        if unit == 3:  # months
            raise NotImplementedError("unsupported step unit: months")
        if unit == 4:  # years
            raise NotImplementedError("unsupported step unit: years")
        if unit == 5:  # decades
            raise NotImplementedError("unsupported step unit: decades")
        if unit == 6:  # normals
            raise NotImplementedError("unsupported step unit: normals")
        if unit == 7:  # centuries
            raise NotImplementedError("unsupported step unit: centuries")
        if unit == 10:  # 3-hours
            return cls(value * 3)
        if unit == 11:  # 6-hours
            return cls(value * 6)
        if unit == 12:  # 12-hours
            return cls(value * 12)
        if unit == 13:  # seconds
            if value % 3600 != 0:
                raise NotImplementedError(f"unsupported step {value} seconds")
            return cls(value // 3600)
        raise ValueError(f"Unsupported GRIB time unit: {unit!r}")


class Instant:
    """
    Identifies an instant of time for which we have data for an input.

    Note that different combinations of reftime+step that would map to the same
    physical instant of time are considered distinct for arkimaps purposes
    """

    __slots__ = ("_reftime", "_step")

    _reftime: datetime.datetime
    _step: ModelStep

    def __init__(self, reftime: datetime.datetime, step: Union[int, str, ModelStep]):
        self._reftime = reftime
        self._step = ModelStep(step)

    @property
    def reftime(self) -> datetime.datetime:
        """
        Access the model reference time.
        """
        return self._reftime

    @property
    def step(self):
        return self._step

    def __eq__(self, other):
        if isinstance(other, Instant):
            return self._reftime == other._reftime and self._step == other._step
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Instant):
            if self._reftime < other._reftime:
                return True
            if self._reftime > other._reftime:
                return False
            return self._step < other._step
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._reftime, self._step))

    def __str__(self):
        return f"{self._reftime:%Y-%m-%dT%H:%M:%S}{self._step.suffix()}"

    def __repr__(self):
        return f"Instant({self})"

    def pantry_suffix(self) -> str:
        """
        Return a suffix that identifies a product for this instance in the
        pantry
        """
        return (
            f"_{self._reftime.year}_{self._reftime.month}_{self._reftime.day}"
            f"_{self._reftime.hour}_{self._reftime.minute}_{self._reftime.second}"
            f"+{self._step._value}"
        )

    def product_suffix(self) -> str:
        """
        Return a suffix that identifies a product for this instance in the
        output
        """
        return f"_{self.reftime:%Y-%m-%dT%H:%M:%S}{self._step.suffix()}"

    def step_suffix(self) -> str:
        """
        Return a suffix that can be used in filenames to identify a step
        """
        return self._step.suffix()
