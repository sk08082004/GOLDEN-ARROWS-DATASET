# Golden Arrows Dataset V3.1

Golden Arrows Dataset V3.1 is a simulation-generated, transition-level
multi-drone swarm dataset for research in swarm intelligence, autonomous
multi-agent systems, swarm behavior, network-aware coordination, mission
intelligence, and machine learning. It contains simulated data, not real-world
flight data, and does not establish real-world flight performance.

## Dataset summary

| Item | V3.1 value |
| --- | --- |
| Missions | 1,000 |
| Mission distribution | 250 each: PATROL, SURVEILLANCE, SEARCH, RECOVERY |
| Transitions | 113,954 |
| Drone-transition records | 3,418,620 (= 113,954 transitions × 30 drones) |
| Drones per transition | 30 |
| Completed missions | 1,000/1,000 |
| Simulation time step | `dt = 0.5` |
| Maximum steps | 1,000 |
| Schema version | `golden_arrows_v3_rich_transition_1.0` |
| Policy representation | `SCRIPTED_MISSION_CONTROLLER+ADVANCED_SWARM_BEHAVIOR` |
| Behavior mode | `BOUNDED_CORRECTION_ON_MISSION_MOTION` |
| Collection seed | `20260916` |
| Mission seed range | `20260917`–`20261916` |

The drone-transition record count is a derived count: each transition contains
30 drone records. These records are repeated measurements nested within
transitions and missions; they must not be treated as 3,418,620 independent
samples.

## Dataset scope and behavior

The dataset covers four mission types: PATROL, SURVEILLANCE, SEARCH, and
RECOVERY. Their transition totals are:

| Mission type | Missions | Transitions |
| --- | ---: | ---: |
| PATROL | 250 | 63,694 |
| SURVEILLANCE | 250 | 22,036 |
| SEARCH | 250 | 11,856 |
| RECOVERY | 250 | 16,368 |
| **Total** | **1,000** | **113,954** |

Advanced Swarm Behavior is enabled throughout the dataset. Its documented
components are cohesion, alignment, separation, formation, target attraction,
network preservation, and boundary avoidance. The architecture terminology
retained for this dataset is:

```text
swarm_manager.py
  → advanced_swarm_controller.py
    → swarm_behavior.py
      → 30 drones
```

The policy representation and behavior mode above describe the logged
simulation configuration; they do not indicate that a learned policy was
used.

## Data organization

```text
Golden_Arrows_Dataset_V3.1/
├── data/
│   ├── metadata.csv
│   ├── raw/
│   │   └── missions/            # 1,000 raw mission JSON files
│   └── processed/
│       └── transitions/         # 1,000 processed transition JSONL files
├── examples/
├── schema/
├── validation/
├── CITATION.cff
├── CHANGELOG.md
├── dataset_card.md
├── dataset_description.pdf
├── LICENSE
└── README.md
```

Each raw mission JSON contains collection and mission information and its
transitions. Processed JSONL records use the schema version
`golden_arrows_v3_rich_transition_1.0`. Raw and processed filenames correspond
one-to-one. The accompanying `data/metadata.csv` has one row per mission and
records mission ID, type, seed, status, transition count, drone count, time
step, maximum steps, advanced-behavior status, and policy type.

The transition data includes mission- and swarm-level information as well as
per-drone records. Consult the schema files for the precise field definitions;
the examples illustrate reading or preparing the published data and do not
represent additional generated training datasets.

## Validation

The V3.1 validation results report 1,000 raw mission files and 1,000 processed
transition files with exact filename correspondence; 250 missions per type;
113,954 transitions and 30 drones per transition; schema consistency; and
`advanced_behavior_applied = true` throughout. Mission-level structural
integrity passed, with zero duplicate-tick missions, malformed/structural
errors, NaN values, or Inf values. Mission transition counts range from 9 to
373, with a reported average of 113.95.

## Use and limitations

The data can support descriptive studies and research on simulated swarm
coordination, mission behavior, transition modeling, and preprocessing
methods. Any train/validation/test evaluation should split at the mission
level to reduce leakage between transitions from the same mission. For
example, a stratified 68%/16%/16% mission split corresponds to 680/160/160
missions overall (170/40/40 per mission type). This is a split methodology,
not a set of included split files or a claim about generated CSV row counts.

This is simulation-generated data from a scripted mission controller with
advanced swarm behavior. It is not real-world flight data, does not validate
real-world safety or performance, and does not by itself support causal
conclusions or claims of learned-policy performance. Repeated drone records
within a transition and transitions within a mission are not independent
samples. Account for this hierarchy and inspect feature timing before using
the data for causal or predictive modeling.

No generated ML-ready datasets or train/validation/test CSV files are part of
this publication package.

## Citation, version, and license

Please cite **Golden Arrows Dataset V3.1** and use the author and version
information in [CITATION.cff](CITATION.cff). A DOI for V3.1 has not been
assigned in this package; the V3.0 DOI identifies a different release and
must not be used for V3.1.

Version 3.1 expands the V3.0 release from 100 to 1,000 missions and is a
separate dataset release, not a renaming of V3.0. The dataset is provided
under the [CC BY 4.0 license](LICENSE).
