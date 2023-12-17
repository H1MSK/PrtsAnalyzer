import os
import cv2
import numpy as np
from adb_shell.adb_device import AdbDevice, AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen

_device:AdbDevice = None

def _loadRSA():
    adbkey = 'config/adbkey'
    if not os.path.exists(adbkey):
        os.makedirs(os.path.dirname(adbkey), exist_ok=True)
        keygen(adbkey)
    with open(adbkey) as f:
        priv = f.read()
    with open(adbkey + '.pub') as f:
        pub = f.read()
    signer = PythonRSASigner(pub, priv)
    return [signer]

def connectTcp(host='localhost', port=5555):
    global _device
    _device = AdbDeviceTcp(host, port)
    _device.connect(rsa_keys=_loadRSA())
    assert _device.available

def connectUsb(serial=None):
    global _device
    _device = AdbDeviceUsb(serial)
    _device.connect(rsa_keys=_loadRSA())
    assert _device.available

def screenshot():
    result = _device.shell("screencap -p", decode=False)
    arr = np.asarray(bytearray(result), dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def swipe(start_x, start_y, stop_x, stop_y, duration = 0.5):
    _device.shell(f"input swipe {start_x} {start_y} {stop_x} {stop_y} {int(duration*1000)}")

def tap(x, y):
    _device.shell(f"input tap {x} {y}")