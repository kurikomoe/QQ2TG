import logging

# 尝试载入用户配置
try:
    import config_user

    LEVEL = config_user.LEVEL

    # Telegram Bot Token
    TOKEN = config_user.TOKEN

    # QQBOT_PLUGIN_QQ2TG Listen Address
    QQBOT_PLUGIN_QQ2TG_LOCK = config_user.QQBOT_PLUGIN_QQ2TG_LOCK

    # QQBOT的监听端口，默认值是8188
    QQBOT_PORT = config_user.QQBOT_PORT

    # QQBOT 的用户配置 -u 参数的
    QQBOT_USER_CONFIG_NAME = config_user.QQBOT_USER_CONFIG_NAME

    # TGBOT Listen Address
    TGBOT_LOCK = config_user.TGBOT_LOCK

    # 静态黑名单 TODO 以后实现动态存取
    BLOCK_LIST = config_user.BLOCK_LIST

    # 用于存储跨模块的全局变量
    USERNAME = config_user.USERNAME
    #非必须项，通过/start命令刷新
    CHAT_ID = None

    class store:
        focus = config_user.store.focus

except Exception as e:
    print(e)
    LEVEL = logging.INFO

    # 用户配置载入失败，使用默认值
    TOKEN = None

    if TOKEN == None:
        print("必须提供BOT TOKEN")
        exit(-1)

    # QQBOT_PLUGIN_QQ2TG Listen Address
    QQBOT_PLUGIN_QQ2TG_LOCK = "/tmp/qq.lock"

    # QQBOT_USER_CONFIG_NAME
    QQBOT_USER_CONFIG_NAME = None

    if QQBOT_USER_CONFIG_NAME == None:
        print("必须提供 QQBOT_USER_CONFIG_NAME ")
        exit(-1)

    # QQBOT的监听端口，默认值是8188
    QQBOT_PORT = 8188

    # TGBOT Listen Address
    TGBOT_LOCK = '/tmp/tg.lock'

    # 静态黑名单 TODO 以后实现动态存取
    BLOCK_LIST = []

    # 用于存储跨模块的全局变量
    # 必须填写，用于判断机器人使用用户
    USERNAME = None
    #非必须项，通过/start命令刷新
    CHAT_ID = None
    if USERNAME == None:
        print("必须提供USERNAME")
        exit(-1)

    class store:
        focus = {
            'isFocus': False,
            'type': '',
            'name': '',
        },
        qqbot = False,

'''
报文格式说明：

    tg -> qq:
        [type, name, msg]

    qq -> tg:
        [type, name, msg, member]

'''
