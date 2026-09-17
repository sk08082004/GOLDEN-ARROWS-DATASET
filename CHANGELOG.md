# Changelog

All notable changes to Golden Arrows Dataset are documented here.

## [3.0.0]

Release date: To be assigned at publication

### Added

- Rich transition-level simulation dataset for 100 missions.
- Four mission types represented equally: PATROL, SURVEILLANCE, SEARCH, and RECOVERY.
- 11,570 transitions and 347,100 drone-transition records across 30 drones per transition.
- Advanced Swarm Behavior telemetry included throughout the dataset.
- Seven verified behavior components: cohesion, alignment, separation, formation, target attraction, network preservation, and boundary avoidance.
- Separate raw mission data and processed transition data organization.
- Schema, validation, and statistical documentation supporting the released dataset.
- Optional ML-ready derivatives and preprocessing examples provided as separate resources.

### Changed

- V3.0 introduces richer, behavior-aware transition telemetry with explicit swarm behavior, transition-level records, and raw/processed dataset organization.
- Dataset V2 was an internal development and validation baseline and is not part of the Golden Arrows Dataset V3.0 public release.
- V3.0 retains raw mission context and processed transition records to support transition-level analysis and ML-oriented preparation.

### Fixed

- Final validation state for the public V3.0 release was verified with consistent mission counts, transition counts, drone cardinality, mission-type balance, and Advanced Swarm Behavior activation.
- Independent audit and validation checks were completed for the final dataset package.

### Validation

- 100 missions completed.
- 25 PATROL, 25 SURVEILLANCE, 25 SEARCH, and 25 RECOVERY missions.
- 11,570 transitions validated.
- 347,100 drone-transition records validated.
- 30 drones per transition validated.
- Advanced Swarm Behavior enabled and preserved in the dataset.
- Schema and policy consistency verified.
- Independent audit passed for the released dataset package.

