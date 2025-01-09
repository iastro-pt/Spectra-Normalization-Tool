# pylint=disable
from contextlib import AbstractContextManager, nullcontext
from pathlib import Path
from typing import Any, Iterable, Tuple

import pytest

from SNT.utils import parameter_validators
from SNT.utils.exceptions import InternalError, InvalidConfiguration


@pytest.mark.parametrize(
    "test_input,mode,expectation",
    [
        ([1, 2, 3], "all", nullcontext(1)),
        ((1, 2, 3), "all", nullcontext(1)),
        ({1, 2, 3}, "all", nullcontext(1)),
        ({1, 2}, "either", nullcontext(1)),
        ({1}, "either", nullcontext(1)),
        ([1, 2], "all", pytest.raises(InvalidConfiguration)),
        ([55], "either", pytest.raises(InvalidConfiguration)),
    ],
)
def test_IterableMustHave(test_input: Iterable, mode: str, expectation: AbstractContextManager) -> None:
    with expectation as e:
        validator = parameter_validators.IterableMustHave(available_options=(1, 2, 3), mode=mode)
        validator.check_if_value_meets_constraint("foo", test_input)


@pytest.mark.parametrize(
    "test_input,expectation",
    [
        ([1, 2, 3], pytest.raises(InvalidConfiguration)),
        (1, nullcontext(1)),
        (None, nullcontext(1)),
        ("text", nullcontext(1)),
    ],
)
def test_ValueFromList(test_input: Any, expectation: AbstractContextManager) -> None:
    with expectation as e:
        validator = parameter_validators.ValueFromList(available_options=(1, None, "text"))
        validator.check_if_value_meets_constraint("foo", test_input)


@pytest.mark.parametrize(
    "test_input,include_edges,expectation",
    [
        (0, False, pytest.raises(InvalidConfiguration)),
        (5, False, pytest.raises(InvalidConfiguration)),
        (6, False, pytest.raises(InvalidConfiguration)),
        (6, True, pytest.raises(InvalidConfiguration)),
        (5, True, nullcontext()),
        (0, True, nullcontext()),
        (2, True, nullcontext()),
    ],
)
def test_ValueInInterval(test_input: int, include_edges: bool, expectation: AbstractContextManager) -> None:
    with expectation as e:
        validator = parameter_validators.ValueInInterval(interval=(0, 5), include_edges=include_edges)
        validator.check_if_value_meets_constraint("foo", test_input)


@pytest.mark.parametrize(
    "test_input,dtypes,expectation",
    [
        (0, [int], pytest.raises(InternalError)),
        (0.0, (int,), pytest.raises(InvalidConfiguration)),
        (0, (int,), nullcontext()),
    ],
)
def test_ValueFromDtype(test_input: Any, dtypes: Iterable[type], expectation: AbstractContextManager) -> None:
    with expectation as e:
        validator = parameter_validators.ValueFromDtype(dtypes)
        validator.check_if_value_meets_constraint("foo", test_input)


@pytest.mark.parametrize(
    "test_input,include_edges,expectation",
    [
        (0, False, pytest.raises(InvalidConfiguration)),
        (5, False, pytest.raises(InvalidConfiguration)),
        (6, False, pytest.raises(InvalidConfiguration)),
        (4.5, True, pytest.raises(InvalidConfiguration)),
        (1, True, nullcontext()),
        (2, True, nullcontext()),
    ],
)
def test_sum_of_conds(test_input: Any, include_edges: bool, expectation: AbstractContextManager) -> None:
    with expectation as e:
        validator = (
            parameter_validators.ValueInInterval(interval=(0, 5), include_edges=include_edges)
            + parameter_validators.ValueFromList((1, 2, 3, 4.5))
            + parameter_validators.ValueFromDtype((int,))
        )
        validator.check_if_value_meets_constraint("foo", test_input)


@pytest.mark.parametrize(
    "test_input,expectation",
    [
        (Path(__file__) / "random.asda", pytest.raises(InvalidConfiguration)),
        (Path(__file__), nullcontext()),
    ],
)
def test_PathValue(test_input: Path, expectation: AbstractContextManager) -> None:
    with expectation as e:
        validator = parameter_validators.predefined_constraints["PathValue"]
        validator.check_if_value_meets_constraint("foo", test_input)
