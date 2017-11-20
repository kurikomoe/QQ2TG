#! /usr/bin/env python
################################################################################
#     File Name           :     telegram/commands.py
#     Created By          :     kuriko
#     Creation Date       :     [2017-10-31 21:36]
#     Last Modified       :     [2017-10-31 21:42]
#     Description         :     telegram bot command list
#                   TODO 大概需要一个全局状态列表，应该是由主进程提供
################################################################################
import logging
import socket
import functools
import config
import json


logging.basicConfig(level=config.LEVEL)
logger = logging.getLogger(__name__)

# import configs
CHAT_ID = config.CHAT_ID
USERNAME = config.USERNAME
TOKEN = config.TOKEN
QQBOT_PLUGIN_QQ2TG_LOCK = config.QQBOT_PLUGIN_QQ2TG_LOCK
TGBOT_LOCK = config.TGBOT_LOCK

'''打算实现的commands

屏蔽某个群的消息：屏蔽，显示屏蔽，解除屏蔽
设置特别关注某个id的发言
'''


def cmdformat(text):
    def _doc(func):
        tmp = "命令格式：" + text
        func.__doc__ %= tmp
        func.cmd = tmp
        return func
    return _doc


@cmdformat("/start")
def start(bot, update):
    """开始转发，初始化username以及chat_id
    :ussage: %s

    :bot: Telegram bot
    :update: Telegram update
    :returns: None

    """
    logger.info('start invoked')
    config.store.started = True
    config.USERNAME = update.message.from_user['username']
    config.CHAT_ID = update.message.chat_id
    logger.info(config.USERNAME)
    logger.info(config.CHAT_ID)

    bot.send_message(chat_id=update.message.chat_id,
                     text="已初始化会话 %s: %s" % (config.USERNAME, config.CHAT_ID)
                     )
    return


@cmdformat("/stop")
def stop(bot, update):
    """停止转发，初始化username以及chat_id
    :ussage: %s

    :bot: Telegram bot
    :update: Telegram update
    :returns: None

    """
    logger.info('stop invoked')
    tmp1 = config.USERNAME
    tmp2 = config.CHAT_ID
    config.USERNAME = None
    config.CHAT_ID = None
    config.store.started = False
    bot.send_message(chat_id=update.message.chat_id,
                     text="已结束会话 %s: %s" % (tmp1, tmp2)
                     )
    return


@cmdformat("/msg buddy|group name msg")
def msg(bot, update, args):
    """发送消息
    :ussage: %s

    :bot: Telegram Bot
    :update: Telegram Update
    :returns: None

    """
    logger.info("msg invoked")
    # 获得与QQBOTPLUGIN的通信socket
    s = config.store.s

    # 对于一点都不友好的带 Space 的名字进行解析
    # 不妨用「下划线」表示空格，之后统一替换，岂不美哉
    logger.info("origin: %s" % args)
    args[1] = args[1].replace('_',' ')
    logger.info("replaced: %s" % args)

    ''' data 格式说明
        list[type, name, msg]
            type: group|buddy
            name: name|qq
            msg: msg
    '''
    logger.info(" ".join(args[2:]))
    data = json.dumps([args[0], args[1], " ".join(args[2:])]).encode('utf-8')
    s.sendto(data, QQBOT_PLUGIN_QQ2TG_LOCK)
    return


@cmdformat("/block [group|buddy|group-buddy name|qq]")
def block(bot, update, args, cmdstr=233):
    """屏蔽某个群的消息
    :ussage: %s

    :bot: Telegram bot
    :update: update
    :returns: None

    """
    logger.info('block invoked')
    try:
        if len(args) == 0:
            # TODO 屏蔽列表
            bot.send_message(chat_id=update.message.chat_id,
                             text="当前Block列表为："
                             )
        elif len(args) == 2:
            if args[0] not in ['group', 'buddy', 'group-buddy'] or len(args) != 2:
                raise Exception('ErrorCmd')
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="你已经屏蔽了%s: %s，利用/undo撤销上一个命令" % (args[0], args[1]))
        else:
            raise Exception('ErrorCmd')
    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id,
                         text="错误的命令\n" + block.cmd)
    return


@cmdformat("/unblock [group|buddy|group-buddy name|qq]")
def unblock(bot, update, args):
    """解除屏蔽
    :ussage: %s

    :bot: Telegram Bot
    :update: Telegram Update
    :returns: None

    """
    logger.info('unblock invoked')
    return


@cmdformat("/focus [group|buddy name]")
def focus(bot, update, args):
    """特别关注
    :ussage: %s

    :bot: Telegram Bot
    :update: Telegram Update
    :returns: None

    """
    logger.info('focus invoked')
    tmp = config.store.focus

    if tmp['isFocus']:
        bot.send_message(chat_id=update.message.chat_id,
                         text='你刚才正在focus %s: %s\n现在切换focus %s: %s，\n利用/undo命令可以撤销' % (tmp['type'], tmp['name'], args[0], args[1]))
        tmp['isFocus'] = True
        tmp['type'] = args[0]
        tmp['name'] = args[1]
    else:
        tmp['isFocus'] = True
        tmp['type'] = args[0]
        tmp['name'] = args[1]
        bot.send_message(chat_id=update.message.chat_id,
                         text='你现在focus %s: %s' % (tmp['type'], tmp['name']))
    return


@cmdformat("/unfocus")
def unfocus(bot, update):
    """取消特别关注
    :ussage: %s

    :bot: Telegram Bot
    :update: Telegram Update
    :returns: None

    """
    logger.info('unfocus invoked')
    item = config.store.focus
    if item['isFocus']:
        item['isFocus'] = False
        bot.send_message(chat_id=update.message.chat_id,
                         text='成功unfocus %s: %s' % (item['type'], item['name'])
                         )
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text='你没有focus任何东西哦'
                         )

    return


def test(bot, update):
    """test function

    :bot: TODO
    :update: TODO
    :args: TODO
    :returns: TODO

    """
    s = config.store.s
    logger.info("sending test")
    s.sendto("test".encode('utf-8'), config.QQBOT_PLUGIN_QQ2TG_LOCK)

    return


def main():
    """Main function and used for testing
    :returns: None

    """
    return


if __name__ == "__main__":
    main()
