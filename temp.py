import time
import adb

if __name__ == '__main__':
    adb.connectUsb()
    print(adb._device)

    count = 0
    while(True):
        count += 1
        adb.tap(1069, 706)
        print(f"Count={count:5d}  0", end='\r')
        time.sleep(0.5)
        adb.tap(1292, 702)
        print(f"Count={count:5d}  1", end='\r')
        for i in range(36):
            print(f"Count={count:5d} {i+2:2d}", end='\r')
            time.sleep(1)
