"""Prepare the verified V3.0 state-only tabular representation."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

FEATURES = [
    "active_links", "connected_drones", "progress_before", "position_x",
    "position_y", "altitude", "speed", "direction_x", "direction_y",
    "battery", "signal_strength", "latency", "packet_loss",
]
METADATA = ["mission_id", "mission_type", "drone_id", "tick"]
TARGETS = ["next_position_x", "next_position_y"]
EXCLUDED = ["progress_after", "actual_movement", "behavior", "action", "decision"]
MISSION_TYPES = ["PATROL", "SURVEILLANCE", "SEARCH", "RECOVERY"]
SEED = 20260916


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def coordinate(value, label):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must be a two-dimensional list")
    return [number(value[0], f"{label}[0]"), number(value[1], f"{label}[1]")]


def split_missions(mission_ids, seed):
    partitions = {}
    rng = random.Random(seed)
    for mission_type in MISSION_TYPES:
        ids = sorted(mission_ids[mission_type])
        if len(ids) != 25:
            raise ValueError(f"{mission_type} must contain 25 missions, found {len(ids)}")
        shuffled = ids[:]
        rng.shuffle(shuffled)
        partitions.update({mission_id: "train" for mission_id in shuffled[:17]})
        partitions.update({mission_id: "validation" for mission_id in shuffled[17:21]})
        partitions.update({mission_id: "test" for mission_id in shuffled[21:]})
    return partitions


def load_rows(source_root):
    transition_dir = source_root / "processed" / "transitions"
    files = sorted(transition_dir.glob("*.jsonl"))
    if len(files) != 100:
        raise ValueError(f"Expected exactly 100 JSONL mission files, found {len(files)}")
    records = []
    mission_ids = defaultdict(set)
    transitions_by_mission = Counter()
    mission_transition_ticks = defaultdict(set)
    mission_drone_ids = defaultdict(set)
    seen_row_keys = set()
    transition_count = 0
    for path in files:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path}:{line_number}") from exc
                mission = record.get("mission")
                swarm = record.get("swarm")
                transition = record.get("transition")
                result = record.get("result")
                if not all(isinstance(value, dict) for value in (mission, transition, result, swarm)):
                    raise ValueError(f"Missing mission, transition, result, or swarm metadata in {path}:{line_number}")
                required_mission = {"mission_id", "mission_type"}
                if not required_mission.issubset(mission):
                    raise ValueError(f"Missing mission metadata fields in {path}:{line_number}")
                if "tick" not in transition:
                    raise ValueError(f"Missing transition tick in {path}:{line_number}")
                if not {"active_links", "connected_drones", "progress_before"}.issubset(result):
                    raise ValueError(f"Missing result metadata fields in {path}:{line_number}")
                mission_id = mission.get("mission_id")
                mission_type = mission.get("mission_type")
                drones = swarm.get("drones")
                if mission_type not in MISSION_TYPES or not isinstance(mission_id, str):
                    raise ValueError(f"Invalid mission metadata in {path}:{line_number}")
                if not isinstance(drones, list) or len(drones) != 30:
                    raise ValueError(f"Expected 30 drones in {path}:{line_number}")
                if not isinstance(transition, dict) or not isinstance(result, dict):
                    raise ValueError(f"Missing transition/result in {path}:{line_number}")
                tick = transition["tick"]
                if not isinstance(tick, int) or isinstance(tick, bool):
                    raise ValueError(f"tick must be an integer in {path}:{line_number}")
                mission_ids[mission_type].add(mission_id)
                if tick in mission_transition_ticks[mission_id]:
                    raise ValueError(f"Duplicate transition tick for mission {mission_id}: {tick}")
                mission_transition_ticks[mission_id].add(tick)
                transitions_by_mission[mission_id] += 1
                transition_count += 1
                transition_drone_ids = set()
                for drone in drones:
                    before = drone.get("state_before")
                    after = drone.get("state_after")
                    if not isinstance(before, dict) or not isinstance(after, dict):
                        raise ValueError(f"Missing drone state in {path}:{line_number}")
                    drone_id = drone.get("drone_id")
                    if not isinstance(drone_id, str):
                        raise ValueError(f"drone_id must be a string in {path}:{line_number}")
                    if drone_id in transition_drone_ids:
                        raise ValueError(f"Duplicate drone_id in transition at {path}:{line_number}")
                    transition_drone_ids.add(drone_id)
                    required_after = {
                        "position", "altitude", "speed", "direction", "battery",
                        "signal_strength", "latency", "packet_loss",
                    }
                    if not required_after.issubset(after):
                        raise ValueError(f"Missing state_after fields in {path}:{line_number}")
                    position = coordinate(before.get("position"), "state_before.position")
                    next_position = coordinate(after.get("position"), "state_after.position")
                    direction = coordinate(after.get("direction"), "state_after.direction")
                    row = {
                        "mission_id": mission_id, "mission_type": mission_type,
                        "drone_id": drone_id, "tick": tick,
                        "active_links": result.get("active_links"),
                        "connected_drones": result.get("connected_drones"),
                        "progress_before": result.get("progress_before"),
                        "position_x": position[0], "position_y": position[1],
                        "altitude": after.get("altitude"), "speed": after.get("speed"),
                        "direction_x": direction[0], "direction_y": direction[1],
                        "battery": after.get("battery"),
                        "signal_strength": after.get("signal_strength"),
                        "latency": after.get("latency"), "packet_loss": after.get("packet_loss"),
                        "next_position_x": next_position[0], "next_position_y": next_position[1],
                    }
                    for key in FEATURES + TARGETS:
                        row[key] = number(row[key], key)
                    row_key = (mission_id, tick, drone_id)
                    if row_key in seen_row_keys:
                        raise ValueError(f"Duplicate (mission_id, tick, drone_id) row: {row_key}")
                    seen_row_keys.add(row_key)
                    records.append(row)
                if mission_id in mission_drone_ids and mission_drone_ids[mission_id] != transition_drone_ids:
                    raise ValueError(
                        f"Inconsistent drone ID set for mission {mission_id} at {path}:{line_number}"
                    )
                mission_drone_ids.setdefault(mission_id, transition_drone_ids)
    if transition_count != len(records) // 30:
        raise ValueError("Transition and drone-record counts are inconsistent")
    if any(len(ids) != 30 for ids in mission_drone_ids.values()):
        raise ValueError("Every mission must contain exactly 30 distinct drone IDs")
    unique_mission_tick_transitions = sum(len(ticks) for ticks in mission_transition_ticks.values())
    if unique_mission_tick_transitions != transition_count:
        raise ValueError("Unique mission/tick transition count does not match transition count")
    return (
        files,
        records,
        mission_ids,
        transitions_by_mission,
        transition_count,
        mission_drone_ids,
        unique_mission_tick_transitions,
    )


def write_outputs(source_root, output_root, seed):
    (
        files,
        rows,
        mission_ids,
        transitions_by_mission,
        transition_count,
        mission_drone_ids,
        unique_mission_tick_transitions,
    ) = load_rows(source_root)
    if transition_count != 11570 or len(rows) != 347100:
        raise ValueError(f"Expected 11,570 transitions and 347,100 rows; found {transition_count} and {len(rows)}")
    if sum(len(ids) for ids in mission_ids.values()) != 100:
        raise ValueError("Expected 100 unique missions")
    if any(len(mission_ids[t]) != 25 for t in MISSION_TYPES):
        raise ValueError("Expected 25 missions per mission type")
    partitions = split_missions(mission_ids, seed)
    split_missions_by_name = defaultdict(set)
    for mission_id, split in partitions.items():
        split_missions_by_name[split].add(mission_id)
    split_mission_overlap = sum(len(left & right) for index, left in enumerate(split_missions_by_name.values()) for right in list(split_missions_by_name.values())[index + 1:])
    source_missions = set(mission_drone_ids)
    assigned_missions = set().union(*split_missions_by_name.values())
    if assigned_missions != source_missions:
        raise ValueError("Every source mission must appear in exactly one split")
    if split_mission_overlap != 0 or sum(len(ids) for ids in split_missions_by_name.values()) != len(source_missions):
        raise ValueError("Mission-level splits overlap")
    split_counts_by_type = {
        split: {
            mission_type: len(
                split_missions_by_name[split] & mission_ids[mission_type]
            )
            for mission_type in MISSION_TYPES
        }
        for split in ("train", "validation", "test")
    }
    expected_split_counts = {
        "train": 17,
        "validation": 4,
        "test": 4,
    }
    for split, expected_count in expected_split_counts.items():
        if any(count != expected_count for count in split_counts_by_type[split].values()):
            raise ValueError(
                f"Invalid {split} mission counts by type: {split_counts_by_type[split]}"
            )
    duplicate_rows = len(rows) - len({(r["mission_id"], r["tick"], r["drone_id"]) for r in rows})
    if duplicate_rows != 0:
        raise ValueError(f"Duplicate mission/tick/drone rows found: {duplicate_rows}")
    transition_tick_integrity = (
        unique_mission_tick_transitions == transition_count
    )
    if not transition_tick_integrity:
        raise ValueError(
            "Unique mission/tick transition count does not match transition count"
        )
    rows.sort(key=lambda r: (partitions[r["mission_id"]], r["mission_id"], r["tick"], r["drone_id"]))
    output_root.mkdir(parents=True, exist_ok=True)
    groups = {name: [] for name in ("train", "validation", "test")}
    for row in rows:
        groups[partitions[row["mission_id"]]].append(row)
    columns = METADATA + FEATURES + TARGETS
    for name, group in groups.items():
        with (output_root / f"{name}.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(group)
    mission_counts = {name: len(split_missions_by_name[name]) for name in groups}
    missing_values = sum(1 for row in rows for key in FEATURES + TARGETS if row[key] is None)
    nonfinite_values = sum(
        1 for row in rows for key in FEATURES + TARGETS
        if isinstance(row[key], float) and not math.isfinite(row[key])
    )
    schema = {
        "dataset_name": "Golden Arrows Dataset V3.0",
        "representation_name": "state_only",
        "input_features": FEATURES, "metadata_features": METADATA, "targets": TARGETS,
        "excluded_fields": EXCLUDED,
        "split_methodology": "Mission-level split: 17 train / 4 validation / 4 test per mission type",
        "split_seed": seed, "source_location": "datasetv3_final/processed/transitions/*.jsonl",
        "row_counts": {name: len(group) for name, group in groups.items()},
        "mission_counts": mission_counts,
        "causal_claim": False,
        "temporal_semantics": "position uses state_before.position; physical/network fields and next-position targets use state_after values and are not automatically strict pre-action observations",
    }
    (output_root / "feature_schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    report = [
        "GOLDEN ARROWS DATASET V3.0 — STATE-ONLY PREPARATION", "",
        "RESULT: PASS", f"Source path: {source_root / 'processed' / 'transitions'}",
        f"Source file count: {len(files)}", "Representation: state_only",
        f"Source missions: {len(mission_drone_ids)}",
        f"Source transitions: {transition_count}", f"Source drone-transition records: {len(rows)}",
        f"Output rows: {len(rows)}", f"Model features ({len(FEATURES)}): {', '.join(FEATURES)}",
        f"Metadata features: {', '.join(METADATA)}", f"Targets ({len(TARGETS)}): {', '.join(TARGETS)}",
        f"Excluded fields: {', '.join(EXCLUDED)}",
        f"Train missions: {mission_counts['train']}", f"Validation missions: {mission_counts['validation']}", f"Test missions: {mission_counts['test']}",
        f"Train rows: {len(groups['train'])}", f"Validation rows: {len(groups['validation'])}",
        f"Test rows: {len(groups['test'])}", f"Split seed: {seed}",
        f"Duplicate-row check: PASS ({duplicate_rows} duplicate mission/tick/drone rows)",
        "30-drones-per-transition check: PASS",
        f"Transition tick integrity: {'PASS' if transition_tick_integrity else 'FAIL'} ({unique_mission_tick_transitions} unique mission/tick transitions)",
        f"Mission-level split check: PASS (no overlap; every source mission assigned once; overlap count {split_mission_overlap})",
        f"Missing-value check: PASS ({missing_values} missing required values)",
        f"Finite-value check: PASS ({nonfinite_values} non-finite values)",
        "Temporal semantics warning: state_before.position is used for position; several physical/network values are logged under state_after and are not automatically pre-action observations.",
        "Source dataset modified: NO",
    ]
    (output_root / "preparation_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Source missions: {len(mission_drone_ids)}\nSource transitions: {transition_count}\nSource drone records: {len(rows)}")
    print(f"Output rows: {len(rows)}\nModel feature count: {len(FEATURES)}\nTarget count: {len(TARGETS)}")
    print(f"Train missions: {mission_counts['train']}\nValidation missions: {mission_counts['validation']}\nTest missions: {mission_counts['test']}")
    print(f"Duplicate rows: {duplicate_rows}")
    print("Drone identity consistency: PASS")
    print(
        f"Transition tick integrity: "
        f"{'PASS' if transition_tick_integrity else 'FAIL'} "
        f"({unique_mission_tick_transitions} unique mission/tick transitions)"
    )
    print(f"Mission-level split: PASS\nMission overlap: {split_mission_overlap}")
    print(f"Missing values: {missing_values}\nNon-finite values: {nonfinite_values}")
    print("Source modified: NO\nRESULT: PASS")


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=root / "datasetv3_final")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--split-seed", type=int, default=SEED)
    args = parser.parse_args()
    output = args.output_root or (args.source_root / "ml_ready_state_only")
    try:
        write_outputs(args.source_root.resolve(), output.resolve(), args.split_seed)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"RESULT: FAIL\n{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
