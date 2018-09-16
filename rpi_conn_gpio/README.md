# rpi-conn-gpio

#### 使用说明

共2个文件：`door.py`   `tcp_client.py`

其中door.py需要在树莓派上运行，`tcp_client.py` 作为封装好的通信类置于人脸识别的服务器上

当需要开门时，按如下示例使用即可

```python
#!/usr/bin/env python3
# coding: utf-8
import time

from tcp_client import Client

if __name__ == '__main__':
    '''消息使用aes加密解密，server维护一个有效时间戳，初始化为server开始运行-100s，
    server解密消息后先检查时间戳，若消息时间戳≤有效时间戳直接抛弃，(过大是否要检查并抛弃?)
    时间没问题，则用该时间更新有效时间戳，以保证每个消息包只能使用一次'''
    client = Client('192.168.0.108:8002', 'password')  # password 需和door.py内一致
    # client = Client('127.0.0.1:8002', 'password')
    # client = Client('10.42.0.186:8002', 'password')
    client.send_command('open')    # 返回 ‘ok, opened'
    client.send_command('close')    # 每秒只能发送一次指令，第二次会被丢弃
    time.sleep(1)
    client.send_command('close')    # 返回 'ok, closed'
    time.sleep(1)
    client.send_command('closesss')    # 返回 unknown command
```

