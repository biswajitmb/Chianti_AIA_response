# SDO/AIA Temperature Response Functions with CHIANTI v11

This repository provides Python and IDL tools to calculate **SDO/AIA EUV temperature response functions** using **CHIANTI v11**, with an emphasis on exploring **different elemental abundance assumptions** for solar-plasma forward modeling.

## Motivation

AIA temperature response functions depend on the adopted atomic data, elemental abundances, ionization equilibrium, and instrument calibration. Standard response products do not always match the abundance assumptions used in a particular forward model. This project enables users to:

- Generate AIA responses for different **photospheric and coronal abundance models**.
- Recalculate responses using the updated atomic data in **CHIANTI v11**.
- Compare independently calculated responses with **SolarSoft/SSW** reference responses.

## Method

For each AIA channel, the CHIANTI synthetic spectrum is folded through the wavelength-dependent AIA effective area. Detector conversion and normalization factors are applied as required by the chosen response units.

The seven EUV channels considered are **94, 131, 171, 193, 211, 304, and 335 Å**.

## Repository contents

- `codes/generate_AIA_tresp_from_Chianti.py` — generate temperature response functions. The scripts require precomputed CHIANTI spectral emissivity tables, generated assuming a constant electron pressure of \(P_e/k_B = 10^{15}\ \mathrm{cm^{-3}\,K}\). Due to their large file sizes, these tables are not included in the repository.
- `codes/compare_tresp.py` — compare response functions.
- `codes/make_idl_format.pro` — Convert the geerated HDF5 (.h5) files to SSW IDL (.sav) format.
- `effective_area/` — AIA effective-area and reference-response utilities.
- `codes/plots/` — channel-specific comparison figures.
- `outputs/` — generated response products.


```bash
git clone https://github.com/biswajitmb/Chianti_AIA_response.git
cd Chianti_AIA_response
```

Review the configuration and input paths in `codes/generate_AIA_tresp_from_Chianti.py` before running it.

## Notes

- **Comparison with SolarSoft (SSW):** The newly calculated temperature response functions agree well with the SSW-derived responses for most AIA EUV channels. However, noticeable differences are found for the **94 Å and 304 Å passbands**, which require further investigation.

## References

- [CHIANTI atomic database](https://www.chiantidatabase.org/)
- [SDO/AIA instrument paper — Lemen et al. (2012)](https://doi.org/10.1007/s11207-011-9776-8)
- [AIA calibration — Boerner et al. (2014)](https://doi.org/10.1007/s11207-013-0452-z)

**Author:** Biswajit Mondal · [GitHub](https://github.com/biswajitmb)

