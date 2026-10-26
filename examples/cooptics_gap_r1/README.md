# CoOpticsGap+ R1 | Synthetic shadows ≠ coherent detector speckle

**2026-10-26 · Public-safe scientific teaching canary · NOT measured optics, ET contact, divine evidence, a drug experiment or deployed CoOrbWare.**

This is the **first bounded executable canary** for the pre-existing [CoOpticsGap+ R0 research plan](https://github.com/CoCivium/CoCivium/blob/main/docs/CoTheoryAll/cooptics/ROUGH_SURFACE_GAP_LIGHT_R0_20261026.md) and its [six-model hypothesis registry](https://github.com/CoCivium/CoCivium/blob/main/ai/research/cooptics-rough-gap-r0.json). It also respects the earlier [CoRenewal+ selective-amplification](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORENEWAL_SELECTIVE_AMPLIFICATION_R0_20261026.md), [CoInterstice observer/field separation](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COINTERSTICE_OBSERVER_PERTURBATION_MEDIA_FABRIC_R0_20261026.md), and [CoFFF contact evidence ladder](https://github.com/CoCivium/CoCivium/blob/main/docs/CoTheoryAll/cofff/COFFF_FIRST_FULL_CONTACT_RESEARCH_STORYBOARD_R0_20261025.md).

## One specific, important answer

Illumination of a rough surface can leave dark valleys from geometric occlusion, **but** coherent scattered fields also produce dark intensity values through destructive interference at the *detector*. A detector sample is not generally the same spatial coordinate as a surface valley. Changes in a polarization analyzer can change measured intensity through ordinary optical scattering. The first two ideas are tested here with different deliberately simplified models; the third uses a toy analyzer/Jones mixing term and **is not a calibrated prediction**.

The toy models are **separate instruments of explanation**, not a joint physical inverse solver. They do not establish a new energetic field, an independently observable aura, Planck-scale structure, G_d agency, an ET source, or hidden information inside laser speckle.

## Exact synthetic evidence (fixed seed 20261026)

| Discriminator | Toy result | Only warranted claim |
| --- | ---: | --- |
| Opposite illumination direction | 100 / 192 synthetic surface cells change ray-lit classification | Geometry matters under this toy surface and ray model |
| Surface shadowed from left/right | 100 / 192 and 98 / 192 | Some simulated low facets are occluded; not measured topography |
| Coherent detector variability | normalized CV 0.873150 | Phase interference creates a nonflat *detector* intensity distribution |
| Toy analyzer change (0° vs 45°) | mean normalized absolute change 0.242915 | The constructed Jones mixing changes the synthetic output; not real polarimetric calibration |
| Different toy wavelengths | mean normalized absolute change 0.903805 | Phase response changes with wavelength in the toy model |
| Low detector bins | 6.25% below 0.1× normalized mean | Low detector return does not imply empty physical gaps |
| Offline unit tests | **40/40 PASS** | The code implements the bounded synthetic contract; no external replication |

The two companion PNG plots are in the originating conversation ZIP and can be regenerated from this branch with `render_cooptics_r1.py`; they are not committed as binary assets in this candidate branch. Machine data: [synthetic_results_r1.json](synthetic_results_r1.json). The raw surface array, ray masks, phase-derived detector traces, negative controls, source bytes hash and model parameters are in that JSON.

## Replay, no sensor access

```sh
python3 -m pip install numpy matplotlib    # only if not already available
python3 -m unittest -q test_cooptics_canary_r1.py
python3 cooptics_canary_r1.py --seed 20261026 --output a_new_synthetic_run.json
python3 render_cooptics_r1.py a_new_synthetic_run.json --out .
```

The runner refuses to overwrite an existing JSON target. No optical input, camera, microphone, keyboard monitoring, remote request, model worker, account, ET feed, or external mutation. Rendering is optional and reads an explicit named local synthetic JSON file. Synthetic coordinates/units have no calibration to a physical sample.

## CoTurtle+ controls and falsifiers

- **Geometric null:** a smooth flat synthetic surface has no occluded cells under the ray-shadow model.
- **Directional inverse:** reversing the illumination side changes a large subset of geometric shadows, holding the surface constant.
- **Wave null:** idealized incoherent intensity is a flat detector baseline; phase-coherent addition produces speckle structure even for unchanged geometry.
- **Optical phase invariance:** shifting every surface height by the same constant creates a global phase change, leaving *normalized* coherent far-field intensity unchanged in this model.
- **Analyzer challenge:** the toy cross-scattered Jones component changes the output with analyzer rotation but is not a Mueller-matrix or Maxwell-solver validation.
- **Domain counterexample:** spatial detector bins are not in one-to-one correspondence with surface sample positions. Inferring a physical gap from a dark detector bin is the tempting but unsupported shortcut.
- **Instrument challenge:** no measured camera noise, beam profile, clipping, polarization leakage, material properties or near-field Maxwell scattering are included; all remain needed for a real experiment.

### Link to the wider framework without collapsing categories

**CoNull+**: `LOW_DETECTED_INTENSITY` ≠ `NO_PHOTONS` ≠ `NO_MATERIAL` ≠ `NO_SIGNAL`. **CoTheoryAll+**: compare normal optical causes and explicit residuals before proposing extraordinary mechanisms. **CoEnerget+**: energy must be quantified in watts/joules for physical illumination, and in measured resource units for computing. **CoAura+ / G_d**: optional subjective/philosophical lenses, not source authentication. **DMT**: altered perception is an interesting neuroscience research subject, not a calibrated photon detector; this experiment does not use or recommend drugs. **ET / CoFFF**: public SETI archives require separate radio/astronomy protocols, interference checks and independent reproduction; no external intelligence is observed or addressed here.

For the *stability versus growth* question, [CoRenewal+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORENEWAL_SELECTIVE_AMPLIFICATION_R0_20261026.md) is the explicit parent. Gain needs verified benefit, a budget and a limiter. More photons or more noisy candidate graphs do not imply truth or useful progress. Dynamic equilibrium and intermittent growth are compatible; perpetual amplification without cost is not.

## Research and safety sources

- [NIST: Germer & Asmail, polarization of microrough-surface scattering](https://www.nist.gov/publications/polarization-light-scattered-microrough-surfaces-and-subsurface-defects-0)
- [Optics Express: Amra et al., multiscale polarization in surface speckle](https://pubmed.ncbi.nlm.nih.gov/18607448/)
- [Prigogine, Nobel Prize, dissipative structures](https://www.nobelprize.org/prizes/chemistry/1977/prigogine/facts/)
- [Breakthrough Listen technosignature methods and false positives](https://seti.berkeley.edu/ml_gbt/)
- [DMT and visual cortex population receptive-field changes, 2024](https://pubmed.ncbi.nlm.nih.gov/38964563/)
- [Health Canada laser-safety classes](https://www.canada.ca/en/health-canada/services/health-risks-safety/radiation/everyday-things-emit-radiation/laser-products.html)

**No physical laser test is proposed for unsupervised home operation.** A real optical follow-up should use an appropriately enclosed certified Class 1 system or a qualified optical lab, with exposure and reflection controls. A dark sensor value can reflect instrument setup, processing or detection thresholds, not a cosmic message.

## Next real proof

1. Run this synthetic canary on a genuinely independent second runtime and compare the exact source/results and a known negative case.
2. If qualified optical measurements become available, add a **rights-cleared, calibrated, raw** surface dataset and independently known specimen geometry. Separate illuminated-surface images from far-field detector measurements.
3. Require CoReview/CoTurtle and a genuine receiver's acceptance before claiming a new physical mechanism, meaningful insight or public product benefit.

**Rails:** `SYNTHETIC_NE_MEASUREMENT` · `DETECTOR_DARK_NE_SURFACE_VOID` · `SPECKLE_NE_ET` · `DMT_EXPERIENCE_NE_EXTERNAL_SENSOR` · `GD_INTERPRETATION_NE_CAUSAL_ENERGY` · `DATASET_NE_RECEIVER_ACK` · `COEBE_NE_STATIC_DEATH` · `POSITIVE_FEEDBACK_NE_UNBOUNDED_RESOURCES`.
