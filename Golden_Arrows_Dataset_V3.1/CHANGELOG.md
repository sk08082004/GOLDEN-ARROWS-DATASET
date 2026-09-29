# Changelog

All notable changes to Golden Arrows Dataset are documented here.

## [3.1.0]

Release date: To be assigned at publication

### Added

- Rich transition-level simulation dataset for 1,000 missions.
- Four mission types represented equally: PATROL, SURVEILLANCE, SEARCH, and RECOVERY.
- 113,954 transitions and 3,418,620 drone-transition records across 30 drones per transition.
- Advanced Swarm Behavior telemetry included throughout the dataset.
- Seven verified behavior components: cohesion, alignment, separation, formation, target attraction, network preservation, and boundary avoidance.
- Separate raw mission data and processed transition data organization.
- Schema, validation, metadata, and statistical documentation supporting the released dataset.
- Updated publication package corresponding to the V3.1 collection.

### Changed

- V3.1 expands the released mission collection from 100 missions in V3.0 to 1,000 missions.
- Each mission type is represented by 250 completed missions.
- The collection uses the documented seed configuration 20260916, with mission seeds spanning 20260917 through 20261916.
- V3.1 retains the V3.0 rich transition schema and publication organization while providing a substantially larger mission collection.
- Dataset V2 was an internal development and validation baseline and is not part of the Golden Arrows Dataset V3.1 public release.
- Generated ML-ready derivatives remain outside the publication package; preprocessing and ML preparation are documented as examples rather than distributed generated training datasets.

### Fixed

- Final validation state for the public V3.1 release was verified with consistent mission counts, transition counts, drone cardinality, mission-type balance, schema consistency, and Advanced Swarm Behavior activation.
- Raw mission files and processed transition files were independently checked for one-to-one correspondence.
- Mission-level structural and transition integrity checks were completed for the V3.1 collection.

### Validation

- 1,000 missions completed.
- 250 PATROL, 250 SURVEILLANCE, 250 SEARCH, and 250 RECOVERY missions.
- 113,954 transitions validated.
- 3,418,620 drone-transition records validated.
- 30 drones per transition validated.
- Advanced Swarm Behavior enabled throughout the dataset.
- Schema version `golden_arrows_v3_rich_transition_1.0` verified.
- Policy representation `SCRIPTED_MISSION_CONTROLLER+ADVANCED_SWARM_BEHAVIOR` verified.
- Behavior mode `BOUNDED_CORRECTION_ON_MISSION_MOTION` verified.
- Independent structural, integrity, and publication checks passed for the V3.1 dataset package.
