
import argparse
import pickle
from etc.gamestate import GameState
from typing import List

parser = argparse.ArgumentParser(description='View game snapshots.')
parser.add_argument('snapshot_path', metavar='PATH', type=str, nargs=1,
                    help='path to snapshot file (.bin)')


def main():
    args = parser.parse_args()
    with open(args.snapshot_path[0], "rb") as f:
        gamestates: List[GameState] = pickle.load(f)
        for gamestate in gamestates:
            print(gamestate)


if __name__ == "__main__":
    main()
