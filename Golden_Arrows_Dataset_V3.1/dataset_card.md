# Golden Arrows Dataset V3.1

## Dataset Overview

Golden Arrows Dataset V3.1 is a simulation-generated, transition-level
multi-drone swarm dataset for research in swarm intelligence, autonomous
multi-agent systems, swarm behavior, network-aware coordination, mission
intelligence, machine learning, and reinforcement learning.

This is simulated data, not real-world flight telemetry. It does not establish
real-world flight validation, safety, or operational effectiveness.

## Dataset Summary

| Item | Verified V3.1 value |
| --- | --- |
| Dataset name | Golden Arrows Dataset V3.1 |
| Dataset type | Simulation-generated multi-drone swarm transition dataset |
| Missions | 1,000 |
| Mission distribution | 250 PATROL, 250 SURVEILLANCE, 250 SEARCH, 250 RECOVERY |
| Transitions | 113,954 |
| Drone-transition records | 3,418,620 |
| Drones per transition | 30 |
| Completed missions | 1,000/1,000 |
| Time step | `dt = 0.5` |
| Maximum steps | 1,000 |
| Schema version | `golden_arrows_v3_rich_transition_1.0` |
| Policy representation | `SCRIPTED_MISSION_CONTROLLER+ADVANCED_SWARM_BEHAVIOR` |
| Behavior mode | `BOUNDED_CORRECTION_ON_MISSION_MOTION` |
| Collection seed | `20260916` |
| Mission seed range | `20260917`–`20261916` |

The 3,418,620 drone-transition records are derived from 113,954 transitions
with 30 drones per transition. They are nested, repeated records and must not
be treated as independent samples.

## Dataset Motivation

V3.1 provides simulated mission transitions, drone-level records, and
Advanced Swarm Behavior telemetry for studying multi-agent coordination,
mission behavior, and network-aware swarm dynamics. It is an expansion of the
V3.0 dataset and a separate release; V3.0 remains unchanged.

## Data Generation

The dataset was generated in simulation with 30 drones per transition across
four mission types, using the documented scripted mission controller and
Advanced Swarm Behavior configuration. Raw mission JSON and processed
transition JSONL files are provided. Verified configuration values are:

- Collection seed: `20260916`
- Mission seed range: `20260917` through `20261916`
- `dt = 0.5`
- `max_steps = 1000`
- Advanced behavior: enabled throughout

The architecture terminology retained for the dataset is:
`swarm_manager.py` → `advanced_swarm_controller.py` → `swarm_behavior.py` →
30 drones. No additional architecture components are asserted here.

## Mission Types

The dataset contains four mission types, with 250 missions of each type:

| Mission type | Missions | Transitions |
| --- | ---: | ---: |
| PATROL | 250 | 63,694 |
| SURVEILLANCE | 250 | 22,036 |
| SEARCH | 250 | 11,856 |
| RECOVERY | 250 | 16,368 |
| **Total** | **1,000** | **113,954** |

## Advanced Swarm Behavior

Advanced Swarm Behavior is enabled throughout V3.1. Its seven documented
components are:

1. Cohesion
2. Alignment
3. Separation
4. Formation
5. Target attraction
6. Network preservation
7. Boundary avoidance

The behavior mode is `BOUNDED_CORRECTION_ON_MISSION_MOTION`. These terms
describe the simulator configuration and logged behavior, not learned
representations or evidence of real-world performance.

## Data Structure

The raw mission JSON files include `schema_version`, `collection`, `mission`,
`manager`, and `transitions`. The processed transition files are JSON Lines
(JSONL) and use schema version
`golden_arrows_v3_rich_transition_1.0`. There are 1,000 files in each form,
and their filenames correspond one-to-one.

`data/metadata.csv` contains one row per mission. Its columns are:

`mission_id,mission_type,seed,status,transition_count,drone_count,dt,max_steps,advanced_behavior_enabled,policy_type`

The `schema/` directory provides the package's schema materials. Consult
those files for field-level definitions and validation constraints.

## Data Representation

### Raw Data

`data/raw/missions/` contains the 1,000 raw mission-level JSON files,
including collection and mission information and the transitions.

### Processed Data

`data/processed/transitions/` contains the 1,000 processed transition JSONL
files. These files use the retained rich-transition schema and correspond
one-to-one with the raw mission files.

### Metadata

`data/metadata.csv` indexes the missions and reports each mission's type,
seed, status, transition count, drone count, time step, maximum steps,
advanced-behavior status, and policy type.

## ML Preparation

The publication package contains the raw and processed data, metadata,
examples, schemas, and validation materials. It does not include generated
ML-ready datasets or `train.csv`, `validation.csv`, or `test.csv` files.

Users preparing model inputs should document preprocessing and split data at
the mission level rather than randomly splitting individual transitions. If
using the 68%/16%/16% mission-level split methodology, the conceptual split
is 680/160/160 missions overall, or 170/40/40 per mission type. These are
mission counts, not generated artifact counts or CSV row counts. A
mission-level split reduces direct mission leakage but does not make
transitions or drone records independent.

## Temporal and Causal Considerations

Transition-level datasets have temporal and mission-level structure. Users
should inspect the schema and field timing before defining model inputs,
targets, or causal variables. Do not assume that records from different
drones or transitions are independent observations.

## Data Quality and Validation

The verified V3.1 validation results include:

- 1,000 raw mission JSON files and 1,000 processed transition JSONL files
- Exact one-to-one raw/processed filename correspondence
- 250 missions per mission type
- 113,954 total transitions and 3,418,620 derived drone-transition records
- 30 drones per transition
- Consistent schema version and `advanced_behavior_applied = true` for all
  transitions
- Behavior mode `BOUNDED_CORRECTION_ON_MISSION_MOTION`
- Policy type `SCRIPTED_MISSION_CONTROLLER+ADVANCED_SWARM_BEHAVIOR`
- 1,000/1,000 completed missions
- Zero NaN values, Inf values, duplicate-tick missions, or malformed/
  structural errors
- Mission-level structural integrity: PASS
- Minimum 9 and maximum 373 transitions per mission; reported mean 113.95

These checks assess structural and numerical integrity within the simulation.
They do not establish real-world validity or operational readiness.

## Known Considerations

The data are generated in a particular simulated setting with four mission
types, a scripted mission controller, and the documented swarm behavior.
Simulation assumptions and mission-generation rules constrain the
distribution. Assess the impact of mission-level dependence and simulation
specificity in any statistical or modeling work.

## Intended Uses

The dataset is intended to support research and analysis such as:

- Simulated swarm behavior and coordination analysis
- Multi-agent and reinforcement-learning methodology research
- Transition modeling and next-state prediction
- Network-aware coordination studies
- Preprocessing and feature-representation comparisons
- Reproducible analysis of the published simulation records

## Out-of-Scope Uses

V3.1 is not real-world flight telemetry, safety certification evidence, or
proof of production flight-control performance. It is not a substitute for
real-world testing and must not be represented as evidence of real-world
swarm effectiveness.

## Responsible / Ethical Considerations

The records represent simulated behavior rather than real-world operational
outcomes. Simulation assumptions may introduce bias, and models trained on
these data may learn simulation-specific patterns. Any real-world application
requires independent validation; simulation results alone do not establish
safety or effectiveness.

## Bias and Representativeness

The dataset covers only four mission types and one documented simulation
configuration. Its mission distribution is balanced by mission count, but
this does not make the simulated environment representative of all swarm
systems or operating conditions. Generalization beyond this setting must be
evaluated separately.

## Dataset Version and Citation

This package is **Golden Arrows Dataset V3.1**. It expands V3.0 from 100
missions (25 per type) to 1,000 missions (250 per type); V3.0 remains frozen
as a separate release.

Use the author and version information in `CITATION.cff`. A V3.1 DOI has not
been assigned in this package. The V3.0 DOI, `10.5281/zenodo.22816408`, must
not be cited as the DOI for V3.1.

## License

The dataset is released under CC BY 4.0. See `LICENSE` for the license terms.

## Reproducibility

The verified collection seed is `20260916`; mission seeds range from
`20260917` through `20261916`. The verified simulation parameters include
`dt = 0.5` and `max_steps = 1000`. No unsupported hardware, operating-system,
software-version, or performance claims are made here.
