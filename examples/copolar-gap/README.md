# CoPolarGap+ R0 | One measurable in-between

**25 October 2026 | Public-safe scientific teaching candidate.**

The user's question: why do the valleys and apparent spaces between the peaks of a rough surface light up or become dark under incident polarized laser light? Could optical structures be studied through CoMap+/CoOrbWare+ without confusing beautiful patterns with evidence for ET contact, holographic-universe claims, Planck effects, or G_d?

## Run on a browser without any installation

Open the published [`index.html`](index.html). It is a single UTF-8 self-contained HTML file: no network, imports, telemetry, logging, cookies, key hooks, camera or laser control. In the two-panel interface, set roughness, illumination angle, analyzer orientation, coherence, wavelength and a reproducible seed. The resulting image and 1D profile update locally. Use **Export my simulation receipt** only if you want to save parameters and statistics.

**Published-branch source scope:** this branch contains the bundled model and UI inside [`index.html`](index.html), not the individually named `model.mjs`, `app.js`, `index.template.html` or `build.mjs` files. Those files and the original 50-case source/fake-DOM test harness were reported as retained in the originating conversation ZIP; they are **not reproduced by this GitHub branch**. To verify what an actual downloader receives, run `node --test examples/copolar-gap/published_source.test.mjs` from the repository root (Node 22). The exact embedded pure model is executed without running the browser UI, and negative no-effect controls are exercised. No claim of complete browser or physical apparatus verification follows.

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

### Observer reports and DMT (not an optical detector)

Some accounts connect laser-speckle patterns with DMT-associated geometric or glyph-like experiences. Such experiences can be studied as **subjective perception**, with careful controls for visual cortex effects, expectation, priming, camera/surface structure and reproducibility. The following published research documents drug-related changes in visual/brain activity, **not** externally sourced glyphs or ET/G_d communication:
- Pais et al., *NeuroImage* (2024), DOI 10.1016/j.neuroimage.2024.120718: https://pubmed.ncbi.nlm.nih.gov/38964563/
- Timmermann et al., *PNAS* (2023), DOI 10.1073/pnas.2218949120: https://pubmed.ncbi.nlm.nih.gov/36940333/

**No psychedelic use or laser viewing under intoxication is an accepted part of this optics canary.** An investigator can compare sober, pre-registered, blinded interpretations of ordinary stored imagery instead. A pattern recognized by an observer, even repeatedly, is not an independently measured source or message. Observation → optics/brain/instrument null models → prospective controls → independent repeat → scientific review precede any stronger claim.

### What a passing GitHub test actually proves

`published_source.test.mjs` checks that the exact self-contained **published HTML** contains and runs the pure deterministic toy and has defined negative boundaries. It neither reconstructs the original separately archived modular source, nor executes real browser rendering, nor demonstrates a microscope, laser, camera, alien signal, fractal scaling or physical field. Preserve the original README's 50/50 private test description as historical scope, and keep native/observer acceptance HELD.
