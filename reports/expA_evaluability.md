# E1 evaluability and E3 exclusion composition

Evaluability was computed from empty rasters only, before outcome analysis. No furniture, solver output or FCI was read.

Frozen units: 2742; retained: 2619; excluded: 123.

The 0.60 m walking disc must reach every fixed-service target. At least 50% of raster-furnishable cells must be covered or within 0.60 m extra free-cell travel. The eight-neighbour expansion cannot cross walls or cut blocked corners. Raster-furnishable cells exclude door keepouts and blocked partial boundary cells. Existing 0.15 m source-gap treatment is unchanged; no repair is introduced.

| source   | group    |   n_units |   fraction_within_source |   source_share_within_group |   nia_m2_mean |   nia_m2_median |   nia_m2_q25 |   nia_m2_q75 |   nia_m2_min |   nia_m2_max |   n_rooms_mean |   n_rooms_median |   n_rooms_q25 |   n_rooms_q75 |   n_rooms_min |   n_rooms_max |
|:---------|:---------|----------:|-------------------------:|----------------------------:|--------------:|----------------:|-------------:|-------------:|-------------:|-------------:|---------------:|-----------------:|--------------:|--------------:|--------------:|--------------:|
| all      | excluded |       123 |                    0.045 |                       1.000 |        36.073 |          36.720 |       29.103 |       44.487 |       12.319 |       49.792 |          1.407 |            1.000 |         1.000 |         2.000 |         1.000 |         3.000 |
| all      | retained |      2619 |                    0.955 |                       1.000 |        37.143 |          40.881 |       31.631 |       46.600 |        8.000 |       49.997 |          1.563 |            1.000 |         1.000 |         2.000 |         1.000 |         5.000 |
| D1       | excluded |       112 |                    0.083 |                       0.911 |        36.195 |          36.849 |       29.442 |       44.420 |       12.319 |       49.792 |          1.330 |            1.000 |         1.000 |         2.000 |         1.000 |         3.000 |
| D1       | retained |      1236 |                    0.917 |                       0.472 |        39.291 |          40.471 |       33.547 |       46.402 |       16.750 |       49.997 |          1.355 |            1.000 |         1.000 |         2.000 |         1.000 |         3.000 |
| D2       | excluded |        11 |                    0.012 |                       0.089 |        34.827 |          32.016 |       24.257 |       47.322 |       17.917 |       49.769 |          2.182 |            2.000 |         2.000 |         2.000 |         2.000 |         3.000 |
| D2       | retained |       873 |                    0.988 |                       0.333 |        44.493 |          45.483 |       42.336 |       48.042 |       25.560 |       49.958 |          2.186 |            2.000 |         2.000 |         2.000 |         2.000 |         5.000 |
| D3       | retained |       510 |                    1.000 |                       0.195 |        19.353 |          16.000 |       12.000 |       25.000 |        8.000 |       40.000 |          1.000 |            1.000 |         1.000 |         1.000 |         1.000 |         1.000 |

Pooled outcome means must state this source/size composition shift. NIA-bin and source-specific results describe the retained sample only; binning does not eliminate all within-bin selection bias. D3 is a designed grid, not a population sample.

The fixed-seed E2 sample is in `exclusion_audit_sample.csv`. Cause rendering and classification are a separate no-repair audit.
