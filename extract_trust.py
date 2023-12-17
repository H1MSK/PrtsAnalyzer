
import json


def main():
    with open("operators.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    counts = [0 for _ in range(201)]

    for i in data:
        counts[i['trust']] += 1

    with open("trust.csv", "w") as f:
        f.write("\n".join(f"{i},{counts[i]}" for i in range(201)))

if __name__ == '__main__':
    main()
