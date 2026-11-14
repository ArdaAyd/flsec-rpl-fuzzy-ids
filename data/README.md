# Data

| File | Content |
|---|---|
| `paper_reported_ranges.csv` | Min-max values reported by Kim et al. (2024) for accuracy, F1 and first-time detection, taken from the text describing Figs. 10, 11, 15, 16, 17 and 21. Used to compare the reproduction with the paper. |
| `windows.csv.gz` | Observation windows scored by FLSec-RPL in passive mode. Training and validation data for the membership-function tuning. |

## windows.csv.gz

Generated with `python experiments/proposed/make_dataset.py` (about 4 minutes on 8 cores).

FLSec-RPL runs on every legitimate node in passive mode: it computes the phase I variables and the
aggressive weight of every neighbor at the end of every 30 s window, but it never quarantines or
blocks anyone. The data therefore does not depend on the paper's membership functions.

- Scenarios: 16 and 32 sensors, static and mobile, PAN 10-50 %, ARI 1-8 s (100 combinations).
- Seeds 100-102 form the `train` split and seeds 103-104 the `val` split. Seeds 0-4 are reserved for
  the closed-loop test and never appear here.
- 3,181,576 windows were collected. At most 2,000 windows per (scenario, split, class) cell are kept,
  which leaves 614,218 rows. `weight` (cell size / kept rows) restores the original class and
  scenario mix.

| Column | Description |
|---|---|
| `n_sensors`, `mobile`, `pan`, `ari`, `seed` | scenario |
| `t` | end of the window (s) |
| `detector`, `neighbor` | node ids, 0 is the root |
| `dio_counter`, `dti`, `stia`, `rdt_flag` | phase I variables of the neighbor in this window |
| `omega_paper` | aggressive weight computed with the paper's membership functions |
| `attacker` | ground truth: the neighbor is an attacker |
| `split`, `weight` | see above |
