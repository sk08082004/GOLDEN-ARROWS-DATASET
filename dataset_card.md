# Golden Arrows Dataset V3.0

## Dataset Overview

Golden Arrows Dataset V3.0 is a simulation-generated multi-drone swarm transition dataset designed for research in swarm intelligence, autonomous multi-agent systems, swarm behavior, network-aware coordination, mission intelligence, machine learning, and reinforcement learning.

This dataset is simulation-generated. It is not real-world flight telemetry, it is not a real-world operational dataset, it has not established real-world flight validation, and it should not be interpreted as evidence of real-world operational effectiveness.

## Dataset Summary

| Item | Verified value |
| --- | --- |
| Dataset name | Golden Arrows Dataset V3.0 |
| Dataset type | Simulation-generated multi-drone swarm transition dataset |
| Missions | 100 |
| Mission distribution | 25 PATROL, 25 SURVEILLANCE, 25 SEARCH, 25 RECOVERY |
| Transitions | 11,570 |
| Drone-transition records | 347,100 |
| Drones per transition | 30 |
| Completed missions | 100/100 |
| Time step | 0.5 |
| Schema version | `golden_arrows_v3_rich_transition_1.0` |
| Policy representation | `SCRIPTED_MISSION_CONTROLLER+ADVANCED_SWARM_BEHAVIOR` |
| Behavior mode | `BOUNDED_CORRECTION_ON_MISSION_MOTION` |
| Advanced behavior | Enabled across all transitions |

The 347,100 drone-transition records are repeated observations from 30 drones across 11,570 transitions. They should not be treated as 347,100 independent samples.

## Dataset Motivation

V3.0 was created to provide a richer simulation dataset for studying mission transitions, drone-level state evolution, movement dynamics, network conditions, swarm behavior, coordination variables, and mission context. Conventional swarm datasets often focus on positions, states, or mission outcomes. This release preserves explicit behavior telemetry alongside mission transition information so that researchers can study how swarm-level behavior and environmental or network conditions relate to movement and decision processes.

V3.0 is intended to support research beyond simple position or state prediction by preserving behavior-aware information. It is not presented as the first, largest, or uniquely superior data resource unless such a claim is objectively supported by project evidence, which is not the case here.

## Data Generation

The dataset was generated in simulation using a multi-drone swarm setup with 30 simulated drones. The mission generation process uses four mission types and a scripted mission controller. Advanced Swarm Behavior is enabled across transitions and contributes behavior-aware telemetry to the logged event stream. Network simulation, mission context, and transition-level logging are all retained in the processed representation. The data are written as raw mission outputs and then transformed into processed JSON Lines (JSONL) transition records for analysis and ML preparation.

Verified configuration values:

- seed = 20260916
- dt = 0.5
- max_steps = 1000

This release does not claim additional hardware or software configuration details beyond what is verified in project metadata.

## Mission Types

The dataset contains four mission types. Each type contributes 25 missions to the 100-mission release.

### PATROL

PATROL missions are configured around patrol-like movement and formation-aware coordination. The simulated objective is mission-motion behavior within a coordinated swarm context, with transition data capturing decision, action, network state, and drone-level motion variables.

### SURVEILLANCE

SURVEILLANCE missions represent mission behavior focused on monitoring-oriented movement and coordination. The transition records preserve motion, assignment, network, and drone behavior information associated with surveillance objectives.

### SEARCH

SEARCH missions represent distributed search behavior in a multi-drone setting. The transition records capture task assignment, mission progression, network state, and swarm motion under search-oriented mission logic.

### RECOVERY

RECOVERY missions represent mission behavior oriented around recovery-related objectives and coordinated movement. The transition records include decision and action information, network conditions, and drone-level state and behavior variables relevant to recovery scenarios.

## Advanced Swarm Behavior

One of the central features of V3.0 is the explicit preservation of Advanced Swarm Behavior telemetry. The seven behavior components in the dataset are:

1. Cohesion
2. Alignment
3. Separation
4. Formation
5. Target Attraction
6. Network Preservation
7. Boundary Avoidance

These behaviors are conceptual coordination components used by the simulator rather than learned representations. They capture how drones maintain local coordination, preserve formation, manage spacing, preserve connectivity, avoid boundary conflicts, and respond to mission targets. The behavior system is part of the simulator's advanced behavior logic and is retained in the transition records.

Where verified in the schema, the dataset also includes associated telemetry such as:

- behavior vector
- vector x/y
- behavior weight
- behavior magnitude
- current position
- current velocity
- desired velocity
- movement vector
- speed scale
- neighbor count
- minimum neighbor distance
- formation error
- connectivity risk
- boundary risk

Preserving these variables is useful for behavior-aware ML and RL research because they explicitly encode behavior-level structure in addition to state and mission context, while still remaining grounded in simulation-generated data.

## Data Structure

The transition data follow the conceptual structure:

STATE → ACTION → RESULT → NEXT STATE

The processed records are JSON Lines (JSONL). One JSON object represents one transition. The verified top-level fields include:

- `schema_version`
- `mission`
- `transition`
- `decision`
- `action`
- `result`
- `network`
- `swarm`

The `swarm` object contains:

- `drone_count`
- `drones`

Each drone record includes state, movement, network, assignment or task information where available, and behavior telemetry. The complete schema is not reproduced here; the authoritative machine-readable definitions are provided in:

- `schema/transition_schema.json`
- `schema/behavior_schema.json`
- `schema/mission_schema.json`

## Data Representation

The dataset distinguishes between raw and processed representations.

### Raw Data

`data/raw/missions/` contains raw mission-level simulation outputs. These files preserve mission context and the original mission-level structure.

### Processed Data

`data/processed/transitions/` contains the processed transition JSONL representation. This is the primary machine-readable representation of the dataset and is the core resource for transition-level analysis and ML-oriented use. The raw files are not described as ground truth.

## ML-Ready Derivatives

The dataset includes derived ML-ready representations. These are not replacements for the authoritative transition JSONL dataset.

At minimum, the release includes:

- `ml_ready_state_only/`: a state-only representation without Advanced Swarm Behavior fields
- `ml_ready_behavior_aware/`: a behavior-aware representation retaining Advanced Swarm Behavior telemetry

The derivatives are created for preprocessing and experimentation, not as a new dataset version or a substitute for the original transition records. No new V3.x version number is introduced for these derived datasets.

## ML Splits

The verified mission-level split for the ML-ready derivatives is:

| Split | Missions | Rows |
| --- | ---: | ---: |
| Train | 68 | 234,600 |
| Validation | 16 | 58,860 |
| Test | 16 | 53,640 |

The split is performed at the mission level rather than independently at row level. This reduces direct mission leakage between training and evaluation. The verified split seed is `20260916`.

This does not imply complete independence between all observations, and mission-level effects remain relevant when evaluating generalization.

## Temporal and Causal Considerations

The transition data contain fields associated with different points in time. Behavior proposal information corresponds to the pre-action context, while several physical and network fields are stored under `state_after` and therefore represent the resulting state after action execution.

For ML or RL use, researchers must explicitly define:

- `S_t`
- `A_t`
- `R_t`
- `S_(t+1)`

It is not appropriate to assume that every flattened CSV feature is a strict pre-action observation. This distinction is particularly important for causal analysis, next-state prediction, policy learning, reinforcement learning, and action prediction. The timing audit identified this as a methodological consideration rather than a reason to reject the dataset.

## Data Quality and Validation

The project includes validation and quality-control checks that assess dataset structure and methodological integrity. Verified checks include:

- 100 mission files
- 11,570 transitions
- 347,100 drone-transition records
- 30 drones per transition
- 100/100 completed missions
- balanced mission distribution
- consistent schema version
- Advanced Swarm Behavior coverage
- numerical integrity
- ML split integrity
- mission leakage checks where applicable
- state/action/outcome analysis
- temporal/state timing audit

These checks are intended to verify structural and methodological integrity. They do not prove real-world validity and should not be interpreted as definitive proof of operational readiness beyond the simulated scope.

## Known Behavioral Limitations

Internal diagnostics identified observations at very small inter-drone distances, including collision-level proximity observations. In particular, the separation behavior vector was often oriented away from nearby drones, but the final movement did not consistently follow that direction because mission motion and behavior correction interact.

This should be interpreted as a simulation limitation and an area for further research without inferring operational safety conclusions.

## Statistical Interpretation

The 347,100 drone-transition records are repeated observations generated from 100 missions. They should not be treated as 347,100 independent experimental units. Temporal correlation, mission-level effects, and repeated measurements are present in the data and matter when estimating uncertainty, confidence intervals, statistical significance, training performance, and generalization.

## Intended Uses

The dataset is intended for:

- swarm behavior analysis
- multi-agent learning
- reinforcement learning
- behavior-aware machine learning
- next-state prediction
- mission transition modeling
- network-aware coordination research
- swarm coordination analysis
- representation comparison
- ablation studies
- reproducibility research

## Out-of-Scope Uses

V3.0 should not be used as:

- real-world flight telemetry
- safety certification evidence
- military operational evidence
- a production flight-control model
- a substitute for real-world testing
- evidence of real-world swarm effectiveness

## Responsible / Ethical Considerations

The dataset represents simulated behavior rather than real-world operational outcomes. Simulation assumptions may introduce bias, and learned models may inherit simulation-specific patterns. Real-world deployment requires independent validation, and users should not interpret simulation performance as proof of operational safety or effectiveness.

The scope of this dataset is research and analysis within simulation-generated multi-drone coordination, not broad operational or ethical claims beyond that documented scope.

## Bias and Representativeness

The dataset includes only four mission types and 100 missions, and the distribution is determined by the mission generation and behavior rules used in simulation. The environment and network model are simulated, and behavior distributions may differ from real-world systems. The dataset therefore represents a specific simulation setting rather than all possible swarm environments. Generalization beyond the simulation should be tested empirically.

## Dataset Version

Golden Arrows Dataset V3.0

V3.0 is the 100-mission behavior-aware release and remains distinct from earlier baselines. If Dataset V2.2 is mentioned, it should be described only as a previous baseline or reference dataset and kept separate from V3.0.

## Reproducibility

Only reproducibility information that is verified from project files is included here. The known verified configuration values are:

- `seed = 20260916`
- `dt = 0.5`
- `max_steps = 1000`

No unsupported hardware, OS, Python, package, or GPU claims are included unless explicitly verified in project files.

## Data Access

The expected final public package contains the following directories and resources:

- `data/raw/missions/`
- `data/processed/transitions/`
- `schema/`
- `validation/`
- `examples/preprocessing/`

These paths correspond to the final public package layout and do not expose the temporary internal directory used during dataset preparation.

## Documentation Relationship

The dataset package is documented with multiple complementary materials:

- `README.md` provides the concise public landing page.
- `dataset_card.md` provides the structured technical description.
- `dataset_description.pdf` provides the formal publication-oriented description.
- `schema/` contains machine-readable schema definitions.
- `validation/` contains validation and quality-control materials.
- `examples/preprocessing/` provides example preprocessing workflows.

The dataset card complements the README rather than duplicating it.

## Citation

Users should cite the dataset via `CITATION.cff` once it is finalized. No fabricated authors, DOI, journal, conference, URL, year, or ORCID information is included here.

## License

The licensing terms are defined in `LICENSE`. No license is selected or inferred here beyond the actual project terms.

## Final Dataset Card Quality Requirements

The dataset card is written to be professional, research-oriented, structured, technically precise, transparent about limitations, reproducibility-oriented, suitable for a public research dataset, and free of marketing language, exaggerated claims, and unsupported claims.
