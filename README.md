# Golden Arrows Dataset

**Golden Arrows** is a simulation-generated dataset for studying multi-drone
swarm behavior at mission and transition level. It brings together mission
context, controller decisions and actions, network conditions, drone state
and movement, and explicit swarm-behavior telemetry. The project is intended
to support transparent, reproducible research in swarm intelligence,
autonomous multi-agent systems, network-aware coordination, and machine
learning.

The project currently publishes two releases: V3.0, a 100-mission dataset
with documented ML-ready derivatives, and V3.1, a separate 1,000-mission
expansion. V3.1 retains the rich transition schema and expands the balanced
mission collection; it does not replace or modify V3.0.

> **Scope:** These are simulated data, not real-world flight telemetry. The
> logged policy is a scripted mission controller with advanced swarm
> behavior—not a learned policy—and the data do not establish real-world
> safety, flight performance, or operational effectiveness.

## Published datasets

| Release | Missions | Transitions | Drones per transition | Data and documentation |
| --- | ---: | ---: | ---: | --- |
| [V3.0](Golden_Arrows_Dataset_V3.0/README.md) | 100 (25 per mission type) | 11,570 | 30 | [Zenodo record](https://zenodo.org/records/22816408) · [Version package](https://github.com/sk08082004/GOLDEN-ARROWS-DATASET/tree/main/Golden_Arrows_Dataset_V3.0) |
| [V3.1](Golden_Arrows_Dataset_V3.1/README.md) | 1,000 (250 per mission type) | 113,954 | 30 | [Version package](https://github.com/sk08082004/GOLDEN-ARROWS-DATASET/tree/main/Golden_Arrows_Dataset_V3.1) · [Reserved DOI in citation metadata](https://doi.org/10.5281/zenodo.23030808) |

**V3.1 publication status:** its `CITATION.cff` lists DOI
[`10.5281/zenodo.23030808`](Golden_Arrows_Dataset_V3.1/CITATION.cff), but the
Zenodo record was not resolving when this README was prepared, and the V3.1
changelog still says its release date is pending publication. Use the V3.1
GitHub package for its available documentation; confirm that the Zenodo
record is public before treating that DOI as a live data download or citing
it as a published record.

### What is in each release?

Both releases cover four simulated mission types—PATROL, SURVEILLANCE,
SEARCH, and RECOVERY—with 30 drones represented per transition. The
transition records use the schema version
`golden_arrows_v3_rich_transition_1.0` and include mission and transition
context, drone-level state and movement, network information, and logged
swarm behavior.

Advanced Swarm Behavior is enabled across both releases. Its documented
components are cohesion, alignment, separation, formation, target attraction,
network preservation, and boundary avoidance. These are simulator behavior
components, not learned representations.

V3.0 additionally documents three prepared export families:

- `ml_ready/` — general ML-ready export
- `ml_ready_state_only/` — state-only baseline
- `ml_ready_behavior_aware/` — state plus behavior features

The V3.0 README documents mission-level train/validation/test splits for
these exports. V3.1's publication package documents raw and processed data,
metadata, schemas, examples, and validation; it does **not** include
generated ML-ready datasets or train/validation/test CSV files.

## Explore the releases

Each version folder contains its own release documentation and citation
metadata:

| Resource | V3.0 | V3.1 |
| --- | --- | --- |
| Dataset README | [README](Golden_Arrows_Dataset_V3.0/README.md) | [README](Golden_Arrows_Dataset_V3.1/README.md) |
| Dataset card | [Dataset card](Golden_Arrows_Dataset_V3.0/dataset_card.md) | [Dataset card](Golden_Arrows_Dataset_V3.1/dataset_card.md) |
| Citation | [CITATION.cff](Golden_Arrows_Dataset_V3.0/CITATION.cff) | [CITATION.cff](Golden_Arrows_Dataset_V3.1/CITATION.cff) |
| Changelog | [CHANGELOG.md](Golden_Arrows_Dataset_V3.0/CHANGELOG.md) | [CHANGELOG.md](Golden_Arrows_Dataset_V3.1/CHANGELOG.md) |
| Dataset description | [PDF](Golden_Arrows_Dataset_V3.0/dataset_description.pdf) | [PDF](Golden_Arrows_Dataset_V3.1/dataset_description.pdf) |
| Examples | [Examples](Golden_Arrows_Dataset_V3.0/examples/) | [Examples](Golden_Arrows_Dataset_V3.1/examples/) |
| Schemas | [Schemas](Golden_Arrows_Dataset_V3.0/schema/) | [Schemas](Golden_Arrows_Dataset_V3.1/schema/) |
| Validation materials | [Validation](Golden_Arrows_Dataset_V3.0/validation/) | [Validation](Golden_Arrows_Dataset_V3.1/validation/) |

For the V3.0 data download, use the [Zenodo record](https://zenodo.org/records/22816408).
The GitHub release folders are the place to review version-specific
documentation, schemas, and supporting materials.

## Data and research considerations

- **Observations are hierarchical.** Drone-transition records are nested
  within transitions and missions. For example, V3.1's 3,418,620
  drone-transition records are 113,954 transitions with 30 drones each, not
  3,418,620 independent samples.
- **Split by mission for evaluation.** Randomly splitting individual rows or
  transitions can leak mission-specific information across train and test
  sets. Use mission-level splits and document the method.
- **Check feature timing.** Inspect the schemas and timing of fields before
  choosing inputs and targets, especially for causal or reinforcement
  learning work. Logged post-transition values are not automatically
  pre-action observations.
- **Interpret validation within scope.** Structural and numerical checks
  describe integrity of the simulated release; they do not validate
  real-world performance or safety.
- **Account for simulation specificity.** The documented data were generated
  with a scripted mission controller, a particular simulation setup, and
  four mission types. Findings should be interpreted accordingly.

## Future directions

Potential next steps for the project include expanding scenario and
environment diversity, improving reproducible preprocessing and validation
tools, and publishing additional documented dataset releases. Any future
release should retain versioned schemas, validation evidence, and
mission-level evaluation guidance. These are intended directions, not
promises about a release schedule or features.

## Citation and license

Please cite the specific release you used, using its `CITATION.cff` file:
[V3.0 citation](Golden_Arrows_Dataset_V3.0/CITATION.cff) or
[V3.1 citation](Golden_Arrows_Dataset_V3.1/CITATION.cff). V3.0's DOI is
[`10.5281/zenodo.22816408`](https://doi.org/10.5281/zenodo.22816408). The
V3.1 DOI is listed in its citation file, but its Zenodo record was not
resolving at the time this README was prepared; see the publication-status
note above.

The dataset is provided under the
[Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/).
