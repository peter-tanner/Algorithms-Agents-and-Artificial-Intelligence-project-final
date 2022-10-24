import json
import pickle

from etc.util import NoCopyShelf, RecursiveDict
from etc.messages import BLUE_MESSAGES


def main() -> None:
    data = NoCopyShelf.open(
        "blue_training.bin",
        protocol=pickle.HIGHEST_PROTOCOL,
        writeback=True  # Yes this makes it less performant, but it will be more readable.
    )['data']

    for x in data:
        for y in data[x]:
            for z in data[x][y]:
                for w in data[x][y][z]:
                    d: RecursiveDict = data[x][y][z][w]
                    d_ = []
                    samples = []
                    for k in range(0, len(BLUE_MESSAGES)):
                        if k in d.keys():
                            samples.append(str(d[k][0]).ljust(4))
                            d_.append("{:.2f}".format(d[k][1] / d[k][0]).ljust(7))
                        else:
                            samples.append(str(0).ljust(4))
                            d_.append("_NaN_".ljust(7))
                    print(f"(red_op={x},blue_op={y},red_f={z},blue_e={w}) | {d_} | {samples}")
    # print(json.dumps(data, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
