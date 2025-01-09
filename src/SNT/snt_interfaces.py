from SNT.snt import normalize_spectra


def normalize_sBART_object(frame, output_path, user_configs, store_to_disk=True):
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
