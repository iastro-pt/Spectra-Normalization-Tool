
Configuration of SNT
============================

Every configurable value of SNT comes with a default value that provides a reasonable starting point 
high-resolution and high-SNR spectra. However, it is possible to fine tune the algorithm.

The available (tunable) parameters (alongisde with a description) can be found by doing the following::

    from SNT.utils.SNT_configs import construct_SNT_configs
    confs = construct_SNT_configs()
    confs.print_table_of_descriptions()


In order to update the configurable options, we can pass a dictionary when calling the :py:meth:`SNT.normalize_spectra` function.

Assuming that we previously loaded the wavelengths and spectra: ::

    from SNT import normalize_spectra
    normalize_spectra(
        wavelengths=wavelengths,
        spectra=spectra,
        header=header,
        output_path=output_path,
        user_config={"parallel_orders": True, "Ncores": 2, "run_plot_generation": False},
    )

The new values will go through a validation layer, ensuring that they comply with the expected values