from scipy import interpolate
import math
from scipy.signal import find_peaks
import numpy as np
# class p_map:  # defines methods for computing the penalty map (to increase or decrease the radius in diferent zones)


def b_search(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
    while low <= high:
        mid = (high + low) // 2
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return mid
    return -1


def rolling_max(ys, xs, w_size):
    # adjust aprox continuum using rolling max (w_size=size of the window) and linear interpolation
    x_cont = []
    y_cont = []
    i = 0
    flag = 0
    end_inter = min(xs) + w_size
    while True:
        points_cont = []
        while xs[i] < end_inter:
            points_cont.append((xs[i], ys[i]))
            i += 1
            if i == (len(xs) - 1):
                flag = 1
                break
        max_p = max(points_cont, key=lambda v: v[1])
        x_cont.append(max_p[0])
        y_cont.append(max_p[1])
        end_inter += w_size
        if flag == 1:
            s1 = interpolate.interp1d(
                x_cont,
                y_cont,
                kind="linear",
                axis=-1,
                copy=True,
                bounds_error=False,
                fill_value="nan",
                assume_sorted=False,
            )
            return s1


def penalty(s1, s2, wavelengths):
    # calculates the relative difference between continuums s1 and s2
    ps = []
    s1_w = s1(wavelengths)
    s2_w = s2(wavelengths)

    for s1w, s2w in zip(s1_w, s2_w):
        if math.isnan(s1w) or math.isnan(s2w) or s2w == 0:
            ps.append(0)
        else:
            ps.append(s2w - s1w)
    minp = min(ps)
    maxp = max(ps)
    for idx, p in enumerate(ps):
        ps[idx] = (p - minp) / (maxp - minp)
    return ps


def step_transform(ys, xs, step_size):
    # transforms function into a step function, modifies original YS values
    peak_indices, peaks = find_peaks(ys, height=0, threshold=None, distance=step_size)
    peak_heights = peaks["peak_heights"]
    for i in range(1, len(peak_indices) + 1):  # absolute maximums by descending order
        h2_peak_idx = peak_indices[np.argpartition(peak_heights, -i)[-i]]
        j = 0
        while h2_peak_idx + j < len(xs) and (xs[h2_peak_idx + j] < xs[h2_peak_idx] + step_size):  # step right
            ys[h2_peak_idx + j] = ys[h2_peak_idx]
            j += 1
        j = 0
        while h2_peak_idx - j >= 0 and (xs[h2_peak_idx - j] > xs[h2_peak_idx] - step_size):  # step left
            ys[h2_peak_idx - j] = ys[h2_peak_idx]
            j += 1
    return ys, xs


def r_map(x, p_y, p_x, lambda_min, r_min, r_max, nu):
    # computes the radius at a given x point, p_y, p_x is the computed penalty
    p_idx = b_search(p_x, x)
    p = p_y[p_idx]
    c = x / lambda_min
    return c * (r_min + (r_max - r_min) * (p**nu))
