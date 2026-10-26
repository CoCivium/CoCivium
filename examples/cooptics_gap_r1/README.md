# CoOpticsGap+ R1 | Ray shadows are not detector speckle

**State:** offline synthetic method donor; not measured optics, a Maxwell solver, a laser/device installation, a DMT protocol, an ET detection, or evidence of an external G_d agent.

Follows the pre-existing CoOpticsGap+ R0 test plan in `docs/CoTheoryAll/cooptics/ROUGH_SURFACE_GAP_LIGHT_R0_20261026.md` and the corresponding `ai/research/cooptics-rough-gap-r0.json`. Do not create another optical theory authority.

## Run without installing packages

Requires Node.js 22+ and its standard library only.

```sh
node --check cooptics_gap_r1.mjs
node --test cooptics_gap_r1.test.mjs
node cooptics_gap_r1.mjs
node cooptics_gap_r1.mjs --seed=73
```

All commands are offline. No image pixels, raw keys, cameras, microphones, lasers, provider APIs, models, network requests, account logins or external messages are accessed. Exact version/seed and a SHA-256 of the generated synthetic surface are included in the JSON output.

## Four strictly separate synthetic controls

1. A **one-dimensional ray-shadow toy** uses a known generated height profile. Opposite virtual illumination directions cast shadows in different *surface coordinates*. This is geometric occlusion only.
2. A **one-dimensional scalar coherent phase-screen toy** transforms a reflection-like phase `4*pi*height/lambda` into far-field detector angular-bin intensity. Bright/dark interference values are in *detector coordinates*, not actual surface valleys. A smooth phase screen produces a central diffraction peak, while a rough synthetic phase screen produces diffuse angular-bin energy. A dark detector bin therefore cannot be interpreted as an empty physical surface gap.
3. An **independent phase-decorrelation surrogate** adds independently sampled random phases to the same synthetic height description, then averages 16 detector frames. This reduces synthetic speckle contrast; it is not a physical partial-coherence or multi-scattering model for an actual fixed rough specimen.
4. An **ideal polarization analyzer** shows Malus' law (`cos^2(theta)` at 0, 45 and 90 degrees). It is an instrument/reference projection, **not** a roughness or polarization-conversion solver.

This deliberately omits 2D/3D vector Maxwell fields, Fresnel coefficients, Stokes calibration, topographic metrology, camera artifacts, depolarization, wavelength-swept material spectroscopy, evanescent waves, rough nanogaps, and plasmons. Those require separately qualified simulations and, later, real calibration.

## Fixed synthetic example (seed 20261026, 64 samples, 16 decorrelated phase frames)

| Synthetic statistic | Result | Scoped interpretation |
| --- | ---: | --- |
| Geometry dark positions, light from left | 39 | Surface occlusion toy |
| Geometry dark positions, light from right | 30 | Same height map, changed illumination side |
| Positions with changed visibility | 31 | Direction-specific geometric shadow |
| Smooth phase diffuse fraction | 0 | Rectangular periodic phase reference |
| Rough phase diffuse fraction | 0.992897 | Angular-bin scalar diffraction only |
| Rough single-frame contrast | 0.975462 | Far-field coherent phase toy |
| Decorrelated mean contrast | 0.245228 | 16 phase-perturbed toy frames |
| Total rough/smooth scalar power ratio | 1 | Parseval/normalization check |
| Ideal analyzer 0 / 45 / 90 degrees | 1 / 0.5 / 0 | Malus-law reference; not measured polarization |

These contrasts are deterministic outputs of THIS chosen seeded fixture, not measured constants or evidence that rough gaps emit, absorb, hide, or encode external messages.

## Human-time acceptance

**Verified locally:** 50/50 Node v22.16.0 deterministic tests passed, including direct CLI replay, malformed input rejection, geometry inversion, far-field normalization, phase averaging, ideal analyzer controls, zero effects and uncertainty boundaries.

**Still HELD:** actual surface/camera data, material calibration, crossed-polarizer observations, 2D/vector field modeling, sensor errors, independent review, user comprehension, native X2 use, CoStead landing and cross-provider receiver ACK. A GitHub CI pass, when available, will prove only reproducible synthetic code and tests.

The next *physical* test should be performed only by a qualified optical laboratory using an appropriately enclosed, engineered laser system with explicit owner permission and safety review. Do not improvise laser exposure or couple drug use with instrumentation.

**Testable falsifier for the naive view:** if a dark **detector bin** can arise from interference while the geometric surface is fully specified, then `DARK_DETECTOR_BIN => EMPTY_SURFACE_GAP` is not valid as a general inference. This toy demonstrates the logical non-equivalence, not a novel optical mechanism.

`DARK_PIXEL_NE_SURFACE_VOID | SYNTHETIC_NE_MEASUREMENT | SPECKLE_NE_ET | G_D_SYMBOL_NE_PHYSICAL_FIELD | PERCEIVED_ENTITY_NE_EXTERNAL_ENTITY | PHOTON_ENERGY_NE_INFINITE_RESOURCES | SOURCE_NE_RECEIVER_ACK`.
