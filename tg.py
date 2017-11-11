#! /usr/bin/env python
################################################################################
#     File Name           :     tg.py
#     Created By          :     kuriko
#     Creation Date       :     [2017-10-31 21:37]
#     Last Modified       :     [2017-10-31 22:04]
#     Description         :     Telegram main function
################################################################################
import os
import logging
import socket
import threading
import json
import re

import telegram
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.filters import InvertedFilter
from telegram.ext.dispatcher import DispatcherHandlerStop

import tgplugin.commands as cmds

import config


# logging settings
logging.basicConfig(level=config.LEVEL)
logger = logging.getLogger(__name__)

# import configs
CHAT_ID = config.CHAT_ID
USERNAME = config.USERNAME
TOKEN = config.TOKEN
QQBOT_PLUGIN_QQ2TG_LOCK = config.QQBOT_PLUGIN_QQ2TG_LOCK
TGBOT_LOCK = config.TGBOT_LOCK

# global variables
config.store.started = False
config.store.s = None
s = None   # 占位方便TagBar显示全局变量


# MESSAGE HANDLERS

# filter: all   rank: -1
def precheck(bot, update):
    """检测权限，防止其他人使用bot

    :bot: Telegram Bot
    :message:  Telegram Update
    :returns: None

    """
    #  logger.info(update.message.from_user)
    if "/start" == update.message.text:
        logger.info("got /start in precheck")
        return
    if config.USERNAME == None or config.CHAT_ID == None:
        bot.send_message(chat_id=update.message.chat_id,
                         text='请使用/start开始聊天'
                         )
        logger.info("没有使用/start初始化config相关参数")
        raise DispatcherHandlerStop
    if update.message.from_user['username'] != config.USERNAME:
        bot.send_message(chat_id=update.message.chat_id,
                         text="目前栗子只喜欢 %s 噢，不能为你服务" % config.username
                         )
        logger.info("不合法的用户")
        raise DispatcherHandlerStop

    return


# filter: reply rank: 0
def quickreply(bot, update):
    """通过reply功能快速答复

    :bot: Telegram Bot
    :update: Telegram Update
    :returns: None

    """
    logger.info("quickreply invoked")
    tmp = config.store.focus
    # 处于focus中，流程转交给chatting处理，即无视reply状态
    if tmp['isFocus']:
        return

    # 从reply message里面提取要发送的对象
    replymsg = update.message.reply_to_message.text
    logger.info(replymsg)
    # 提取reply对象
    # 分为两种情况，buddy或者组聊天？
    # 否定，从简化代码考虑，统一提取形式
    pattern = r'「(.*)：(.*)」'
    name, type = re.match(pattern, replymsg).groups()

    logger.info((name, type))

    cmds.msg(bot, update, [type, name, update.message.text])

    # 结束之后的所有流程处理
    raise DispatcherHandlerStop


# filter: not command  rank: 1
def chatting(bot, update):
    """从tg上得到消息，之后转发给qqbot

    :bot: tg bot
    :update: update
    :returns: None

    """
    global s
    logging.info(config.store)
    tmp = config.store.focus
    # focus 专注于某一个群的聊天
    if tmp['isFocus']:
        logger.info("focusing")
        if update.message.text:
            logger.info(update.message.text)
            bot.send_message(chat_id=update.message.chat_id,
                             text="DEBUG 正在转发信息到%s: %s" % (
                                 tmp['type'], tmp['name'])
                             )
            #  s.sendto(bytes(update.message.text, 'utf-8'),
            #           QQBOT_PLUGIN_QQ2TG_LOCK)
            ''' data 格式说明
                list[type, name, msg]
                type: group|buddy
                name: name|qq
                msg: msg
            '''
            # 考虑focus其实是msg的特例，因此把这个转移到commands里面
        else:
            if update.message.sticker:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="看起来你发送的是一个表情，或许用文字卖个萌会更好一点？"
                                 )
            # TODO 依据smartqq协议，逐步增加其他的处理，不过我觉得没有什么必要
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text='目前SmartQQ协议不支持发送非文字信息')
    else:
        # 通用的一般聊天处理机制，以后添加人工智能相应的部分
        logger.info("unfocusing")
        bot.send_message(chat_id=update.message.chat_id,
                         text="诶，是在和栗子说话么？栗子还没有实现/focus命令呢"
                         )

    return bot


# MAIN FUNCTION

def GetMsgFromQQ(bot):
    """用于接受来自QQBot的消息的伴随线程，并把消息转发到TG
    在这个线程中初始化和QQBot Plugin通信的Socket？
    算了还是把初始化这么重要的socket的任务交给main吧
    :returns: None

    """
    global s
    logger.info("GetMsgFromQQ started")
    while True:
        data, addr = s.recvfrom(65565)
        data = json.loads(data)
        if len(data[2]) == 0:
            data[2] = "SYS: 这里可能有一张图片？？"
        # 如果没有启动转发，则抛弃信息
        if not config.store.started:
            logger.info("没有进行/start命令操作")
            continue
        ''' 接受 qq -> tg  data格式说明
            list[type, name, msg, member]
            type: group|buddy
            name: name|qq
            msg: msg
            member: member
        '''

        # data需要进行解码，重新格式化
        logger.info("recv data: %s" % data)
        #  print(data[0], data[1], data[2], data[3])

        # 最简化检测Block_List
        if True in [i in data[1] for i in config.BLOCK_LIST]:
            continue

        if data[3]:
            # 群消息
            bot.send_message(chat_id=config.CHAT_ID,
                             text="「{1}：{0}」{3}：\n\t{2}".format(
                                 data[0], data[1], data[2], data[3]),
                             )
        else:
            # buddy 消息
            bot.send_message(chat_id=config.CHAT_ID,
                             text="「{1}：{0}」：{2}".format(
                                 data[0], data[1], data[2], data[3]),
                             )
    return


def main():
    """Main Function
    :returns: None

    """
    global s
    try:
        logger.info("prog started")

        # 初始化对QQBOT的Unix Socket链接
        # 转发消息到QQBot 考虑用Unix Socket进行通讯？还是用tcp？
        s = config.store.s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            os.unlink(TGBOT_LOCK)
        except Exception as e:
            print(e)
        s.bind(TGBOT_LOCK)
        logger.info("connect to qqbot established")

        # 新建Bot类型，直接转发消息
        bot = telegram.Bot(token=TOKEN)

        # Socket初始化完成，开启监听来自QQPlugin消息的线程
        t = threading.Thread(target=GetMsgFromQQ, args=(bot,))
        t.start()

        # 初始化Updater
        updater = Updater(token=TOKEN)
        dispatcher = updater.dispatcher

        # 消息处理机制
        precheckHandle = MessageHandler(Filters.all, precheck)
        replyHandle = MessageHandler(Filters.reply, quickreply)
        chattingHandle = MessageHandler(
            InvertedFilter(Filters.command), chatting)

        dispatcher.add_handler(precheckHandle, -1)
        dispatcher.add_handler(replyHandle, 0)
        dispatcher.add_handler(chattingHandle, 1)

        # 命令处理机制
        startHandle = CommandHandler('start', cmds.start)
        stopHandle = CommandHandler('stop', cmds.stop)
        msgHandle = CommandHandler('msg', cmds.msg, pass_args=True)
        blockHandle = CommandHandler('block', cmds.block, pass_args=True)
        focusHandle = CommandHandler('focus', cmds.focus, pass_args=True)
        unfocusHandle = CommandHandler('unfocus', cmds.unfocus)
        testHandle = CommandHandler('test', cmds.test)

        dispatcher.add_handler(startHandle)
        dispatcher.add_handler(stopHandle)
        dispatcher.add_handler(msgHandle)
        dispatcher.add_handler(blockHandle)
        dispatcher.add_handler(focusHandle)
        dispatcher.add_handler(unfocusHandle)
        dispatcher.add_handler(testHandle)

        logger.info('start_polling')
        updater.start_polling()
    except KeyboardInterrupt as e:
        print("closing")
    return


if __name__ == "__main__":
    main()
