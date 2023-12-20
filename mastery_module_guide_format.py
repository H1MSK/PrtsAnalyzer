# from 化学老师
from enum import Enum
import re

class State(Enum):
    initial = 0
    desc = 2
    operators = 3

def format_mastery_module(in_file):
    Levels = ("sss (", "ss (", "s (", "A (", "B (")

    skills = []
    modules = []
    title = None

    with open(in_file, "r", encoding='utf-8') as fin:
        s = State.initial
        level = ""
        for line in fin:
            if title == None:
                title = line[:-1]
            if s == State.initial:
                if line.startswith(Levels):
                    s = State.desc
                    level = line.split(' ')[0].upper()
            if s == State.operators:
                if line.startswith(Levels):
                    s = State.desc
                    level = line.split(' ')[0].upper()
                else:
                    ops = line.split("，")
                    for op in ops:
                        m = re.match(R"([\u4e00-\u9fa5]+) ?(\d)(&(\d))?((\*+)([XY])?(&?(\*+)([XY])?)?)?", op)
                        if m == None:
                            continue
                        skills.append((level, m[1], m[2]))
                        if m[3] != None:
                            skills.append((level, m[1], m[4]))
                        if m[5] != None:
                            modules.append((level, m[1], len(m[6]), (m[7] if m[7] != None else 'A')))
                            if m[8] != None:
                                modules.append((level, m[1], len(m[9]), m[10]))
                            # print(m[1], m[2], m[3], m[4], m[5], m[6], m[7])
            elif s == State.desc:
                s = State.operators

    return title, skills, modules

if __name__ == "__main__":
    title, skills, modules = format_mastery_module("temp.in")
    print(title)
    print("技能:")
    print('\n'.join(",".join(skill) for skill in skills))
    print("\n模组:")
    print('\n'.join(",".join(map(str, module)) for module in modules))
    with open(title+"技能.csv", "w", encoding='utf-8') as f:
        f.write('\n'.join(",".join(skill) for skill in skills))

    with open(title+"模组.csv", "w", encoding='utf-8') as f:
        f.write('\n'.join(",".join(map(str, module)) for module in modules))
