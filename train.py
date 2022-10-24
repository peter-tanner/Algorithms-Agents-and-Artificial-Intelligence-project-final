import csv
from datetime import datetime
import pathlib
import pickle
from time import time
import numpy as np
from copy import deepcopy
from types import FunctionType
from typing import Callable, Dict, List
from etc.gamestate import GameState, Winner
from etc.util import debug_print
from play_config import ENABLE_SNAPSHOTS, GAMESTATE_PARAMETER_SNAPSHOT_OUTPUT_DIR, INITIAL_UNCERTAINTY_RANGE, N_GRAY_AGENT, N_GREEN_AGENT,\
    P_GRAY_AGENT_FRIENDLY, P_GREEN_AGENT_BLUE, P_GREEN_AGENT_CONNECTION


def rand_rounds(gs: GameState) -> GameState:
    blue_gamestate = deepcopy(gs)
    gs.blue_agent.dumb_influence(gs)
    red_gamestate = deepcopy(gs)
    gs.red_agent.dumb_influence(gs)
    # gs.draw_green_network()
    # gs.green_round()
    # gs.draw_green_network()
    # spy = bool(gs.rand.getrandbits(1))
    # spy = False
    gs.green_round()
    gs.red_agent.update_short_term_mem(red_gamestate, gs)
    gs.blue_agent.update_short_term_mem(blue_gamestate, gs)
    gs.draw_green_network()
    gs.iteration += 1
    return gs


def intelligent_rounds(gs: GameState) -> GameState:
    blue_gamestate = deepcopy(gs)
    gs.blue_agent.smart_influence(gs)
    red_gamestate = deepcopy(gs)
    gs.red_agent.smart_influence(gs)
    gs.green_round()
    gs.red_agent.update_short_term_mem(red_gamestate, gs)
    gs.blue_agent.update_short_term_mem(blue_gamestate, gs)
    gs.draw_green_network()
    gs.iteration += 1
    return gs


def round(round_func: FunctionType) -> List[GameState]:
    state_buffer: List[GameState] = []
    # gs: GameState = GameState.short_init((100, 0.05, 0.5), (10, 0.5))
    gs: GameState = GameState(
        green_agents=(N_GREEN_AGENT, P_GREEN_AGENT_CONNECTION, P_GREEN_AGENT_BLUE),
        gray_agents=(N_GRAY_AGENT, P_GRAY_AGENT_FRIENDLY),
        uncertainty_interval=INITIAL_UNCERTAINTY_RANGE,
        seed=None, graphics=False)
    state_buffer.append(deepcopy(gs))

    debug_print("INITIAL CONDITIONS.")
    debug_print(gs)
    debug_print("STARTING GAME.")

    # gs.draw_green_network()
    while gs.winner == Winner.NO_WINNER:
        gs = round_func(gs)
        # debug_print(gs.red_agent.red_followers, gs.blue_agent.blue_energy, len(list(gs.green_agents)))
        debug_print(gs)
        gs.update_winner()
        gs.draw_green_network()
        state_buffer.append(deepcopy(gs))
        # print(gs)
    gs.close()

    # state_buffer.append(deepcopy(gs))

    print(f"{gs.iteration} WINNER {gs.winner}")
    return state_buffer

# Calibrator


def training_rounds(win_file_blue, win_file_red, round_func: Callable, training_iterations: int) -> None:
    # state_buffer: List[GameState] = round(rand_rounds)
    # exit()
    ending_states: Dict[Winner, int] = {
        Winner.BLUE_NO_ENERGY: 0,
        Winner.BLUE_WIN: 0,
        Winner.RED_NO_FOLLOWERS: 0,
        Winner.RED_WIN: 0,
    }

    blue_win_round_len = []
    red_win_round_len = []

    for x in range(0, training_iterations):
        t = time()
        print(f"Game {x}")
        state_buffer: List[GameState] = round(round_func)

        ending_state: GameState = state_buffer[-1]

        ending_states[ending_state.winner] += 1
        if ending_state.winner == Winner.BLUE_NO_ENERGY or ending_state.winner == Winner.RED_WIN:
            red_win_round_len.append(ending_state.iteration)
            blue_win_round_len.append(-ending_state.iteration)
        elif ending_state.winner == Winner.RED_NO_FOLLOWERS or ending_state.winner == Winner.BLUE_WIN:
            red_win_round_len.append(-ending_state.iteration)
            blue_win_round_len.append(ending_state.iteration)
        print(f"dt={time() - t} s")
    print(ending_states)
    print(blue_win_round_len)
    print(red_win_round_len)

    with open(win_file_blue, "w") as f:
        writer = csv.writer(f)
        writer.writerow(blue_win_round_len)

    with open(win_file_red, "w") as f:
        writer = csv.writer(f)
        writer.writerow(red_win_round_len)


if __name__ == "__main__":
    N_RANDOM_ROUNDS = 120
    N_INTELLIGENT_ROUNDS = 300
    training_rounds("rand_blue_win.csv", "rand_red_win.csv", rand_rounds, N_RANDOM_ROUNDS)
    training_rounds("intel_blue_win.csv", "intel_red_win.csv", intelligent_rounds, N_INTELLIGENT_ROUNDS)
