import math
from collections import deque

import numpy as np

from SNT import penalty, smooth


def angle(Cx, Cy, Px, Py, r):
    if (Cy - Py) >= 0:
        return -math.acos((Cx - Px) / r) + math.pi
    else:
        return -math.asin((Cy - Py) / r) + math.pi


def anchors(
    max_index, ys, xs, p_ys, p_xs, min_lambda, r_min, r_max, nu, use_pmap, global_stretch
):  # Calculates the anchor points in the alpha hull
    w_stretch = global_stretch
    max_lambda = max(xs)
    min_flux = min(ys)
    max_flux = max(ys)
    furthest_point = (
        math.sqrt(pow(max_lambda, 2) + pow(max_flux, 2)) * global_stretch
    )  # <--adjusted to reflect stretching

    P = np.array(
        [xs[max_index[0]], smooth.normalize(ys[max_index[0]], min_lambda, max_lambda, min_flux, max_flux, w_stretch)]
    )
    Pidx = 0  # index in the max_index array of current anchor
    l = len(max_index)  # total number of points
    anchors_x = []  # list of anchor points
    anchors_y = []  # list of values
    anchors_index = []  # index of anchor points in original arrays

    anchors_x.append(xs[max_index[0]])
    anchors_y.append(ys[max_index[0]])
    anchors_index.append(max_index[0])

    if use_pmap:  # noqa: SIM108
        r = penalty.r_map(
            xs[max_index[0]], p_ys, p_xs, min_lambda, r_min, r_max, nu
        )  # radius adjusted acording to penalty map
    else:
        r = r_min
    while True:
        M = deque()  # list of index of candidate points
        A = []  # list of angles and index of candidate points
        while not M:
            for i in range(Pidx + 1, l):  # test all points to the right of P
                Nx = xs[max_index[i]]
                Ny = smooth.normalize(ys[max_index[i]], min_lambda, max_lambda, min_flux, max_flux, w_stretch)
                if Nx > P[0] + (2 * r):  # if x>Px+(2*r) further points are outside
                    break
                d = np.linalg.norm(P - np.array([Nx, Ny]))
                if d < 2 * r and (P[0] != Nx or P[1] != Ny):  # second condition to avoid duplicate points
                    M.append(i)  # save index of those inside the circ
            r = 1.5 * r
            if P[0] + (2 * r) > furthest_point:  # stop searching for points and return anchors list
                return anchors_x, anchors_y, anchors_index
        r = r / 1.5
        while M:  # for all points in M, compute the angle
            Nidx = M.popleft()
            delta = np.array(
                [
                    xs[max_index[Nidx]] - P[0],
                    smooth.normalize(ys[max_index[Nidx]], min_lambda, max_lambda, min_flux, max_flux, w_stretch) - P[1],
                ]
            )
            delta_norm = math.sqrt((delta[0] ** 2) + (delta[1] ** 2))
            delta_inv = np.array([-delta[1], delta[0]])
            h = math.sqrt((r**2) - ((delta_norm**2) / 4))
            C = P + (0.5 * delta) + ((h / delta_norm) * delta_inv)
            A.append([Nidx, angle(C[0], C[1], P[0], P[1], r)])  # save index and angle in A

        min_val = min(A, key=lambda v: v[1])  # select the min angle
        min_idx = min_val[0]
        # print(P[0], P[1], max_pos[min_idx], max_heights[min_idx], "radius", r)
        P[0] = xs[max_index[min_idx]]  # update P to be the newly selected point
        P[1] = smooth.normalize(ys[max_index[min_idx]], min_lambda, max_lambda, min_flux, max_flux, w_stretch)
        Pidx = min_idx
        if use_pmap:  # update radius
            r = penalty.r_map(P[0], p_ys, p_xs, min_lambda, r_min, r_max, nu)
        else:
            r = r_min
        anchors_x.append(P[0])  # save point coordinates in anchors list
        anchors_y.append(ys[max_index[min_idx]])
        anchors_index.append(max_index[min_idx])
