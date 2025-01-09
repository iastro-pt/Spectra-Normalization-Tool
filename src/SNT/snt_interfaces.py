from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from SBART.Base_Models import Frame

from SNT.snt import normalize_spectra


def normalize_sBART_object(frame: "Frame", output_path, user_configs, store_to_disk):
    wave, flux, _, _ = frame.get_data_from_full_spectrum()

    return normalize_spectra(
        wavelengths=wave,
        spectra=flux,
        header={},
        FWHM_override=frame.get_KW_value("FWHM"),
        fname=frame.fname,
        store_to_disk=store_to_disk,
        output_path=output_path,
        user_config=user_configs,
    )
