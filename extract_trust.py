
import json


def main():
    with open("operators.json", "r", encoding='utf8') as f:
        data = json.load(f)

    counts = [0 for _ in range(201)]

    for i in data:
        counts[i['trust']] += 1

    for i in range(201):
        print(f"{i}: {counts[i]}")

if __name__ == '__main__':
    main()
