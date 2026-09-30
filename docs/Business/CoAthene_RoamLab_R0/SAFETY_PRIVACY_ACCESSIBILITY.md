# Safety, Privacy and Accessibility

## 1. Operating principle

Immersive learning is optional. No learner should be excluded because they cannot, should not, or do not want to wear a headset.

IMMERSION_NE_REQUIREMENT  
ACCESSIBILITY_NE_AFTERTHOUGHT

## 2. Physical safety

Before every session:

- inspect headset straps, lenses, controllers and cables;
- confirm clear play boundaries;
- remove trip hazards;
- mark seated and standing zones;
- preserve fire/egress routes;
- confirm ventilation;
- confirm charging/electrical safety;
- keep bags/coats away from movement areas;
- provide staff-controlled stop/pause;
- keep first-aid/emergency procedures available;
- follow device manufacturer age/use guidance.

During operation:

- active facilitator observation;
- stop immediately for dizziness, nausea, disorientation, pain, panic or discomfort;
- no forced participation;
- no running while wearing a headset;
- no unsupervised roaming;
- provide regular breaks;
- clean shared contact surfaces appropriately between users.

## 3. Motion and sensory comfort

Every lesson should carry a comfort profile:

- seated / standing;
- artificial locomotion;
- teleport movement;
- camera acceleration;
- flashing/flicker;
- loud audio;
- height exposure;
- enclosed spaces;
- intense emotional content.

Provide:

- motion-reduced mode;
- seated mode;
- observer/display mode;
- immediate stop;
- content preview for facilitators.

## 4. Privacy defaults

Default to collecting less.

Avoid by default:

- facial recognition;
- eye-tracking retention;
- emotion inference;
- voice profiling;
- persistent biometric identifiers;
- advertising IDs;
- behavioural ad profiles;
- unnecessary video/audio recording;
- persistent learner accounts.

Where a device technically captures sensor data for normal operation, distinguish temporary device processing from retained/exported data.

## 5. Identity

Prefer session-level pseudonyms or no identity at all when the learning goal does not need identity.

A useful learner artifact can often be:

session -> activity -> output -> teacher-selected attribution

rather than:

global learner account -> persistent behaviour graph

DEVICE_NE_PERSON  
SESSION_NE_PERMANENT_IDENTITY

## 6. Recording

Default: no recording.

If recording is needed:

- define purpose;
- identify exact camera/microphone;
- obtain required consent;
- show visible recording status;
- minimize field of view/data;
- define retention;
- define access;
- define deletion;
- prohibit unrelated reuse.

PUBLIC_EVENT_NE_BLANKET_CHILD_RECORDING_CONSENT

## 7. Data classes

Classify at minimum:

- public lesson content;
- operational telemetry;
- school/business contact data;
- attendance;
- learner work;
- learner identifiers;
- accessibility/accommodation information;
- photos/video/audio;
- biometric/sensor-derived data;
- health/emergency information.

Do not treat all data as one blob called "analytics."

## 8. Retention

Every retained class should have:

- reason;
- owner/steward;
- retention period;
- deletion path;
- export path;
- sharing scope.

If no reason survives review, delete or do not collect.

## 9. Child safety / supervision

The operator should define:

- who has custody/supervision responsibility;
- facilitator-to-participant capacity;
- arrival/departure process;
- bathroom/break procedure;
- lost-child procedure where relevant;
- emergency contacts where appropriate;
- staff/volunteer screening/training required for the actual operating model;
- one-adult-alone-with-child boundaries;
- photography rules.

Exact requirements depend on school/venue/program and must be qualified before operation.

## 10. Accessibility design

Provide a meaningful alternative to the default immersive path.

Candidate features:

- wheelchair-accessible route/station;
- seated version;
- large shared display;
- captions;
- audio description where useful;
- adjustable text;
- high contrast;
- colour-independent cues;
- controller remapping;
- one-hand or assisted interaction;
- sensory-sensitive mode;
- quiet zone;
- motion-reduced mode;
- extra response time;
- facilitator-assisted navigation;
- multilingual text/audio where feasible.

Do not make the accessible path an inferior worksheet while everyone else receives the real experience.

## 11. AODA

Ontario's Accessibility for Ontarians with Disabilities Act and associated standards apply differently by organization type and employee count.

Operators must determine their own requirements. Educational/training organizations may have additional accessibility-training duties.

Regardless of threshold, RoamLab should use accessibility as a product-quality requirement.

## 12. Transport boundary

Parked/mobile learning and passenger transport are separate capabilities.

Before carrying passengers, separately qualify:

- vehicle classification;
- CVOR where applicable;
- correct driver class;
- daily inspection;
- semi-annual inspection;
- insurance;
- school-purpose requirements;
- accessibility;
- vendor/board requirements;
- emergency procedures;
- passenger supervision.

PARKED_LAB_NE_PASSENGER_BUS

## 13. Network/security

Prefer:

- local/offline content cache;
- isolated learning network;
- least privilege;
- no exposed admin interfaces;
- per-device inventory;
- update/currentness tracking;
- staged updates;
- recovery image/config;
- no default public inbound access.

Do not require students to join an operator's administrative network.

## 14. Content safety

Each module should identify:

- age range;
- sensitive themes;
- intense sensory content;
- historical trauma;
- medical/health boundaries;
- simulation limitations;
- AI-generated material;
- source provenance.

A historically or culturally sensitive immersive reconstruction must clearly distinguish:

- documented evidence;
- expert interpretation;
- artistic reconstruction;
- uncertainty.

## 15. AI boundary

AI may assist with:

- question generation;
- explanations;
- translation;
- adaptive difficulty;
- simulation support;
- facilitator prep.

Do not default to:

- diagnosing learners;
- assigning personality types;
- inferring mental health;
- ranking children by opaque models;
- hidden persuasion;
- consequential decisions without human review.

AI_OUTPUT_NE_EDUCATIONAL_TRUTH

## 16. Incident handling

Record:

- time;
- session/module;
- device;
- observed event;
- immediate response;
- people notified;
- whether personal data was involved;
- whether equipment was quarantined;
- corrective action;
- follow-up.

Preserve privacy. Incident transparency does not mean publishing a child's details.

## 17. Release gate

A module is not ready merely because it runs.

Require:

- safety test;
- accessibility path;
- privacy review;
- source/provenance review;
- facilitator instructions;
- offline/failure fallback;
- currentness date;
- correction path.

RUNS_NE_READY
