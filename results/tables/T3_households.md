# T3. Household schedules

Author defaults; not empirically calibrated. Units: hours. Cooking and hygiene in fixed rooms are outside the demand denominator.

| household               |   persons |   variants | scope    |   mean_demanded_hours |
|:------------------------|----------:|-----------:|:---------|----------------------:|
| H1_single_commuter      |         1 |          1 | main     |                  18.9 |
| H2_single_remote_worker |         1 |          1 | main     |                  26   |
| H3_couple_one_remote    |         2 |          2 | main     |                  26   |
| H4_parent_child         |         2 |          1 | main     |                  28   |
| H5_older_adult          |         1 |          1 | ablation |                  26   |

Each repeated demand is a separate simultaneous requirement. Storage units affect capacity credit, not demand weight. Alternative days retain their configured frequencies. The mean denominator is descriptive only: FCI must be the frequency-weighted mean of per-variant FCI ratios.

H5 is an ablation only: walking width 0.90 m and global clearance scale 1.2. Full weights, distinct demand IDs and overrides are retained in the CSV.

## H1_single_commuter / normal (frequency 1)

| slot    |   start_hour |   end_hour |   duration_h | demands                                        |   slot_demanded_hours |
|:--------|-------------:|-----------:|-------------:|:-----------------------------------------------|----------------------:|
| night   |           23 |          7 |            8 | sleep_1 (weight=1)                             |                   8   |
| morning |            7 |          9 |            2 | storage (weight=1, units=1); dine_2 (weight=1) |                   4   |
| day     |            9 |         17 |            8 | none                                           |                   0   |
| evening |           17 |         19 |            2 | lounge_1 (weight=1)                            |                   2   |
| dinner  |           19 |         20 |            1 | dine_2 (weight=1)                              |                   1   |
| leisure |           20 |         23 |            3 | lounge_1 (weight=1); work_1 (weight=0.3)       |                   3.9 |

## H2_single_remote_worker / normal (frequency 1)

| slot    |   start_hour |   end_hour |   duration_h | demands                                        |   slot_demanded_hours |
|:--------|-------------:|-----------:|-------------:|:-----------------------------------------------|----------------------:|
| night   |           23 |          7 |            8 | sleep_1 (weight=1)                             |                     8 |
| morning |            7 |          9 |            2 | storage (weight=1, units=1); dine_2 (weight=1) |                     4 |
| day     |            9 |         17 |            8 | work_1 (weight=1)                              |                     8 |
| evening |           17 |         19 |            2 | lounge_1 (weight=1)                            |                     2 |
| dinner  |           19 |         20 |            1 | dine_2 (weight=1)                              |                     1 |
| leisure |           20 |         23 |            3 | lounge_1 (weight=1)                            |                     3 |

## H3_couple_one_remote / normal (frequency 0.857)

| slot    |   start_hour |   end_hour |   duration_h | demands                                        |   slot_demanded_hours |
|:--------|-------------:|-----------:|-------------:|:-----------------------------------------------|----------------------:|
| night   |           23 |          7 |            8 | sleep_2 (weight=1)                             |                     8 |
| morning |            7 |          9 |            2 | storage (weight=1, units=2); dine_2 (weight=1) |                     4 |
| day     |            9 |         17 |            8 | work_1 (weight=1)                              |                     8 |
| evening |           17 |         19 |            2 | lounge_2 (weight=1)                            |                     2 |
| dinner  |           19 |         20 |            1 | dine_2 (weight=1)                              |                     1 |
| leisure |           20 |         23 |            3 | lounge_2 (weight=1)                            |                     3 |

## H3_couple_one_remote / guests (frequency 0.143)

| slot    |   start_hour |   end_hour |   duration_h | demands                                        |   slot_demanded_hours |
|:--------|-------------:|-----------:|-------------:|:-----------------------------------------------|----------------------:|
| night   |           23 |          7 |            8 | sleep_2 (weight=1)                             |                     8 |
| morning |            7 |          9 |            2 | storage (weight=1, units=2); dine_2 (weight=1) |                     4 |
| day     |            9 |         17 |            8 | work_1 (weight=1)                              |                     8 |
| evening |           17 |         19 |            2 | lounge_2 (weight=1)                            |                     2 |
| dinner  |           19 |         20 |            1 | dine_4 (weight=1)                              |                     1 |
| leisure |           20 |         23 |            3 | lounge_2 (weight=1)                            |                     3 |

## H4_parent_child / normal (frequency 1)

| slot    |   start_hour |   end_hour |   duration_h | demands                                          |   slot_demanded_hours |
|:--------|-------------:|-----------:|-------------:|:-------------------------------------------------|----------------------:|
| night   |           23 |          7 |            8 | sleep_1 (weight=1); sleep_1 (weight=1)           |                    16 |
| morning |            7 |          9 |            2 | storage (weight=1, units=1.5); dine_2 (weight=1) |                     4 |
| day     |            9 |         17 |            8 | none                                             |                     0 |
| evening |           17 |         19 |            2 | work_1 (weight=1); lounge_1 (weight=1)           |                     4 |
| dinner  |           19 |         20 |            1 | dine_2 (weight=1)                                |                     1 |
| leisure |           20 |         23 |            3 | lounge_2 (weight=1)                              |                     3 |

## H5_older_adult / normal (frequency 1)

| slot    |   start_hour |   end_hour |   duration_h | demands                                        |   slot_demanded_hours |
|:--------|-------------:|-----------:|-------------:|:-----------------------------------------------|----------------------:|
| night   |           23 |          7 |            8 | sleep_1 (weight=1)                             |                     8 |
| morning |            7 |          9 |            2 | storage (weight=1, units=1); dine_2 (weight=1) |                     4 |
| day     |            9 |         17 |            8 | lounge_1 (weight=1)                            |                     8 |
| evening |           17 |         19 |            2 | lounge_1 (weight=1)                            |                     2 |
| dinner  |           19 |         20 |            1 | dine_2 (weight=1)                              |                     1 |
| leisure |           20 |         23 |            3 | lounge_1 (weight=1)                            |                     3 |

Configuration hash: `bf9718204e1947d63b4d00260c3fc8f3fb1f88322676810f0288f8f29530a3f6`.
