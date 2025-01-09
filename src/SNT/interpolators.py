import math
from collections import deque

import numpy as np
from scipy.signal import find_peaks
from scipy import interpolate


def interpolate_wrapper(xs, ys, interp_type):  # interpolate on x and y, acordding to type
    if interp_type == "cubic":
        return interpolate.CubicSpline(xs, ys, bc_type="not-a-knot")
    if interp_type == "linear":
        return interpolate.interp1d(
            xs, ys, kind="linear", axis=-1, copy=True, bounds_error=False, fill_value="nan", assume_sorted=False
        )
    msg = f"Interpolation type of <{type}> not implemented"
    raise NotImplementedError(msg)
