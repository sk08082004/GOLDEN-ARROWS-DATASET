"""Prepare the verified V3.0 behavior-aware tabular representation."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

BASE = ["active_links", "connected_drones", "progress_before", "position_x", "position_y", "altitude", "speed", "direction_x", "direction_y", "battery", "signal_strength", "latency", "packet_loss"]
LEVEL = ["speed_scale", "neighbor_count", "minimum_neighbor_distance", "formation_error", "connectivity_risk", "boundary_risk"]
VECTORS = ["behavior_current_position", "behavior_current_velocity", "behavior_desired_velocity", "behavior_movement_vector"]
COMPONENTS = ["cohesion", "alignment", "separation", "formation", "target_attraction", "network_preservation", "boundary_avoidance"]
METADATA = ["mission_id", "mission_type", "drone_id", "tick"]
TARGETS = ["next_position_x", "next_position_y"]
EXCLUDED = ["actual_movement", "action", "decision", "progress_after", "state_after"]
MISSION_TYPES = ["PATROL", "SURVEILLANCE", "SEARCH", "RECOVERY"]
SEED = 20260916
FEATURES = BASE + LEVEL + [f"{v}_{axis}" for v in VECTORS for axis in ("x", "y")] + [f"{c}_{x}" for c in COMPONENTS for x in ("x", "y", "weight", "magnitude")]


def num(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{label} must be finite numeric")
    return float(value)


def vec(value, label):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must be a two-dimensional list")
    return [num(value[0], f"{label}[0]"), num(value[1], f"{label}[1]")]


def partitions(missions, seed):
    result = {}
    rng = random.Random(seed)
    for mission_type in MISSION_TYPES:
        ids = sorted(missions[mission_type])
        if len(ids) != 25:
            raise ValueError(f"{mission_type} must contain 25 missions")
        shuffled = ids[:]
        rng.shuffle(shuffled)
        result.update({x: "train" for x in shuffled[:17]})
        result.update({x: "validation" for x in shuffled[17:21]})
        result.update({x: "test" for x in shuffled[21:]})
    return result


def read(source_root):
    files = sorted((source_root / "processed" / "transitions").glob("*.jsonl"))
    if len(files) != 100:
        raise ValueError(f"Expected exactly 100 JSONL files, found {len(files)}")
    rows, missions = [], defaultdict(set)
    mission_drone_ids = {}
    seen_rows = set()
    seen_transitions = set()
    transitions = 0
    behavior_records = 0
    complete_components = 0
    for path in files:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                try:
                    r = json.loads(line)
                    m, swarm, transition, result = r["mission"], r["swarm"], r["transition"], r["result"]
                    mission_id, mission_type = m["mission_id"], m["mission_type"]
                    drones = swarm["drones"]
                except (json.JSONDecodeError, KeyError, TypeError) as exc:
                    raise ValueError(f"Malformed required record at {path}:{line_number}") from exc
                if (
                    not isinstance(mission_id, str)
                    or mission_type not in MISSION_TYPES
                    or not isinstance(drones, list)
                    or len(drones) != 30
                ):
                    raise ValueError(f"Invalid mission type or drone cardinality at {path}:{line_number}")
                if not isinstance(transition["tick"], int) or isinstance(transition["tick"], bool):
                    raise ValueError(f"tick must be an integer at {path}:{line_number}")
                transition_key = (mission_id, transition["tick"])
                if transition_key in seen_transitions:
                    raise ValueError(
                        f"Duplicate (mission_id, tick) transition: {transition_key}"
                    )
                seen_transitions.add(transition_key)
                missions[mission_type].add(mission_id)
                transitions += 1
                transition_drone_ids = set()
                for drone in drones:
                    try:
                        before, after, b = drone["state_before"], drone["state_after"], drone["behavior"]
                    except KeyError as exc:
                        raise ValueError(f"Missing drone field {exc} at {path}:{line_number}") from exc
                    drone_id = drone.get("drone_id")
                    if not isinstance(drone_id, str):
                        raise ValueError(f"drone_id must be a string at {path}:{line_number}")
                    if drone_id in transition_drone_ids:
                        raise ValueError(f"Duplicate drone_id in transition at {path}:{line_number}")
                    transition_drone_ids.add(drone_id)
                    if not isinstance(before, dict) or not isinstance(after, dict) or not isinstance(b, dict):
                        raise ValueError(f"Invalid state or behavior object at {path}:{line_number}")
                    if not {"position"}.issubset(before) or not {
                        "position", "altitude", "speed", "direction", "battery",
                        "signal_strength", "latency", "packet_loss",
                    }.issubset(after):
                        raise ValueError(f"Missing required state fields at {path}:{line_number}")
                    required_behavior = set(LEVEL) | {
                        "current_position", "current_velocity", "desired_velocity",
                        "movement_vector", "behaviors",
                    }
                    if not required_behavior.issubset(b):
                        raise ValueError(f"Missing required behavior fields at {path}:{line_number}")
                    if not isinstance(b["behaviors"], dict) or any(
                        component not in b["behaviors"] for component in COMPONENTS
                    ):
                        raise ValueError(f"Missing behavior component at {path}:{line_number}")
                    behavior_records += 1
                    pos, next_pos, direction = vec(before["position"], "state_before.position"), vec(after["position"], "state_after.position"), vec(after["direction"], "state_after.direction")
                    row = {"mission_id": mission_id, "mission_type": mission_type, "drone_id": drone_id, "tick": transition["tick"],
                           "active_links": result["active_links"], "connected_drones": result["connected_drones"], "progress_before": result["progress_before"],
                           "position_x": pos[0], "position_y": pos[1], "altitude": after["altitude"], "speed": after["speed"],
                           "direction_x": direction[0], "direction_y": direction[1], "battery": after["battery"], "signal_strength": after["signal_strength"],
                           "latency": after["latency"], "packet_loss": after["packet_loss"], "next_position_x": next_pos[0], "next_position_y": next_pos[1]}
                    for key in LEVEL:
                        row[key] = b[key]
                    for name in VECTORS:
                        value = vec(b[name.removeprefix("behavior_")], f"behavior.{name}")
                        row[f"{name}_x"], row[f"{name}_y"] = value
                    behaviors = b["behaviors"]
                    for component in COMPONENTS:
                        if not isinstance(behaviors[component], dict) or not {
                            "x", "y", "weight", "magnitude"
                        }.issubset(behaviors[component]):
                            raise ValueError(f"Missing fields for behavior component {component} at {path}:{line_number}")
                        for key in ("x", "y", "weight", "magnitude"):
                            row[f"{component}_{key}"] = behaviors[component][key]
                    complete_components += 1
                    for key in FEATURES + TARGETS:
                        row[key] = num(row[key], key)
                    row_key = (mission_id, row["tick"], drone_id)
                    if row_key in seen_rows:
                        raise ValueError(f"Duplicate (mission_id, tick, drone_id) row: {row_key}")
                    seen_rows.add(row_key)
                    rows.append(row)
                if mission_id in mission_drone_ids and mission_drone_ids[mission_id] != transition_drone_ids:
                    raise ValueError(f"Inconsistent drone identity set for mission {mission_id}")
                mission_drone_ids.setdefault(mission_id, transition_drone_ids)
    if transitions != 11570 or len(rows) != 347100:
        raise ValueError(f"Source validation failed: {transitions} transitions and {len(rows)} drone records")
    if len(mission_drone_ids) != 100 or any(len(missions[t]) != 25 for t in MISSION_TYPES):
        raise ValueError("Source validation failed: expected 100 missions and 25 missions per type")
    if behavior_records != 347100 or complete_components != 347100:
        raise ValueError("Source validation failed: incomplete behavior telemetry coverage")
    unique_mission_tick_transitions = len(seen_transitions)
    if unique_mission_tick_transitions != transitions:
        raise ValueError(
            "Unique mission/tick transition count does not match transition count"
        )
    return (
        files,
        rows,
        missions,
        mission_drone_ids,
        transitions,
        behavior_records,
        complete_components,
        unique_mission_tick_transitions,
    )


def run(source_root, output_root, seed):
    (
        files,
        rows,
        missions,
        mission_drone_ids,
        transitions,
        behavior_records,
        complete_components,
        unique_mission_tick_transitions,
    ) = read(source_root)
    assignment = partitions(missions, seed)
    split_missions = defaultdict(set)
    for mission_id, split in assignment.items():
        split_missions[split].add(mission_id)
    if set().union(*split_missions.values()) != set(mission_drone_ids):
        raise ValueError("Every source mission must appear in a split")
    if sum(len(value) for value in split_missions.values()) != len(mission_drone_ids):
        raise ValueError("Mission-level splits overlap")
    split_counts_by_type = {
        split: {
            mission_type: len(split_missions[split] & missions[mission_type])
            for mission_type in MISSION_TYPES
        }
        for split in ("train", "validation", "test")
    }
    per_type_split_valid = all(
        split_counts_by_type[split][mission_type] == expected
        for split, expected in (("train", 17), ("validation", 4), ("test", 4))
        for mission_type in MISSION_TYPES
    )
    if not per_type_split_valid:
        raise ValueError(f"Invalid per-type mission split counts: {split_counts_by_type}")
    rows.sort(key=lambda r: (assignment[r["mission_id"]], r["mission_id"], r["tick"], r["drone_id"]))
    groups = {x: [] for x in ("train", "validation", "test")}
    for row in rows:
        groups[assignment[row["mission_id"]]].append(row)
    output_root.mkdir(parents=True, exist_ok=True)
    columns = METADATA + FEATURES + TARGETS
    for name, group in groups.items():
        with (output_root / f"{name}.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader(); writer.writerows(group)
    mission_counts = {k: len(split_missions[k]) for k in groups}
    missing_values = sum(1 for row in rows for key in FEATURES + TARGETS if row[key] is None)
    nonfinite_values = sum(
        1 for row in rows for key in FEATURES + TARGETS
        if isinstance(row[key], float) and not math.isfinite(row[key])
    )
    duplicate_rows = len(rows) - len({(r["mission_id"], r["tick"], r["drone_id"]) for r in rows})
    duplicate_rows_valid = duplicate_rows == 0
    behavior_coverage_valid = behavior_records == len(rows)
    component_coverage_valid = complete_components == len(rows)
    transition_tick_integrity_valid = (
        unique_mission_tick_transitions == transitions
    )
    drone_identity_consistency = (
        len(mission_drone_ids) == 100
        and all(len(ids) == 30 for ids in mission_drone_ids.values())
    )
    all_missions_assigned_once = (
        set().union(*split_missions.values()) == set(mission_drone_ids)
        and len(assignment) == len(mission_drone_ids)
    )
    mission_overlap_count = sum(
        len(left & right)
        for index, left in enumerate(split_missions.values())
        for right in list(split_missions.values())[index + 1:]
    )
    mission_overlap_valid = mission_overlap_count == 0
    missing_values_valid = missing_values == 0
    nonfinite_values_valid = nonfinite_values == 0
    final_validation = all((
        duplicate_rows_valid,
        behavior_coverage_valid,
        component_coverage_valid,
        transition_tick_integrity_valid,
        drone_identity_consistency,
        all_missions_assigned_once,
        mission_overlap_valid,
        per_type_split_valid,
        missing_values_valid,
        nonfinite_values_valid,
    ))
    if not final_validation:
        raise ValueError("Final behavior-aware validation failed")
    schema = {"dataset_name": "Golden Arrows Dataset V3.0", "representation_name": "behavior_aware",
              "input_features": FEATURES, "metadata_features": METADATA, "targets": TARGETS, "excluded_fields": EXCLUDED,
              "behavior_components": COMPONENTS, "split_methodology": "Mission-level split: 17 train / 4 validation / 4 test per mission type",
              "split_seed": seed, "source_location": "datasetv3_final/processed/transitions/*.jsonl",
              "row_counts": {k: len(v) for k, v in groups.items()}, "mission_counts": mission_counts,
              "model_feature_count": len(FEATURES), "advanced_swarm_behavior": True, "causal_claim": False,
              "temporal_semantics": "state_before.position is used for current position; several physical/network values are logged under state_after; behavior telemetry is separate from actual_movement; next-position fields are resulting targets"}
    (output_root / "feature_schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    report = ["GOLDEN ARROWS DATASET V3.0 — BEHAVIOR-AWARE PREPARATION", "",
              f"Source path: {source_root / 'processed' / 'transitions'}", f"Source files: {len(files)}",
              f"Source missions: {len(mission_drone_ids)}", f"Source transitions: {transitions}",
              f"Source drone-transition records: {len(rows)}", "", f"Output rows: {len(rows)}",
              f"Model feature count: {len(FEATURES)}", f"Base features: {len(BASE)}",
              f"Behavior-level features: {len(LEVEL)}", f"Behavior vector features: {len(VECTORS) * 2}",
              f"Behavior component features: {len(COMPONENTS) * 4}", f"Total behavior components: {len(COMPONENTS)}",
              f"Metadata fields: {', '.join(METADATA)}", f"Targets: {', '.join(TARGETS)}",
              f"Excluded fields: {', '.join(EXCLUDED)}", "", f"Train missions: {mission_counts['train']}",
              f"Validation missions: {mission_counts['validation']}", f"Test missions: {mission_counts['test']}",
              f"Train rows: {len(groups['train'])}", f"Validation rows: {len(groups['validation'])}",
              f"Test rows: {len(groups['test'])}", f"Split seed: {seed}", "",
              "30 drones/transition: PASS", f"Behavior coverage: {behavior_records}/{len(rows)}",
              f"Seven behavior components: {complete_components}/{len(rows)}",
              f"Transition tick integrity: "
              f"{'PASS' if transition_tick_integrity_valid else 'FAIL'} "
              f"({unique_mission_tick_transitions} unique mission/tick transitions)",
              f"Duplicate row check: {'PASS' if duplicate_rows_valid else 'FAIL'} ({duplicate_rows})",
              f"Drone identity consistency: {'PASS' if drone_identity_consistency else 'FAIL'}",
              f"Missing-value check: {'PASS' if missing_values_valid else 'FAIL'} ({missing_values})",
              f"Non-finite-value check: {'PASS' if nonfinite_values_valid else 'FAIL'} ({nonfinite_values})",
              f"Mission-level split: {'PASS' if all_missions_assigned_once and per_type_split_valid else 'FAIL'}",
              f"Mission overlap check: {'PASS' if mission_overlap_valid else 'FAIL'} ({mission_overlap_count} overlapping missions)",
              f"Per-type split check: {'PASS' if per_type_split_valid else 'FAIL'} (17/4/4 for every mission type)",
              "Temporal semantics warning: behavior telemetry is recorded separately from actual_movement; state_after contains post-step physical/network values and is not automatically pre-action.",
              "Source dataset modified: NO", "", "RESULT: PASS"]
    (output_root / "preparation_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Source missions: {len(mission_drone_ids)}\nSource transitions: {transitions}\nSource drone records: {len(rows)}\nOutput rows: {len(rows)}")
    print(f"Model feature count: {len(FEATURES)}\nTarget count: {len(TARGETS)}\nTrain missions: {mission_counts['train']}\nValidation missions: {mission_counts['validation']}\nTest missions: {mission_counts['test']}")
    print(f"Behavior coverage: {behavior_records}/{len(rows)}\nBehavior components: {complete_components}/{len(rows)}\nDuplicate rows: {duplicate_rows}\nTransition tick integrity: {'PASS' if transition_tick_integrity_valid else 'FAIL'} ({unique_mission_tick_transitions} unique mission/tick transitions)\nDrone identity consistency: {'PASS' if drone_identity_consistency else 'FAIL'}\nMission-level split: {'PASS' if all_missions_assigned_once and per_type_split_valid else 'FAIL'}\nMission overlap: {mission_overlap_count}\nMissing values: {missing_values}\nNon-finite values: {nonfinite_values}\nSource modified: NO\nRESULT: PASS")


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=root / "datasetv3_final")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--split-seed", type=int, default=SEED)
    args = parser.parse_args()
    try:
        run(args.source_root.resolve(), (args.output_root or (args.source_root / "ml_ready_behavior_aware")).resolve(), args.split_seed)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"RESULT: FAIL\n{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
