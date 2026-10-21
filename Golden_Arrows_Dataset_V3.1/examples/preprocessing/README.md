# Optional Preprocessing Examples

## 1. Overview

This directory contains optional examples for transforming the published
Golden Arrows Dataset V3.1 rich transition records into tabular
machine-learning-oriented representations. The published transition data
remain the source of truth. The scripts read source data without modifying
it; any files they generate are local derivatives and are not part of this
publication package.

The examples require Python 3.9 or newer and use only the Python standard
library; no third-party packages are required.

The examples demonstrate specific feature choices, not mandatory
preprocessing, causal validity, or model performance. Researchers should
review temporal semantics and adapt feature definitions to their research
question.

## 2. Available Examples

### `prepare_state_only.py`

This script constructs 13 model input features:

```text
active_links
connected_drones
progress_before
position_x
position_y
altitude
speed
direction_x
direction_y
battery
signal_strength
latency
packet_loss
```

The targets are `next_position_x` and `next_position_y`. Metadata retained
separately are `mission_id`, `mission_type`, `drone_id`, and `tick`.
`progress_after`, `actual_movement`, `behavior`, `action`, and `decision` are
excluded from model inputs.

### `prepare_behavior_aware.py`

This script uses 55 model input features: 13 base features, 6 behavior-level
features, 8 behavior-vector features, and 28 behavior-component features.

The behavior-level features are `speed_scale`, `neighbor_count`,
`minimum_neighbor_distance`, `formation_error`, `connectivity_risk`, and
`boundary_risk`. The vector fields provide x/y values for behavior current
position, current velocity, desired velocity, and movement vector. The
seven components are cohesion, alignment, separation, formation,
target_attraction, network_preservation, and boundary_avoidance; each has
x, y, weight, and magnitude values.

The targets are `next_position_x` and `next_position_y`. Metadata is retained
separately. The script excludes `actual_movement`, `action`, `decision`,
`progress_after`, and `state_after` from model inputs. Recorded behavior
telemetry is distinct from actual movement; it is not an RL action or an
output from a trained model.

### `prepare_behavior_aware_streaming.py`

This is an optional, memory-efficient alternative to
`prepare_behavior_aware.py`; it preserves the same 55 model input features,
two targets (`next_position_x` and `next_position_y`), metadata, excluded
fields, split seed, mission-level split, and output filenames. It does not
replace the original behavior-aware script.

The streaming implementation stages records in a temporary, disk-backed
SQLite database and writes results to temporary output staging before
publishing them. It therefore uses temporary disk space; ensure sufficient
space is available. The requested output directory must not already exist.
Choose a fresh output path for each run.

Ticks must be integers within the signed 64-bit range, inclusive:
`-9223372036854775808` through `9223372036854775807`. Numeric feature and
target values are validated during ingestion; this script does not perform a
separate scan of the generated CSV files.

## 3. Source Data and Extraction

The Zenodo distribution supplies the dataset in eight independent archives:
`data_metadata.zip`, `data_raw_missions_001.zip`,
`data_raw_missions_002.zip`, `data_raw_missions_003.zip`,
`data_raw_missions_004.zip`, `data_processed_transitions_001.zip`,
`data_processed_transitions_002.zip`, and
`data_processed_transitions_003.zip`. Download all eight and extract each
into the same new, empty destination directory before running either example.
The archives preserve the `data/` prefix; extracting them together creates
the source tree below. No `.z01` or `.z02` companion files are needed.

```text
<extraction-directory>/data/
├── metadata.csv
├── raw/missions/                 # 1,000 raw mission JSON files
└── processed/transitions/        # 1,000 processed transition JSONL files
```

The temporary failed-upload artifact `data/processed/transitions.zip` is
excluded from the release. Do not use it as source data.

All preprocessing scripts read processed JSONL files from the extracted tree:

```text
../../data/processed/transitions/*.jsonl
```

V3.1 contains 1,000 missions: 250 each of PATROL, SURVEILLANCE, SEARCH, and
RECOVERY. It contains 113,954 transitions, each with 30 drones, for
3,418,620 derived drone-transition records. That derived record count is not
a count of independent samples.

The scripts require exactly 1,000 processed JSONL mission files and validate
mission and transition structure, the expected mission distribution and
transition counts, 30-drone cardinality, uniqueness, and finite required
numeric inputs. The behavior-aware examples also check complete behavior
telemetry and all seven behavior components. The streaming implementation
validates numeric feature and target values during ingestion and does not run
a separate output-CSV scan. The retained schema version is
`golden_arrows_v3_rich_transition_1.0`.

## 4. Temporal Semantics

The examples use `state_before.position` for the current x/y coordinates.
Several physical and network fields, including altitude, speed, direction,
battery, signal strength, latency, and packet loss, are read from
`state_after`. The next-position targets also come from
`state_after.position`.

Fields under `state_after` are not automatically valid pre-action
observations. Inspect field timing before using these representations for
prediction, causal analysis, reinforcement learning, or multi-agent
reinforcement learning. Feature exclusion does not guarantee that all
possible leakage has been eliminated.

## 5. Mission-Level Split

The scripts use a deterministic, stratified mission-level split with seed
`20260916`:

| Split | Missions overall | Missions per type |
| --- | ---: | ---: |
| Train (68%) | 680 | 170 |
| Validation (16%) | 160 | 40 |
| Test (16%) | 160 | 40 |
| **Total** | **1,000** | **250** |

Rows from each mission are assigned together to one split. This avoids
placing transitions from the same mission in multiple splits. The examples
do not assert exact CSV row counts; mission transition lengths vary.

## 6. Running the Examples

From `examples/preprocessing/`, inspect supported options with:

```powershell
python .\prepare_state_only.py --help
python .\prepare_behavior_aware.py --help
python .\prepare_behavior_aware_streaming.py --help
```

After extracting all eight archives, set `--source-root` to the extracted
`data` directory (the directory containing `raw/`, `processed/`, and
`metadata.csv`). Specify an output directory outside the publication package.
For example, replace the placeholder with the path you used for extraction:

```powershell
$source = "C:\path\to\extracted\dataset\data"
python .\prepare_state_only.py --source-root $source --output-root "$env:TEMP\golden_arrows_v3_1_state_only"
python .\prepare_behavior_aware.py --source-root $source --output-root "$env:TEMP\golden_arrows_v3_1_behavior_aware"
python .\prepare_behavior_aware_streaming.py --source-root $source --output-root "$env:TEMP\golden_arrows_v3_1_behavior_aware_streaming"
```

All three scripts accept `--source-root`, `--output-root`, and `--split-seed`.
Their default source root is the package's `data` directory. If, as
recommended, you extracted the archives into a separate new empty directory,
pass that extraction's `data` directory explicitly as shown. By default,
generated outputs are written under the system temporary directory, not into
the publication package. All examples reject output directories inside the
package. In addition, the streaming script refuses an output directory that
already exists. Its SQLite database is staged separately in a temporary
directory, and its output staging also requires temporary disk space. Do not
copy generated ML outputs into this release.

## 7. Outputs

When run locally, each script creates `train.csv`, `validation.csv`,
`test.csv`, `feature_schema.json`, and `preparation_report.txt` in its output
directory. These are generated derivatives, not contents of this
publication package. The package does not include ML-ready directories or
generated train/validation/test CSV files.

## 8. Reproducibility and Validation

The examples use deterministic input-file ordering, sorted mission IDs,
mission-level splitting, deterministic row ordering, and split seed
`20260916`. They check the V3.1 source structure and relevant feature
requirements before writing outputs. They do not normalize, standardize,
clip, smooth, or impute values; researchers should document any additional
transformations.

## 9. Research Use and Limitations

The examples may support supervised-learning experiments, behavior analysis,
feature engineering, baseline comparisons, and custom reinforcement-learning
preprocessing. These are possible research uses, not demonstrated
performance claims.

- The source data are simulation-generated, not real-world flight telemetry.
- The mission controller is scripted; behavior telemetry is not learned.
- Mission transitions and drone records are dependent observations.
- Temporal semantics require task-specific review.
- The examples make no model-performance, causal-validity, or deployment-
  readiness claim.

## 10. Related Documentation

- [Package README](../../README.md)
- [Dataset card](../../dataset_card.md)
- [Schema directory](../../schema/)
- [Validation directory](../../validation/)

## 11. Publication Scope

The publication contains the authoritative data and these optional
preprocessing examples. It does not contain generated ML datasets,
`train.csv`, `validation.csv`, `test.csv`, ML-ready directories, analysis
directories, or development/staging artifacts. Locally generated outputs
must remain outside the publication package.
