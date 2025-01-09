import math
import numpy as np

from SNT import smooth


def normalize(f, minl, maxl, minf, maxf, stretch):
    delta_lambda = maxl - minl
    delta_f = maxf - minf
    q = delta_lambda / delta_f
    return f * q * (1 / stretch)


def rolling_sigma_clip(
    y, x, w_size
):  # w_size number of elements in window, returns new list without outliers, uses median as cent function and sigma=1.5*iqr
    y_clipped = []
    x_clipped = []
    nwindows = len(x) // w_size  # number of windows
    rem = len(x) % w_size  # remaining elements
    w_start = 0
    w_end = 0
    for i in range(0, nwindows):
        w_end += w_size
        w_elements = []
        for j in range(w_start, w_end):
            w_elements.append((y[j], x[j]))
        q75, q25 = np.percentile([x[0] for x in w_elements], [75, 25])
        iqr = q75 - q25
        upper = q75 + 1.5 * iqr
        # lower= q25 - 1.5*iqr for symmetric clip
        for w in w_elements:
            if not (w[0] > upper):  # or (w[0] < lower)): for a symmetric clip
                y_clipped.append(w[0])
                x_clipped.append(w[1])
        w_start = w_end
    if rem != 0:  # calculate for remaining elements
        w_elements = []
        for j in range(w_end, w_end + rem):
            w_elements.append((y[j], x[j]))
        q75, q25 = np.percentile([x[0] for x in w_elements], [75, 25])
        iqr = q75 - q25
        upper = q75 + (1.5 * iqr)
        for w in w_elements:
            if not (w[0] > upper):  # or (w[0] < lower)):
                y_clipped.append(w[0])
                x_clipped.append(w[1])
    return y_clipped, x_clipped


def sigma_clip_iqr(
    distance, anchors_y, anchors_x
):  # (asymetric lower bound only) sigma clipping for points that are too close, uses median as cent function and sigma=1.5*iqr
    l = len(distance)
    q75, q25 = np.percentile(distance, [75, 25])
    iqr = q75 - q25
    lower = q25 - 1.5 * iqr
    for i in range(1, l - 1):  # for each pair keeps the one that maximises equidistance to neighbours
        if distance[i] < lower:
            if distance[i - 1] < distance[i + 1]:
                print("removed close points:", anchors_x[i])
                anchors_x.pop(i)
                anchors_y.pop(i)
            else:
                print("removed close points", anchors_x[i])
                anchors_x.pop(i + 1)
                anchors_y.pop(i + 1)
    return


def abs_rl_slope(a, b, c):
    # calculates the sum of the absolute value of right and left derivative
    #  if they have different signs
    left = (b[1] - a[1]) / (b[0] - a[0])
    right = (c[1] - b[1]) / (c[0] - b[0])
    if left * right < 0:
        return abs(left) + abs(right)
    return 0  # returns 0 if they have the same sign


def remove_peaks(anchors_y, anchors_x, anchors_idx, ntimes):
    # removes the sharpest peaks, alters the original lists, iterates ntimes
    derivatives = []  # derivatives[0]: point , derivatives[1]: sum of abs(left) and abs(right) derivatives
    for i in range(1, len(anchors_y) - 1):  # calculate in groups of 3  until second last
        deriv = abs_rl_slope(
            (anchors_x[i - 1], anchors_y[i - 1]), (anchors_x[i], anchors_y[i]), (anchors_x[i + 1], anchors_y[i + 1])
        )
        if deriv != 0:
            derivatives.append((anchors_x[i], anchors_y[i], deriv))
    dvalues = [dvalue[2] for dvalue in derivatives]
    for j in range(0, ntimes):
        percentile_value = np.percentile(dvalues, 99.5)
        for k, d in enumerate(derivatives):
            if d[2] > percentile_value:
                dvalues.pop(k)
                anchors_idx.pop(anchors_x.index(d[0]))
                anchors_x.remove(d[0])
                anchors_y.remove(d[1])
                derivatives.remove(d)
    return


def distance(x1, y1, x2, y2):
    return math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))


def remove_close(anchors_y, anchors_x):
    l = len(anchors_x)
    dist = []
    for i in range(0, l - 1):
        d = smooth.distance(anchors_x[i], anchors_y[i], anchors_x[i + 1], anchors_y[i + 1])
        dist.append(d)

    sigma_clip_iqr(dist, anchors_y, anchors_x)
    return


def denoise(
    anchors_y, anchors_idx, spectra, window_size
):  # changes each maxima to the average in the window_size, changes list passed as function parameter
    l = len(spectra)
    for i, anchors_idx in enumerate(anchors_idx):
        window_elements = []
        for j in range(0, window_size):
            if (anchors_idx - j) > 0:
                window_elements.append(spectra[anchors_idx - j])
            if (anchors_idx + j) < l:
                window_elements.append(spectra[anchors_idx + j])
        anchors_y[i] = np.median(window_elements)
    return
