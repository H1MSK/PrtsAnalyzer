import json
import logging
import math
import os
from typing import List
import requests
import re
import html
import editdistance

_logger = logging.getLogger("OperatorData")
class OperatorData:
    url=r'https://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88'
    info_div_reg = re.compile(r'(<div( data-[a-z_]+="[^"]*")+>.+?</div>)')
    data_reg = re.compile(r'data-[^=]+="[^"]*"')

    def __init__(self):
        _logger.info("Downloading data from PRTS.wiki...")
        result = requests.get(OperatorData.url)
        if not result.ok:
            raise IOError()
        _logger.info("Parsing data...")
        infos=[]
        match_iter = OperatorData.info_div_reg.finditer(html.unescape(result.content.decode()))
        for match in match_iter:
            dom = match[0]
            data: List[str] = OperatorData.data_reg.finditer(dom)
            info = {}
            for d in data:
                t = d[0].split('=')
                k, v = t[0], t[1]
                k = k.replace('data-', '')
                v = v[1:-1]
                if len(v) == 0:
                    continue
                info[k] = v
            self._post_process_info(info)
            infos.append(info)
        self.infos = {info['zh']: info for info in infos}
        self.ambig_names = {}
        if os.path.exists('ambiguous_names.json'):
            with open('ambiguous_names.json', "r", encoding='utf8') as f:
                self.ambig_names = json.load(f)
        _logger.info("Done.")

    def _post_process_info(self, info):
        if "tag" in info.keys():
            info["tag"] = info["tag"].split(" ")
        if "obtain_method" in info.keys():
            info["obtain_method"] = info["obtain_method"].split(", ")

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
