from typing import Any

from SNT.configs import (
    InternalParameters,
    DefaultValues,
    UserParam,
    IntegerValue,
    Positive_Value_Constraint,
    BooleanValue,
    ValueFromList,
    NumericValue,
)

from tabletexifier import Table


class SNT_Configs:
    _default_params = DefaultValues(
        remove_n_first=UserParam(
            default_value=0,
            constraint=Positive_Value_Constraint + IntegerValue,
            comment="removes the first n points in the spectra (only if first points are not useful!) otherwise set to 0",
        ),
        radius_min=UserParam(
            default_value=20,
            constraint=Positive_Value_Constraint + IntegerValue,
            comment="min alpha shape radius",
        ),
        radius_max=UserParam(
            default_value=70,
            constraint=Positive_Value_Constraint + IntegerValue,
            comment="max alpha shape radius (should be at least the size of the largest gap)",
        ),
        max_vicinity=UserParam(
            default_value=10,
            constraint=Positive_Value_Constraint + IntegerValue,
            comment="required number of values between adjacent maxima",
        ),
        stretching=UserParam(
            default_value=40,
            constraint=Positive_Value_Constraint + IntegerValue,
            comment="normalization parameter",
        ),
        use_RIC=UserParam(
            default_value=True,
            constraint=BooleanValue,
            comment="use RIC to avoid large 'dips' in the continuum (see documentation)",
        ),
        interp=UserParam(
            default_value="linear",
            constraint=ValueFromList(["cubic", "linear"]),
            comment="interpolation type",
        ),
        use_denoise=UserParam(
            default_value=False,
            constraint=BooleanValue,
            comment="for noisy spectra use the average of the flux value around the maximum",
        ),
        usefilter=UserParam(
            default_value=True,
            constraint=BooleanValue,
            comment="use savgol filter to smooth spectra ",
        ),
        nu=UserParam(
            default_value=1,
            constraint=NumericValue,
            comment="exponent of the computed penalty (see documentation)",
        ),
        niter_peaks_remove=UserParam(
            default_value=10,
            constraint=Positive_Value_Constraint + IntegerValue,
            comment="number of iterations to remove sharpest peaks before interpolation",
        ),
        denoising_distance=UserParam(
            default_value=5,
            constraint=Positive_Value_Constraint + IntegerValue,
            comment="number of points to calculate the average around a maximum if use_denoise is True, useful for noisy spectra",
        ),
    )

    def __init__(self, **kwargs):
        self._internal_configs = InternalParameters(
            "SNT",
            self._default_params,
        )
        self._internal_configs.receive_user_inputs(kwargs)

    def __getitem__(self, item):
        return self._internal_configs[item]

    def get_value_of_item(self, item: str) -> Any:
        """Get the current value of a configuration

        Args:
            item (str): Parameter name

        Returns:
            Any: Current value
        """
        return self._internal_configs[item]

    def get_description_of_property(self, name: str) -> str:
        """Get the description of a parameter

        Args:
            name (str): Name of the parameter

        Returns:
            str: Textual description
        """
        return self._internal_configs.get_description_of_config(name)

    def print_table_of_descriptions(self):
        """
        Print a description of every configurable parameter in the SNT module
        """
        tab = Table(
            ("Name", "description"),
        )
        for key in self._internal_configs.get_user_configs():
            tab.add_row((key, self.get_description_of_property(key)))
        print(tab)
