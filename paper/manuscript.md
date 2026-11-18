# Translating furniture into floor area shows where compact homes gain space

**Title options (Cell Press declarative style):**
1. **Selected by the author (2026-11-18):** *Translating furniture into floor area shows where compact homes gain space*
1. *Transformable furniture saves floor area mainly for two-person households in mid-sized compact homes*
2. *Floor area alone misjudges how well compact homes work*
3. *How much floor area can transformable furniture save? Evidence from 2,619 compact homes*

**Authors:** [AUTHOR TO FILL]¹,*
**Affiliations:** ¹[AUTHOR TO FILL]
**Lead contact:** *Correspondence: [AUTHOR TO FILL]

**Keywords:** compact housing, minimum space standards, transformable furniture, functional capacity, layout optimization, equivalent area

## Summary

Shrinking urban homes are regulated mainly by floor area, while transformable furniture is promoted to make small dwellings work. Yet area rules, single-room studies, and layout generators cannot establish how much usable area transformable furniture saves across diverse homes and daily routines. Here, we compare each home with itself under static, form-only, and time-switched furniture strategies—each arranged by constraint optimization and independently verified—and translate capacity differences into equivalent floor area (m²). Across 2,619 compact plans and four household types, most observed plans already function with static furniture. Gains concentrate in two-person households of intermediate compact size, with median identified equivalent-area gains of 6.21 m² for couples and 5.00 m² for parent-and-child households. Fixed 45 m² cutoffs disagree with modeled adequacy on 55.7% of couple and 52.7% of parent-and-child cases, while daily switching saves 2.24 m² for couples in Hong Kong model shells, supporting performance-based supplements to area rules.

## Highlights

- Verified layouts for 2,619 compact plans and four household types
- Transformable furniture helps a minority of plans, mostly two-person households
- Floor-area cutoffs misclassify about half of two-person homes in our model
- Switching furniture states is worth about 2.2 m² for couples in Hong Kong shells

## eTOC blurb

Evaluating 2,619 compact floor plans across four daily household schedules with constraint optimization and independent geometric validation, [AUTHOR TO FILL] show that transformable furniture saves floor area mainly for two-person households in mid-sized compact homes, whereas fixed floor-area cutoffs misclassify roughly half of two-person dwellings, motivating performance-based supplements to area standards.

## Introduction

Urban housing pressure and rising construction costs are shrinking homes across dense cities, and governments largely regulate these compact dwellings by internal floor area alone. Hong Kong's Basic Housing Units Ordinance, for instance, sets a statutory minimum internal floor area of 8 m² for subdivided units, mostly commencing on 1 March 2026 (Government of the Hong Kong Special Administrative Region, 2025), whereas normative scholarship on human flourishing proposes 30, 45, and 60 m² for one-, two-, and three-person households (Ulrich, 2025). How much floor area a household requires also carries major environmental stakes, as effective space use in existing housing can cut operational and embodied carbon more than envelope retrofits for many buildings in the cities studied (Weber et al., 2024). Within this squeeze, transformable furniture—such as wall beds, fold-down desks, and drop-leaf tables—is widely promoted to make small homes work without expanding physical footprints (Goessler and Kaluarachchi, 2023; Daglio et al., 2023).

Despite this promotion, current space regulations and functional housing standards cannot establish how much usable floor area transformable furniture adds across diverse homes and households. Area-only rules count square meters of net internal area (NIA) without testing whether beds, tables, storage, and walking paths fit inside a specific plan, making size an incomplete measure of usability (Özer and Jacoby, 2022). Functional space standards and layout audits improve on area thresholds by checking rooms against furniture lists and dimensional indicators (Pedro, 2009; Mustafa and Ali, 2022; Freimane, 2022; Rakhmatillaeva, 2025; Ulrich, 2025), yet they rely on static furniture in fixed, hand-drawn arrangements and omit time-of-day sharing across a household's daily routine.

Existing transformable-interior studies and computational layout generators leave a complementary gap. Architectural and ergonomic analyses report large localized gains—such as roughly 60% more activity area in one 12 m² bedroom when a wall bed folds up (Bu and Che Mat, 2026), depth compression under ergonomic action domains (Zeng et al., 2026), or user-reported flexibility (Ashkevari and Farhady, 2023; Daglio et al., 2023)—but examine single rooms or designer-chosen layouts that mix furniture capability with manual drawing skill. Meanwhile, computational layout methods synthesize static or ergonomics-guided residential scenes (Merrell et al., 2011; Yu et al., 2011; Sun et al., 2025; Li et al., 2026; Nieciecki et al., 2026; Xiang et al., 2026) or design reconfigurable assemblies and multi-state transitions (Garg et al., 2016; Xiong et al., 2021; Fu et al., 2024; Liu et al., 2025; Zhang et al., 2025; Xiong et al., 2026), yet they do not tie shared-position furniture states to a 24-hour household schedule, guarantee walkable reachability from the entrance, or translate capacity gains into floor area across housing stocks. No existing method jointly represents who uses a home and when, which furniture can change state, and whether every scheduled arrangement is collision-free and reachable, expressed in m².

In this paper, we quantify schedule-weighted residential capacity across compact homes and translate the effect of transformable furniture into equivalent floor area (Figure 1). Our key idea is to compare each home with itself under three furniture strategies—static (S0), form only (S1, admitting transformable furniture in a single daily state), and form + time (S2, allowing transformable furniture at fixed positions to switch states between daily time slots)—giving each strategy its best optimized arrangement and checking every layout with an independent geometric validator. Specifically, we measure a functional capacity index (FCI) as the share of scheduled, weighted activity-hours served over 24 h; optimize discrete poses via constraint programming with greedy warm starts and lazy reachability cuts; independently verify zero overlap, unobstructed clearances, and 0.60 m walkable access; and map paired S2 versus S0 differences onto the static area–capacity curve to obtain equivalent-area gain ($\Delta\text{EA}$, in m²) and adequate area ($A_{\min}$ at $\text{FCI} \ge 0.95$). Optimizing each strategy within the same shell isolates furniture capability from designer skill, while separating the form effect ($\text{S1} - \text{S0}$) from the time or switching effect ($\text{S2} - \text{S1}$) distinguishes compact geometry from daily temporal reuse.

Across 2,619 compact plans and four household types, we find that the space-saving value of transformable furniture is substantial where static layouts bottleneck, but conditional on household composition and dwelling size. Most observed plans already function with static furniture, concentrating gains in two-person homes of intermediate compact size, where median identified positive $\Delta\text{EA}$ reaches 6.21 m² for couples and 5.00 m² for parent-and-child households. Because plan geometry creates wide functional spread at a given area, a 45 m² two-person cutoff disagrees with modeled S2 adequacy on 55.7% of couple and 52.7% of parent-and-child cases, mostly rejecting workable compact homes. In Hong Kong model shells, switching furniture states over the day is worth 2.24 m² of minimum adequate area for couples.

This study makes three contributions: (1) a schedule-aware, independently verifiable measure of functional capacity (FCI) translatable to equivalent floor area ($\Delta\text{EA}$) and adequate area ($A_{\min}$); (2) corpus-scale paired evidence showing where transformable form and daily switching save floor area and why the smallest and largest compact homes gain little; and (3) an empirical test of area-only housing standards, with a Hong Kong scenario demonstrating that furniture dimensions should be chosen by size band.

## Results

### A verified, schedule-aware comparison of furniture strategies

To evaluate furniture strategies across diverse residential geometries, we assembled 2,742 compact dwelling units within 8–50 m² of net internal area (NIA)—defined as interior furnishable, storage-only, walkable-only, and fixed-service floor space, excluding walls and balconies—and screened each unfurnished plan on a 0.10 m raster for unobstructed 0.60 m entrance-to-service access (Figure 1; Table 1; Figure S1). Excluding 123 units that failed this empty-geometry walkability screen yielded 2,619 evaluable dwellings: 2,109 observed plans drawn from Swiss Dwellings (1,236 plans; NIA 16.75–50.00 m², median 40.47 m²) and ResPlan (873 plans; NIA 25.56–49.96 m², median 45.48 m²), alongside 510 controlled generated shells spanning 8.00–40.00 m² NIA (median 16.00 m²) that extend coverage down to Hong Kong's 8 m² statutory threshold, below the smallest observed plan at 16.75 m² NIA (Table 1; Figure S1). Each dwelling was evaluated against four 24-hour household schedules partitioned into six daily slots—single commuter, single remote worker, couple (including one remote worker and an alternate guest-dining day occurring at frequency 0.143 alongside normal days at 0.857), and parent and child (requiring two separate single sleeping surfaces)—using a dimension-audited static and transformable furniture library (Table 1; Table 2; Table S1). Across all 2,619 dwellings, four households, and three strategies (S0, S1, and S2), the search and independent validator produced 31,428 geometrically verified layouts.

Tracking individual homes across Night, Workday, and Dinner slots illustrates when daily state switching unlocks capacity and when plan geometry prevents it (Figure 2; Figure S2). In an 18.00 m² generated shell occupied by a couple, static furniture (S0) achieves an FCI of 0.937 with zero transformation burden ($\text{TB} = 0.00$), and form-only transformable furniture (S1) reaches 0.942 ($\text{TB} = 0.00$), because neither single-state arrangement can simultaneously fit a double sleeping surface, a dedicated daytime workspace, two-person lounging, and dining clearances without collision (Figure 2). Allowing daily state switching at fixed furniture anchors (S2; $\text{TB} = 3.00$) deploys a double wall bed at night and stows it during daytime slots, raising coverage to full capacity ($\text{FCI} = 1.000$; Figure 2). By contrast, in a 10.00 m² generated shell, no double sleeping surface fits with valid clearance and access in any slot, capping FCI at 0.577 under S0 and 0.687 under both S1 and S2 with no daily state changes ($\text{TB} = 0.00$; Figure 2; Figure S2). Similarly, in a partitioned 29.97 m² observed plan from Swiss Dwellings, narrow room dimensions and doorway keep-outs restrict FCI to 0.668 under S0 and 0.687 under S1 and S2 ($\text{TB} = 0.00$; Figure 2; Figure S2), showing that interior geometry—not total floor area alone—governs whether multi-state furniture can expand usable capacity.

To check whether paired differences reflect furniture capability rather than incomplete layout search, we benchmarked the warm-started production pipeline against standalone CP-SAT, greedy footprint placement, and standalone simulated annealing across 200 stratified unit–household pairs under S2 (Figure S3; Table S2). Every method returned 100.0% independently valid layouts across all 200 pairs. The production pipeline achieved the highest mean FCI at 0.9428 (median 1.0000; summed S0 + S1 + S2 mean solve time 53.86 s, median 10.68 s), exceeding greedy placement (mean FCI 0.8612; mean 3.47 s), standalone CP-SAT (0.8675; 38.45 s), and standalone simulated annealing (0.9341; 104.12 s, median 108.33 s; paired production-minus-annealing difference +0.0087 FCI, 95% CI [0.0016, 0.0160]). Production matched the highest FCI observed across all four search methods on 189 of the 200 pairs, with a mean shortfall of only 0.0034 FCI across the remaining 11 cases (Figure S3; Table S2).

### Most compact plans already function with static furniture

Across the 2,109 observed compact plans, static furniture (S0) already serves the entire daily activity schedule ($\text{FCI} = 1$) in the clear majority of dwellings for every household type (Figure 3; Table 3). Specifically, S0 achieves full functional capacity in 90.8% of observed plans for a single commuter, 89.1% for a single remote worker, 72.7% for a couple, and 61.0% for a parent and child—spanning 88.5%, 85.9%, 59.1%, and 43.2% in Swiss Dwellings and 94.0%, 93.6%, 92.1%, and 86.3% in the larger-footprint ResPlan sample (Table 3).

Because static layouts already saturate scheduled demand in more than half of observed plans for every household—and pairs with identical S0 and S2 scores map to an exact zero area difference—the all-pair median equivalent-area gain ($\Delta\text{EA}$) on observed plans is 0 m² (support bounds 0.00–0.00 m²) across all four household schedules (Table 3). Even across the 510 generated shells, which deliberately concentrate sampling in 8–16 m² footprints, S0 provides full functional capacity ($\text{FCI} = 1$) for 54.9% of single commuters and 53.9% of single remote workers (yielding 0.00–0.00 m² all-pair median $\Delta\text{EA}$), compared with 31.6% for couples (all-pair median $\Delta\text{EA}$ 1.34 m²) and 26.7% for parent-and-child households (all-pair median bounds 0.83–0.86 m²; Table 3). Transformable furniture therefore acts not as an across-the-board space multiplier, but as a targeted intervention for plans and households where static furniture hits a geometric ceiling.

### Gains concentrate in two-person households at intermediate sizes

Allowing transformable form and daily state switching (S2 versus S0) improves FCI in a small fraction of single-person observed plans—7.5% (159 of 2,109) for the single commuter and 8.7% (184 of 2,109) for the single remote worker—but in a substantial share of two-person observed plans: 23.5% (496 of 2,109) for the couple and 35.9% (757 of 2,109) for the parent and child (Figure 3; Figure 4; Table 3). Among improved observed-plan pairs whose S0 and S2 scores invert within the interior support of the observed-plan static reference curve, the median identified positive $\Delta\text{EA}$ is 1.33 m² (95% CI [0.75, 3.11], $n = 160$ identified plus 24 support-bounded pairs; improved-group median lower bound $\ge 1.33\text{ m}^2$) for the single remote worker, 6.21 m² ([4.20, 10.00], $n = 448$ identified plus 48 bounded; lower bound $\ge 6.21\text{ m}^2$) for the couple, and 5.00 m² ([4.20, 8.00], $n = 721$ identified plus 36 bounded; lower bound $\ge 5.00\text{ m}^2$) for the parent and child (Table 3). For the single commuter, all 159 improved observed-plan pairs invert at the lower boundary of the observed-plan static curve (16.75 m²), leaving the point-identified median unavailable and establishing a support-limited lower bound of $\ge 2.00\text{ m}^2$ among improved pairs (Table 3). Likewise, for the six observed-plan couple pairs in the smallest observed bin (16–18 m²), the observed-plan reference yields a median $\Delta\text{EA}$ lower bound of 16.6 m² with no finite upper bound, whereas re-inverting those same scores on the pooled static reference (which incorporates generated shells down to 8 m²) identifies a median gain of 8.2 m² (Figure 4).

Evaluating the controlled generated shells (8.00–40.00 m² NIA) resolves the complete size profile and reveals a nonmonotonic relationship between dwelling area and space savings (Figure 4). Rather than peaking in the smallest shells, two-person equivalent-area gains start small, peak at intermediate compact sizes, and decline to zero once static layouts fit. For a couple in generated shells, the all-pair median $\Delta\text{EA}$ rises from 0.75 m² (9.2% of NIA) at 8–10 m² to a peak of 7.32 m² (49.8% of NIA) at 14–16 m², before declining to 0 m² in evaluated bins from 24 m² onward (Figure 4). Similarly, for a parent and child, the all-pair median $\Delta\text{EA}$ increases from 0.69 m² (7.6% of NIA) at 8–10 m² to 6.00 m² (33.3% of NIA) at 18–20 m² and reaches 0 m² from 28 m² onward (Figure 4). In the tightest 8–10 m² shells, even stowed or deployed transformable footprints and operating clearances cannot fit alongside wet-service access, limiting how much capacity transformability can add. Measured at the adequacy crossing ($\text{FCI} \ge 0.95$), S2 reduces the minimum adequate area $A_{\min}$ on observed plans by 10.78 m² (95% CI [9.15, 12.70], from 33.96 m² [33.21, 34.67] under S0 to 23.18 m² [21.27, 24.73] under S2) for the parent-and-child household—the one observed-plan contrast with both crossings inside observed NIA support—and reduces $A_{\min}$ across generated shells by 1.68 m² ([1.12, 2.38]) for a single commuter, 3.63 m² ([2.78, 4.77]) for a single remote worker, 5.53 m² ([4.90, 6.12]) for a couple, and 6.45 m² ([5.19, 7.75]) for a parent and child (Table 3).

### Changing form and changing over time help different households

Decomposing the total functional gain ($\text{S2} - \text{S0}$) into the form effect ($\text{S1} - \text{S0}$) and the time or switching effect ($\text{S2} - \text{S1}$) shows that households benefit through distinct physical mechanisms (Figure 3; Table 3). On observed plans, single-person improvements stem almost entirely from compact transformable form rather than slot-to-slot state changes: the mean form effect is 0.0085 FCI (95% CI [0.0071, 0.0100]) versus a mean time effect of 0.0002 FCI ([0.0000, 0.0003]) for the single commuter, and 0.0107 FCI ([0.0090, 0.0125]) versus 0.0001 FCI ([0.0000, 0.0002]) for the single remote worker (Table 3). Between the two-person households, however, the roles of form and time diverge. For the parent-and-child schedule, which requires two single sleeping surfaces at night and concurrent work and lounging in the early evening, the mean form effect on observed plans is 0.0271 FCI ([0.0249, 0.0292]) while the mean time effect is only 0.0017 FCI ([0.0013, 0.0022]), indicating that compact item footprints do nearly all the work without daily state switching. For the couple, by contrast, the mean form effect (0.0130 FCI, [0.0112, 0.0148]) and mean time effect (0.0112 FCI, [0.0094, 0.0130]) contribute almost equally on observed plans—and both remain substantial in generated shells (0.0709 [0.0621, 0.0795] and 0.0372 [0.0303, 0.0447] FCI, respectively; Table 3)—because stowing a double wall bed by day directly frees floor space for daytime remote work, dining, and two-person lounging.

Sensitivity analyses indicate that this mechanistic split is not driven by bed-clearance conventions or solver settings, while highlighting the acute sensitivity of compact plans to circulation width (Figure S5). Because the standard catalogue requires left and right side clearances on double beds and deployed double wall beds (Table S1), we tested a separate variant allowing mirrored one-side access across 348 small units ($\le 20\text{ m}^2$ NIA); the couple's mean time effect changed by only $-0.0122$ FCI (95% CI [$-0.0203$, $-0.0040$]), and across the 18 observed plans in that size band the interval included zero. Across the 200 benchmark pairs and 50-unit solver subsamples, the largest absolute changes in mean S2 FCI were $-0.0160$ when scaling operating clearances by $0.8\times$ or $1.2\times$ (couple at $1.2\times$) and $-0.0102$ when varying solver caps across 30, 60, and 120 s (parent and child at 60 s), while among single-item transformable removals, dropping the drop-leaf table produced the largest reduction ($-0.0267$ for couples and $-0.0199$ for parent and child; Figure S5). In contrast, widening required walking circulation from 0.60 m to 0.90 m reduced mean S2 FCI by 0.5151 for the parent-and-child schedule across 49 matched units (Figure S5), showing that accessibility-grade circulation demands substantially larger shells than standard 0.60 m passage rules.

### Floor area alone misjudges functional adequacy

Testing statutory and normative floor-area cutoffs against modeled functional adequacy ($\text{FCI} \ge 0.95$) shows that area thresholds frequently misclassify two-person compact homes (Figure 5; Table 4). Evaluated across all 2,109 observed plans under S2, Ulrich's (2025) 45 m² two-person benchmark disagrees with modeled adequacy on 55.7% of couple cases and 52.7% of parent-and-child cases (Table 4). Nearly all of these disagreements are false negatives—dwellings smaller than 45 m² that nonetheless serve at least 95% of scheduled activity-hours with independently verified clearances and access (1,150 false negatives versus 25 false positives for couples; 1,090 false negatives versus 22 false positives for parent and child; Table 4). Disagreement is already large under static furniture (S0), reaching 47.0% for couples (940 false negatives, 52 false positives) and 40.5% for parent-and-child households (789 false negatives, 66 false positives), and increases under S2 because transformable layouts make additional sub-45 m² plans adequate. For one-person schedules on observed plans, Ulrich's 30 m² benchmark disagrees with S2 adequacy on 10.4% of single-commuter and 11.1% of single-remote-worker cases (versus 14.5% and 16.4% under S0; Table 4).

This classification error arises because dwellings of identical floor area vary widely in usable capacity owing to room proportions, partition walls, and door and window positions—consistent with Özer and Jacoby's (2022) static usability findings and extending them to scheduled and transformable layouts (Figure 5). Within narrow 2 m² NIA bins on observed plans, the interquartile range of static (S0) FCI reaches 0.205 for couples at 26–28 m² and 0.190 for parent-and-child households at 24–26 m² (Figure 5). At the opposite regulatory extreme, Hong Kong's statutory 8 m² basic housing unit minimum sits below every observed plan in Swiss Dwellings and ResPlan (all $\ge 16.75\text{ m}^2$), yielding zero negative predictions on observed plans (Table 4). On the 510 generated shells (8.00–40.00 m²), however, an 8 m² pass threshold disagrees with S2 adequacy on 30.0% of single-commuter, 27.3% of single-remote-worker, 40.4% of couple (206 false positives), and 49.6% of parent-and-child (253 false positives) cases, passing ultra-small shells that cannot support basic daily schedules (Table 4).

### What this means for Hong Kong's smallest homes

To examine how floor-area minimums, daily switching, and furniture dimensions interact in ultra-compact housing, we evaluated 390 Hong Kong model shells—30 matched aspect-ratio and opening templates at each integer NIA from 8 to 20 m²—using a shared dimension-sensitive quality index ($\text{FCI}_q$, with adequacy at $\text{FCI}_q \ge 0.95$; Figure 6; Table S4). Hong Kong's 2021 Population Census records 215,709 residents and 107,371 households living in 108,202 subdivided units across 33,658 quarters (Table 1), but public tabulations omit the joint distribution of household size and floor area required to weight territory-wide stock totals; our scenario estimates therefore describe the modeled shell templates directly. With standard catalogue dimensions, moving from static (S0) to time-switched transformable furniture (S2) reduces the minimum adequate area $A_{\min}$ from 13.40 m² (95% CI [13.03, 13.73]) to 12.37 m² ([12.00, 12.70]; 12.30 m² [11.90, 12.64] under matched extra catalogue search) for a single commuter, and from 19.58 m² ([18.78, 19.96]) to 17.07 m² ([16.58, 17.64]) for a parent and child—a reduction of 2.51 m² ([1.86, 3.03]; Figure 6). For a couple, static furniture leaves $A_{\min}$ above the 20 m² grid support (only 11 of 30 shells are adequate at 20 m²), whereas moving from fixed-state (S1) to time-switched (S2) transformable furniture lowers $A_{\min}$ from 18.57 m² ([18.18, 19.02]) to 16.33 m² ([15.87, 16.83]), isolating a daily state-switching reduction of 2.24 m² ([1.66, 2.82]; Figure 6).

Testing parametric furniture kits on 8–15 m² training shells ($n = 30$) and transferring the selected fixed designs to held-out generated shells ($n = 15$), small observed plans ($\le 20\text{ m}^2$, $n = 15$), and the 390 Hong Kong model shells shows that custom kit sizing offers no improvement over standard dimensions for a single commuter (Figure 6; Table S4). Across the training shells, the highest-ranking commuter kit (0.80 m single wall bed, $0.80 \times 0.45\text{ m}$ fold-down desk, $0.70 \times 0.60\text{ m}$ drop-leaf table, and 0.60 m wardrobe frontage) differed from the standard catalogue by $+0.0013$ $\text{FCI}_q$ (95% CI [$-0.0153$, $+0.0200$]) while reaching adequacy on fewer shells (11 of 30 versus 13 of 30; Table S4). Across the 390 Hong Kong model shells, this compact kit reached adequacy in 184 of 390 shells versus 246 of 390 for the optimized catalogue (paired mean $\text{FCI}_q$ difference $-0.0389$, [$-0.0564$, $-0.0230$]), because downsized surfaces incur quality penalties without unlocking enough ultra-small shells (Figure 6; Table S4).

For a couple, by contrast, a larger parametric kit (1.50 m double wall bed, $1.20 \times 0.55\text{ m}$ fold-down desk, $1.00 \times 0.75\text{ m}$ drop-leaf table, and 1.40 m wardrobe frontage) creates a clear size-band trade-off (Figure 6; Table S4). On the 30 training shells under matched extra search, its paired mean $\text{FCI}_q$ difference over the catalogue was $+0.0021$ (95% CI [$-0.0336$, $+0.0279$], confidence interval including zero), reaching adequacy on 5 of 30 shells versus 2 of 30 for the catalogue (Table S4). Across the 390 Hong Kong model shells, this larger kit yielded a modeled $A_{\min}$ of 15.39 m² ([14.67, 16.19]) compared with 16.12 m² ([15.70, 16.57]) for the optimized catalogue (154 versus 132 adequate shells overall), raising adequacy in the 13–16 m² band from 30 of 120 to 51 of 120 shells (+21 shells) while achieving adequacy on 0 of 150 shells at 8–12 m² and reducing mean $\text{FCI}_q$ below 13 m² from 0.500 to 0.448 (Figure 6; Table S4). Furniture dimensions should therefore be chosen per floor-area band rather than fixed across all compact homes.

## Discussion

Across 2,619 compact residential plans and four household schedules, our analysis shows that the space-saving value of transformable furniture is substantial where static arrangements hit geometric bottlenecks, yet conditional on household composition and dwelling size. Most observed compact homes already serve scheduled daily activities with static furniture, concentrating equivalent-area gains in two-person households occupying intermediate compact sizes—driven primarily by compact multi-state form for a parent and child, and by nearly equal contributions of form and daily state switching for a couple—whereas the smallest shells lack room even for stowed or deployed transformable clearances. At the same time, dwellings of identical net internal area exhibit wide differences in verified functional capacity, causing fixed area thresholds to misclassify roughly half of observed two-person cases. Floor area alone is therefore a weak proxy for whether a compact dwelling works, whereas schedule-aware geometric verification pinpoints where furniture substitutes for space and where physical footprint remains binding.

These results clarify how large localized gains reported in single-room design studies relate to whole-dwelling performance across housing stocks. Analytical and prototype studies of individual rooms—such as Bu and Che Mat's (2026) comparison of a $4 \times 3\text{ m}$ bedroom reporting roughly 60% more clearance-inclusive free activity area (from about 5–5.5 m² to about 8 m²) when a wall bed is folded, open-floor comparisons in a modeled 35 m² flat (Elmurodov and Mametova, 2026), or case-study projections of adaptive space efficiency (Goessler and Kaluarachchi, 2023)—measure open floor space under a chosen arrangement. Evaluating an approximate $4 \times 3\text{ m}$ room envelope and 12 m² generated analogues under scheduled single-person demand and whole-home body-free accounting (Figure S6) yields 7.60 m² of daytime body-free area under both S0 and S2 in the approximate room because static placement already satisfies the full schedule without forced folding, $-0.52$ to $+1.38\text{ m}^2$ across the 12 m² analogues, and a median daytime body-free area change of 0 m² across all 2,109 observed plans and 510 generated shells for both single-person schedules. Rather than contradicting single-room designs, this difference reflects measure and scope: maximizing open daytime floor space in one room answers a different question than whether a whole dwelling's sleeping, work, dining, lounging, storage, cooking, and sanitary needs are jointly reachable over 24 h. Coupling multi-state furniture and daily schedules with independent access checks thus extends static functional standards (Pedro, 2009; Ulrich, 2025), empirical plan-usability evaluations (Özer and Jacoby, 2022; Freimane, 2022; Mustafa and Ali, 2022; Rakhmatillaeva, 2025), and ergonomic depth-compression models (Zeng et al., 2026), while complementing Weber et al.'s (2024) static excess-area carbon model.

Translating functional capacity into square meters offers actionable guidance for housing regulators, interior designers, and furniture manufacturers. For regulators, fixed floor-area minimums face a sharp classification dilemma: generous cutoffs such as 45 m² reject more than a thousand observed two-person compact plans that accommodate scheduled activities with verified clearances, whereas ultra-low minimums such as 8 m² pass shells in which basic one- and two-person schedules cannot physically fit. Performance-based checks—such as allowing compact units near a regulatory threshold to demonstrate compliance through an independently verified, reachable layout for an intended household schedule—can supplement statutory area minimums without rewarding unworkable micro-shells. For designers and manufacturers, space-saving investment should target two-person dwellings of roughly 12–30 m² NIA, prioritizing reliable day–night state switching for couples and compact multi-state footprints for parent-and-child households. Moreover, standardized furniture kits should be sized by floor-area band rather than marketed as universal micro-living packages, as larger couple surfaces expand adequacy across 13–16 m² Hong Kong model shells while reducing capacity below 13 m², and downsized commuter kits do not improve upon standard catalogue pieces.

For housing and computational design researchers, our modular evaluation pipeline and negative surrogate findings highlight both transferability and the continuing need for explicit geometric search. Because plan rasterization, household schedules, furniture catalogues, constraint solving, and independent validation are decoupled, the framework transfers directly to housing stocks in other cities, alternative cultural schedules, or stricter accessibility rules such as 0.90 m wheelchair circulation (Figure S5). Conversely, geometry-only learned models—including GraphSAGE over room-and-opening graphs—did not reach the prespecified ranking criterion on held-out observed sites (Figure S4; Table S3), showing that doorway keep-outs, discrete pose packing, and multi-slot reachability create sharp geometric thresholds where explicit optimization with independent validation remains necessary.

### Limitations of the study

Three scope boundaries frame the interpretation of our results and point to future research. (1) FCI measures geometric fit and walkable access for scheduled furniture activities, not acoustic or visual privacy, daylight quality, thermal comfort, ceiling-height perception, or occupant satisfaction; future post-occupancy and immersive-evaluation studies should link FCI and transformation burden to resident wellbeing and observed daily switching behavior. (2) Our four primary households and audited furniture library represent stylized daily schedules and representative product dimensions rather than exhaustive population heterogeneity, although the open pipeline accepts custom time-use diaries, assistive-mobility clearances, and local furniture catalogues. (3) Our Hong Kong analysis evaluates a controlled grid of 8–20 m² model shells rather than weighted territory-wide stock totals because public census tables lack the joint distribution of household size and subdivided-unit floor area, motivating future linkage with measured subdivided-unit floor-plan surveys.


## STAR Methods

### Key resources table

| REAGENT or RESOURCE | SOURCE | IDENTIFIER |
| :--- | :--- | :--- |
| **Deposited data** | | |
| Swiss Dwellings v3.0.0 floor-plan dataset (D1) | Standfest et al. (2022) | https://doi.org/10.5281/zenodo.7788422 |
| ResPlan residential floor-plan dataset (D2) | Abouagour and Garyfallidis (2025) | https://doi.org/10.48550/arXiv.2508.14006; https://github.com/m-agour/ResPlan |
| Amazon Berkeley Objects product listings (D4) | Collins et al. (2022) | https://amazon-berkeley-objects.s3.amazonaws.com/index.html |
| Hong Kong 2021 Population Census Subdivided Units (D6) | Census and Statistics Department, Hong Kong SAR | https://data.gov.hk/en-data/dataset/hk-censtatd-census_geo-2021-population-census-su-by-dcd |
| **Software and algorithms** | | |
| Python 3.11.18 | Python Software Foundation | https://www.python.org/ |
| Google OR-Tools CP-SAT 9.15.6755 | Google (Perron et al., 2023) | https://developers.google.com/optimization |
| PyTorch 2.7.1 | PyTorch Foundation | https://pytorch.org/ |
| LightGBM 4.7.0 | Microsoft | https://lightgbm.readthedocs.io/ |
| scikit-learn 1.9.1 | scikit-learn developers | https://scikit-learn.org/ |
| GraphSAGE surrogate implementation (PyTorch 2.7.1) | GraphSAGE architecture; this paper | https://snap.stanford.edu/graphsage/; https://github.com/Casey-sketch-cyber/research |
| Shapely 2.2.0 | Shapely developers | https://shapely.readthedocs.io/ |
| NetworkX 3.6.1 | NetworkX developers | https://networkx.org/ |
| NumPy 2.4.6, pandas 3.1.1, SciPy 1.17.1, Matplotlib 3.11.2 | Scientific Python ecosystem | https://numpy.org/; https://pandas.pydata.org/; https://scipy.org/; https://matplotlib.org/ |
| Blender 4.5.3 LTS | Blender Foundation | https://www.blender.org/ |
| Schedule-constrained layout optimization, independent validator, and analysis pipeline | This paper | https://github.com/Casey-sketch-cyber/research; Zenodo DOI: [TO MINT] |

### Resource availability

#### Lead contact

Further information and requests for resources should be directed to and will be fulfilled by the lead contact, [AUTHOR TO FILL].

#### Materials availability

This study did not generate new physical materials or reagents.

#### Data and code availability

- **Data:** All empirical datasets analyzed in this study are publicly available from their original repositories: Swiss Dwellings v3.0.0 (Standfest et al., 2022; https://doi.org/10.5281/zenodo.7788422), ResPlan (Abouagour and Garyfallidis, 2025; https://doi.org/10.48550/arXiv.2508.14006; https://github.com/m-agour/ResPlan), Amazon Berkeley Objects listings (https://amazon-berkeley-objects.s3.amazonaws.com/index.html), and Hong Kong 2021 Population Census Subdivided Units tabulations (https://data.gov.hk/en-data/dataset/hk-censtatd-census_geo-2021-population-census-su-by-dcd). Derived summary tables, validated showcase layouts, and scene verification manifests are committed in the study repository.
- **Code:** All original source code for corpus normalization, candidate pose generation, warm-started CP-SAT optimization, independent geometric validation, statistical resampling, 2D plotting, and 3D Blender Cycles scene verification is publicly available at https://github.com/Casey-sketch-cyber/research and archived on Zenodo at DOI [TO MINT].
- **Additional information:** Any additional information required to reanalyze the data reported in this paper is available from the lead contact upon request.

### Method details

#### Overview of the evaluation framework

To measure how much usable floor area transformable furniture adds without confounding furniture capability with manual layout drawing, we evaluate each compact dwelling against itself across three furniture strategies—static (S0), form only (S1), and form + time (S2)—using automated constraint optimization followed by an independent geometric and reachability validator (Figure 1). The pipeline comprises eleven modular stages: (1) plan normalization, net internal area (NIA) measurement, and empty-geometry evaluability screening; (2) 24-hour household activity schedules; (3) an audited static and transformable furniture library; (4) within-shell strategy definitions; (5) discrete candidate generation and warm-started CP-SAT optimization; (6) independent validation of collisions, clearances, and walkable access; (7) schedule-weighted scoring of the functional capacity index (FCI) and transformation burden (TB); (8) monotone static curve inversion for equivalent-area gain ($\Delta\text{EA}$) and support bounds; (9) logistic crossing estimation for adequate area ($A_{\min}$); (10) solver benchmarking, area-cutoff comparisons, sensitivity analyses, room-level comparisons, and geometry-only surrogate tests; and (11) parametric furniture kit sizing and the Hong Kong subdivided-unit scenario.

#### Dwelling corpus, net internal area, and evaluability screen

Comparing housing standards and furniture strategies across floor-plan collections requires a consistent interior floor-area definition and a check that unfurnished geometries are physically traversable. We assembled compact dwellings in the inclusion band of 8–50 m² of net internal area (NIA) from two public repositories of observed plans—Swiss Dwellings v3.0.0 (D1; Standfest et al., 2022) and ResPlan (D2; Abouagour and Garyfallidis, 2025)—together with a controlled parametric grid of generated shells (D3; Table 1; Figure S1). NIA is defined as the union of interior furnishable space (bedrooms, living rooms, dining rooms, studies, studios, and general habitable rooms), storage-only space (cloakrooms and storerooms), walkable-only circulation and kitchen circulation space (corridors, halls, foyers, lobbies, and kitchen/kitchen-dining zones), and fixed-service space (bathrooms, sanitary rooms, and wash/dry rooms), excluding structural walls, balconies, loggias, shafts, staircases, basements, and exterior areas. Eligibility required residential usage, at least one habitable furnishable room, an entrance door, at least one window segment, sanitary provision, and kitchen provision.

After normalizing coordinates to meters, closing minor vectorization gaps up to 0.15 m, aligning each plan to its dominant wall axis, and removing normalized geometric duplicates within each source while preserving site identifiers, D1 yielded 2,327 unique eligible compact units (from 46,830 raw records) and D2 yielded 884 unique eligible compact units (from 17,000 raw records; retaining the corpus metric scale calibration). For D1, we drew a stratified sample capped at up to 5 units per building site across 2 m² NIA bins and room counts ($n = 1,348$ selected); all 884 eligible D2 units were retained. Because no eligible observed plan in D1 or D2 had NIA below 16.75 m², we constructed 510 generated shells (D3) spanning 17 target areas (8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 25, 28, 32, 36, and 40 m² NIA) crossed with five aspect ratios (1.0, 1.5, 2.0, 2.5, and 3.0), three entrance positions (short-wall center, short-wall corner, and long-wall corner), and two window positions (opposite short wall and long wall), each containing a fixed $1.20 \times 1.50\text{ m}$ corner toilet pod and a $1.20 \times 0.60\text{ m}$ wall kitchenette near the entrance (2.50 m ceiling height). Observed plans and generated shells are analyzed separately throughout the main text, with pooled curves reported only as an explicit sensitivity analysis.

Before placing furniture, each selected plan was rasterized onto a 0.10 m grid and subjected to a predeclared empty-geometry evaluability screen. To pass, an unfurnished plan had to provide continuous 0.60 m walkable access from the entrance to every fixed-service target and leave at least half of its furnishable raster cells either directly inside the 0.60 m walking coverage or reachable within an additional 0.60 m across unobstructed cells without crossing walls or diagonal corners. Exactly 123 observed units (112 in D1 and 11 in D2, often due to narrow or oblique doorway vectorizations at 0.10 m resolution) failed this unfurnished screen and were excluded altogether, leaving 2,619 evaluable dwellings: 1,236 in D1, 873 in D2 (2,109 observed plans total), and 510 in D3 (Table 1). Any evaluable dwelling in which no furniture item could be feasibly placed retained its independently validated empty layout with $\text{FCI} = 0$ (94 layouts across the primary run), preventing survivor bias in small shells.

#### Household activity schedules

Static furniture checklists ignore whether household members need different activities at different hours or multiple surfaces simultaneously. We therefore represent daily domestic demand over six contiguous time slots summing to 24 h: night (23:00–07:00, 8 h), morning (07:00–09:00, 2 h), day (09:00–17:00, 8 h), evening (17:00–19:00, 2 h), dinner (19:00–20:00, 1 h), and leisure (20:00–23:00, 3 h; Table 2). Four primary household schedules are evaluated on every dwelling: (1) a single commuter (1 person; away during the 8 h day slot, evening/leisure lounging, two-person-capable dining table use in morning and dinner, 1.0 storage unit, and optional leisure desk work weighted at 0.3); (2) a single remote worker (1 person; adding an 8 h daytime `work_1` requirement); (3) a couple with one remote worker (2 persons; requiring double-occupancy sleeping `sleep_2`—satisfiable by one double sleeping surface or two single sleeping surfaces—2.0 storage units, daytime `work_1`, two-person lounging `lounge_2`, and two day variants: normal days at frequency 0.857 requiring `dine_2` and guest-dinner days at frequency 0.143 requiring `dine_4`); and (4) a parent and child (2 persons; requiring two separate single sleeping surfaces `sleep_1, sleep_1` at night, 1.5 storage units, away during the day, simultaneous homework `work_1` and parent lounging `lounge_1` in the evening, `dine_2` at dinner, and `lounge_2` during leisure). A fifth schedule representing an older adult staying home by day with 0.90 m walking width and $1.2\times$ operating clearances is evaluated in sensitivity analyses (Table 2). Cooking and sanitary hygiene are served by the required fixed kitchen and bathroom zones, whose doorways and service targets constrain walkable circulation in every slot. Within any slot, simultaneous non-storage activity tokens must be served by distinct, simultaneously reachable furniture instances; storage demand receives proportional credit $\min(1, \text{reachable placed capacity} / \text{required units})$.

#### Furniture library and operating clearances

Evaluating transformability fairly requires explicit, dimensionally realistic footprints and user clearances for every static and multi-state item. Our reviewed catalogue comprises nine static item types (single bed, double bed, wardrobe, shelving, desk, two-person dining table, four-person dining table, two-seat sofa, and armchair) and seven two-state transformable item types (single wall bed, double wall bed, wall bed over sofa, sofa bed, drop-leaf table, fold-down desk, and extendable dining table; Table S1). Each item state specifies a rigid rectangular body footprint (width along the wall by depth into the room), directional operating clearance strips (`front`, `back`, `left`, `right`), wall-backing requirements, height class (`tall` items may not back onto window segments), storage capacity units (1.0 for standard wardrobe, 0.5 for shelving), maximum instance counts (up to 2 for single beds, single wall beds, wardrobes, shelving, armchairs, and desks—ensuring two-sleeper households can place two single beds or two single wall beds—and 1 otherwise), and per-transition effort weights (0.2 for fold-down desks and drop-leaf tables, 0.3 for extendable tables, 1.0 for single and double wall beds, 1.2 for wall beds over sofas, and 1.5 for sofa beds; Table S1). Catalogue dimensions were audited against 43,002 usable product dimension triples extracted from 147,702 Amazon Berkeley Objects listings (Collins et al., 2022; Table 1; Table S1). Furniture bodies may never overlap walls, fixed services, door-swing keep-out squares (width $\times$ width on the room side, or both sides where ambiguous), or other active furniture bodies; clearance zones may overlap walkable space and other items' clearances, but never another active item's body.

#### Furniture strategies (S0, S1, S2)

To separate the geometric benefit of compact multi-state product forms from the temporal benefit of reconfiguring rooms across the day, we evaluate three nested strategies on every unit–household pair:
1. **Static (S0):** admits only the nine static furniture types in fixed poses.
2. **Form only (S1):** admits both static and transformable furniture types, but restricts each placed item to a single constant state across all slots and day variants (capturing compact product footprints without daily switching).
3. **Form + time (S2):** admits static and transformable furniture at fixed anchor coordinates and orientations across the day and across day variants, while allowing each transformable item to switch between its stowed and deployed states across the six daily slots (and between normal and guest days).

Comparing $\text{S1} - \text{S0}$ isolates the **form effect**, comparing $\text{S2} - \text{S1}$ isolates the **time effect** (or **switching effect**), and comparing $\text{S2} - \text{S0}$ measures the total transformable gain.

#### Schedule-constrained layout optimization

Because discrete furniture packing with doorway keep-outs and multi-slot pedestrian connectivity is combinatorial, manual layouts risk understating one strategy relative to another. For each dwelling, we generate candidate anchor poses aligned with the four orthogonal orientations ($0^\circ, 90^\circ, 180^\circ, 270^\circ$) on the 0.10 m collision grid, filtering out poses whose bodies, clearances, wall-backing strips, or tall-item window restrictions violate empty-shell boundaries. In the accepted production configuration, dwellings with $\text{NIA} \le 20\text{ m}^2$ use a 0.10 m candidate anchor stride and a 120 s solver wall-clock cap per strategy run; dwellings with $\text{NIA} > 20\text{ m}^2$ use a 0.20 m anchor stride (retaining the 0.10 m collision and walkability raster) and a 30 s solver cap.

Each unit–household–strategy instance is solved with Google OR-Tools CP-SAT (Perron et al., 2023) using boolean pose-selection, per-slot state-selection, and slot-demand assignment variables under pairwise body-body and body-clearance conflict constraints. Optimization maximizes a lexicographic-style weighted objective prioritizing served weighted activity-hours (weight $1000.0$), then minimizing cyclic transformation burden (weight $-1.0$), with a minor tie-breaking preference for window proximity (weight $0.01$). To ensure continuous walkable paths without encoding full grid-flow variables upfront, the solver starts from a deterministic greedy feasible layout (and, for S1 and S2 in the production pipeline, can warm-start from the revalidated preceding-strategy solution on the same unit and household, guaranteeing monotonic warm-start availability without relaxing independent validation), solves CP-SAT in rounds of up to 5.0 s (up to 30 lazy-constraint iterations), checks each incumbent with the exact reachability test, adds nogood cuts excluding unreachable pose-state combinations when needed, and retains the highest-scoring independently verified incumbent.

#### Independent geometric and reachability validator

Solver models can harbor subtle discretization or constraint-encoding bugs if evaluated only by their internal objective. Every layout reported in this paper therefore passes an independent validator (`src/fea/validate.py`) that shares zero code or data structures with candidate generation or CP-SAT modeling. From raw configuration files and placed item coordinates $(x, y, \theta)$ plus slot states, the validator independently reconstructs outward-rounded 0.10 m raster masks for every item body, clearance strip, and wall-backing strip, and verifies: (1) strategy and instance-count limits; (2) full containment of non-storage bodies in furnishable cells, storage bodies in furnishable or storage-only cells, and clearances in furnishable, storage-only, or walkable cells; (3) wall contact for wall-backed items and zero window overlap for tall wall-backed items; (4) zero body-body overlap and zero clearance-body collision in every slot and day variant; and (5) continuous 0.60 m walkable reachability from the entrance to every fixed-service target and to at least one clearance cell of every active furniture item credited with serving a scheduled activity. Walkable reachability is computed via explicit disc erosion of diameter $0.60\text{ m}$ on free walkable cells, four-neighbor breadth-first search from the entrance extension, and matching disc dilation. Unreachable items receive zero service credit; any structural or fixed-service access violation invalidates the layout. For 3D visual verification, we exported 10 validated scenes across five showcase dwellings to Blender 4.5.3 LTS (Cycles renderer), generating 30 orthographic stills ($2400 \times 1800\text{ px}$) and auditing projected 3D mesh outlines against 2D validator footprints across 17 placed furniture instances; the maximum Hausdorff outline discrepancy was 2.79 mm, well below the 20 mm tolerance (Figure 2; Figure S2).

#### Functional capacity index (FCI) and transformation burden (TB)

To compare diverse schedules on a common $[0, 1]$ scale, let $V$ denote a household's day variants with frequencies $p_v$ ($\sum_{v \in V} p_v = 1$), $S$ the six daily slots with durations $h_s$ (hours), and $D_{v,s}$ the set of furniture-supported activity demands $d$ in variant $v$ and slot $s$ with importance weights $w_d$ ($w_d = 1.0$ unless specified otherwise). Given validator-verified service credits $c_d \in [0, 1]$ ($c_d \in \{0, 1\}$ for discrete activities and $c_d = \min(1, U_{\text{placed}} / U_{\text{req}})$ for storage), the variant functional capacity index is

$$\text{FCI}_v = \frac{\sum_{s \in S} h_s \sum_{d \in D_{v,s}} w_d \, c_d}{\sum_{s \in S} h_s \sum_{d \in D_{v,s}} w_d}$$

and the household functional capacity index is $\text{FCI} = \sum_{v \in V} p_v \, \text{FCI}_v$. By design, FCI measures physical activity fit and walkable reachability for scheduled domestic tasks, not acoustic or visual privacy, thermal or daylight quality, or subjective comfort. Daily transformation burden (TB) sums effort-weighted cyclic state transitions across all placed items $i \in I$ over the six consecutive slots (including the wrap-around transition from `leisure` back to `night`, $s_0 \equiv s_6$):

$$\text{TB} = \sum_{v \in V} p_v \sum_{i \in I} e_i \sum_{k=1}^{6} \mathbb{I}\!\left[\sigma_{i,v,s_k} \neq \sigma_{i,v,s_{k-1}}\right]$$

where $e_i$ is item $i$'s effort weight and $\sigma_{i,v,s_k}$ is its state in slot $s_k$.

#### Equivalent-area gain ($\Delta\text{EA}$) and support bounds

Expressing functional capacity differences in square meters translates layout performance into the unit used by building codes and housing policy. For each household and reference population (observed plans $\text{D1}+\text{D2}$, generated shells D3, individual sources, or the pooled sensitivity sample), we group dwellings into 2 m² NIA bins $[8, 10), [10, 12), \dots, [48, 50]$, compute the median validated static score $\text{FCI}(\text{S0})$ at each bin midpoint $x_b$, apply a cumulative maximum $y_b = \max_{j \le b} \tilde{y}_j$ to enforce non-decreasing static capacity with area, and linearly interpolate between midpoints to obtain the continuous monotone static reference curve $\hat{f}_0(A)$ over supported midpoints $[A_{\text{lo}}, A_{\text{hi}}]$ (Figure 1D; Figure 3).

For any matched dwelling–household pair $u$ with validated scores $y_0 = \text{FCI}_u(\text{S0})$ and $y_2 = \text{FCI}_u(\text{S2})$, we invert both scores on $\hat{f}_0$ at the smallest supported area attaining each target: $A^*(y) = \inf \{A \in [A_{\text{lo}}, A_{\text{hi}}] : \hat{f}_0(A) \ge y\}$. Three identification cases arise without extrapolation:
1. **Exact zero:** if $y_2 = y_0$, then $\Delta\text{EA}_u = 0\text{ m}^2$ exactly.
2. **Point-identified gain:** if $y_2 > y_0$, $y_0 > \hat{f}_0(A_{\text{lo}})$ (so $A^*(y_0) > A_{\text{lo}}$), and $y_2 \le \hat{f}_0(A_{\text{hi}})$, both inverses lie strictly within interior curve support and $\Delta\text{EA}_u = A^*(y_2) - A^*(y_0)$ is point-identified.
3. **Support-bounded gain:** if $y_2 > y_0$ and either $A^*(y_0) = A_{\text{lo}}$ (left-boundary censoring, because a smaller shell might already achieve $y_0$ below observed NIA support) or $y_2 > \hat{f}_0(A_{\text{hi}})$ (right-boundary censoring, where $A^*(y_2)$ is bounded below by $A_{\text{hi}}$ and unbounded above), the pair yields an identified lower bound $\Delta\text{EA}_u^{\text{lo}} = \max(0, A_{\text{lo or } *}(y_2) - A^*(y_0))$ rather than an extrapolated point value.

Accordingly, we report three complementary summaries per household and population (Table 3; Figure 4): (i) the median among point-identified positive gains, (ii) the support-valid lower bound on the median across all improved pairs ($y_2 > y_0$), and (iii) lower and upper support bounds on the all-pair median across every evaluated dwelling (including unchanged pairs). A pooled-reference sensitivity re-inverts observed-plan scores onto the combined $\text{D1}+\text{D2}+\text{D3}$ static curve extending down to 8 m² NIA.

#### Minimum adequate area ($A_{\min}$)

To estimate the floor area at which half of dwellings satisfy a household's daily schedule, we define binary functional adequacy at threshold $\tau = 0.95$ ($\text{FCI} \ge 0.95$, with sensitivity checks at $\tau = 0.90$ and $\tau = 1.00$). For each household, population, and strategy, we fit an unpenalized logistic regression $\Pr(\text{FCI} \ge \tau \mid \text{NIA} = A) = \text{logit}^{-1}(\beta_0 + \beta_1 A)$ and define the minimum adequate area $A_{\min} = -\beta_0 / \beta_1$ as the 50% adequacy crossing, yielding the strategy reduction $\Delta A_{\min} = A_{\min}(\text{S0}) - A_{\min}(\text{S2})$. Crossings are reported only when $\beta_1 > 0$, both adequate and inadequate outcomes occur without complete separation, and $A_{\min}$ lies within the population's observed NIA range; otherwise the crossing is withheld as unsupported (Table 3).

#### Solver benchmark, area comparators, sensitivity analyses, room comparison, and geometry-only surrogates

To verify that search quality does not drive our findings, we froze a stratified benchmark of 200 unit–household pairs balanced across data source, area tercile, and household schedule, and compared standalone S2 CP-SAT, descending-footprint greedy wall-adjacent placement, and standalone simulated annealing (20,000 proposals $\times$ 3 restarts with a geometric cooling schedule initialized from standalone greedy) against the accepted production pipeline, re-scoring every output with the independent validator (Figure S3; Table S2).

To test how well floor-area rules proxy for modeled adequacy ($\text{FCI} \ge 0.95$), we measured within-bin FCI interquartile ranges across 2 m² NIA bins (Figure 5) and computed confusion matrices (true positives, true negatives, false positives, false negatives, and total disagreement) against Ulrich's (2025) normative thresholds (30 m² for one-person schedules and 45 m² applied to both two-person schedules; Ulrich proposes 60 m² for three-person households) and Hong Kong's statutory 8 m² basic housing unit minimum internal floor area (Government of the Hong Kong Special Administrative Region, 2025), alongside continuous receiver-operating threshold sweeps on area per person and rooms per person (Table 4). Sensitivity analyses varied single-item transformable availability (drop-one ablations), global operating-clearance scale ($0.8\times, 1.0\times, 1.2\times$), required walking width (0.60 m versus 0.90 m), and the older-adult schedule across the 200 benchmark pairs, tested raster/anchor resolution (0.05, 0.10, and 0.20 m) and CP-SAT time limits (30, 60, and 120 s) across a 50-unit subsample, and ran a dedicated 348-unit small-home ($\text{NIA} \le 20\text{ m}^2$) comparison allowing mirrored one-side access ($0.60\text{ m}$ on one long side) for double beds, double wall beds, wall beds over sofas, and deployed sofa beds (Figure S5).

To connect whole-dwelling results with single-room literature, we constructed an approximate $4 \times 3\text{ m}$ bedroom envelope based on Bu and Che Mat (2026) plus three 12 m² generated shell analogues (aspect ratios 1.0, 1.25, and 1.5), comparing daytime body-free floor area ($\text{NIA}$ minus placed daytime furniture bodies, retaining wet-service footprints where present) against Bu and Che Mat's clearance-deducted room figures and across all single-person pairs in $\text{D1}+\text{D2}$ and D3 (Figure S6). To test whether fast learned models could replace optimization, we partitioned D1 by building site into 70% training (884 units across 323 sites), 15% validation (180 units across 69 sites), and 15% held-out test groups (172 units across 70 sites), using D2 ($n = 873$) and D3 ($n = 510$) as external transfer sets. Four models—an area-only linear model, LightGBM gradient-boosted trees, a tabular multilayer perceptron, and a GraphSAGE network over room-polygon and opening adjacency graphs—predicted $\text{FCI}(\text{S0})$, $\text{FCI}(\text{S2})$, and D1-training-referenced $\Delta\text{EA}$ against a prespecified $\text{Spearman } \rho \ge 0.80$ criterion, supplemented by a post-hoc ROC AUC check on ranking $\text{FCI} \ge 0.95$ (Figure S4; Table S3).

#### Parametric furniture kits and Hong Kong subdivided-unit scenario

Standard furniture pieces may be either too wide to fit or unnecessarily narrow in micro-units. We therefore formulated a dimension-sensitive quality index $\text{FCI}_q$ that weights served activities by piecewise-linear dimensional quality factors $q \in [0.60, 1.00]$ across six design variables: single wall-bed width ($0.80, 0.90, 1.00\text{ m}$ with $q = 0.60, 0.85, 1.00$), double wall-bed width ($1.20, 1.40, 1.50\text{ m}$ with $q = 0.60, 0.90, 1.00$), fold-down desk width ($0.80, 1.00, 1.20\text{ m}$ with $q = 0.70, 0.90, 1.00$) and deployed depth ($0.45, 0.55\text{ m}$ with $q = 0.80, 1.00$), drop-leaf table width ($0.70, 0.80, 1.00\text{ m}$ with $q = 0.80, 0.90, 1.00$) and deployed depth ($0.60, 0.75\text{ m}$ with $q = 0.85, 1.00$), and wardrobe frontage ($0.60, 1.00, 1.40\text{ m}$ providing $0.6, 1.0, 1.4$ storage units), keeping stowed depths and operating clearances fixed as in the main catalogue. Identical quality curves were applied to standard catalogue items and candidate kits, with adequacy defined at $\text{FCI}_q \ge 0.95$. Candidate kits for the single commuter and couple were screened via successive halving and ranked by mean $\text{FCI}_q$ (with TB breaking ties) on 30 frozen D3 training shells in the 8–15 m² target band, compared against a per-shell bespoke upper bound (selecting the highest-scoring tested kit vector separately on each shell), evaluated on 15 held-out D3 shells (aspect ratio 2.5, long-wall-corner entrance) and 15 small observed plans ($\text{NIA} \le 20\text{ m}^2$), and checked under matched additional 120 s warm-started S2 search alongside the catalogue (Figure 6; Table S4).

Finally, we evaluated the Hong Kong subdivided-unit scenario across 390 model shells—30 matched aspect-ratio, entrance, and window templates at every integer NIA from 8 to 20 m²—for the single commuter, couple, and parent and child under standard strategies and selected kits using the shared $\text{FCI}_q \ge 0.95$ adequacy rule (Figure 6; Table S4). Territory-wide context counts (108,202 subdivided units, 107,371 households, and 215,709 residents across 33,658 quarters) were extracted from the Hong Kong 2021 Population Census (Table 1); because census tables omit the joint household-size-by-floor-area distribution, results are reported directly on the 390-shell template grid without territory-wide stock weighting.

### Quantification and statistical analysis

All statistical summaries and uncertainty intervals were computed in Python (`numpy 2.4.6`, `scipy 1.17.1`, `scikit-learn 1.9.1`) using fixed random seed `20261105`. Because strategies S0, S1, and S2 (and alternative solvers or furniture kits) are evaluated on the exact same dwellings, all primary comparisons are paired within physical dwelling units. Two-sided 95% confidence intervals use 1,000 non-parametric paired bootstrap resamples: on D1, D2, and D3, the resampling unit is the physical dwelling unit stratified by source (retaining all paired household and strategy evaluations for each resampled unit); in the 390-shell Hong Kong scenario, the resampling unit is the 30-shape geometric template cluster (resampling whole 8–20 m² area trajectories per template to preserve cross-area correlation). Within every bootstrap draw, static reference curves $\hat{f}_0(A)$, equivalent-area inversions, and unpenalized logistic $A_{\min}$ crossings are refitted from scratch before taking the 2.5th and 97.5th percentiles. Confidence intervals for area statistics ($\Delta\text{EA}$ medians and $A_{\min}$ or $\Delta A_{\min}$ crossings) are reported only when at least two distinct units contribute and at least 80% of the 1,000 bootstrap draws produce finite within-support estimates; otherwise point estimates are reported without intervals or withheld as unsupported, and boundary-censored equivalent-area estimates are explicitly denoted with `≥` lower bounds or lower–upper support intervals. Sample sizes ($n$, representing physical dwellings, unit–household pairs, or template shells as labeled) are stated in every table, figure legend, and Results subsection.

## Acknowledgments

[AUTHOR TO FILL]

## Author contributions

[AUTHOR TO FILL]

## Declaration of interests

The authors declare no competing interests. [AUTHOR TO VERIFY/FILL]

## References

- Abouagour, M., and Garyfallidis, E. (2025). ResPlan: A Large-Scale Vector-Graph Dataset of 17,000 Residential Floor Plans. arXiv preprint, arXiv:2508.14006. https://doi.org/10.48550/arXiv.2508.14006
- Ashkevari, S., and Farhady, M. (2023). Evaluation of Functional Flexibility in Contemporary Japanese Housing Layouts: Integration of User Perspective. *A|Z ITU Journal of the Faculty of Architecture*, 20(1), 101–116. https://www.az.itu.edu.tr/jfa/article/view/755
- Bu, S., and Che Mat, R. (2026). Research on Space Optimization Design Strategies for Compact Bedrooms Based on Smart Built Environment. *Civil Engineering and Architecture*, 14(5), 3617–3633. https://doi.org/10.13189/cea.2026.140514
- Collins, J., Goel, S., Deng, K., Luthra, A., Xu, L., Gundogdu, E., Zhang, X., Vicente, T. F. Y., Dideriksen, T., Arora, H., Guillaumin, M., and Malik, J. (2022). ABO: Dataset and Benchmarks for Real-World 3D Object Understanding. In *2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 21094–21104. https://doi.org/10.1109/cvpr52688.2022.02045
- Daglio, L., Ginelli, E., and Vignati, G. (2023). Housing Design: Furniture or Fixtures? Accommodating Change through Technological and Typological Innovation. *Buildings*, 13(7), 1862. https://doi.org/10.3390/buildings13071862
- Elmurodov, S., and Mametova, N. (2026). Increasing Space Efficiency in Small Apartments Through Furniture Transformation. *O‘zbekistonda Uchinchi Renessans va innovatsion jarayonlar jurnali*, 2(4), 172–188. https://globalsciences.uz/renessans/article/view/3547
- Freimane, S. (2022). Quality of Apartment Layouts in Contemporary Urban Housing: The Study of Riga. *SPACE International Journal of Conference Proceedings*, 2(1), 19–27. https://doi.org/10.51596/sijocp.v2i1.36
- Fu, Q., Zhang, F., Li, X., and Fu, H. (2024). Magic Furniture: Design Paradigm of Multi-Function Assembly. *IEEE Transactions on Visualization and Computer Graphics*, 30(7), 4068–4079. https://doi.org/10.1109/tvcg.2023.3250488
- Garg, A., Jacobson, A., and Grinspun, E. (2016). Computational design of reconfigurables. *ACM Transactions on Graphics*, 35(4), 1–14. https://doi.org/10.1145/2897824.2925900
- Goessler, T., and Kaluarachchi, Y. (2023). Smart Adaptive Homes and Their Potential to Improve Space Efficiency and Personalisation. *Buildings*, 13(5), 1132. https://doi.org/10.3390/buildings13051132
- Government of the Hong Kong Special Administrative Region (2025). Basic Housing Units Ordinance (Cap. 658). Ordinance No. 41 of 2025, Hong Kong Government Gazette (Schedule 1, section 1. Phase one commenced on 1 March 2026). https://www.elegislation.gov.hk/hk/cap658
- Li, W., Ju, X., Qin, Z., Fang, R., and Li, H. (2026). HomeWorld: A Unified Floorplan-to-Furnished Framework for Generating Controllable, Densely Interactive Whole-Home Scenes. In *Computer Vision – ECCV 2026*, pp. 40–58. https://doi.org/10.1007/978-3-032-37335-9_3
- Liu, J.-H., Zhang, S.-K., Sun, S., Wang, Z., and Zhang, S.-H. (2025). DIFF: A dataset for indoor flexible furniture. *Graphical Models*, 141, 101293. https://doi.org/10.1016/j.gmod.2025.101293
- Merrell, P., Schkufza, E., Li, Z., Agrawala, M., and Koltun, V. (2011). Interactive furniture layout using interior design guidelines. *ACM Transactions on Graphics*, 30(4), 1–10. https://doi.org/10.1145/2010324.1964982
- Mustafa, C., and Ali, A. (2022). The Effect of Architectural Area Standards on Living Room’s Spatial Functional efficiency for Low- Prize Residential Complexes in Sulaymaniyah City. *Sulaimani Journal for Engineering Sciences*, 9(2), 23–37. https://doi.org/10.17656/sjes.10154
- Nieciecki, P., Plocharski, A., and Musialski, P. (2026). What a ComfortableWorld: Ergonomic Principles Guided Apartment Layout Generation. In *Eurographics 2026 – Short Papers* (The Eurographics Association). https://doi.org/10.2312/egs.20261019
- Özer, S., and Jacoby, S. (2022). Dwelling size and usability in London: a study of floor plan data using machine learning. *Building Research & Information*, 50(6), 694–708. https://doi.org/10.1080/09613218.2022.2070452
- Pedro, J. A. C. B. de O. (2009). How small can a dwelling be? A revision of Portuguese building regulations. *Structural Survey*, 27(5), 390–410. https://doi.org/10.1108/02630800911002648
- Perron, L., Didier, F., and Gay, S. (2023). The CP-SAT-LP Solver (Invited Talk). In *29th International Conference on Principles and Practice of Constraint Programming (CP 2023)*, Leibniz International Proceedings in Informatics (LIPIcs), vol. 280 (Schloss Dagstuhl – Leibniz-Zentrum für Informatik), pp. 3:1–3:2. https://doi.org/10.4230/LIPIcs.CP.2023.3
- Rakhmatillaeva, Z. (2025). Spatial Analysis of Contemporary One-Room Apartment Layouts in Tashkent’s New Residential Buildings. *International Multidisciplinary Journal for Research & Development*, 12(7). https://www.ijmrd.in/index.php/imjrd/article/view/3565
- Standfest, M., Franzen, M., Schröder, Y., Medina, L. G., Villanueva Hernandez, Y., Buck, J. H., Tan, Y.-L., Niedzwiecka, M., and Colmegna, R. (2022). Swiss Dwellings: A large dataset of apartment models including aggregated geolocation-based simulation results covering viewshed, natural light, traffic noise, centrality and geometric analysis. Zenodo (Dataset, version 3.0.0). https://doi.org/10.5281/zenodo.7788422
- Sun, F.-Y., Liu, W., Gu, S., Lim, D., Bhat, G., Tombari, F., Li, M., Haber, N., and Wu, J. (2025). LayoutVLM: Differentiable Optimization of 3D Layout via Vision-Language Models. In *2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 29469–29478. https://doi.org/10.1109/cvpr52734.2025.02744
- Ulrich, K. T. (2025). Minimum Spatial Housing Requirements for Human Flourishing. *Buildings*, 15(15), 2623. https://doi.org/10.3390/buildings15152623
- Weber, R. E., Mueller, C., and Reinhart, C. (2024). A hypergraph model shows the carbon reduction potential of effective space use in housing. *Nature Communications*, 15(1), 8327. https://doi.org/10.1038/s41467-024-52506-z
- Xiang, C., Bao, R., Feng, B., Wu, W., Liu, Z., Guan, Y., and Liu, L. (2026). Co-Layout: LLM-driven Co-optimization for Interior Layout. *Proceedings of the AAAI Conference on Artificial Intelligence*, 40(17), 14371–14379. https://doi.org/10.1609/aaai.v40i17.38452
- Xiong, G., Cai, S., and Luo, G. (2026). MAFC-Driven Dynamic Layout Transformation System for Reconfigurable Furniture. *Computer Animation and Virtual Worlds*, 37(2), e70113. https://doi.org/10.1002/cav.70113
- Xiong, G., Fu, Q., Fu, H., Zhou, B., Luo, G., and Deng, Z. (2021). Motion Planning for Convertible Indoor Scene Layout Design. *IEEE Transactions on Visualization and Computer Graphics*, 27(12), 4413–4424. https://doi.org/10.1109/tvcg.2020.3005680
- Yu, L.-F., Yeung, S.-K., Tang, C.-K., Terzopoulos, D., Chan, T. F., and Osher, S. J. (2011). Make it home: automatic optimization of furniture arrangement. *ACM Transactions on Graphics*, 30(4), 1–12. https://doi.org/10.1145/2010324.1964981
- Zeng, F., Feng, X., Zou, D., and Lei, J. (2026). Breaking the Fixed-Room Bottleneck: Generative SBF Model, Power-Law Scaling, and Adaptability Surcharge Index for Extreme Residential Intensification. *Buildings*, 16(16), 3219. https://doi.org/10.3390/buildings16163219
- Zhang, S.-K., Liu, J.-H., Huang, J., Chi, Z., Tam, H., Yang, Y.-L., and Zhang, S.-H. (2025). SceneExplorer: An Interactive System for Expanding, Scheduling, and Organizing Transformable Layouts. *IEEE Transactions on Visualization and Computer Graphics*, 31(9), 6008–6021. https://doi.org/10.1109/tvcg.2024.3488744

## Figure legends

**Figure 1. Schedule-aware, independently verified framework for translating furniture strategies into equivalent floor area**
(A) Study inputs: 2,619 evaluable compact dwellings within 8–50 m² of net internal area (NIA), comprising 2,109 observed floor plans (1,236 from Swiss Dwellings and 873 from ResPlan; schematic at left shows a 29.97 m² observed apartment) and 510 controlled generated shells (schematic at right shows an 18.00 m² shell; 390 Hong Kong model shells spanning 8–20 m² are evaluated in the policy scenario); four 24-hour household schedules (single commuter, single remote worker, couple, and parent and child) partitioned into six daily slots across night, daytime work, and meals; and an audited furniture library combining conventional static items (top icon row) with two-state transformable items (`⇄`: deployed solid footprints versus stowed outlines, with explicit directional operating clearances).
(B) Within-dwelling comparison across three nested furniture strategies (`paper/figures/fig1/Figure1.pdf`) illustrated on the same validated 18.00 m² couple shell across Night, Workday, and Dinner slots: static (S0, blue; fixed-state furniture only), form only (S1, orange; admitting transformable furniture held in a single constant state all day), and form + time (S2, green; allowing transformable furniture at fixed anchor coordinates and orientations to switch states across daily slots [`⇄ Switch`], with green outlines highlighting the double wall bed deployed at Night and stowed [hatched] during Workday).
(C) Verified optimization: warm-started constraint programming (`CP-SAT`) searches discrete poses and slot states for each strategy, while a zero-shared-code geometric validator checks zero body-body or clearance-body overlap, unobstructed operating clearances, and continuous $\ge 0.60\text{ m}$ walkable access from the entrance to fixed wet services and active clearances—rejecting unreachable incumbents (`✗`) via lazy cuts—to produce 31,428 independently verified layouts ($2,619\text{ plans} \times 4\text{ households} \times 3\text{ strategies}$).
(D) Translation from function to floor area: the functional capacity index ($\text{FCI} \in [0, 1]$, defined as served divided by scheduled weighted activity-hours over 24 h) is mapped onto the monotone static reference curve ($\text{FCI}$ on the vertical axis versus $\text{NIA}$ in m² on the horizontal axis); inverting a dwelling's paired S0 and S2 validated scores yields its equivalent-area gain ($\Delta\text{EA}$, green bracket, in m²; with minimum adequate area $A_{\min}$ defined in STAR Methods as the 50% crossing of $\text{FCI} \ge 0.95$), while total capacity gain ($\text{S2} - \text{S0}$) decomposes into the form effect ($\text{S1} - \text{S0}$, orange) and the time or switching effect ($\text{S2} - \text{S1}$, green).

**Figure 2. Validated couple layouts across daily slots and strategies in 2D plan and 3D orthographic views**
(A) Validated 2D floor-plan arrangements (`results/figures/g4/F3.pdf`) for a couple on a normal day across Night, Workday, and Dinner slots under static (S0), form only (S1), and form + time (S2) strategies in three showcase dwellings: a 10.00 m² generated shell (top row), an 18.00 m² generated shell (middle row), and a 29.97 m² observed plan from Swiss Dwellings (bottom row). Furniture bodies are colored by activity function (sleep, work, dine, lounge, storage, fixed service); hatched polygons indicate stowed transformable states, and scale is held constant within each row. In the 10.00 m² shell, no double sleeping surface fits with valid clearance in any slot ($\text{FCI} = 0.577$ under S0; $\text{FCI} = 0.687$ under S1 and S2), and in both the 10.00 m² and 29.97 m² showcases S2 furniture states remain fixed across the day ($\text{TB} = 0.00$).
(B) Matched Blender Cycles 3D orthographic renders (`results/figures/g4/F3b_18.pdf`) of the 18.00 m² generated shell under S0 ($\text{FCI} = 0.937$, $\text{TB} = 0.00$) and S2 ($\text{FCI} = 1.000$, $\text{TB} = 3.00$) across Night, Workday, and Dinner with fixed camera, lighting, and scale. Deploying the double wall bed at night and stowing it by day unlocks full schedule coverage in the 18.00 m² shell. See also Figure S2 for 3D renders of the 10.00 m² and 29.97 m² showcases.

**Figure 3. Functional capacity across net internal area by household and furniture strategy**
Median validated functional capacity index (FCI) per 2 m² net internal area (NIA) bin under static (S0, blue), form only (S1, orange), and form + time (S2, green) strategies for single commuter, single remote worker, couple, and parent-and-child schedules across observed plans ($\text{D1} + \text{D2}$, $n = 2,109$ dwellings; top row) and generated shells ($\text{D3}$, $n = 510$ dwellings; bottom row) (`results/figures/g4/F4.pdf`). Dashed dark lines show the cumulative-maximum monotone static reference curve $\hat{f}_0(A)$ fitted to S0 bin medians for equivalent-area inversion; horizontal dotted lines mark the $\text{FCI} = 0.95$ adequacy threshold. Strategy separation is minimal for single-person schedules on observed plans and largest for two-person schedules across compact intermediate bins.

**Figure 4. Equivalent-area gains from transformable form and daily state switching across dwelling sizes**
All-pair median equivalent-area gain ($\Delta\text{EA}$) between S2 and S0 per 2 m² NIA bin expressed in absolute floor area (m², top row) and percentage of dwelling NIA (%, bottom row) across the four primary households on observed plans ($n = 2,109$, circles) and generated shells ($n = 510$, squares), including pairs with equal S0 and S2 scores (`results/figures/g4/F5.pdf`). Solid lines mark lower support bounds, dotted lines and shaded bands indicate upper support bounds where finite, grey markers denote sparse bins with fewer than 10 unit–household pairs (the smallest observed-plan bin at 16–18 m² contains $n = 6$ pairs), and upward triangles indicate bins whose upper median bound is unbounded on the within-population static curve. Equivalent-area gains peak at intermediate compact sizes for two-person households rather than in the smallest shells.

**Figure 5. Within-bin dispersion of functional capacity across equal-sized dwellings**
Interquartile range (75th minus 25th percentile) of validated FCI within each 2 m² NIA bin under static (S0, blue), form only (S1, orange), and form + time (S2, green) strategies across observed plans ($n = 2,109$; top row) and generated shells ($n = 510$; bottom row) for the four primary households (`results/figures/g4/F6.pdf`). Dwellings in the same narrow floor-area bin exhibit substantial spread in usable capacity, explaining why area-only cutoffs misclassify individual plans.

**Figure 6. Adequacy, daily state switching, and parametric furniture kit trade-offs in Hong Kong model shells**
(A–C) Share of modeled shells achieving quality-weighted adequacy ($\text{FCI}_q \ge 0.95$) at each integer NIA from 8 to 20 m² ($n = 30$ matched shape templates per integer m², 390 shells per household) for a single commuter, couple, and parent and child under S0, S1, S2, matched extra-search catalogue S2, the tested compact commuter kit, and the selected larger couple kit (`results/figures/g4/F10.pdf`, top row; shaded band highlights 13–16 m² for the couple).
(D–F) Couple quality-scored capacity and size-band trade-offs (`results/figures/g4/F10.pdf`, bottom row): (D) mean $\text{FCI}_q$ by integer area comparing the larger couple kit against the optimized catalogue (shaded band highlights 8–12 m²); (E) modeled 50% adequate area crossings ($A_{\min}$) with 95% template-cluster bootstrap confidence intervals (1,000 resamples of the 30 shape templates); and (F) enumeration counts at 13–16 m² ($51/120$ versus $30/120$ adequate shells) and mean $\text{FCI}_q$ at 8–12 m² ($0.448$ versus $0.500$).
(G) Plan-view body footprints (deployed and stowed states at common scale, in meters) and training ($n = 30$ shells, 8–15 m²) plus transfer ($n = 15$ held-out shells and $n = 15$ observed plans $\le 20\text{ m}^2$) summary tables for the top-ranked commuter and couple parametric kits (`results/figures/g4/F12.pdf`). Larger couple furniture expands adequacy at 13–16 m² while reducing capacity below 13 m², whereas downsized commuter furniture does not improve on the standard catalogue. See also Table S4.

## Tables

**Table 1. Datasets and analysis coverage**
Summary of floor-plan, product-dimension, and census sources, showing raw record counts, unique eligible compact residential plans (8–50 m² NIA), units selected for the primary experiment, evaluable units passing the predeclared 0.10 m empty-geometry walkability screen, and NIA range statistics (`results/tables/g4/T1.md`).

| ID | Dataset | Raw records | Unique eligible | Selected | Evaluable | NIA min / median / max (m²) | Role in study |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- | :--- |
| D1 | Swiss Dwellings | 46,830 | 2,327 | 1,348 | 1,236 | 16.75 / 40.47 / 50.00 | Observed floor plans (normalized) |
| D2 | ResPlan | 17,000 | 884 | 884 | 873 | 25.56 / 45.48 / 49.96 | Observed floor plans (normalized) |
| D3 | Generated shells | 510 | 510 | 510 | 510 | 8.00 / 16.00 / 40.00 | Controlled parametric shell grid |
| D4 | Amazon Berkeley Objects | 147,702 | — | — | — | — | Furniture dimension audit (43,002 usable triples) |
| D5 | American Time Use Survey | — | — | — | — | — | Optional schedule calibration (omitted) |
| D6 | Hong Kong 2021 Census | 108,202 | — | — | — | — | Territory context (subdivided units) |

**Table 2. Household daily activity schedules**
Twenty-four-hour slot partitions, day-variant frequencies, and furniture-supported capability demands for the four primary households and the older-adult sensitivity schedule (`results/tables/g4/T3.md`). Fixed bathroom and kitchen spaces serve hygiene and cooking; storage is credited proportionally up to required capacity units.

| Household | Persons | Day variant | Frequency | Slot | Clock (duration) | Scheduled furniture demand |
| :--- | ---: | :--- | ---: | :--- | :--- | :--- |
| Single commuter | 1 | normal | 1.000 | night | 23:00–07:00 (8 h) | `sleep_1` |
| Single commuter | 1 | normal | 1.000 | morning | 07:00–09:00 (2 h) | `storage` (1.0 unit), `dine_2` |
| Single commuter | 1 | normal | 1.000 | day | 09:00–17:00 (8 h) | Away |
| Single commuter | 1 | normal | 1.000 | evening | 17:00–19:00 (2 h) | `lounge_1` |
| Single commuter | 1 | normal | 1.000 | dinner | 19:00–20:00 (1 h) | `dine_2` |
| Single commuter | 1 | normal | 1.000 | leisure | 20:00–23:00 (3 h) | `lounge_1`, `work_1` (weight 0.3) |
| Single remote worker | 1 | normal | 1.000 | night | 23:00–07:00 (8 h) | `sleep_1` |
| Single remote worker | 1 | normal | 1.000 | morning | 07:00–09:00 (2 h) | `storage` (1.0 unit), `dine_2` |
| Single remote worker | 1 | normal | 1.000 | day | 09:00–17:00 (8 h) | `work_1` |
| Single remote worker | 1 | normal | 1.000 | evening | 17:00–19:00 (2 h) | `lounge_1` |
| Single remote worker | 1 | normal | 1.000 | dinner | 19:00–20:00 (1 h) | `dine_2` |
| Single remote worker | 1 | normal | 1.000 | leisure | 20:00–23:00 (3 h) | `lounge_1` |
| Couple | 2 | normal | 0.857 | night | 23:00–07:00 (8 h) | `sleep_2` |
| Couple | 2 | normal | 0.857 | morning | 07:00–09:00 (2 h) | `storage` (2.0 units), `dine_2` |
| Couple | 2 | normal | 0.857 | day | 09:00–17:00 (8 h) | `work_1` |
| Couple | 2 | normal | 0.857 | evening | 17:00–19:00 (2 h) | `lounge_2` |
| Couple | 2 | normal | 0.857 | dinner | 19:00–20:00 (1 h) | `dine_2` |
| Couple | 2 | normal | 0.857 | leisure | 20:00–23:00 (3 h) | `lounge_2` |
| Couple | 2 | guests | 0.143 | night | 23:00–07:00 (8 h) | `sleep_2` |
| Couple | 2 | guests | 0.143 | morning | 07:00–09:00 (2 h) | `storage` (2.0 units), `dine_2` |
| Couple | 2 | guests | 0.143 | day | 09:00–17:00 (8 h) | `work_1` |
| Couple | 2 | guests | 0.143 | evening | 17:00–19:00 (2 h) | `lounge_2` |
| Couple | 2 | guests | 0.143 | dinner | 19:00–20:00 (1 h) | `dine_4` |
| Couple | 2 | guests | 0.143 | leisure | 20:00–23:00 (3 h) | `lounge_2` |
| Parent and child | 2 | normal | 1.000 | night | 23:00–07:00 (8 h) | `sleep_1`, `sleep_1` |
| Parent and child | 2 | normal | 1.000 | morning | 07:00–09:00 (2 h) | `storage` (1.5 units), `dine_2` |
| Parent and child | 2 | normal | 1.000 | day | 09:00–17:00 (8 h) | Away |
| Parent and child | 2 | normal | 1.000 | evening | 17:00–19:00 (2 h) | `work_1`, `lounge_1` |
| Parent and child | 2 | normal | 1.000 | dinner | 19:00–20:00 (1 h) | `dine_2` |
| Parent and child | 2 | normal | 1.000 | leisure | 20:00–23:00 (3 h) | `lounge_2` |
| Older adult (sensitivity) | 1 | normal | 1.000 | night | 23:00–07:00 (8 h) | `sleep_1` |
| Older adult (sensitivity) | 1 | normal | 1.000 | morning | 07:00–09:00 (2 h) | `storage` (1.0 unit), `dine_2` |
| Older adult (sensitivity) | 1 | normal | 1.000 | day | 09:00–17:00 (8 h) | `lounge_1` |
| Older adult (sensitivity) | 1 | normal | 1.000 | evening | 17:00–19:00 (2 h) | `lounge_1` |
| Older adult (sensitivity) | 1 | normal | 1.000 | dinner | 19:00–20:00 (1 h) | `dine_2` |
| Older adult (sensitivity) | 1 | normal | 1.000 | leisure | 20:00–23:00 (3 h) | `lounge_1` |

**Table 3. Matched functional capacity effects, equivalent-area gains ($\Delta\text{EA}$), and minimum adequate area reductions ($\Delta A_{\min}$)**
Paired within-dwelling outcomes across observed plans ($\text{D1} + \text{D2}$), generated shells ($\text{D3}$), individual observed datasets, and the pooled sensitivity reference (`results/tables/g4/T4.md`). Bracketed ranges indicate 95% unit-bootstrap confidence intervals (1,000 resamples) where supported ($\ge 2$ contributing units and $\ge 80\%$ supported draws); `≥` denotes reference-curve support lower bounds; `—` indicates unavailable point identification or unsupported logistic crossings. Higher values indicate greater capacity or floor-area savings.

| Sample / Household | Pairs ($n$) | Full S0 ($\text{FCI}=1$) | S2 improves ($\text{S2}>\text{S0}$) | Mean form effect ($\text{S1}-\text{S0}$, FCI ↑) | Mean time effect ($\text{S2}-\text{S1}$, FCI ↑) | Identified positive $n$ | Median identified $\Delta\text{EA}$ (m² ↑) | Bound-only improved $n$ | Improved-group median lower bound (m² ↑) | All-pair median $\Delta\text{EA}$ bounds (m² ↑) | $\Delta A_{\min}$ at $\tau=0.95$ (m² ↑) |
| :--- | ---: | ---: | ---: | :--- | :--- | ---: | :--- | ---: | :--- | :--- | :--- |
| **Observed plans (D1 + D2)** | | | | | | | | | | | |
| Single commuter | 2,109 | 90.8% | 7.5% | 0.0085 [0.0071, 0.0100] | 0.0002 [0.0000, 0.0003] | 0 | — | 159 | ≥2.00 | 0.00–0.00 | — |
| Single remote worker | 2,109 | 89.1% | 8.7% | 0.0107 [0.0090, 0.0125] | 0.0001 [0.0000, 0.0002] | 160 | 1.33 [0.75, 3.11] | 24 | ≥1.33 | 0.00–0.00 | — |
| Couple | 2,109 | 72.7% | 23.5% | 0.0130 [0.0112, 0.0148] | 0.0112 [0.0094, 0.0130] | 448 | 6.21 [4.20, 10.00] | 48 | ≥6.21 | 0.00–0.00 | — |
| Parent and child | 2,109 | 61.0% | 35.9% | 0.0271 [0.0249, 0.0292] | 0.0017 [0.0013, 0.0022] | 721 | 5.00 [4.20, 8.00] | 36 | ≥5.00 | 0.00–0.00 | 10.78 [9.15, 12.70] |
| **Generated shells (D3)** | | | | | | | | | | | |
| Single commuter | 510 | 54.9% | 29.4% | 0.0280 [0.0234, 0.0328] | 0.0023 [0.0009, 0.0041] | 148 | 2.00 [0.95, 2.00] | 2 | ≥2.00 | 0.00–0.00 | 1.68 [1.12, 2.38] |
| Single remote worker | 510 | 53.9% | 37.8% | 0.0594 [0.0516, 0.0667] | 0.0009 [0.0003, 0.0017] | 180 | 2.29 [2.00, 2.33] | 13 | ≥2.00 | 0.00–0.00 | 3.63 [2.78, 4.77] |
| Couple | 510 | 31.6% | 59.2% | 0.0709 [0.0621, 0.0795] | 0.0372 [0.0303, 0.0447] | 286 | 3.34 [2.32, 4.07] | 16 | ≥2.81 | 1.34–1.34 | 5.53 [4.90, 6.12] |
| Parent and child | 510 | 26.7% | 65.7% | 0.0595 [0.0542, 0.0652] | 0.0052 [0.0034, 0.0071] | 322 | 1.79 [1.16, 2.44] | 13 | ≥1.73 | 0.83–0.86 | 6.45 [5.19, 7.75] |
| **Swiss Dwellings (D1)** | | | | | | | | | | | |
| Single commuter | 1,236 | 88.5% | 10.1% | 0.0119 [0.0097, 0.0142] | 0.0000 [0.0000, 0.0001] | 0 | — | 125 | ≥2.00 | 0.00–0.00 | — |
| Single remote worker | 1,236 | 85.9% | 12.7% | 0.0164 [0.0138, 0.0192] | 0.0001 [0.0000, 0.0002] | 133 | 1.33 [0.75, 3.06] | 24 | ≥1.33 | 0.00–0.00 | — |
| Couple | 1,236 | 59.1% | 36.0% | 0.0182 [0.0157, 0.0209] | 0.0176 [0.0149, 0.0203] | 398 | 8.00 [4.36, 12.00] | 47 | ≥8.00 | 0.00–0.00 | — |
| Parent and child | 1,236 | 43.2% | 51.9% | 0.0413 [0.0381, 0.0445] | 0.0027 [0.0020, 0.0035] | 606 | 7.00 [5.75, 10.00] | 35 | ≥6.00 | 0.91–2.00 | 12.63 [10.78, 15.16] |
| **ResPlan (D2)** | | | | | | | | | | | |
| Single commuter | 873 | 94.0% | 3.9% | 0.0037 [0.0024, 0.0051] | 0.0003 [0.0000, 0.0007] | 0 | — | 34 | ≥0.00 | 0.00–0.00 | — |
| Single remote worker | 873 | 93.6% | 3.1% | 0.0027 [0.0017, 0.0038] | 0.0001 [0.0000, 0.0003] | 0 | — | 27 | ≥0.00 | 0.00–0.00 | — |
| Couple | 873 | 92.1% | 5.8% | 0.0055 [0.0032, 0.0081] | 0.0021 [0.0010, 0.0035] | 35 | 0.68 [0.25, 6.23] | 16 | ≥1.95 | 0.00–0.00 | — |
| Parent and child | 873 | 86.3% | 13.3% | 0.0070 [0.0054, 0.0088] | 0.0004 [0.0001, 0.0009] | 82 | 0.50 | 34 | ≥0.50 | 0.00–0.00 | — |
| **Pooled sensitivity (D1 + D2 + D3)** | | | | | | | | | | | |
| Single commuter | 2,619 | 83.8% | 11.8% | 0.0123 [0.0108, 0.0140] | 0.0006 [0.0003, 0.0009] | 306 | 2.10 [1.38, 2.40] | 3 | ≥2.00 | 0.00–0.00 | 1.01 [−0.44, 2.45] |
| Single remote worker | 2,619 | 82.2% | 14.4% | 0.0202 [0.0179, 0.0226] | 0.0002 [0.0001, 0.0004] | 363 | 2.57 [2.29, 3.00] | 14 | ≥2.57 | 0.00–0.00 | 6.32 |
| Couple | 2,619 | 64.7% | 30.5% | 0.0243 [0.0217, 0.0267] | 0.0162 [0.0143, 0.0181] | 782 | 6.29 [2.29, 9.37] | 16 | ≥6.29 | 0.00–0.00 | 10.77 [9.66, 11.94] |
| Parent and child | 2,619 | 54.3% | 41.7% | 0.0334 [0.0312, 0.0356] | 0.0024 [0.0019, 0.0030] | 1,079 | 5.00 [2.80, 12.00] | 13 | ≥4.41 | 0.00–0.00 | 10.16 [9.28, 11.06] |

**Table 4. Classification disagreement between fixed floor-area cutoffs and modeled functional adequacy ($\text{FCI} \ge 0.95$)**
Confusion counts and disagreement shares (`(FP + FN) / Cases`, lower is better) comparing Ulrich's (2025) normative area cutoffs (30 m² for one person; 45 m² applied to two-person schedules) and Hong Kong's statutory 8 m² basic housing unit minimum against validated layout adequacy under static (S0) and form + time (S2) strategies across observed plans and generated shells (`results/tables/g4/T7.md`; full source-specific and pooled breakdowns in `results/expD/confusion.csv`). Positive prediction means $\text{NIA} \ge \text{cutoff}$; true positive (TP) means both $\text{NIA} \ge \text{cutoff}$ and $\text{FCI} \ge 0.95$; false negative (FN) means $\text{NIA} < \text{cutoff}$ while $\text{FCI} \ge 0.95$; false positive (FP) means $\text{NIA} \ge \text{cutoff}$ while $\text{FCI} < 0.95$.

| Sample / Household | Strategy | Area comparator | NIA cutoff (m²) | Cases ($n$) | TP | TN | FP | FN | Disagreement (↓) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Observed plans (D1 + D2)** | | | | | | | | | |
| Single commuter | S0 | Ulrich (2025) area comparator | 30 | 2,109 | 1,787 | 16 | 135 | 171 | 14.5% |
| Single commuter | S0 | Hong Kong basic housing unit minimum | 8 | 2,109 | 1,958 | 0 | 151 | 0 | 7.2% |
| Single commuter | S2 | Ulrich (2025) area comparator | 30 | 2,109 | 1,883 | 7 | 39 | 180 | 10.4% |
| Single commuter | S2 | Hong Kong basic housing unit minimum | 8 | 2,109 | 2,063 | 0 | 46 | 0 | 2.2% |
| Single remote worker | S0 | Ulrich (2025) area comparator | 30 | 2,109 | 1,736 | 28 | 186 | 159 | 16.4% |
| Single remote worker | S0 | Hong Kong basic housing unit minimum | 8 | 2,109 | 1,895 | 0 | 214 | 0 | 10.1% |
| Single remote worker | S2 | Ulrich (2025) area comparator | 30 | 2,109 | 1,870 | 5 | 52 | 182 | 11.1% |
| Single remote worker | S2 | Hong Kong basic housing unit minimum | 8 | 2,109 | 2,052 | 0 | 57 | 0 | 2.7% |
| Couple | S0 | Ulrich (2025) area comparator | 45 | 2,109 | 814 | 303 | 52 | 940 | 47.0% |
| Couple | S0 | Hong Kong basic housing unit minimum | 8 | 2,109 | 1,754 | 0 | 355 | 0 | 16.8% |
| Couple | S2 | Ulrich (2025) area comparator | 45 | 2,109 | 841 | 93 | 25 | 1,150 | 55.7% |
| Couple | S2 | Hong Kong basic housing unit minimum | 8 | 2,109 | 1,991 | 0 | 118 | 0 | 5.6% |
| Parent and child | S0 | Ulrich (2025) area comparator | 45 | 2,109 | 800 | 454 | 66 | 789 | 40.5% |
| Parent and child | S0 | Hong Kong basic housing unit minimum | 8 | 2,109 | 1,589 | 0 | 520 | 0 | 24.7% |
| Parent and child | S2 | Ulrich (2025) area comparator | 45 | 2,109 | 844 | 153 | 22 | 1,090 | 52.7% |
| Parent and child | S2 | Hong Kong basic housing unit minimum | 8 | 2,109 | 1,934 | 0 | 175 | 0 | 8.3% |
| **Generated shells (D3)** | | | | | | | | | |
| Single commuter | S0 | Ulrich (2025) area comparator | 30 | 510 | 77 | 177 | 13 | 243 | 50.2% |
| Single commuter | S0 | Hong Kong basic housing unit minimum | 8 | 510 | 320 | 0 | 190 | 0 | 37.3% |
| Single commuter | S2 | Ulrich (2025) area comparator | 30 | 510 | 83 | 146 | 7 | 274 | 55.1% |
| Single commuter | S2 | Hong Kong basic housing unit minimum | 8 | 510 | 357 | 0 | 153 | 0 | 30.0% |
| Single remote worker | S0 | Ulrich (2025) area comparator | 30 | 510 | 74 | 200 | 16 | 220 | 46.3% |
| Single remote worker | S0 | Hong Kong basic housing unit minimum | 8 | 510 | 294 | 0 | 216 | 0 | 42.4% |
| Single remote worker | S2 | Ulrich (2025) area comparator | 30 | 510 | 85 | 134 | 5 | 286 | 57.1% |
| Single remote worker | S2 | Hong Kong basic housing unit minimum | 8 | 510 | 371 | 0 | 139 | 0 | 27.3% |
| Couple | S0 | Ulrich (2025) area comparator | 45 | 510 | 0 | 313 | 0 | 197 | 38.6% |
| Couple | S0 | Hong Kong basic housing unit minimum | 8 | 510 | 197 | 0 | 313 | 0 | 61.4% |
| Couple | S2 | Ulrich (2025) area comparator | 45 | 510 | 0 | 206 | 0 | 304 | 59.6% |
| Couple | S2 | Hong Kong basic housing unit minimum | 8 | 510 | 304 | 0 | 206 | 0 | 40.4% |
| Parent and child | S0 | Ulrich (2025) area comparator | 45 | 510 | 0 | 337 | 0 | 173 | 33.9% |
| Parent and child | S0 | Hong Kong basic housing unit minimum | 8 | 510 | 173 | 0 | 337 | 0 | 66.1% |
| Parent and child | S2 | Ulrich (2025) area comparator | 45 | 510 | 0 | 253 | 0 | 257 | 50.4% |
| Parent and child | S2 | Hong Kong basic housing unit minimum | 8 | 510 | 257 | 0 | 253 | 0 | 49.6% |

## Supplemental information

### Supplemental figure legends

**Figure S1. Net internal area distributions and normalized plan examples across the evaluable dwelling corpus, related to Figure 1 and Table 1**
Top: step histograms of net internal area (NIA, in 2 m² bins from 8 to 50 m²) across evaluable units in Swiss Dwellings (D1, $n = 1,236$), ResPlan (D2, $n = 873$), and generated shells (D3, $n = 510$) (`results/figures/g4/F2.pdf`). Bottom: representative normalized geometries from D1 (42.8 m² NIA), D2 (46.5 m² NIA), and D3 (11.0 m² NIA) showing furnishable, storage-only, walkable-only, and fixed-service zones alongside entrance and window segments. Observed plans supply larger compact units ($\ge 16.75\text{ m}^2$), while generated shells extend systematic coverage down to 8.00 m².

**Figure S2. Orthographic 3D renders of showcase dwellings where multi-state furniture remains fixed across the day, related to Figure 2**
(A) Blender Cycles 3D cutaway renders (`results/figures/g4/F3b_10.pdf`) of the 10.00 m² generated shell for a couple on a normal day across Night, Workday, and Dinner under static S0 ($\text{FCI} = 0.577$, $\text{TB} = 0.00$) and form + time S2 ($\text{FCI} = 0.687$, $\text{TB} = 0.00$), with the foreground toilet enclosure cut away to expose the room interior. No double sleeping surface is deployed in any slot because operating clearances and wet-service access cannot fit simultaneously, and S2 furniture states remain fixed across all slots ($\text{TB} = 0.00$).
(B) Whole-flat 3D orthographic renders across Night, Workday, and Dinner (top two rows) and low-wall daytime main-room close-ups (bottom row) (`results/figures/g4/F3b_30.pdf`) of the 29.97 m² Swiss Dwellings observed plan for a couple under S0 ($\text{FCI} = 0.668$, $\text{TB} = 0.00$) and S2 ($\text{FCI} = 0.687$, $\text{TB} = 0.00$), with shared camera, lighting, and scale across whole-flat views. S2 furniture states do not change across slots ($\text{TB} = 0.00$), illustrating how narrow partitioned room geometry restricts multi-state gains even near 30 m² NIA.

**Figure S3. Layout validity, functional capacity, and runtime across four search methods on the 200-pair S2 benchmark, related to Figure 1 and Table S2**
Horizontal bar comparisons (`results/figures/g4/F7.pdf`) across $n = 200$ stratified unit–household pairs comparing standalone CP-SAT, descending-footprint greedy placement, standalone simulated annealing (20,000 proposals $\times$ 3 restarts), and the warm-started production pipeline on (left) share of independently valid layouts (%), (middle) mean validator FCI under S2, and (right) mean elapsed runtime (s; summing recorded S0 + S1 + S2 solve times for production and including S2 preparation plus validation for standalone methods). All methods return 100% valid layouts, and the warm-started production pipeline achieves the highest mean FCI at half the mean runtime of simulated annealing.

**Figure S4. Parity plots of geometry-only GraphSAGE predictions against solver-validated labels, related to Discussion and Table S3**
Scatter plots (`results/figures/g4/F8.pdf`) comparing GraphSAGE predictions (trained on grouped Swiss Dwellings training sites, $n = 884$ units across 323 sites) against solver-validated labels for static FCI (top row), form + time FCI (middle row), and point-identified equivalent-area gain $\Delta\text{EA}$ in m² (bottom row; excluding bound-only labels) across held-out Swiss Dwellings test sites ($n = 172$ units across 70 sites; left column), external ResPlan transfer ($n = 873$ units; middle column), and external generated shells ($n = 510$ units; right column), colored by household schedule around the dashed $y = x$ parity line. On held-out Swiss Dwellings sites, GraphSAGE Spearman rank correlations ranged from 0.087 to 0.661 for S0 FCI and from 0.088 to 0.588 for S2 FCI—below the prespecified $\rho \ge 0.80$ criterion—and predictions fell below retained lower bounds in 23 of 33 bound-only $\Delta\text{EA}$ cases (despite post-hoc S0 adequacy ROC AUCs of 0.796 for couples and 0.888 for parent and child; Table S3).

**Figure S5. Sensitivity of equivalent-area gains and adequate-area reductions to geometric, furniture, and solver parameters, related to Figures 3 and 4**
Paired changes relative to matched production controls (`results/figures/g4/F9.pdf`) in median identified positive $\Delta\text{EA}$ (m², top row) and $\Delta A_{\min}$ at $\tau = 0.95$ (m², bottom row; `×` marks contrasts where at least one logistic crossing is unsupported) across the four primary households when varying global clearance scale ($0.8\times, 1.2\times$; $n = 200$ pairs), grid/anchor resolution ($0.05\text{ m}, 0.20\text{ m}$; $n = 50$ units), solver time limit ($60\text{ s}, 120\text{ s}$; $n = 50$ units), single-item transformable removals ($n = 200$ pairs), and required walking width ($0.90\text{ m}$; $n = 200$ pairs). Note that changes in median identified $\Delta\text{EA}$ condition on each run's own subset of pairs with an identified positive gain, which can shift between conditions. Widening required walking circulation from 0.60 m to 0.90 m causes the largest capacity and adequacy shifts across all households.

**Figure S6. Room-level daytime body-free area versus whole-dwelling equivalent-area gains, related to Discussion**
(A) Daytime body-free floor area (m²) under S0 and S2 for single commuter and single remote worker schedules in an approximate $4 \times 3\text{ m}$ bedroom envelope using the study furniture catalogue, plotted alongside Bu and Che Mat's (2026) clearance-deducted static band (shaded, ~5–5.5 m²) and folded-bed value (dashed line, ~8 m²) (`results/figures/g4/F11.pdf`, left).
(B) Proportions of single-person dwelling–household pairs in observed plans ($n = 2,109$) and generated shells ($n = 510$) whose daytime body-free floor area decreased, stayed equal, or increased from S0 to S2 (`results/figures/g4/F11.pdf`, middle).
(C) Paired equivalent-area gain ($\Delta\text{EA}$, m²; filled circles for point-identified pairs, open upward triangles for lower-bounded pairs) plotted against the $\text{S2} - \text{S0}$ change in daytime body-free area across observed single-person plans (`results/figures/g4/F11.pdf`, right). Under scheduled whole-home optimization, daytime body-free area remains unchanged in the median single-person dwelling because static arrangements already satisfy daily demand without folding.

### Supplemental tables

**Table S1. Audited furniture library: body footprints, operating clearances, capabilities, and Amazon Berkeley Objects check, related to STAR Methods**
Dimensions (width along wall $\times$ depth into room, in meters), required directional clearance depths, served capability tokens, allowed strategies, per-unit instance caps, and dimensional comparison flags against 43,002 Amazon Berkeley Objects product triples (`results/tables/g4/T2.md`; full anchoring, height-class, storage-unit, and transition-effort attributes in `config/furniture.yaml`).

| Item | State | Body (m) | Clearance (m) | Capabilities | Strategies | Max. count | ABO check flag |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| single bed | static | 0.90 × 2.00 | left 0.60 | `sleep_1` | S0, S1, S2 | 2 | `OUTSIDE_IQR` |
| double bed | static | 1.40 × 2.00 | left 0.60, right 0.50 | `sleep_2` | S0, S1, S2 | 1 | `WITHIN_IQR` |
| wardrobe | static | 1.00 × 0.60 | front 0.70 | `storage` | S0, S1, S2 | 2 | `OUTSIDE_IQR` |
| shelving | static | 0.80 × 0.35 | front 0.60 | `storage` | S0, S1, S2 | 2 | `WITHIN_IQR` |
| desk | static | 1.20 × 0.60 | front 0.75 | `work_1` | S0, S1, S2 | 2 | `WITHIN_IQR` |
| dining table 2 | static | 0.75 × 0.75 | front 0.60, back 0.60 | `dine_2` | S0, S1, S2 | 1 | `OUTSIDE_IQR` |
| dining table 4 | static | 1.20 × 0.80 | front 0.60, back 0.60 | `dine_4`, `dine_2` | S0, S1, S2 | 1 | `OUTSIDE_IQR` |
| sofa 2 | static | 1.60 × 0.85 | front 0.60 | `lounge_2` | S0, S1, S2 | 1 | `OUTSIDE_IQR` |
| armchair | static | 0.80 × 0.80 | front 0.50 | `lounge_1` | S0, S1, S2 | 2 | `WITHIN_IQR` |
| wall bed single | stowed | 1.00 × 0.45 | front 0.40 | — | S1, S2 | 2 | `NO_MATCH;UNVALIDATED_STATE` |
| wall bed single | deployed | 1.00 × 2.10 | left 0.60 | `sleep_1` | S1, S2 | 2 | `OUTSIDE_IQR;UNVALIDATED_STATE` |
| wall bed double | stowed | 1.50 × 0.45 | front 0.40 | — | S1, S2 | 1 | `NO_MATCH;UNVALIDATED_STATE` |
| wall bed double | deployed | 1.50 × 2.15 | left 0.60, right 0.50 | `sleep_2` | S1, S2 | 1 | `UNVALIDATED_STATE` |
| wall bed over sofa | stowed | 1.60 × 0.90 | front 0.60 | `lounge_2` | S1, S2 | 1 | `OUTSIDE_IQR;UNVALIDATED_STATE` |
| wall bed over sofa | deployed | 1.60 × 2.15 | left 0.60, right 0.50 | `sleep_2` | S1, S2 | 1 | `UNVALIDATED_STATE` |
| sofa bed | stowed | 1.90 × 0.90 | front 0.60 | `lounge_2` | S1, S2 | 1 | `UNVALIDATED_STATE` |
| sofa bed | deployed | 1.90 × 2.00 | front 0.50 | `sleep_2` | S1, S2 | 1 | `UNVALIDATED_STATE` |
| drop leaf table | stowed | 0.80 × 0.20 | — | — | S1, S2 | 1 | `NO_MATCH;UNVALIDATED_STATE` |
| drop leaf table | deployed | 0.80 × 0.75 | front 0.60 | `dine_2`, `work_1` | S1, S2 | 1 | `OUTSIDE_IQR;UNVALIDATED_STATE` |
| fold down desk | stowed | 1.00 × 0.25 | front 0.40 | — | S1, S2 | 1 | `NO_MATCH;UNVALIDATED_STATE` |
| fold down desk | deployed | 1.00 × 0.55 | front 0.75 | `work_1` | S1, S2 | 1 | `UNVALIDATED_STATE` |
| extendable table | stowed | 0.80 × 0.80 | front 0.60, back 0.60 | `dine_2` | S1, S2 | 1 | `OUTSIDE_IQR;UNVALIDATED_STATE` |
| extendable table | deployed | 1.60 × 0.80 | front 0.60, back 0.60 | `dine_4`, `dine_2`, `work_1` | S1, S2 | 1 | `OUTSIDE_IQR;UNVALIDATED_STATE` |

**Table S2. Solver benchmark across 200 stratified unit–household pairs under S2, related to Results and Figure S3**
Independent validator pass rate, mean and median S2 FCI, and mean and median elapsed runtime across four search methods (`results/tables/g4/T5.md`).

| Search method | Matched cases ($n$) | Independently valid (↑) | Mean S2 FCI (↑) | Median S2 FCI (↑) | Mean time (s ↓) | Median time (s ↓) | Runtime accounting basis |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Standalone CP-SAT | 200 | 100.0% | 0.8675 | 0.9615 | 38.45 | 30.44 | Standalone S2 elapsed including preparation and validation |
| Greedy footprint | 200 | 100.0% | 0.8612 | 1.0000 | 3.47 | 1.94 | Standalone S2 elapsed including preparation and validation |
| Simulated annealing | 200 | 100.0% | 0.9341 | 1.0000 | 104.12 | 108.33 | Standalone S2 elapsed including preparation and validation |
| Production pipeline (S0–S2) | 200 | 100.0% | 0.9428 | 1.0000 | 53.86 | 10.68 | Accepted production S0 + S1 + S2 recorded solve time |

**Table S3. Geometry-only surrogate accuracy on held-out Swiss Dwellings sites and external transfer sets, related to Discussion and Figure S4**
Held-out Swiss Dwellings site-group test performance ($n = 172$ units across 70 sites) for predicting static FCI (`fci_S0`), form + time FCI (`fci_S2`), and D1-training-referenced equivalent-area gain (`saving_m2`, in m²) across linear area, LightGBM (`gbm_features`), tabular MLP (`mlp_features`), and GraphSAGE (`gnn_graph`) models (`results/tables/g4/T6.md`; full external transfer tables for ResPlan [$n = 873$] and generated shells [$n = 510$] are committed in `results/tables/g4/T6.md` and `results/expC/metrics.csv`). Point errors (MAE, RMSE, $R^2$, Spearman $\rho$) evaluate point-identified labels including exact zeros; `Bounds n` counts left- or right-bounded equivalent-area cases evaluated separately against lower bounds. `Adequacy ROC AUC` is a post-hoc diagnostic evaluating whether continuous FCI predictions rank cases at or above $\text{FCI} \ge 0.95$.

| Household | Target | Model | Evaluated $n$ | Bounds $n$ | MAE (↓) | RMSE (↓) | $R^2$ (↑) | Spearman $\rho$ (↑) | Inference (ms/unit ↓) | Post-hoc adequacy ROC AUC (↑) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Single commuter | `fci_S0` | `linear_area` | 172 | 0 | 0.032 | 0.048 | −0.048 | −0.019 | 0.0022 | 0.398 |
| Single commuter | `fci_S0` | `gbm_features` | 172 | 0 | 0.028 | 0.052 | −0.241 | 0.153 | 0.0395 | 0.598 |
| Single commuter | `fci_S0` | `mlp_features` | 172 | 0 | 0.052 | 0.081 | −2.031 | −0.101 | 0.0068 | 0.367 |
| Single commuter | `fci_S0` | `gnn_graph` | 172 | 0 | 0.022 | 0.052 | −0.279 | 0.087 | 0.0041 | 0.528 |
| Single commuter | `fci_S2` | `linear_area` | 172 | 0 | 0.011 | 0.015 | −0.368 | 0.056 | 0.0022 | 0.734 |
| Single commuter | `fci_S2` | `gbm_features` | 172 | 0 | 0.010 | 0.025 | −2.885 | −0.032 | 0.0395 | 0.406 |
| Single commuter | `fci_S2` | `mlp_features` | 172 | 0 | 0.040 | 0.069 | −29.417 | −0.017 | 0.0068 | 0.452 |
| Single commuter | `fci_S2` | `gnn_graph` | 172 | 0 | 0.006 | 0.025 | −3.056 | 0.088 | 0.0041 | 0.742 |
| Single commuter | `saving_m2` | `linear_area` | 155 | 17 | 0.000 | 0.000 | — | — | 0.0022 | — |
| Single commuter | `saving_m2` | `gbm_features` | 155 | 17 | 0.180 | 0.330 | — | — | 0.0395 | — |
| Single commuter | `saving_m2` | `mlp_features` | 155 | 17 | 0.343 | 0.645 | — | — | 0.0068 | — |
| Single commuter | `saving_m2` | `gnn_graph` | 155 | 17 | 0.199 | 0.428 | — | — | 0.0041 | — |
| Single remote worker | `fci_S0` | `linear_area` | 172 | 0 | 0.038 | 0.065 | −0.004 | 0.084 | 0.0021 | 0.555 |
| Single remote worker | `fci_S0` | `gbm_features` | 172 | 0 | 0.031 | 0.064 | 0.040 | 0.265 | 0.0408 | 0.721 |
| Single remote worker | `fci_S0` | `mlp_features` | 172 | 0 | 0.060 | 0.096 | −1.173 | 0.021 | 0.0062 | 0.512 |
| Single remote worker | `fci_S0` | `gnn_graph` | 172 | 0 | 0.028 | 0.067 | −0.082 | 0.142 | 0.0041 | 0.602 |
| Single remote worker | `fci_S2` | `linear_area` | 172 | 0 | 0.009 | 0.013 | −0.258 | 0.015 | 0.0021 | 0.560 |
| Single remote worker | `fci_S2` | `gbm_features` | 172 | 0 | 0.009 | 0.023 | −2.795 | 0.002 | 0.0408 | 0.555 |
| Single remote worker | `fci_S2` | `mlp_features` | 172 | 0 | 0.050 | 0.079 | −43.064 | 0.037 | 0.0062 | 0.499 |
| Single remote worker | `fci_S2` | `gnn_graph` | 172 | 0 | 0.006 | 0.022 | −2.420 | 0.223 | 0.0041 | 0.783 |
| Single remote worker | `saving_m2` | `linear_area` | 167 | 5 | 0.206 | 0.358 | 0.010 | 0.079 | 0.0021 | — |
| Single remote worker | `saving_m2` | `gbm_features` | 167 | 5 | 0.267 | 0.446 | −0.536 | 0.208 | 0.0408 | — |
| Single remote worker | `saving_m2` | `mlp_features` | 167 | 5 | 0.432 | 0.822 | −4.212 | −0.010 | 0.0062 | — |
| Single remote worker | `saving_m2` | `gnn_graph` | 167 | 5 | 0.277 | 0.522 | −1.102 | 0.098 | 0.0041 | — |
| Couple | `fci_S0` | `linear_area` | 172 | 0 | 0.082 | 0.131 | 0.089 | 0.469 | 0.0020 | 0.732 |
| Couple | `fci_S0` | `gbm_features` | 172 | 0 | 0.064 | 0.124 | 0.177 | 0.523 | 0.0432 | 0.794 |
| Couple | `fci_S0` | `mlp_features` | 172 | 0 | 0.083 | 0.140 | −0.040 | 0.402 | 0.0068 | 0.725 |
| Couple | `fci_S0` | `gnn_graph` | 172 | 0 | 0.063 | 0.131 | 0.090 | 0.588 | 0.0043 | 0.796 |
| Couple | `fci_S2` | `linear_area` | 172 | 0 | 0.045 | 0.090 | 0.020 | 0.373 | 0.0020 | 0.620 |
| Couple | `fci_S2` | `gbm_features` | 172 | 0 | 0.042 | 0.093 | −0.052 | 0.343 | 0.0432 | 0.672 |
| Couple | `fci_S2` | `mlp_features` | 172 | 0 | 0.071 | 0.113 | −0.551 | 0.287 | 0.0068 | 0.565 |
| Couple | `fci_S2` | `gnn_graph` | 172 | 0 | 0.035 | 0.093 | −0.048 | 0.479 | 0.0043 | 0.722 |
| Couple | `saving_m2` | `linear_area` | 164 | 8 | 3.267 | 4.583 | 0.094 | 0.441 | 0.0020 | — |
| Couple | `saving_m2` | `gbm_features` | 164 | 8 | 2.865 | 4.286 | 0.208 | 0.510 | 0.0432 | — |
| Couple | `saving_m2` | `mlp_features` | 164 | 8 | 2.972 | 4.710 | 0.043 | 0.388 | 0.0068 | — |
| Couple | `saving_m2` | `gnn_graph` | 164 | 8 | 2.834 | 4.195 | 0.241 | 0.533 | 0.0043 | — |
| Parent and child | `fci_S0` | `linear_area` | 172 | 0 | 0.066 | 0.087 | 0.257 | 0.588 | 0.0021 | 0.821 |
| Parent and child | `fci_S0` | `gbm_features` | 172 | 0 | 0.048 | 0.077 | 0.421 | 0.688 | 0.0419 | 0.901 |
| Parent and child | `fci_S0` | `mlp_features` | 172 | 0 | 0.078 | 0.112 | −0.229 | 0.386 | 0.0063 | 0.722 |
| Parent and child | `fci_S0` | `gnn_graph` | 172 | 0 | 0.048 | 0.077 | 0.420 | 0.661 | 0.0041 | 0.888 |
| Parent and child | `fci_S2` | `linear_area` | 172 | 0 | 0.040 | 0.059 | 0.091 | 0.485 | 0.0021 | 0.771 |
| Parent and child | `fci_S2` | `gbm_features` | 172 | 0 | 0.031 | 0.062 | −0.020 | 0.443 | 0.0419 | 0.767 |
| Parent and child | `fci_S2` | `mlp_features` | 172 | 0 | 0.061 | 0.093 | −1.269 | 0.251 | 0.0063 | 0.627 |
| Parent and child | `fci_S2` | `gnn_graph` | 172 | 0 | 0.025 | 0.056 | 0.170 | 0.588 | 0.0041 | 0.835 |
| Parent and child | `saving_m2` | `linear_area` | 169 | 3 | 4.058 | 5.147 | 0.187 | 0.482 | 0.0021 | — |
| Parent and child | `saving_m2` | `gbm_features` | 169 | 3 | 2.945 | 4.259 | 0.443 | 0.630 | 0.0419 | — |
| Parent and child | `saving_m2` | `mlp_features` | 169 | 3 | 3.467 | 4.717 | 0.317 | 0.562 | 0.0063 | — |
| Parent and child | `saving_m2` | `gnn_graph` | 169 | 3 | 3.755 | 4.951 | 0.248 | 0.558 | 0.0041 | — |

**Table S4. Kit comparisons: training selection, transfer cohorts, and Hong Kong per-size adequacy, related to Results and Figure 6**
Quality-scored capacity ($\text{FCI}_q$) and adequacy ($\text{FCI}_q \ge 0.95$) comparisons between parametric furniture kits and standard catalogue dimensions (`results/g3_review_k3/kit.yaml`, `results/g3_review_k3/paired_effects.csv`, `results/g3_review_k3/hk_h3_size_bands.csv`, `results/g3_review_k3/hk_adequacy_by_size.csv`, and `reports/phase_11d_K3.md`). Part A compares the top-ranked fixed kit per household against the optimized catalogue and the per-shell bespoke upper bound across the 30 frozen 8–15 m² generated training shells (`H1_kit_01`: 0.80 m single wall bed, $0.80 \times 0.45\text{ m}$ fold-down desk, $0.70 \times 0.60\text{ m}$ drop-leaf table, 0.60 m wardrobe; `H3_kit_02`: 1.50 m double wall bed, $1.20 \times 0.55\text{ m}$ fold-down desk, $1.00 \times 0.75\text{ m}$ drop-leaf table, 1.40 m wardrobe; commuter matched-search parity candidate `H1_kit_02`: 1.00 m single wall bed, $1.20 \times 0.55\text{ m}$ fold-down desk, $1.00 \times 0.75\text{ m}$ drop-leaf table, 1.40 m wardrobe). Part B reports paired kit-minus-catalogue differences with 95% bootstrap confidence intervals (1,000 resamples of shell pairs for training, held-out, and observed cohorts; 1,000 resamples of the 30 shape templates for Hong Kong). Part C enumerates adequate shells ($n = 30$ templates per integer m²) across the 8–20 m² Hong Kong grid; for the couple, band totals (`Larger kit S2` versus `Optimized catalogue S2`) are 0/150 versus 0/150 at 8–12 m² (mean $\text{FCI}_q$ 0.448 versus 0.500), 51/120 versus 30/120 at 13–16 m², and 103/120 versus 102/120 at 17–20 m² (modeled $A_{\min}$ 15.39 [14.67, 16.19] versus 16.12 [15.70, 16.57] m², a 0.73 m² point difference; single commuter compact kit $A_{\min}$ 14.38 [13.83, 14.98] versus 12.30 [11.90, 12.64] m²).

*Part A. Training selection and bespoke upper bound ($n = 30$ generated shells, 8–15 m² NIA)*

| Household | Selected kit ID | Runner-up | Catalogue mean $\text{FCI}_q$ (↑) | Selected kit mean $\text{FCI}_q$ (↑) | Bespoke mean $\text{FCI}_q$ (↑) | Bespoke gain captured (↑) | Adequate ($\text{FCI}_q \ge 0.95$): kit vs catalogue (bespoke) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| Single commuter | `H1_kit_01` | Catalogue | 0.7127 | 0.7141 | 0.7343 | 6.2% | 11/30 vs 13/30 (13/30) |
| Couple | `H3_kit_02` | Catalogue | 0.6322 | 0.6344 | 0.6612 | 7.4% | 5/30 vs 2/30 (6/30) |

*Part B. Paired kit-versus-catalogue comparisons across training, transfer, and Hong Kong cohorts*

| Household | Candidate kit | Cohort | Pairs ($n$) | Mean $\text{FCI}_q$: kit − catalogue [95% CI] | Kit higher / equal / lower | Adequate: kit vs catalogue | Adequate only on kit / only on catalogue |
| :--- | :--- | :--- | ---: | :--- | ---: | ---: | ---: |
| Single commuter | `H1_kit_02` | Training, matched extra search | 30 | −0.0284 [−0.0557, −0.0042] | 14 / 7 / 9 | 7 vs 13 | 0 / 6 |
| Single commuter | `H1_kit_01` | Training, best saved | 30 | +0.0013 [−0.0153, +0.0200] | 8 / 7 / 15 | 11 vs 13 | 0 / 2 |
| Single commuter | `H1_kit_01` | Training, original confirmation | 30 | +0.0009 [−0.0156, +0.0195] | 8 / 7 / 15 | 11 vs 13 | 0 / 2 |
| Single commuter | `H1_kit_01` | Held-out generated shells | 15 | +0.0185 [−0.0166, +0.0551] | 3 / 9 / 3 | 7 vs 6 | 2 / 1 |
| Single commuter | `H1_kit_01` | Observed plans ($\le 20\text{ m}^2$) | 15 | +0.0036 [−0.0055, +0.0121] | 4 / 10 / 1 | 13 vs 13 | 0 / 0 |
| Single commuter | `H1_kit_01` | Hong Kong model shells | 390 | −0.0389 [−0.0564, −0.0230] | 54 / 168 / 168 | 184 vs 246 | 5 / 67 |
| Couple | `H3_kit_02` | Training, matched extra search | 30 | +0.0021 [−0.0336, +0.0279] | 21 / 3 / 6 | 5 vs 2 | 3 / 0 |
| Couple | `H3_kit_02` | Training, original confirmation | 30 | −0.0044 [−0.0395, +0.0220] | 20 / 3 / 7 | 4 vs 2 | 2 / 0 |
| Couple | `H3_kit_02` | Held-out generated shells | 15 | −0.0242 [−0.0946, +0.0315] | 9 / 2 / 4 | 3 vs 0 | 3 / 0 |
| Couple | `H3_kit_02` | Observed plans ($\le 20\text{ m}^2$) | 15 | +0.0066 [−0.0040, +0.0181] | 7 / 3 / 5 | 10 vs 8 | 2 / 0 |
| Couple | `H3_kit_02` | Hong Kong model shells | 390 | −0.0228 [−0.0345, −0.0120] | 184 / 71 / 135 | 154 vs 132 | 35 / 13 |

*Part C. Per-size adequacy counts ($\text{FCI}_q \ge 0.95$) across Hong Kong model shells ($n = 30$ templates per integer m²)*

| NIA (m²) | Commuter S0 | Commuter rescored S2 | Commuter optimized catalogue S2 | Commuter compact kit S2 (`H1_kit_01`) | Couple S0 | Couple S1 | Couple rescored S2 | Couple optimized catalogue S2 | Couple larger kit S2 (`H3_kit_02`) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 9 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 10 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 11 | 0/30 | 4/30 | 4/30 | 3/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 12 | 4/30 | 12/30 | 12/30 | 5/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 13 | 11/30 | 21/30 | 21/30 | 12/30 | 0/30 | 0/30 | 0/30 | 0/30 | 4/30 |
| 14 | 22/30 | 27/30 | 29/30 | 18/30 | 0/30 | 0/30 | 2/30 | 2/30 | 7/30 |
| 15 | 27/30 | 30/30 | 30/30 | 19/30 | 0/30 | 0/30 | 9/30 | 10/30 | 16/30 |
| 16 | 29/30 | 30/30 | 30/30 | 22/30 | 1/30 | 4/30 | 16/30 | 18/30 | 24/30 |
| 17 | 30/30 | 30/30 | 30/30 | 26/30 | 2/30 | 5/30 | 23/30 | 23/30 | 24/30 |
| 18 | 30/30 | 30/30 | 30/30 | 24/30 | 8/30 | 17/30 | 24/30 | 25/30 | 26/30 |
| 19 | 30/30 | 30/30 | 30/30 | 26/30 | 4/30 | 14/30 | 26/30 | 27/30 | 26/30 |
| 20 | 30/30 | 30/30 | 30/30 | 29/30 | 11/30 | 23/30 | 26/30 | 27/30 | 27/30 |
| **Overall (8–20, $n = 390$)** | **54.6%** | **62.6%** | **63.1% (246/390)** | **47.2% (184/390)** | **6.7%** | **16.2%** | **32.3%** | **33.8% (132/390)** | **39.5% (154/390)** |
