import sys
from typing import Tuple

from etc.custom_float import Uncertainty

# Enable graphing
ENABLE_GRAPHICS = False

# Debug messages
ENABLE_DIAGNOSTIC_MESSAGES = False

# Serialize each game and save to a file
ENABLE_SNAPSHOTS = False
GAMESTATE_PARAMETER_SNAPSHOT_OUTPUT_DIR = "./snapshots/"

# Check Uncertainty class
INITIAL_UNCERTAINTY_RANGE: Tuple[Uncertainty] = (Uncertainty(0.0), Uncertainty(0.0))
INITIAL_BLUE_ENERGY: float = 300.0

DAYS_UNTIL_ELECTION = sys.maxsize

# Training data path
BLUE_AGENT_LUT_PATH = "blue_training.bin"
RED_AGENT_LUT_PATH = "red_training.bin"

N_GREEN_AGENT = 100
P_GREEN_AGENT_CONNECTION = 0.05
P_GREEN_AGENT_BLUE = 0.5

N_GRAY_AGENT = 10
P_GRAY_AGENT_FRIENDLY = 0.5
