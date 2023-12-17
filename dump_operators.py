import json
import time
import adb
from operator_data import operator_data
from operators.detect import detect


if __name__ == '__main__':
    # for filename in os.listdir('resources'):
    #     img = cv2.imdecode(np.fromfile("resources/" + filename, dtype=np.uint8),-1)[:, :, :3]
    #     info = detect(img)
    #     print(info)
    infos = []
    last_info = {'name': None}
    last_same_count = 0
    adb.connectTcp(port=65495)
    retry = 0

    while True:
        data = adb.screenshot()
        info = detect(data)
        if (info is None) or (not 'name' in info):
            retry += 1
            if retry > 3:
                break
        elif isinstance(last_info, dict) and info['name'] == last_info['name']:
            last_same_count += 1
            if last_same_count == 3:
                break
        else:
            retry = 0
            last_info = info
            print(info)
            infos.append(info)
            adb.swipe(960, 599, 233, 599, 0.2)
            print("Swipped!", end='\r')
        time.sleep(0.6)
    
    with open("operators.json", "w", encoding='utf8') as f:
        json.dump(infos, f, ensure_ascii=False)

    operator_data.saveAmbiguousNames()
