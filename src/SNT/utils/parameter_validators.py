"""Implements Constraints, that will be used as the validation layer of the software.

Each implements a different condition, that can then be applied to the values that the user pass.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, NoReturn

import numpy as np

from SNT.utils.exceptions import InternalError, InvalidConfiguration


class Constraint:
    """Base class for the constraints implemented within SNT."""

    def __init__(self, const_text: str):
        self._constraint_list = [self._evaluate]
        self.constraint_text = const_text

    def __add__(self, other: Constraint) -> Constraint:
        new_const = Constraint(self.constraint_text)
        # ensure that we don't propagate changes to all existing constraints
        new_const._constraint_list = deepcopy(self._constraint_list)
        new_const._constraint_list.append(other._evaluate)
        new_const.constraint_text += " and " + other.constraint_text

        return new_const

    def __radd__(self, other: Constraint) -> Constraint:
        return self.__add__(other)

    def check_if_value_meets_constraint(self, param_name: str, value: Any) -> None:
        """Loop through all constraints set for this value.

        Args:
            param_name (str): Name of parameter
            value (Any): Value that the parameter is currently taking

        Raises:
            InvalidConfiguration: if the constraint is not met

        """
        for evaluator in self._constraint_list:
            evaluator(param_name, value)

    def _evaluate(self, value: Any) -> None:
        del value

    def __str__(self) -> str:
        return self.constraint_text

    def __repr__(self) -> str:
        return self.constraint_text

    def __call__(self, value: Any) -> None:
        for evaluator in self._constraint_list:
            evaluator(value)


class ValueInInterval(Constraint):
    def __init__(self, interval: list, include_edges: bool = False):
        """Check if this value is inside a given interval.

        Args:
            interval (list): Interval to check, must be comparable to the value
            include_edges (bool, optional): Include the edges of the interval in the comparison. Defaults to False.

        """
        super().__init__(const_text=f"Value inside interval <{interval}>; Edges: {include_edges}")
        self._interval = interval
        self._include_edges = include_edges

    def _evaluate(self, param_name: str, value: Any) -> NoReturn:
        good_value = False
        try:
            if self._include_edges:
                if self._interval[0] <= value <= self._interval[1]:
                    good_value = True
            elif self._interval[0] < value < self._interval[1]:
                good_value = True
        except TypeError as e:
            msg = f"Config ({param_name}) value can't be compared with the the interval: {type(value)} vs {self._interval}"
            raise InvalidConfiguration(msg) from e

        if not good_value:
            msg = f"Config ({param_name}) value not inside the interval: {value} vs {self._interval}"
            raise InvalidConfiguration(
                msg,
            )


class ValueFromDtype(Constraint):
    def __init__(self, dtype_list: tuple[type, ...]):
        """Check if value is from any of the provided dtypes.

        Args:
            dtype_list (tuple[type, ...]): Possible data types

        Raises:
            InternalError: If the dtype_list is not a tuple

        """
        super().__init__(const_text=f"Value from dtype <{dtype_list}>")
        self.valid_dtypes = dtype_list
        if not isinstance(dtype_list, tuple):
            msg = "Dtype list must be a tuple"
            raise InternalError(msg)

    def _evaluate(self, param_name: str, value: Any):
        if not isinstance(value, self.valid_dtypes):
            msg = (
                f"Config ({param_name}) value ({value}) not from the valid dtypes: {type(value)} vs {self.valid_dtypes}"
            )
            raise InvalidConfiguration(msg)


class ValueFromList(Constraint):
    def __init__(self, available_options: Iterable[Any]):
        """Check if the value is one of the provided ones.

        Args:
            available_options (Iterable[Any]): Values that are available

        """
        super().__init__(const_text=f"Value from list <{available_options}>")
        self.available_options = available_options

    def _evaluate(self, param_name: str, value) -> NoReturn:
        bad_value = False
        if isinstance(value, (list, tuple)):
            for element in value:
                if element not in self.available_options:
                    bad_value = True
                    break
        elif value not in self.available_options:
            bad_value = True

        if bad_value:
            msg = f"Config ({param_name})  value not one of the valid ones: {value} vs {self.available_options}"
            raise InvalidConfiguration(msg)


class IterableMustHave(Constraint):
    def __init__(self, available_options: Iterable[Any], mode: str = "all"):
        """Check if this iterable has any or all of the provided options.

        Args:
            available_options (Iterable[Any]): Options
            mode (str, optional): all/either. Defaults to "all".

        Raises:
            InternalError: If the mode is not of the two

        """
        super().__init__(const_text=f"Must have value from list <{available_options}>")
        self.available_options = available_options
        self.mode = mode

        if mode not in ["all", "either"]:
            msg = "Using the wrong mode"
            raise InternalError(msg)

    def _evaluate(self, param_name: str, value: Any) -> NoReturn:
        if not isinstance(value, Iterable):
            msg = "Constraint needs a list or tuple"
            raise InvalidConfiguration(msg)

        evaluation = [i in value for i in self.available_options]

        good_value = False

        if self.mode == "all":
            good_value = all(evaluation)
        elif self.mode == "either":
            good_value = any(evaluation)

        if not good_value:
            msg = f"Config ({param_name}) value {value} does not have {self.mode} of {self.available_options}"
            raise InvalidConfiguration(
                msg,
            )


class PathExists(Constraint):
    """Imposes that a given path must exist."""

    def __init__(self) -> None:
        """Imposes that a given path exists."""
        super().__init__(const_text="The path must exist")

    def _evaluate(self, param_name: str, value: Any) -> None:
        if not Path(value).exists():
            msg = f"Path {value} given in {param_name} does not exist"
            raise InvalidConfiguration(msg)


Positive_Value_Constraint = ValueInInterval([0, np.inf], include_edges=True)
StringValue = ValueFromDtype((str,))
PathValue = ValueFromDtype((str, Path))
NumericValue = ValueFromDtype((int, float))
IntegerValue = ValueFromDtype((int,))
BooleanValue = ValueFromDtype((bool,))
ListValue = ValueFromDtype((list, tuple))

predefined_constraints = {
    "Positive_Value_Constraint": ValueInInterval((0, np.inf), include_edges=True),
    "StringValue": ValueFromDtype((str,)),
    "PathValue": ValueFromDtype((str, Path)) + PathExists(),
    "NumericValue": ValueFromDtype((int, float)),
    "IntegerValue": ValueFromDtype((int,)),
    "BooleanValue": ValueFromDtype((bool,)),
}
