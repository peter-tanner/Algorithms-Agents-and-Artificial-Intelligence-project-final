
from copy import deepcopy
from datetime import datetime
import math
import pathlib
import pickle
from typing import List
from etc.custom_float import Uncertainty
from etc.gamestate import GameState, Winner
from etc.messages import Message, Opinion
from agents.blue import BlueAgent
from agents.red import RedAgent

import play_config as cfg


def rand_rounds(gs: GameState) -> GameState:
    blue_gamestate = deepcopy(gs)
    gs.blue_agent.smart_influence(gs)
    red_gamestate = deepcopy(gs)
    gs.red_agent.smart_influence(gs)
    # gs.draw_green_network()
    # gs.green_round()
    # gs.draw_green_network()
    # spy = bool(gs.rand.getrandbits(1))
    # spy = False
    gs.green_round()
    gs.draw_green_network()
    gs.red_agent.update_short_term_mem(red_gamestate, gs)
    gs.blue_agent.update_short_term_mem(blue_gamestate, gs)
    gs.iteration += 1
    return gs


def main():
    sel_parameters = input_opts("""Would you like to select parameters?
[y] -> Yes
[n] -> No
> """, ['y', 'n'])
    if sel_parameters == 'y':
        select_parameters()

    cfg.ENABLE_SNAPSHOTS = ('y' == input_opts("""Would you like to enable snapshots?
[y] -> Yes
[n] -> No
> """, ['y', 'n']))

    if cfg.ENABLE_SNAPSHOTS:
        snapshot_path = pathlib.Path(cfg.GAMESTATE_PARAMETER_SNAPSHOT_OUTPUT_DIR)
        snapshot_path.mkdir(parents=True, exist_ok=True)

    cfg.ENABLE_GRAPHICS = ('y' == input_opts("""Enable graphics?
Note that this option is currently exporting to an image file for compatibility on headless operating systems (WSL)
[y] -> Graphics
[n] -> No graphics
> """, ['y', 'n']))

    while True:
        print("Starting new game")
        state_buffer: List[GameState] = []
        # gs: GameState = GameState.short_init((100, 0.05, 0.5), (10, 0.5))
        gs: GameState = GameState(
            green_agents=(cfg.N_GREEN_AGENT, cfg.P_GREEN_AGENT_CONNECTION, cfg.P_GREEN_AGENT_BLUE),
            gray_agents=(cfg.N_GRAY_AGENT, cfg.P_GRAY_AGENT_FRIENDLY),
            uncertainty_interval=cfg.INITIAL_UNCERTAINTY_RANGE,
            seed=None, graphics=cfg.ENABLE_GRAPHICS)

        player = input_opts("""Choose a team
[r] -> Red
[b] -> Blue
[n] -> None
> """, ['r', 'b', 'n'])

        player: Opinion = {
            'r': Opinion.RED,
            'b': Opinion.BLUE,
            'n': Opinion.UNDEFINED
        }[player]

        state_buffer.append(deepcopy(gs))

        while gs.winner == Winner.NO_WINNER:
            print(gs.print_gamestate_pretty())

            print("Blue turn")
            blue_gamestate = deepcopy(gs)
            if player == Opinion.BLUE:
                option = select_potency(BlueAgent.choices())
                gs.blue_agent.influence(gs, option)
            else:
                gs.blue_agent.dumb_influence(gs)

            print("Red turn")
            red_gamestate = deepcopy(gs)
            if player == Opinion.RED:
                option = select_potency(RedAgent.choices())
                gs.red_agent.influence(gs, option)
            else:
                gs.red_agent.dumb_influence(gs)

            print("Green turn")
            gs.green_round()
            gs.draw_green_network()

            gs.red_agent.update_short_term_mem(red_gamestate, gs)
            gs.blue_agent.update_short_term_mem(blue_gamestate, gs)
            gs.iteration += 1
            gs.update_winner()
            state_buffer.append(deepcopy(gs))
        gs.close()

        print(f"""
Game over
Round {gs.iteration}, reason {gs.winner}
Winner {Winner.winner_opinion(gs.winner)}""")
        if player != Opinion.UNDEFINED:
            print("YOU WIN 🎉" if Winner.winner_opinion(gs.winner) == player else "YOU LOSE 💀")
        print(gs.print_gamestate_pretty())
        input("Press enter to continue...")

        # Save snapshot of game
        if cfg.ENABLE_SNAPSHOTS:
            with snapshot_path.joinpath(f"game_snapshot_{datetime.now().isoformat().replace(':','_')}.bin").open("wb") as f:
                pickle.dump(state_buffer, f, protocol=pickle.HIGHEST_PROTOCOL)


def select_potency(messages: List[Message]) -> Message:
    prompt_str = "Choose a potency\n"
    for i in range(0, len(messages)):
        prompt_str += f"[{i}] -> {str(messages[i])}\n"
    return messages[input_p_int(prompt_str, 0, len(messages))]


def select_parameters() -> None:
    # Override config defaults

    print("\nBlue agent\n---")
    cfg.INITIAL_BLUE_ENERGY = input_float("Blue agent initial energy?\n> ")
    print("\nBounds of uniform uncertainty distribution at start of game for green agents\n---")
    cfg.INITIAL_UNCERTAINTY_RANGE = (input_uncertainty("Lower\n> "), input_uncertainty("Upper\n> "))

    print("\nGreen agents\n---")
    cfg.N_GREEN_AGENT = input_p_int("Number of green agents\n> ")
    cfg.P_GREEN_AGENT_CONNECTION = input_probability("Probability of green agent connections [0,1]\n> ")
    cfg.P_GREEN_AGENT_BLUE = input_p_int("Probability of green agents initialized to blue opinion\n> ")

    print("\nGray agents\n---")
    cfg.N_GRAY_AGENT = input_p_int("Number of gray agents\n> ")
    cfg.P_GRAY_AGENT_FRIENDLY = input_probability("Probability of gray agents being blue\n> ")


def input_probability(prompt: str) -> float:
    while True:
        value = input_T(prompt, float)
        if value > 0.0 and value < 1.0:
            return value
        else:
            print("Invalid input")


def input_p_int(prompt: str, l_=0, u_=math.inf) -> int:
    while True:
        value = input_T(prompt, int)
        if value >= l_ and value < u_:
            return value
        else:
            print("Invalid input")


def input_float(prompt: str) -> float:
    return input_T(prompt, float)


def input_uncertainty(prompt: str) -> Uncertainty:
    return input_T(prompt, Uncertainty)


def input_T(prompt: str, type):
    num: type = None
    while num is None:
        try:
            num = type(input(prompt))
        except ValueError:
            print("Invalid input")
    return num


def input_opts(prompt: str, opts: List[str]) -> str:
    option: str = ""
    while option not in opts:
        if len(option) > 0:
            print("Invalid input")
        option = input(prompt).strip().lower()
    return option


if __name__ == "__main__":
    main()
