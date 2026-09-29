# Optional Preprocessing Examples

## 1. Overview

This directory contains optional examples for transforming the published
Golden Arrows Dataset V3.1 rich transition records into tabular
machine-learning-oriented representations. The published transition data
remain the source of truth. The scripts read source data without modifying
it; any files they generate are local derivatives and are not part of this
publication package.

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

## 3. Source Data

The scripts read processed JSONL files from:

```text
../../data/processed/transitions/*.jsonl
```

V3.1 contains 1,000 missions: 250 each of PATROL, SURVEILLANCE, SEARCH, and
RECOVERY. It contains 113,954 transitions, each with 30 drones, for
3,418,620 derived drone-transition records. That derived record count is not
a count of independent samples.

The scripts validate V3.1's 1,000 source files, mission and transition
structure, 30-drone cardinality, uniqueness, finite numeric inputs, and
behavior-field coverage where applicable. The retained schema version is
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
```

To run either example, specify a local output directory outside the
publication package. For example:

```powershell
python .\prepare_state_only.py --output-root "$env:TEMP\golden_arrows_v3_1_state_only"
python .\prepare_behavior_aware.py --output-root "$env:TEMP\golden_arrows_v3_1_behavior_aware"
```

Both scripts accept `--source-root`, `--output-root`, and `--split-seed`.
The default source root is the package's `data` directory. By default,
generated outputs are written under the system temporary directory, not into
the publication package. Do not copy generated ML outputs into this release.

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
