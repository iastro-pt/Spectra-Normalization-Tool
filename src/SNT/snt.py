import json
import multiprocessing
from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import Any, Optional

import numpy as np
import scipy.constants as constant
from loguru import logger
from matplotlib import pyplot as plt
from scipy.signal import find_peaks, savgol_filter

from SNT.utils.json_compatible import json_ready_converter
from SNT.utils.SNT_configs import construct_SNT_configs

from .proj_functions import a_shape, continuum, p_map, smooth


def normalize_spectra(
    wavelengths,
    spectra,
    header,
    output_path,
    user_config: dict[str, Any] | None = None,
    FWHM_KW: Optional[str] = None,
    FWHM_override: Optional[float] = None,  # noqa: N803
    store_to_disk: bool = True,
):
    wavelengths = np.asarray(wavelengths)
    spectra = np.asarray(spectra)
    if spectra.ndim == 1:
        wavelengths = wavelengths[np.newaxis, :]
        spectra = spectra[np.newaxis, :]

    if FWHM_KW is None:
        # Default to ESO pipeline
        FWHM_KW = "HIERARCH ESO QC CCF FWHM"

    FWHM = header[FWHM_KW] if FWHM_override is None else FWHM_override  # FWHM in Km/s

    # FWHM_WL=0.1 in case the spectre doesn't include information about FWHM

    config = construct_SNT_configs(user_configs=user_config)

    # ---------------------------------
    logger.debug("Running...")
    # -----------Smoothing------------------------------------------
    continuum_values = np.zeros_like(wavelengths)

    byproducts = defaultdict(list)
    if config["parallel_orders"]:
        ff = partial(normalize_row, FWHM=FWHM, config=config)
        with multiprocessing.Pool(config["Ncores"]) as p:
            out = p.starmap(ff, zip(wavelengths, spectra))
        for index, entry in enumerate(out):
            continuum_values[index] = entry[0]
            for key, value in entry[1].items():
                byproducts[key].append(value)
            byproducts["order_index"].append(index)
    else:
        for row_index, row in enumerate(spectra):
            cont, fit_metrics = normalize_row(wavelengths[row_index], row, FWHM, config=config)
            for key, value in fit_metrics.items():
                byproducts[key].append(value)
            byproducts["order_index"].append(row_index)
            continuum_values[row_index] = cont
    # export results to csv

    if not isinstance(output_path, Path):
        output_path = Path(output_path)
    output_path /= "SNT_data"

    if store_to_disk:
        output_path.mkdir(exist_ok=True)

        logger.info(f"Data storage folder set to {output_path}")
        logger.info("Saving text files")

        with open(output_path / "anchors.csv", mode="w") as tow:
            json.dump(fp=tow, obj=json_ready_converter(byproducts))

        array1 = wavelengths.T
        array2 = continuum_values.T
        merged_array = np.empty((array1.shape[0], array1.shape[1] + array2.shape[1]), dtype=array1.dtype)

        merged_array[:, ::2] = array1
        merged_array[:, 1::2] = array2

        np.savetxt(fname=output_path / "continuum.txt", X=merged_array, delimiter=",", header="wave, flux")
        if config["run_plot_generation"]:
            logger.info("Generating plots")
            fig, ax = plt.subplots(2, sharex=True)
            # To account for the fact that everything will be a list of lists
            for a, b in zip(byproducts["max_pos"], byproducts["max_ys"]):
                ax[0].scatter(a, b, color="g", s=15)
            for a, b in zip(byproducts["anchors_x"], byproducts["anchors_y"]):
                ax[0].scatter(a, b, color="r", s=20)
            for row_index in range(wavelengths.shape[0]):
                ax[0].plot(wavelengths[row_index], spectra[row_index])
                ax[0].plot(wavelengths[row_index], continuum_values[row_index], color="r")
            ax[0].set_ylabel("flux")

            for a, b in zip(byproducts["step_x"], byproducts["step_y"]):
                ax[1].plot(a, b, color="black")
            ax[1].set_xlabel("wavelengths")
            ax[1].set_ylabel("RIC")
            fig.savefig(output_path / "continuum_plot.png", dpi=600)
            # ----------------------------------
    else:
        logger.warning("Disabled disk storage of data products")

    return continuum_values


def normalize_row(wavelengths, spectra, FWHM, config):
    remove_n_first = config["remove_n_first"]
    radius_min = config["radius_min"]
    radius_max = config["radius_max"]
    max_vicinity = config["max_vicinity"]
    global_stretch = config["stretching"]
    use_pmap = config["use_RIC"]
    interp = config["interp"]
    use_denoise = config["use_denoise"]
    usefilter = config["usefilter"]
    nu = config["nu"]
    niter_peaks_remove = config["niter_peaks_remove"]
    denoising_distance = config["denoising_distance"]

    wavelengths_clip = wavelengths[remove_n_first:]
    spectra_clip = spectra[remove_n_first:]

    min_lambda = np.min(wavelengths_clip)
    FWHM_WL = min_lambda * (FWHM / (constant.c / 1000))  # FWHM in A

    spectra_clip, wavelengths_clip = smooth.rolling_sigma_clip(spectra_clip, wavelengths_clip, 20)  # sigma clip twice
    spectra_clip, wavelengths_clip = smooth.rolling_sigma_clip(spectra_clip, wavelengths_clip, 20)

    if usefilter:
        spectra_clip = savgol_filter(spectra_clip, window_length=11, polyorder=3)

    s1 = p_map.rolling_max(spectra_clip, wavelengths_clip, FWHM_WL * 40)
    s2 = p_map.rolling_max(spectra_clip, wavelengths_clip, FWHM_WL * 40 * 10)

    ps = p_map.penalty(s1, s2, wavelengths_clip)
    step = 1 if radius_max < 4 else radius_max / 4
    step_y, step_x = p_map.step_transform(ps, wavelengths_clip, step)

    # ----------Alpha shape maxima selection---------------------

    max_index, peaks = find_peaks(spectra_clip, height=0, threshold=None, distance=max_vicinity)
    wavelengths_a = np.array(wavelengths_clip)
    max_ys = peaks["peak_heights"]
    max_pos = wavelengths_a[max_index]
    anchors_x, anchors_y, anchors_idx = a_shape.anchors(
        max_index,
        spectra_clip,
        wavelengths_clip,
        step_y,
        step_x,
        min_lambda,
        radius_min,
        radius_max,
        nu,
        use_pmap,
        global_stretch,
    )

    # ------------Outlier removal--------------------------------

    smooth.remove_peaks(anchors_y, anchors_x, anchors_idx, niter_peaks_remove)
    smooth.remove_close(anchors_y, anchors_x)

    # --------------Interpolation--------------------------------

    if use_denoise:
        smooth.denoise(anchors_y, anchors_idx, spectra_clip, denoising_distance)

    fx = continuum.interpolate(anchors_x, anchors_y, interp_type=interp)
    fit_metrics = {
        "anchors_x": anchors_x,
        "anchors_y": anchors_y,
        "max_pos": max_pos,
        "max_ys": max_ys,
        "step_y": step_y,
        "step_x": step_x,
        "ps": ps,
    }
    return fx(wavelengths), fit_metrics
