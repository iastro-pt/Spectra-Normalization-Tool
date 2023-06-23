# Spectra-Normalization-Tool
Spectre Normalization Tool (SNT), written by Diogo Marques

## Installation:

```shell
git clone git@github.com:iastro-pt/Spectra-Normalization-Tool.git
```
```shell
cd Spectra-Normalization-Tool
```
```shell
pip install .
```

## How to use:

See the jupyter notebook in the examples folder

## Configuring the tool

The algorithm allows some configuration/tuning of the initial parameters.

Either do:

```python
from SNT import SNT_Configs
config = SNT_Configs()
config.get_description_of_property("remove_n_first")
```

Or check the full table that is provided here:


| Name               | description |
|--------------------|--------------|
| remove_n_first     | removes the first n points in the spectra (only if first points are not useful!) otherwise set to 0 |
| radius_min         | min alpha shape radius                                                                                      |
| radius_max         | max alpha shape radius (should be at least the size of the largest gap)                                     |
| max_vicinity       | required number of values between adjacent maxima                                                           |
| stretching         | normalization parameter                                                                                     |
| use_RIC            | use RIC to avoid large 'dips' in the continuum (see documentation)                                          |
| interp             | interpolation type                                                                                          |
| use_denoise        | for noisy spectra use the average of the flux value around the maximum                                      |
| usefilter          | use savgol filter to smooth spectra                                                                         |
| nu                 | exponent of the computed penalty (see documentation)                                                        |
| niter_peaks_remove | number of iterations to remove sharpest peaks before interpolation                                          |
| denoising_distance | number of points to calculate the average around a maximum if use_denoise is True, useful for noisy spectra |


