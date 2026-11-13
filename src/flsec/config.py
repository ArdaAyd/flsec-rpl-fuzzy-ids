"""FLSec-RPL parameters from Kim et al. (2024). Equation/table numbers refer to the paper."""

from dataclasses import dataclass

# Phase I
OBSERVATION_WINDOW_S = 30.0  # phi
SMOOTHING_ALPHA = 0.1  # Eq. 3

# Phase II
INPUT_NAMES = ("dio_counter", "dti", "stia")
INPUT_UNIVERSE = (0.0, 30.0)
TERMS = ("L", "M", "H")

# Trapezoids (a, b, c, d) from Fig. 6
PAPER_INPUT_MFS = {
    "dio_counter": {"L": (0, 0, 2, 5), "M": (1, 5, 7, 11), "H": (7, 11, 30, 30)},
    "dti": {"L": (0, 0, 3, 10), "M": (3, 10, 13, 20), "H": (13, 20, 30, 30)},
    "stia": {"L": (0, 0, 3, 9), "M": (3, 9, 13, 20), "H": (13, 20, 30, 30)},
}

OUTPUT_NAME = "aggressive_weight"
OUTPUT_UNIVERSE = (0.0, 1.0)
OUTPUT_TERMS = ("normal", "quarantine", "malicious")
PAPER_OUTPUT_MFS = {  # triangles (a, b, c)
    "normal": (0.0, 0.0, 0.5),
    "quarantine": (0.0, 0.5, 1.0),
    "malicious": (0.5, 1.0, 1.0),
}

# Table 2: (DIO_Counter, DTI, STIA) -> aggressive weight
PAPER_RULES = (
    ("H", "L", "L", "malicious"),   # 1
    ("H", "L", "M", "quarantine"),  # 2
    ("H", "L", "H", "quarantine"),  # 3
    ("H", "M", "L", "malicious"),   # 4
    ("H", "M", "M", "quarantine"),  # 5
    ("H", "M", "H", "normal"),      # 6
    ("H", "H", "L", "quarantine"),  # 7
    ("H", "H", "M", "normal"),      # 8
    ("H", "H", "H", "normal"),      # 9
    ("M", "L", "L", "malicious"),   # 10
    ("M", "L", "M", "quarantine"),  # 11
    ("M", "L", "H", "normal"),      # 12
    ("M", "M", "L", "quarantine"),  # 13
    ("M", "M", "M", "normal"),      # 14
    ("M", "M", "H", "normal"),      # 15
    ("M", "H", "L", "quarantine"),  # 16
    ("M", "H", "M", "normal"),      # 17
    ("M", "H", "H", "normal"),      # 18
    ("L", "L", "L", "quarantine"),  # 19
    ("L", "L", "M", "quarantine"),  # 20
    ("L", "L", "H", "normal"),      # 21
    ("L", "M", "L", "quarantine"),  # 22
    ("L", "M", "M", "normal"),      # 23
    ("L", "M", "H", "normal"),      # 24
    ("L", "H", "L", "normal"),      # 25
    ("L", "H", "M", "normal"),      # 26
    ("L", "H", "H", "normal"),      # 27
)

FUZZY_FILTER_DELTA = 0.5


@dataclass(frozen=True)
class Phase3Params:
    delta: float = FUZZY_FILTER_DELTA
    beta: float = 1.0  # upper bound of omega (Fig. 8A)
    md_lower: float = 1.0  # L, Eq. 13
    md_upper: float = 6.0  # U, Eq. 13
    window_s: float = OBSERVATION_WINDOW_S
    bp0_windows: float = 10.0  # BP_0 = 10 * phi
    q: float = 2.0  # Eq. 16
    lam: int = 3  # soft blocks before a permanent block

    @property
    def qp_lower(self) -> float:
        return self.md_lower * self.window_s

    @property
    def qp_upper(self) -> float:
        return self.md_upper * self.window_s

    @property
    def bp0(self) -> float:
        return self.bp0_windows * self.window_s


# Simulation setup (Table 4)
AREA_M = 150.0
RADIO_RANGE_M = 50.0
SIM_DURATION_S = 30 * 60.0
ATTACK_START_S = 90.0
DETECTION_START_S = ATTACK_START_S + OBSERVATION_WINDOW_S
PAN_LEVELS = (0.1, 0.2, 0.3, 0.4, 0.5)
ARI_LEVELS_S = (1.0, 2.0, 4.0, 6.0, 8.0)
TRICKLE_IMIN_S = 4.096  # 2^12 ms
TRICKLE_DOUBLINGS = 8  # Imax = 1048.6 s (~17.5 min)
TRICKLE_K = 10
