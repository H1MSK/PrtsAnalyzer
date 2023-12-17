import json
import math
import os
from typing import List
import requests
import re
import html
import editdistance

class OperatorData:
    url=r'https://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88'
    info_div_reg = re.compile(r'<div [^>]+ id="filter-data">.+?</div>')
    data_reg = re.compile(r'data-[^=]+="[^"]*"')

    def __init__(self):
        result = requests.get(OperatorData.url)
        if not result.ok:
            raise IOError()
        matches = OperatorData.info_div_reg.findall(html.unescape(result.content.decode()))
        infos=[]
        for match in matches:
            match = match[1:].replace('></div>', '')
            data: List[str] = OperatorData.data_reg.findall(match)
            info = {}
            for d in data:
                t = d.split('=')
                k, v = t[0], t[1]
                k = k.replace('data-', '')
                v = v[1:-1]
                info[k] = v
            infos.append(info)
        self.infos = {info['cn']: info for info in infos}
        self.ambig_names = {}
        if os.path.exists('ambiguous_names.json'):
            with open('ambiguous_names.json', "r", encoding='utf8') as f:
                self.ambig_names = json.load(f)

    def findOperatorName(self, ambig_name):
        if ambig_name in self.infos.keys():
            return ambig_name, True
        if ambig_name in self.ambig_names.keys():
            return self.ambig_names[ambig_name], True
        min_dis = math.inf
        guess = None
        for name in self.infos.keys():
            d = editdistance.distance(name, ambig_name)
            if d >= min_dis:
                continue
            min_dis = d
            guess = name
        return guess, False

    def setAmbiguousName(self, ambig_name, name):
        assert name in self.infos.keys()
        self.ambig_names[ambig_name] = name
        self.saveAmbiguousNames()

    def saveAmbiguousNames(self):
        with open('ambiguous_names.json', "w", encoding='utf8') as f:
            json.dump(self.ambig_names, f, ensure_ascii=False)

operator_data = OperatorData()

if __name__ == '__main__':
    print(operator_data.infos)
    with open("data.json", "w", encoding='utf8') as f:
        json.dump(operator_data.infos, f, ensure_ascii=False)
