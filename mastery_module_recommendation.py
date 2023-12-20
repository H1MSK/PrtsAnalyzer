import json
import os
from typing import Dict, List


def recommend():
    with open("operators.json", "r", encoding="utf-8") as f:
        op = json.load(f)

    op: Dict[str, dict] = {x["name"]: x for x in op}

    mastery_recomm = [x for x in os.listdir() if x.endswith('技能.csv')]
    module_recomm = [x for x in os.listdir() if x.endswith('技能.csv')]

    result = []
    for recom in mastery_recomm:
        with open(recom, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                level, name, id = line[:-1].split(',')
                if name in op.keys() and op[name].get("skill_mastery_" + str(id), 0) != 3:
                    result.append((recom, i + 1, level, name, id))
                    break

    return result

if __name__ == '__main__':
    result = recommend()
    print("\n".join(f"{table}:\n#{i}: {level} {name} {id}" for table, i, level, name, id in result))
