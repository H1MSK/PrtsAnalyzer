import re
import time
from typing import Any, Callable
from cnocr import CnOcr
from cnstd import CnStd
import numpy as np
import logging
import cv2
from operator_data import operator_data

_std = CnStd()

_logger = logging.getLogger("OperatorAnalyzer")

_all_ocr = CnOcr(rec_model_name='densenet_lite_136-gru')
_num_ocr = CnOcr(rec_model_name='en_PP-OCRv3', det_model_name='en_PP-OCRv3_det')
def _ocrText(cropped: np.ndarray):
    result = _all_ocr.ocr_for_single_line(cropped)
    _logger.debug(result)
    return result['text']

def _ocrAndConvert(cropped: np.ndarray, func: Callable[[str], Any]):
    text = _ocrText(cropped)
    return func(text)

def _ocrAndConvertToNumber(cropped: np.ndarray):
    def converter(text: str):
        exp = re.compile(r"\d+")
        x = exp.findall(text.replace('O', '0').replace('Q', '0'))
        if len(x) > 1:
            _logger.error(f"\"{text}\" contains more than 1 number: {x}")
            raise ValueError
        elif len(x) == 0:
            _logger.error(f"\"{text}\" does not contain number")
            raise ValueError
        return int(x[0])
    result = _num_ocr.ocr_for_single_line(cropped)
    _logger.debug(result)
    idx = converter(result['text'])
    _logger.debug(f"index = {idx}")
    return idx

def _ocrAndLookup(cropped: np.ndarray, list: list):
    def lookup(text):
        idx = list.index(text)
        if idx == -1:
            _logger.error(f'Text "{text}" is not found in list {list}')
            raise IndexError
        return idx
    idx = _ocrAndConvert(cropped, lookup)
    _logger.debug(f"index = {idx}")
    return idx

_name_fix = {
    "兴恩纳": "玛恩纳",
    "北影草": "焰影苇草",
    "假日威龙红": "假日威龙陈",
    "养落": "暮落"
}
def _ocrAndMap(cropped: np.ndarray, dict: dict, keepIfNotFound: bool=False):
    def mapping(text):
        try:
            return dict[text]
        except KeyError as e:
            if keepIfNotFound:
                return text
            raise e
    value = _ocrAndConvert(cropped, mapping)
    _logger.debug(f"mapped = {value}")
    return value

def _masteryDetect(cropped: np.ndarray):
    # Top
    point1 = cropped[7:8, 14:15, :].sum()
    # Left bottom
    point3 = cropped[17:18, 8:9, :].sum()
    # Right bottom
    point2 = cropped[17:18, 20:21, :].sum()

    return (0 if point1 < 500 else 
            1 if point2 < 500 else 
            2 if point3 < 500 else
            3)

def _eliteDetect(cropped: np.ndarray):
    point1 = cropped[26, 15, :].sum()
    point2 = cropped[8, 15, :].sum()
    return (2 if point2 > 500 else 
            1 if point1 > 500 else
            0)

_whiteColor = np.array([255, 255, 255], dtype=np.uint8)
_lowerThanWhite = np.array([252, 252, 252], dtype=np.uint8)
def _ocrName(cropped: np.ndarray):
    preprocessed = cv2.inRange(cropped, _lowerThanWhite, _whiteColor)
    preprocessed[:-1, :] = cv2.max(preprocessed[:-1, :], preprocessed[1:, :])
    preprocessed[2:, :] = cv2.max(preprocessed[2:, :], preprocessed[:-2, :])
    cv2.imshow("Name", preprocessed)
    cv2.waitKey(1)
    return _ocrText(preprocessed)

# Name: (x, y, w, h)
_positions = {
    "name": ((25, 736, 590, 133), _ocrName),
    "level": ((1331, 166, 132, 90), _ocrAndConvertToNumber),
    "hp": ((63, 413, 153, 34), _ocrAndConvertToNumber),
    "atk": ((63, 458, 153, 34), _ocrAndConvertToNumber),
    "def": ((63, 503, 153, 34), _ocrAndConvertToNumber),
    "res": ((63, 548, 153, 34), _ocrAndConvertToNumber),
    "dt": ((264, 413, 153, 34), _ocrText),
    "dc": ((264, 458, 153, 34), _ocrAndConvertToNumber),
    "block": ((264, 503, 153, 34), _ocrAndConvertToNumber),
    "cd": ((264, 548, 153, 34), _ocrText),
    "trust": ((509, 602, 94, 30), _ocrAndConvertToNumber),
    "skill_level": ((1822, 541, 24, 30), _ocrAndConvertToNumber),
    "elite_level": ((1371, 380, 33, 53), _eliteDetect),
    "skill_mastery_1": ((1327, 504, 30, 26), _masteryDetect),
    "skill_mastery_2": ((1459, 504, 30, 26), _masteryDetect),
    "skill_mastery_3": ((1591, 504, 30, 26), _masteryDetect),
}

def _overlapped(region, box):
    p1 = box[0]
    p2 = box[1]
    p3 = box[2]
    p4 = box[3]
    def _inside(p):
        a = (p2[0]-p1[0])*(p[1]-p1[1])-(p2[1]-p1[1])*(p[0]-p1[0])
        b = (p3[0]-p2[0])*(p[1]-p2[1])-(p3[1]-p2[1])*(p[0]-p2[0])
        c = (p4[0]-p3[0])*(p[1]-p3[1])-(p4[1]-p3[1])*(p[0]-p3[0])
        d = (p1[0]-p4[0])*(p[1]-p4[1])-(p1[1]-p4[1])*(p[0]-p4[0])
        return (a>0 and b>0 and c>0 and d>0) or (a<0 and b<0 and c<0 and d<0)
    return (_inside((region[0], region[1])) or
            _inside((region[0] + region[2], region[1])) or
            _inside((region[0] + region[2], region[1] + region[3])) or
            _inside((region[0], region[1] + region[3])))

def _box_and(original_box, rect):
    if not _overlapped(rect, original_box):
        return None
    regulated = (min(original_box[0, 0], original_box[3, 0]), # left most
                 min(original_box[0, 1], original_box[1, 1]), # top most
                 max(original_box[1, 0], original_box[2, 0]), # right most
                 max(original_box[2, 1], original_box[3, 1])) # bottom most
    
    l = int(max(regulated[0], rect[0]))
    u = int(max(regulated[1], rect[1]))
    r = int(min(regulated[2], rect[0] + rect[2]))
    d = int(min(regulated[3], rect[1] + rect[3]))
    if r - l < 0.7*rect[2] or d - u < 0.7*rect[3]:
        return None
    return (l, u, r - l, d - u)

def detect(img: np.ndarray):
    img_boxes = {k: v[0] for k, v in _positions.items()}
    img_sizes = {k: 0 for k in _positions.keys()}
    result = _std.detect(img)
    for text_box in result['detected_texts']:
        for k, v in _positions.items():
            regulated_box = _box_and(text_box['box'], v[0])
            if regulated_box:
                size = regulated_box[2] * regulated_box[3]
                if img_sizes.setdefault(k, size) <= size:
                    box = regulated_box
                    img_boxes[k] = box
                    _logger.debug(f"Update box of key {k} to {box}(size={size})")

    info = {}
    for k, v in _positions.items():
        count = 0
        while True:
            try:
                box = img_boxes[k]
                cropped = img[box[1]:box[1]+box[3], box[0]:box[0] + box[2], :]
                info[k] = v[1](cropped, *v[2:])
                break
            except Exception as e:
                count += 1
                box = _positions[k][0]
                if count >= 1:
                    _logger.error(f"Error while trying to parse {k}(box={box})", stack_info=False)
                    break

    try:
        actual_name, trusted = operator_data.findOperatorName(info['name'])
    except KeyError as e:
        _logger.error(f"Info has no name: {info}")
        raise e
    if not trusted or actual_name == None:
        x = input(f"Detected {info['name']}, Guessed {actual_name}.\nLeave empty if it's correct, input actual name if it is not, or input \"r\" to retry:")
        if "r" == x:
            return None
        if len(x):
            actual_name = x
        if "y" == input("Should I remember this ambiguous name? (y/[n]):").lower():
            operator_data.setAmbiguousName(info['name'], actual_name)
    info["name"] = actual_name
    return info

if __name__ == '__main__':
    img = cv2.imdecode(np.fromfile('resources/屏幕截图 2023-04-22 113258.png',dtype=np.uint8), cv2.IMREAD_COLOR)
    info = detect(img)
    print(info)
