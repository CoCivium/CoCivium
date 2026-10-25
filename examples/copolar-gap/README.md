# CoPolarGap+ R0 | One measurable in-between

**25 October 2026 | Public-safe scientific teaching candidate.**

The user's question: why do the valleys and apparent spaces between the peaks of a rough surface light up or become dark under incident polarized laser light? Could optical structures be studied through CoMap+/CoOrbWare+ without confusing beautiful patterns with evidence for ET contact, holographic-universe claims, Planck effects, or G_d?

## Run on a browser without any installation

Open `CoPolarGap_Atelier_R0.html`. It is a single UTF-8 self-contained HTML file: no network, imports, telemetry, logging, cookies, key hooks, camera or laser control. In the two-panel interface, set roughness, illumination angle, analyzer orientation, coherence, wavelength and a reproducible seed. The resulting image and 1D profile update locally. Use **Export my simulation receipt** only if you want to save parameters and statistics.

Source lives separately in `model.mjs` (pure deterministic model), `app.js` (local UI), `index.template.html` and `build.mjs`; use `node build.mjs` to regenerate the standalone HTML. Use `node --test model.test.mjs ui.test.mjs` and `node benchmark.mjs` for bounded synthetic verification. Node 22 used for this reference wave.

## What the toy does and does not model

The rough surface is a 1D height proxy made of multi-frequency sinusoids. `geometricAt()` approximates normal incidence and upstream ridge masking, not ray-traced shadow formation. A deterministic 27-scatterer phasor sum constructs a **far-field-inspired** toy intensity. Each artificial scatterer has amplitude, phase, spatial slope and approximate polarization mixing. The analyzer projects the field onto one linear direction. The `coherence` slider blends coherent phasor intensity with incoherent intensity as a **pedagogical interpolation**, not a calibrated measured degree of coherence or a full Stokes/Mueller treatment. Colour is deliberately false-colour: brightness represents calculated intensity only.

Useful conceptual distinction:

- A **geometric valley** may be physically shadowed, have a different surface normal, or experience multiple bounces.
- An **optical dark speckle** may occur at a well-illuminated spot because coherent wavelets cancel in the observer direction.
- A **polarization dark region** may be suppressed by the selected analyzer while still carrying light in another electric-field orientation.
- A **camera dark pixel** may reflect exposure, sensor response or compression, not an actual microphysical darkness.

Thus do **not** infer 3D roughness or material composition uniquely from one intensity photograph.

## Real experiment: one independent question, multiple lenses

**Safety first.** Start with a flashlight, matte paper, textured cardboard and a viewing polarizer. For coherent speckle measurements, use only an appropriately labeled, low-power **Class 2 visible laser (continuous wave <=1 mW)** in a fixed safe geometry and as instructed by manufacturer. Never direct a beam at eyes, people, mirrors, a camera lens, optical magnifiers or anything that could redirect it into an observer. Do not use Class 3B or Class 4 equipment casually. In a shared space control bystanders and pets. Camera photos should capture *diffusely scattered* light from a matte sample, not the beam.

1. Hold sample, detector position, focus, ISO/exposure and white balance fixed. Record one broad-light image as the geometry/shadow reference.
2. With qualified laser illumination and the same matte surface, observe the speckle with no analyzer, then rotate the analyzer through at least 0°, 45°, 90° and 135° while controlling exposure. Record exact angle and photon/sensor dynamic range.
3. Translate the sample slightly and repeat. Coherent speckle may decorrelate or shift even while macroscopic valleys remain. Repeat with broader incoherent illumination to distinguish stable geometric shadows from coherence-dependent grains.
4. Compare intensity histograms and contrast `std(intensity)/mean(intensity)`, cross-correlation under polarizer/sample shifts, sensor saturation and regions with shadow geometry. Calibrate with a smooth or known-roughness control where practical.
5. Only *if* multi-scale structure persists across calibrated spatial scales, test quantitative self-similarity against nonfractal noise and instrument response; one fractal-looking photo is insufficient.
6. Preserve raw images, device power/class, geometry, field of view, analyzer angle, calibration, false positives, prior samples and independent repeat conditions. The simulated receipt is `HYPOTHESIS`, not physical observation.

Good controls: unpolarized LED, a flat matte card, a deliberately roughened card, polarization rotation, independent sample motion, a no-beam dark frame and exposure-locked repeats. Unexpected structure first triggers ordinary explanations including interference, diffraction, aliasing, glare, internal reflection, autofocusing and sensor electronics.

## Relation to existing CoCivium sources

- `docs/Architecture/COLIVING_HIGHLIGHT_R0.md`: one stable source, many typed, loss-aware projections.
- `examples/colensmedia/README.md`: text/map/orb thematic views, not physics certification.
- `docs/Architecture/COEXPERIMENT_SPACE_TURTLES_R0.md`: separate huge logical candidate spaces from a tiny bounded executed frontier.
- CoFFF+ and First Full Contact+: contact/shared reference remain **hypotheses of relations** and are **NOT** established by optical texture. G_d symbolism is a philosophical or artistic lens, not a measured optical cause.

## External research foundation

- NIST, T. A. Germer, *Measuring Interfacial Roughness by Polarized Optical Scattering*: https://www.nist.gov/publications/measuring-interfacial-roughness-polarized-optical-scattering
- Optics Express, Amra et al. (2008), surface/bulk defects and partial polarization: https://pubmed.ncbi.nlm.nih.gov/18607448/
- Optica, *Rough surface scattering using a source able to produce an incident beam with controlled polarization and coherence*: https://opg.optica.org/ao/abstract.cfm?uri=ao-60-5-1182
- Phys Rev E, *Coherence of light scattered from a randomly rough surface*: https://journals.aps.org/pre/abstract/10.1103/PhysRevE.71.036606
- Health Canada, Laser Products: https://www.canada.ca/en/health-canada/services/health-risks-safety/radiation/everyday-things-emit-radiation/laser-products.html

## Verification truth

- `model.test.mjs` + `ui.test.mjs`: **50/50 PASS** in synthetic Node VM and deterministic model checks.
- An initial test run yielded **40/41** because of a *test expectation error* for a negative grid dimension. The failing output remains `tests_initial.tap`; the revised valid clamp expectation is retained as one of the 50 passing tests. No original source was overwritten.
- Chromium headless screenshot could not complete in the current environment (timed out); **BROWSER_VISUAL=HELD**, real user/X2 acceptance remains **HELD**.
- `performance.json` is a host-specific synthetic grid frame-time benchmark, **not** any optical measurement.
- No device or laser was accessed. No external model, Claude, X2, Pi, Ollama or ET feed was queried as part of this experimental implementation.
- No scientific discovery, new physics, ET evidence, Planck-scale measurement or proof of holographic ontology is claimed.

FOSS Forever | CoGoAll | Working Together Respectfully | Privacy by design | CoFFF hypothesis, not contact confirmation.
