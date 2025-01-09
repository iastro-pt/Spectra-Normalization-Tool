from __future__ import annotations

from typing import Any

from SNT.utils.configs import ConfigHolder, UserParam
from SNT.utils.parameter_validators import (
    BooleanValue,
    IntegerValue,
    NumericValue,
    Positive_Value_Constraint,
    ValueFromList,
)

_default_params = {
    "remove_n_first": UserParam(
        name="remove_n_first",
        default_value=0,
        constraints=Positive_Value_Constraint + IntegerValue,
        description="removes the first n points in the spectra (only if first points are not useful!) otherwise set to 0",
    ),
    "radius_min": UserParam(
        name="radius_min",
        default_value=20,
        constraints=Positive_Value_Constraint + IntegerValue,
        description="min alpha shape radius",
    ),
    "radius_max": UserParam(
        name="radius_max",
        default_value=70,
        constraints=Positive_Value_Constraint + IntegerValue,
        description="max alpha shape radius (should be at least the size of the largest gap)",
    ),
    "max_vicinity": UserParam(
        name="max_vicinity",
        default_value=10,
        constraints=Positive_Value_Constraint + IntegerValue,
        description="required number of values between adjacent maxima",
    ),
    "stretching": UserParam(
        name="stretching",
        default_value=40,
        constraints=Positive_Value_Constraint + IntegerValue,
        description="normalization parameter",
    ),
    "use_RIC": UserParam(
        name="use_RIC",
        default_value=True,
        constraints=BooleanValue,
        description="use RIC to avoid large 'dips' in the continuum (see documentation)",
    ),
    "interp": UserParam(
        name="interp",
        default_value="linear",
        constraints=ValueFromList(["cubic", "linear"]),
        description="interpolation type",
    ),
    "use_denoise": UserParam(
        name="use_denoise",
        default_value=False,
        constraints=BooleanValue,
        description="for noisy spectra use the average of the flux value around the maximum",
    ),
    "usefilter": UserParam(
        name="usefilter",
        default_value=True,
        constraints=BooleanValue,
        description="use savgol filter to smooth spectra ",
    ),
    "nu": UserParam(
        name="nu",
        default_value=1,
        constraints=NumericValue,
        description="exponent of the computed penalty (see documentation)",
    ),
    "niter_peaks_remove": UserParam(
        name="niter_peaks_remove",
        default_value=10,
        constraints=Positive_Value_Constraint + IntegerValue,
        description="number of iterations to remove sharpest peaks before interpolation",
    ),
    "denoising_distance": UserParam(
        name="denoising_distance",
        default_value=5,
        constraints=Positive_Value_Constraint + IntegerValue,
        description="number of points to calculate the average around a maximum if use_denoise is True, useful for noisy spectra",
    ),
    "parallel_orders": UserParam(
        name="parallel_orders",
        default_value=False,
        constraints=BooleanValue,
        description="Run spectral orders in parallel",
    ),
    "Ncores": UserParam(
        name="Ncores",
        default_value=1,
        constraints=Positive_Value_Constraint,
        description="Number of cores to use, if runnung in parallel mode",
    ),
    "run_plot_generation": UserParam(
        name="run_plot_generation",
        default_value=True,
        constraints=BooleanValue,
        description="Construct plots with the result of the fit",
    ),
}


def construct_SNT_configs(user_configs: dict[str, Any] | None = None) -> ConfigHolder:
    """Construct the SNT config object, with the relevant parameters.

    Args:
        user_configs (dict[str, Any] | None, optional): _description_. Defaults to None.

    Returns:
        ConfigHolder: ConfigHolder object

    """
    internal_configs = ConfigHolder(parameters=_default_params)
    user_configs = {} if user_configs is None else user_configs
    internal_configs.update_values_from_dict(user_configs)
    return internal_configs
