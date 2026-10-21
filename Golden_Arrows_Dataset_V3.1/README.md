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

## Download and extract the data

The Zenodo upload provides the dataset payload as eight independent ZIP
archives at the release root:

- `data_metadata.zip`
- `data_raw_missions_001.zip`
- `data_raw_missions_002.zip`
- `data_raw_missions_003.zip`
- `data_raw_missions_004.zip`
- `data_processed_transitions_001.zip`
- `data_processed_transitions_002.zip`
- `data_processed_transitions_003.zip`

The metadata CSV is in its own archive, the raw mission JSON files are split
across four archives, and the processed transition JSONL files are split
across three. These are independent ZIP files, not multivolume segments; no
`.z01` or `.z02` companion files are required. Download all eight archives
and extract each into the same new, empty destination directory. Each archive
preserves the `data/` prefix, so the resulting layout is:

```text
<extraction-directory>/
└── data/
    ├── metadata.csv
    ├── raw/
    │   └── missions/            # 1,000 raw mission JSON files
    └── processed/
        └── transitions/         # 1,000 processed transition JSONL files
```

Extracting fewer than all eight archives yields an incomplete dataset. The
temporary failed-upload artifact `data/processed/transitions.zip` is excluded
from the release and is not one of the published archives. The upload also
includes this README, the dataset card and description, changelog, citation
metadata, license, examples, schemas, and validation materials as separate
files.

## Run the optional preprocessing examples

The examples require Python 3.9 or newer and use only the Python standard
library; no third-party packages are required. Download all eight archives
and extract them as described above before running an example. From the
release package root, set `--source-root` to the `data` directory created by
extraction:

```powershell
$source = "C:\path\to\extracted\dataset\data"
python .\examples\preprocessing\prepare_state_only.py --source-root $source --output-root "$env:TEMP\golden_arrows_v3_1_state_only"
python .\examples\preprocessing\prepare_behavior_aware.py --source-root $source --output-root "$env:TEMP\golden_arrows_v3_1_behavior_aware"
python .\examples\preprocessing\prepare_behavior_aware_streaming.py --source-root $source --output-root "$env:TEMP\golden_arrows_v3_1_behavior_aware_streaming"
```

The behavior-aware streaming command is an optional, memory-efficient
alternative to `prepare_behavior_aware.py`; it does not replace the original.
To inspect its options, run:

```powershell
python .\examples\preprocessing\prepare_behavior_aware_streaming.py --help
```

All three examples require exactly 1,000 processed JSONL mission files and
check the documented mission distribution, transition counts, 30-drone
cardinality, uniqueness, and finite required values. The behavior-aware
examples also check behavior telemetry and component coverage. Both
behavior-aware implementations retain the same 55 model features and two
next-position targets.

The streaming implementation stages records in a temporary, disk-backed
SQLite database and uses temporary output staging before publishing results.
It requires sufficient temporary disk space and refuses to run if the
requested output directory already exists; choose a fresh destination for
each run. Its input ticks must be integers within the signed 64-bit range
(-9223372036854775808 through 9223372036854775807). Numeric feature and
target values are validated during ingestion; the streaming script does not
perform a separate output-CSV scan.

Each run creates `train.csv`, `validation.csv`, `test.csv`,
`feature_schema.json`, and `preparation_report.txt` in its output directory.
Outputs default to a system temporary directory and are not written into the
release package; the examples also reject output paths inside that package.

The examples use a stratified 68%/16%/16% mission-level split (680/160/160
missions overall, 170/40/40 per mission type); they do not provide generated
split files in this release. Drone-transition records are nested within
transitions and missions, not independent samples. Review the timing of
`state_after` fields before using features for prediction or causal analysis;
the examples do not establish causal validity, learned-policy performance,
or real-world flight performance. See
[the preprocessing guide](examples/preprocessing/README.md) for feature
details and further limitations.

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

Please cite **Golden Arrows Dataset V3.1** using the author and version
information in [CITATION.cff](CITATION.cff). The citation file and dataset
description list DOI `10.5281/zenodo.23030808`; however, the DOI resolver
returned HTTP 404 when checked on 2026-10-20, so its active publication status
is unconfirmed. Confirm the record with the maintainer before treating the
DOI as a live publication link. The V3.0 DOI identifies a different release
and must not be used for V3.1.

The CFF lists `date-released: 2026-10-02`, while the changelog says the V3.1
release date is to be assigned at publication. This conflict is unresolved;
confirm the authoritative release date with the maintainer. Neither value
has been changed here.

Version 3.1 expands the V3.0 release from 100 to 1,000 missions and is a
separate dataset release, not a renaming of V3.0. The dataset is provided
under the [CC BY 4.0 license](LICENSE).
