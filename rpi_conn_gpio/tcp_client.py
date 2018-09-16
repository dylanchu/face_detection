#!/usr/bin/env python3
# coding: utf-8

import hashlib
import socket
import sys
import time

from Crypto.Cipher import AES  # package is pycrypto
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


class Client(object):
    def __init__(self, server, password):
        self._VERIFICATION_CODE = 'ohh, moon!'
        self.aes = PrpCrypt(password)
        self.server_address, self.server_port = server.split(':')

    def set_verification_code(self, code):
        self._VERIFICATION_CODE = code

    def send_command(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((self.server_address, int(self.server_port)))
        str_to_send = self.aes.encrypt('%s:%s:%s' % (command, int(time.time()), self._VERIFICATION_CODE))
        print(str_to_send)
        s.send(str_to_send)
        buf = []
        while True:
            d = s.recv(1024)
            if d:
                buf.append(d)
            else:
                break
        data = b''.join(buf)
        print(data)
        # s.close()


if __name__ == '__main__':
    '''消息明文用json，包含：{命令，时间，密码}，客户端使用公钥加密，发给server，server用私钥解密。
    server维护一个有效时间戳，初始化为server开始运行-100s，server解密消息后先检查时间戳，
    若消息时间戳≤有效时间戳直接抛弃，(过大是否要检查并抛弃?)
    时间没问题，则用该时间更新有效时间戳，以保证每个消息包只能使用一次'''
    if sys.argv[1] != 'open' and sys.argv[1] != 'close':
        print("usage: /path/to/tcp_client.py open|close")
        raise Exception('unknown command')
    # client = Client('127.0.0.1:8002', 'password')
    client = Client('172.16.0.35:8002', 'password')
    # client = Client('10.42.0.186:8002', 'password')
    client.send_command(sys.argv[1])
