from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, NoReturn, Optional

from loguru import logger

from SNT.utils.exceptions import InternalError, InvalidConfiguration
from SNT.utils.parameter_validators import Constraint


class UserParam:
    def __init__(self, name: str, description: str, default_value: Any, constraints: Optional[Constraint] = None):
        self.name = name
        self._description = description
        self.default_value = default_value
        self.current_value = default_value
        self.constraints = constraints

        if self.constraints is not None:
            try:
                self.constraints.check_if_value_meets_constraint(name, self.default_value)
                self.constraints.check_if_value_meets_constraint(name, self.current_value)
            except InvalidConfiguration as e:
                msg = f"Failed loading of {self.name}"
                raise InvalidConfiguration(msg) from e

    def apply_constraints_to_value(self, param_name: str, value: Any) -> NoReturn:
        """Apply the internal constraints to the value of this parameter.

        Args:
            param_name (str): Name of parameter
            value (Any): Value that it takes

        Raises:
            InvalidConfiguration: If the constraint does not evaluate to True
        """
        self._valueConstraint.check_if_value_meets_constraint(param_name, value)

    def update_value(self, new_value: Any) -> None:
        """Update the value of a parameter, after passing the validation stage.

        Args:
            new_value (Any): New value that this parameter shall take

        """
        if self.constraints is not None:
            self.constraints.check_if_value_meets_constraint(self.name, new_value)
        self.current_value = new_value

    def validate(self) -> None:
        """Validate the current value of the parameter."""
        self.constraints.check_if_value_meets_constraint(self.current_value)

    def reset_value(self) -> None:
        """Reset the current value to be the same as the default one."""
        self.current_value = self.default_value

    @property
    def existing_constraints(self) -> Constraint:
        """Return the constraint associated with this parameter."""
        return self._valueConstraint

    @property
    def is_mandatory(self) -> bool:
        """True if the parameter is mandatory."""
        return self._mandatory

    @property
    def quiet_output(self) -> bool:
        """True if this object should not produce logs."""
        return self.quiet

    def __repr__(self) -> str:
        return f"Default Value: {self.default_value}; Mandatory Flag: {self._mandatory}; Constraints: {self._valueConstraint}\n"

    @property
    def description(self) -> str:
        """Return description of the parameter."""
        return self._comment if self._comment is not None else ""


class ConfigHolder:
    """Stores every single configurable parameter in the PSS.

    Each different module has its own configurable parameters stored inside a given "Section",
    under which we will have user parameters associated with it. This means that in order to
    collect/update a given parameter, we must know its "section_name" and its "name"

    """

    def __init__(self, parameters: dict[str, UserParam]) -> None:
        self._config_values: dict[str, UserParam] = parameters

    def get_current_value(self, parameter_name: str) -> Any:
        return self._config_values[parameter_name].current_value

    def update_value(self, parameter_name: str, new_value: Any) -> None:
        self._config_values[parameter_name].update_value(new_value)

    def validate_all(self) -> None:
        for parameter in self._config_values.values():
            parameter.validate()

    def get_all_current_values(self) -> dict[str, Any]:
        """Retrieve a dictionary with all current values."""
        return {i: j.current_value for i, j in self._config_values.items()}
