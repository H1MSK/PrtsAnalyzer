
import json
import math


def extract_trust():
    with open("operators.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    counts = [0 for _ in range(201)]

    for i in data:
        counts[max(0, min(i['trust'], 200))] += 1

    return counts


if __name__ == '__main__':
    counts = extract_trust()
    with open("trust.csv", "w") as f:
        f.write("\n".join(f"{i},{counts[i]}" for i in range(201)))
