import os
import math
import json
import base64
import string
import shutil
import subprocess

from pathlib import Path
from typing import Generator
from Crypto.Cipher import AES

# The pipeline class for encoding and decoding the 'encrypted save' or the 'decrypted json'
class Interpreter:
    def __init__(self) -> None:
        self.header = [0, 1, 0, 0, 0, 255, 255, 255, 255, 1, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0]
        self.key = b'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    @staticmethod
    def _padding(text:str | bytes, block:int=16) -> bytes:
        text = text if type(text) == bytes else text.encode()
        amount = (block - len(text) % block)
        return text + bytes([amount]) * amount

    @staticmethod
    def _getLength(input:str | bytes) -> bytes:
        lenBin = format(len(input), 'b')
        lenBinReverse = lenBin[::-1]
        dataLen = math.ceil(len(lenBinReverse) / 7.0)
        data = list(range(dataLen))

        for i in range(dataLen - 1):
            data[i] = lenBinReverse[i * 7: (i + 1) * 7] + "1"

        data[-1] = lenBinReverse[(len(data) - 1) * 7: len(lenBinReverse)]
        output = list(range(dataLen))

        for i in range(len(output)):
            output[i] = int(data[i][: : -1], 2)

        return bytes(output)

    def encode(self, text:str) -> bytes:

        def encrypt(txt):
            return self.cipher.encrypt(txt)

        content = json.dumps(text, separators=(',', ':'))
        content = self._padding(content, 16)
        encrypted_content = encrypt(content)
        encrypted_content = base64.encodebytes(encrypted_content)
        encrypted_content = encrypted_content.replace(bytes([13]), b'')
        encrypted_content = encrypted_content.replace(bytes([10]), b'')
        final_content = bytearray()
        final_content.extend(self.header)
        final_content.extend(self._getLength(encrypted_content))
        final_content.extend(encrypted_content)
        final_content.extend([11])

        print(Menu.ok("> Save Encoded."))
        return bytes(final_content)

    def decode(self, secret:bytes) -> str:

        def decrypt(sec):
            return self.cipher.decrypt(sec)

        secret = base64.decodebytes(secret)
        plain = decrypt(secret)
        plain = plain[: -plain[-1]]

        print(Menu.ok("> Save Decoded."))
        return json.loads(plain)

# The pipline class for backupping and fetching save file
class Handler:
    def __init__(self, target:str) -> None:
        self.target = target

    def search(self, mode:str='default') -> Generator:
        if mode == 'auto':
            drives = []
            for drive in string.ascii_uppercase:
                if os.path.exists(f"{drive}:\\"):
                    drives.append(f"{drive}:\\")

            for drive in drives:
                for root, _, files in os.walk(str(drive)):
                    if self.target in files:
                        yield os.path.join(root, self.target)
                    else:
                        pass

            raise FileNotFoundError

        if mode == 'default':
            username = str(subprocess.run(['echo', '%username%'], capture_output=True, text=True, shell=True).stdout).strip()
            path = f"C:\\Users\\{username}\\AppData\\LocalLow\\Team Cherry\\Hollow Knight\\" + self.target

            if os.path.exists(path):
                yield path
            else:
                raise FileNotFoundError

        if mode == 'spesify':
            if os.path.exists(self.target) and os.path.isfile(self.target):
                yield self.target
            else:
                raise FileNotFoundError

    def backup(self, src:str, back:str) -> None:
        if os.path.exists(src):
            shutil.copy(src, back)
            print(Menu.ok(f"> Save backed up at {Path.absolute(back)}."))
        else:
            raise FileNotFoundError

# The global menu to be printed
class Menu:

    @staticmethod
    def warn(text:str) -> str:
        return "\033[91m" + text + '\033[0m'

    @staticmethod
    def ok(text:str) -> str:
        return "\033[92m" + text + '\033[0m'

    @staticmethod
    def ask(text:str) -> str:
        return "\033[93m" + text + '\033[0m'

    @staticmethod
    def log(text:str) -> str:
        return "\033[94m" + text + '\033[0m'

    @staticmethod
    def boolCheckbox() -> bool:
        while True:
            try:
                choice = str(input("> ")).lower()[0]
            except:
                print(Menu.warn("> Please enter Y/n"))
                continue
            else:
                if choice == 'y' or choice == 'n':
                    return True if choice == 'y' else False
                else:
                    print(Menu.warn("> Please enter Y/n"))
                    continue

    @staticmethod
    def printReplace(path:str) -> str:
        print(Menu.ok(f"> Save replaced at {path}."))

# The class for performing save modification
class Modifier:
    def __init__(self, raw):
        self.data = raw

    def getData(self):
        return self.data

    def showDetails(self):
        data_str = json.dumps(self.data, indent=4)

        print(f"\t· Save: ")
        print(Menu.log("\t" + data_str.replace("\n", "\n\t")))

    def resurrectInnGhost(self):
        res_list = []
        for idx, item in enumerate(self.data["sceneData"]["persistentBoolItems"]):
            if "ghost" in item["id"].lower():
                if self.data["sceneData"]["persistentBoolItems"][idx]["activated"]:
                    res_list.append(item["id"])
                    self.data["sceneData"]["persistentBoolItems"][idx]["activated"] = False

        if res_list:
            print(f"\t· Ghost: {Menu.log(res_list[0])} Resurrected")
            for idx in range(1, len(res_list)):
                print(f"\t         {Menu.log(res_list[idx])} Resurrected")

    def modifyGeo(self, num=100000):
        prev = self.data["playerData"]["geo"]
        self.data["playerData"]["geo"] = num

        print(f"\t· Geo: {Menu.log(prev)} -> {Menu.log(num)}")

    def modifySlots(self, num=24):
        prev = self.data["playerData"]["charmSlots"]
        self.data["playerData"]["charmSlots"] = num

        print(f"\t· CharmSlot: {Menu.log(prev)} -> {Menu.log(num)}")

    def modifyWhiteHealth(self, num=20):
        prev = self.data["playerData"]["maxHealth"]
        self.data["playerData"]["health"] = num
        self.data["playerData"]["maxHealth"] = num
        self.data["playerData"]["maxHealthBase"] = num
        self.data["playerData"]["MPCharge"] = self.data["playerData"]["maxMP"]

        print(f"\t· WhiteHealth: {Menu.log(prev)} -> {Menu.log(num)}")

    def modifyBlueHealth(self, num=10):
        prev = self.data["playerData"]["healthBlue"]
        self.data["playerData"]["healthBlue"] = num

        print(f"\t· BlueHealth: {Menu.log(prev)} -> {Menu.log(num)}")

    def reset(self, backup):
        with open(backup, 'rb') as f:
            content = f.read()
            f.close()

        itp = Interpreter()
        self.data = itp.decode(content)
        print(f"\t· Save: " + Menu.log("Reset"))

