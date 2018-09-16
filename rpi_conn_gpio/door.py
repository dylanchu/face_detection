#!/usr/bin/env python3
# coding: utf-8

import RPi.GPIO as GPIO
import hashlib
import socket
import time
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class PrpCrypt(object):
    def __init__(self, password):
        self.key = self.md5sum(password, 'just a salt')[:16]   # AES key must 16/24/32 (AES-128/192/256) bytes
        self.mode = AES.MODE_CBC
        self.iv = self.md5sum(password, 'just a salt')[4:20]   # any 16 bytes you like

    def encrypt(self, message):
        # 如果text不是16的倍数，补足为16的倍数 - 加密文本text必须为16的倍数！
        count = 16 - len(message) % 16
        if count != 0:
            message = ''.join((message, '\0' * count))
        aes = AES.new(self.key, self.mode, self.iv)
        cipher = aes.encrypt(message)
        # AES加密得到的字符串不一定是ascii字符集的，这里把加密后的字符串转化为16进制字符串，方便输出到终端或保存
        return b2a_hex(cipher)

    def decrypt(self, cipher):
        aes = AES.new(self.key, self.mode, self.iv)
        message = aes.decrypt(a2b_hex(cipher)).decode()
        # decode()后尾部仍可能有补足的空字符，用strip()去掉
        return message.rstrip('\0')

    @classmethod
    def md5sum(cls, message, salt):
        md5 = hashlib.md5(salt.encode('utf-8'))
        md5.update(message.encode('utf-8'))
        return md5.hexdigest()


class Server(object):
    def __init__(self, bind_on, password, timestamp):
        self._VERIFICATION_CODE = 'ohh, moon!'
        self._DEBUG = False
        self.aes = PrpCrypt(password)
        self.min_timestamp = timestamp
        self.bind_address, self.bind_port = bind_on.split(':')

    def set_verification_code(self, code):
        self._VERIFICATION_CODE = code

    def enable_debug(self):
        self._DEBUG = True

    def disable_debug(self):
        self._DEBUG = False

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.bind_address, int(self.bind_port)))
        s.listen()
        while True:    # maybe multi threads is needed to avoid attack (that try to keep server busy waiting)
            sock, _ = s.accept()
            sock.settimeout(3)
            try:
                buf = sock.recv(1024)    # timeout if client don't send message
                # print(buf)
                command, timestamp, code = (self.aes.decrypt(buf)).split(':')
                if self._DEBUG:
                    print(command, timestamp, code)
                if code == self._VERIFICATION_CODE and int(timestamp) > self.min_timestamp:
                    self.min_timestamp = int(timestamp)
                    if command == 'open':
                        sock.send(b'ok, opened')
                        sock.close()
                        door('open')
                    elif command == 'close':
                        sock.send(b'ok, closed')
                        sock.close()
                        door('close')
                    else:
                        sock.send(b'unknown command')
                else:
                    sock.send(b'damn')
                    if self._DEBUG:
                        sock.send(b" Please check VERIFICATION_CODE and don't send twice in one second")
            except Exception as e:
                if self._DEBUG:
                    sock.send(bytes(e.__str__().encode()))
            finally:
                sock.close()


def door(command):
    if command == 'open':
        GPIO.output(21, True)
        time.sleep(1)
        GPIO.output(21, False)
    elif command == 'close':
        for _ in (0,1):
            GPIO.output(21, True)
            time.sleep(0.5)
            GPIO.output(21, False)
            time.sleep(0.5)


if __name__ == '__main__':
    min_timestamp = int(time.time()) - 100
    server = Server('0.0.0.0:8002', 'password', min_timestamp)
    server.enable_debug()
    GPIO.setmode(GPIO.BCM)
    try:
        GPIO.setup(21, GPIO.OUT)
        server.run()
    finally:
        GPIO.cleanup()
