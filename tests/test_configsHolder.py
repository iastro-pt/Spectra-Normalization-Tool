# # pylint=disable
from typing import Any

import pytest

from SNT.utils.configs import ConfigHolder, UserParam
from SNT.utils.exceptions import InvalidConfiguration
from SNT.utils.parameter_validators import predefined_constraints


def test_Params() -> None:
    param = UserParam(
        name="foo",
        description="foofoofoo",
        default_value=10,
    )
    param.update_value(new_value=15)
    assert param.current_value == 15
    param.reset_value()
    assert param.current_value == 10


def test_Params_with_constraint() -> None:
    const = predefined_constraints["Positive_Value_Constraint"]
    param = UserParam(name="foo", description="foofoofoo", default_value=10, constraints=const)
    param.update_value(new_value=15)
    assert param.current_value == 15
    param.reset_value()
    assert param.current_value == 10

    with pytest.raises(InvalidConfiguration):
        param.update_value(-10)


@pytest.mark.parametrize("default", [(-10), (-2210), (-0.1), ("str")])
def test_init_with_constraint(default: Any) -> None:
    with pytest.raises(InvalidConfiguration):
        _ = UserParam(
            name="foo",
            description="foofoofoo",
            default_value=default,
            constraints=predefined_constraints["Positive_Value_Constraint"],
        )


def test_Holder_updates() -> None:
    holder = ConfigHolder(
        parameters={
            "foo": UserParam(
                "foo", "bar", default_value=10, constraints=predefined_constraints["Positive_Value_Constraint"]
            )
        }
    )

    assert holder.get_current_value("foo") == 10

    with pytest.raises(InvalidConfiguration):
        holder.update_value("foo", "bar")

    assert holder.get_current_value("foo") == 10
    holder.update_value("foo", 30)
    assert holder.get_current_value("foo") == 30
