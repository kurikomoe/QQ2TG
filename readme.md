# 一句话概述

Linux下不管是Wine、Crossover还是虚拟机跑QQ都太麻烦了，因此写了个东西把TG和QQ连接到了一起。于是可以在TG上愉快的聊QQ了。

# 具体描述

为QQBot写了一个插件（不妨叫做「QQBOT_PLUGIN」），为Telegram写了一个Bot（不妨叫做「TGBOT」），通过（现阶段）Unix Socket通信，基本工作原理就是

QQBot <--> QQBOT_PLUGIN <--(Unix Socket)--> TGBOT <--> Telegram

这样子进行通信。把QQ消息转发到TG，把发送给TGBOT的消息转发到QQ。

## 要点

不同于关联QQ-TG群组的组件，此BOT为个人独享，直接作为TG和QQ的中间层，把一个BOT当作QQ信息的终端，以此来接受和发送信息。

## 优点

- 不用忍受wine系列qq的高cpu占用，不用忍受开虚拟机的费电。所有的东西都整合在TG里面，方便又开心。

- 不怕别人召回了？？

- TG可以和系统内置的Notification结合，实时提示新的信息，以及内容。

## 缺点

- 由于WebQQ本身协议的问题，因此只能接受发送文字信息（考虑到大部分时间图片，表情包都是卖萌的。。也就无所谓了，不过以后可以考虑利用酷Q实现）

- 对QQBot的源代码理解不是很深入，因此目前是通过插件的形式导入进去，以后希望能把QQBot的代码内置到本项目里面，就不用分别启动了。

- 掉线重连机制目前还没有实现

- QQ消息全部整合到BOT中，容易看走眼？？（有几万个群的dalao估计会被刷爆的）

- 目前没有过滤自己发送的信息，因为weibqq存在发送失败的可能性，因此读取自己的信息并显示出来有利于判断消息是否成功发送。

# 安装

## 需要安装的组件

- **环境：python3**

- [QQBot](https://github.com/pandolia/qqbot)：QQBot: A conversation robot base on Tencent's SmartQQ

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)：We have made you a wrapper you can't refuse [https://python-telegram-bot.org](https://python-telegram-bot.org)

## config.py

配置文件，可以建立config_user.py 修改相应的配置

## qq.py

作为QQBOT的Plugin载入，同时确保qq.py可以import到config.py

建议把qq.py config.py config_user.py 直接ln -s 「软链接」到~/.qqbot-tmp/plugins目录下

## tg.py

telegram bot，直接
```
python3 tg.py
```
就可以启动

# 功能描述

## 基础聊天功能

通过/start开启和机器人的聊天（为了刷新username和chat_id）
```
基本发送消息命令
/msg group|buddy|discuss username|qq message
```

## 快速回复功能

因为每次打/msg balabala 实在是太麻烦了，于是利用TG的reply功能，可以快速回复消息

具体做法：

- 右键含有「name： type」的这种消息，选择reply

- 直接输入要回复的信息，之后TGBOT会自动提取出要回复联系人的类型和名字，直接回复。

# 鸣谢

- [pandolia/qqbot](https://github.com/pandolia/qqbot) -- 逆向smartqq协议真不是人干的事儿，感谢作者的轮子

- [python-telegram-bot/python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) -- 如果用raw http请求写tg bot，我大概会死吧。
