import logging
logging.basicConfig(level=logging.INFO)


from argparse import ArgumentParser
import json
from sys import argv
import time
import adb
from operator_data import operator_data
from operators.detect import detect


def parse():
    parser = ArgumentParser()
    parser.add_argument("port")
    return parser.parse_args(argv[1:])


def dump_operators():
    # for filename in os.listdir('resources'):
    #     img = cv2.imdecode(np.fromfile("resources/" + filename, dtype=np.uint8),-1)[:, :, :3]
    #     info = detect(img)
    #     print(info)
    logger = logging.getLogger("main")
    args = parse()
    infos = []
    last_info = {"name": None}
    last_same_count = 0
    logger.info("Connecting via adb...")
    adb.connectTcp(port=args.port)
    retry = 0

    logger.info("Parsing...")
    try:
        while True:
            data = adb.screenshot()
            info = detect(data)
            if (info is None) or (not "name" in info):
                retry += 1
                if retry > 3:
                    break
            elif isinstance(last_info, dict) and info["name"] == last_info["name"]:
                last_same_count += 1
                if last_same_count == 3:
                    break
            else:
                retry = 0
                last_info = info
                infos.append(info)
                logger.info(f"Parsed info for {info['name']}")
                adb.swipe(960, 599, 233, 599, 0.2)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected. Saving info...")
        pass

    try:
        with open("operators.json", "r", encoding="utf-8") as f:
            old_infos = json.load(f)
    except FileNotFoundError:
        old_infos = []

    flushed_names = [x["name"] for x in infos]
    logger.info("Updated info for: " + ", ".join(flushed_names))
    for entry in old_infos:
        if entry["name"] not in flushed_names:
            infos.append(entry)

    with open("operators.json", "w", encoding="utf-8") as f:
        json.dump(infos, f, ensure_ascii=False)

    operator_data.saveAmbiguousNames()
    logger.info("Done!")

if __name__ == "__main__":
    dump_operators()
