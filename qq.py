#! /usr/bin/env python
################################################################################
#     File Name           :     qq.py
#     Created By          :     kuriko
#     Creation Date       :     [2017-10-31 21:02]
#     Last Modified       :     [2017-10-31 21:33]
#     Description         :     qq的消息转发模块
#           需要注意的几点：
#           1. onPlug需要开启TGBot进程
#           2. onQQMessage需要给TG发送相应的消息
#           3. onPlug需要开启监听TGBog发来消息的守护进程
################################################################################
import os
import socket
import logging
import config
import threading
import json
import urllib
import string

# Some Configs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QQBOT_PLUGIN_QQ2TG_LOCK = config.QQBOT_PLUGIN_QQ2TG_LOCK
TGBOT_LOCK = config.TGBOT_LOCK


def GetMsgFromTG(bot):
    global s
    while True:
        data, addr = s.recvfrom(65535)
        data = data.decode('utf-8')
        data = json.loads(data)
        logger.info(data)
        ''' data 格式说明
            list[type, name, msg]:
                0 type: group|buddy
                1 name: name|qq
                2 msg: msg
        '''
        #  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #  sock.connect(("localhost", config.QQBOT_PORT))
        #  cmd = "send %s %s %s" % (data[0],data[1], data[2])
        #  sock.send(cmd.encode('utf-8'))
        #  sock.close()
        # 修改为利用 url 发送消息。。因为 socket 发送的方式对于 space 处理有问题
        # 8188 需要读取 qqbot 的配置信息，以后考虑自动启动 qqbot 。
        url = 'http://localhost:{3}/send/{0}/{1}/{2}'.format(data[0],data[1], data[2], config.QQBOT_PORT)
        url = urllib.parse.quote(url, safe = string.printable)
        logger.info("msg in GetMsgFromTG: %s" % urllib.parse.quote(url))
        urllib.request.urlopen(url)

    return


def onPlug(bot):
    """插件启动时候，唤起TGBot，并启动守护进程监听来自TGBot的消息

    :bot: QQBot
    :returns: None

    """
    # Stage 1 启动TGBot
    # 放弃，TGBOT要和QQBOT不相关，仅通过unix socket进行通信

    # Stage 2 启动守护进程
    # 守护进程用于监听来自TGBot的消息，并利用qq命令直接发送消息
    logger.info('Plugin onPlug invoked')
    global s

    # 建立与TGBOT的通讯链接
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        os.unlink(QQBOT_PLUGIN_QQ2TG_LOCK)
    except Exception as e:
        print(e)
    s.bind(QQBOT_PLUGIN_QQ2TG_LOCK)

    # 准备完毕，启动TG消息监听进程
    t = threading.Thread(target=GetMsgFromTG, args=(bot,))
    t.start()
    return


def onQQMessage(bot, contact, member, content):
    """QQ收到消息的回调函数 采用QQ -> TG数据报文格式

    :bot: QQBOt对象，提供List/SendTo/Stop/Restart等接口
    :contact: QContact对象，消息的发送者，具有ctype/qq/uin/nick/mark/card/name等属性
    :member: QContact对象，仅当本消息为群消息或讨论组消息时有效，代表实际发送消息的成员
    :content: Str对象，消息内容
    :returns: None

    """
    global s
    logger.info("Plugin onQQMessage invoked")
    #  if bot.isMe(contact, member):
    #      logger.info("忽略自己的消息")
    #      return
    if member ==None:
        # 为好友发送
        data = [contact.ctype, contact.name, content, None]
    else:
        # 为群组发送
        data = [contact.ctype, contact.name, content, member.name]
    data = json.dumps(data).encode("utf-8")
    s.sendto(data, TGBOT_LOCK)

    return


# 以下为测试用代码
if __name__ == "__main__":
    onPlug()
