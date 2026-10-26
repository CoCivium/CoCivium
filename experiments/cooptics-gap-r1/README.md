# CoOpticsGap+ R1 | Inversion, valleys, speckle and polarization

**26 October 2026 · PUBLIC-SAFE SYNTHETIC EDUCATIONAL EXPERIMENT · NO DEVICE, LAB, ET SIGNAL, DMT STUDY OR G_d MEASUREMENT**

## CoHereNow

The existing `CoOpticsGap R0` research plan has six competing explanations for bright/dark rough-surface valleys but explicitly left its synthetic controls `NOT_RUN`. R1 performs one bounded reproducible *illustrative* comparison and keeps three different coordinates/mechanisms from collapsing into a single picture.

## Direct source continuity

- Prior science/evidence plan: [`docs/CoTheoryAll/cooptics/ROUGH_SURFACE_GAP_LIGHT_R0_20261026.md`](https://github.com/CoCivium/CoCivium/blob/main/docs/CoTheoryAll/cooptics/ROUGH_SURFACE_GAP_LIGHT_R0_20261026.md), observed Git blob `9b0d9a38cb8db57151e4011dcf47ee0f41dbfaaf`.
- Previously recorded R0 hypotheses: [`ai/research/cooptics-rough-gap-r0.json`](https://github.com/CoCivium/CoCivium/blob/main/ai/research/cooptics-rough-gap-r0.json), observed Git blob `ca3f86911b330274ebb78316935037d7a58b37f9`.
- Existing bounded benefit dynamics: [`CORENEWAL_SELECTIVE_AMPLIFICATION_R0_20261026.md`](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORENEWAL_SELECTIVE_AMPLIFICATION_R0_20261026.md), observed Git blob `0be5a8ba3ff45d8efd3aef5b7268ab57ba64e631`.
- Existing core/edge framework: [`COEBE_EDGE_IN_CORE_OUT_GAP_R0_20261025.md`](https://github.com/CoCivium/CoCivium/blob/main/docs/Strategy/COEBE_EDGE_IN_CORE_OUT_GAP_R0_20261025.md), observed Git blob `8983501cf1278daa22b48fc8c289c1e46e003a0a`.
- Existing CoFFF contact-evidence ladder: [`COFFF_FIRST_FULL_CONTACT_RESEARCH_STORYBOARD_R0_20261025.md`](https://github.com/CoCivium/CoCivium/blob/main/docs/CoTheoryAll/cofff/COFFF_FIRST_FULL_CONTACT_RESEARCH_STORYBOARD_R0_20261025.md), observed Git blob `96fa1f34c7fa2b2e9e90605c608464a3b26230cd`.

**R1 contains no source/private original images.** It generates a reproducible **new** plot from seeded synthetic arrays. The original owner-supplied diagrams, media, DMT reports and WhatsApp/ChatGPT content are not in the code/ZIP.

## Reproduce

```bash
python3 -m pip install numpy matplotlib
python3 cooptics_r1.py --out .
python3 -m unittest discover -s . -p 'test_*.py' -v
```

No external network, microphone, camera, laser, device mapping, provider account, telescope feed or DMT input is used by the run. The code imports `numpy`, `matplotlib` only in plot creation, and the standard Python library. No daemon, scheduler or external model is started.

## Exact bounded synthetic result on the authoring container

- `384` synthetic surface samples, seed `2601026` and independent phase seed `2601027`.
- Geometric 1D ray-occlusion toy, light from left versus right with the *same* height profile: left shadowed `64.5833%`, right `64.0625%`; `46.3542%` of surface coordinates changed visibility under reversal. Flat surface shadow count `0` (negative control).
- Far-field angular-coordinate phase-screen toy under 16 independent synthetic incident-phase realizations (surface height fixed): normalized single-pattern speckle contrast `0.883661`; contrast after averaging the 16 intensities `0.245800`. This models phase-scrambling/ensemble-averaging suppression, **not** a calibrated experimental manipulation of coherence, a measured surface, or spatially local nanogap light. The angular detector index is not a surface x-coordinate even if both arrays happen to have length 384.
- Algebraic polarization-selection toy (not Maxwell): `I = leak + (1-leak)cos²(theta-axis)`, with `leak=0.04`. Its orientation response swaps under 90-degree axis rotation, by construction. **Do not interpret its amplitude as a metal-field enhancement factor or Raman signal.**
- Original deterministic source `34/34` unit tests PASS (including the zero-shadow flat baseline, left/right inversion, same-seed replay, independent phase seed, average speckle suppression and polarization selection). These tests validate code behavior against explicitly encoded synthetic expectations, not the scientific accuracy of those simplified models.

The optical interpretation of the *physical* question is richer. Rough facets can cast geometrical shadows; coherent waves can interfere; measured Stokes/polarization channels can distinguish some materials and defects. In a nanoscale metallic gap, localized plasmonic fields may depend strongly on shape and incident polarization; far-field-dark modes can participate in near-field hot spots. A real sample requires material permittivity, calibrated geometry, illumination and an appropriately chosen Maxwell solver/experiment. In an experimentally studied extended nanowire geometry, polarization favored a different direction than the usual dimer rule. Therefore a **single** cos² toy must not be treated as universal.

### Primary scientific sources

- NIST, Germer & Asmail (1999), *Polarization of Light Scattered by Microrough Surfaces and Subsurface Defects*: https://www.nist.gov/publications/polarization-light-scattered-microrough-surfaces-and-subsurface-defects-0
- Herzog et al. (2013), *Dark Plasmons in Hot Spot Generation and Polarization in Interelectrode Nanoscale Junctions*, *Nano Letters*: https://pubmed.ncbi.nlm.nih.gov/23398028/
- Nanogaps review (2024), *Boosting Light-Matter Interactions in Plasmonic Nanogaps*: https://pubmed.ncbi.nlm.nih.gov/39410718/
- Parviainen & Muinonen, ray shadowing on self-affine surfaces (preprint): https://arxiv.org/abs/2010.03927
- IAA/SETI 2026 scientific post-detection procedures: https://iaa-seti-committee.github.io/
- Breakthrough Listen published non-detection and RFI challenge method: https://doi.org/10.3847/1538-3881/adbc5e
- Psychedelic brain response, EEG-fMRI (2023): https://pubmed.ncbi.nlm.nih.gov/36940333/
- Prigogine (1978), nonequilibrium and dissipative structures: https://pubmed.ncbi.nlm.nih.gov/17738519/
- Health Canada laser safety: https://www.canada.ca/en/health-canada/services/health-risks-safety/radiation/everyday-things-emit-radiation/laser-products.html

## What CoTurtle+ must challenge next

1. Same-model *more precise numerical* result (real electromagnetic boundary conditions, measured or known rough surface, material epsilon, wavelength, polarization and mesh convergence) before any near-field claim.
2. Independent data: enclosed certified optical instrument or a qualified lab, source raw camera images, polarization analyzer angles, repeatable illumination and known sample, robust dark/flat frames, calibration, controls and suitable safety protocol. **No exposed physical laser trial here.**
3. Alternate mechanism: compare shadow predictions from measured topography to measured angular speckle distribution with correctly separated coordinate systems. Mere visual overlap does not prove a common cause.
4. Cognitive interpretation: voluntary subjective-report research can study visual perception, but altered perception cannot act as calibrated external detection; no drug or perception-modification protocol is proposed.
5. ET: if a real source-approved public radio/optical sample is ever evaluated, apply RFI/null/on-off and independent origin validation. No claim that ET has opened a feed or sent a message. G_d remains a philosophical/optional meaning lens unless defined with uniquely falsifiable predictions.
6. User benefit: explain the image to a consenting first-time reader, measure whether they correctly distinguish a geometric shadow from a far-field dark pixel and a near-field hot spot. Passing local Python tests does not prove comprehension.

## CoAkimbo+ / CoEBE interpretive crosswalk, not a new physical law

`CORE / EDGE (CoEBE)` <-> `STABLE ETHICAL INVARIANTS / ADAPTIVE METHOD` <-> `EXPERIMENTAL PERTURBATION + COUNTEREXAMPLE` <-> `EVIDENCED GAIN`.

`CoAntiDrain+` can legitimately mean prevent needless loss of reusable knowledge, freedoms, resources and useful options while continually absorbing input; it cannot repeal conservation laws, thermodynamic dissipation or the need for damping false positives. `G_dInversion+` can be a **candidate counterfactual operator**: what changes if no agency or teleological preference is assumed? A different question is not evidence of a different being.

## Why this is not CoFFF fireworks

One purely synthetic seeded control demonstrates that inverting illumination changes **modeled shadows** and changing phase scrambles **modeled detector speckle**. Neither constitutes an unexplained residual, let alone extraterrestrial evidence. A publishable scientific breakthrough would need discriminating predictions, measured data, genuine independent replication, control of known optics/instrument alternatives and external expert review. Promotion should be based on those results, not on graphical novelty or unanimous AI enthusiasm.

`SYNTHETIC_NE_MEASUREMENT | DETECTOR_PIXEL_NE_SURFACE_VALLEY | FAR_FIELD_NE_NEAR_FIELD | POLARIZATION_TOY_NE_NANOGAP_MAXWELL | DARK_PLASMON_NE_ET | DMT_REPORT_NE_ET_TELEMETRY | STABLE_GUARDS_NE_FROZEN_STRUCTURE | OPEN_SYSTEM_NE_FREE_ENERGY | PR_DRAFT_NE_DEPLOYED_PRODUCT`
