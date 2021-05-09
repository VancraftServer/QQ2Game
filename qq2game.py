"""An MCDR plugin that synchronizes QQ messages to the game.

Copyright © 2021 Vancraft Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import re

import requests
from flask import Flask, request
from mcdreforged.api.command import Literal, Integer
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rcon import RconConnection
from mcdreforged.api.types import ServerInterface, Info

# 请在此处配置具体参数
CONFIGURES = {
    # Rcon连接
    'RCON_CONN':
        RconConnection(address='127.0.0.1', port=25575, password='12345678'),
    # 群号
    'GROUP_ID':
        12345678,
    # QQ到游戏命令前缀
    'Q2G_PREFIX':
        '!!q2g',
    # 游戏到QQ命令前缀
    'G2Q_PREFIX':
        '!!g2q',
    # QQ到游戏默认状态
    'Q2G_STATUS':
        1,
    # 游戏到QQ命令前缀
    'G2Q_STATUS':
        0,
}

PLUGIN_METADATA = {
    'id': 'q2g',
    'version': '1.1.2',
    'name': 'QQ2Game',
    'description': '群消息与游戏同步插件',
    'author': 'ShootKing233',
    'link': 'https://github.com/VancraftServer/QQ2Game/',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
    },
}

RCON_CONN = CONFIGURES['RCON_CONN']
GROUP_ID = CONFIGURES['GROUP_ID']
Q2G_PREFIX = CONFIGURES['Q2G_PREFIX']
G2Q_PREFIX = CONFIGURES['G2Q_PREFIX']
Q2G_STATUS = CONFIGURES['Q2G_STATUS']
G2Q_STATUS = CONFIGURES['G2Q_STATUS']

# 机器人监听服务器
BOT_SERVER = Flask(__name__)


def get_status(target):
    """获取目标功能状态
    Args:
        target: 要获取功能的名称（字符串）
    Returns:
        1或0（目标当前的状态）
    Raises:
        TypeError: 当参数类型不合法时
        ValueError: 当目标不存在或目标的状态值不合法时
    """
    if not isinstance(target, str):
        raise TypeError
    if target not in ['q2g', 'g2q']:
        raise ValueError
    if target == 'q2g':
        if Q2G_STATUS not in (1, 0):
            raise ValueError
        return Q2G_STATUS
    if target == 'g2q':
        if G2Q_STATUS not in (1, 0):
            raise ValueError
        return G2Q_STATUS
    return -1


def set_status(target, status):
    """设置目标功能的状态
    Args:
        target: 要获取功能的名称（字符串）
        status: 要设置的状态（1或0）
    Returns:
        1或0（目标被设置的状态）
    Raises:
        TypeError: 当参数类型不合法时
        ValueError: 当目标不存在或所要设置的状态值不合法时
    """
    if not isinstance(target, str) and not isinstance(status, int):
        raise TypeError
    if target not in ['q2g', 'g2q'] and status not in [0, 1]:
        raise ValueError
    if target == 'q2g':
        global Q2G_STATUS
        Q2G_STATUS = status
        return Q2G_STATUS
    if target == 'g2q':
        global G2Q_STATUS
        G2Q_STATUS = status
        return G2Q_STATUS
    return -1


def on_unload(server: ServerInterface):
    server.logger.info('QQ2Game正在卸载')
    requests.post('http://127.0.0.1:5701/plugin/stop')
    server.logger.info('QQ2Game卸载完成')


def on_load(server: ServerInterface, _prev):
    """插件初始化函数"""
    server.logger.info('QQ2Game正在加载')

    # 注册帮助信息
    server.register_help_message(
        Q2G_PREFIX, '''{0} status -- 查看当前QQ->游戏功能是否打开
        {1} status <0/1> -- 打开/关闭QQ->游戏功能(0:关闭/1:打开)'''.format(
            Q2G_PREFIX, Q2G_PREFIX))
    server.register_help_message(
        G2Q_PREFIX, '''{0} status -- 查看当前QQ<-游戏功能是否打开
        {1} status <0/1> -- 打开/关闭QQ<-游戏功能(0:关闭/1:打开)'''.format(
            G2Q_PREFIX, G2Q_PREFIX))

    # 注册命令
    server.register_command(
        Literal(Q2G_PREFIX).then(
            Literal('status').runs(
                lambda src: src.reply('当前QQ->游戏功能处于{0}状态'.format(
                    '开启' if get_status('q2g') == 1 else '关闭'))).then(
                Integer('statusId').in_range(0, 1).runs(lambda src, ctx: src.reply(
                    '已将QQ->游戏功能设置为{0}状态'.format('开启' if set_status('q2g', ctx['statusId']) == 1 else '关闭'))))))
    server.register_command(
        Literal(G2Q_PREFIX).then(
            Literal('status').runs(
                lambda src: src.reply('当前QQ<-游戏功能处于{0}状态'.format(
                    '开启' if get_status('g2q') == 1 else '关闭'))).then(
                Integer('statusId').in_range(0, 1).runs(lambda src, ctx: src.reply(
                    '已将QQ<-游戏功能设置为{0}状态'.format('开启' if set_status('g2q', ctx['statusId']) == 1 else '关闭'))))))

    server.register_command(Literal(Q2G_PREFIX).runs(
        lambda src: src.reply('请使用!!{0} status或!!{0} status <0/1>'.format(Q2G_PREFIX, Q2G_PREFIX))))
    server.register_command(Literal(G2Q_PREFIX).runs(
        lambda src: src.reply('请使用!!{0} status或!!{0} status <0/1>'.format(G2Q_PREFIX, G2Q_PREFIX))))

    # 创建机器人监听线程
    run_bot_server()

    server.logger.info('QQ2Game加载完成')


def send_message(server: ServerInterface, info: Info):
    """QQ消息发送函数"""
    # 判断是否发送消息以及消息是否为玩家或控制台发出
    if (G2Q_STATUS == 1 and not info.content.startswith('!!') and
        (info.is_player or info.is_from_console)) or (
            G2Q_STATUS == 0 and info.content.startswith('!!send ') and
            (info.is_player or info.is_from_console)):

        # 发送者ID（若为控制台则为CONSOLE）
        sender = '<{0}> '.format(info.player if info.is_player else 'CONSOLE')

        # 若为手动发送则截取发送内容
        if info.content.startswith('!!send '):
            msg = sender + info.content[7::]
        else:
            msg = sender + info.content

        # 消息荷载
        payload = {
            'group_id': GROUP_ID,
            'message': msg,
            'auto_escape': False,
        }

        try:
            # 请求消息发送API
            response = requests.post('http://127.0.0.1:5700/send_group_msg',
                                     data=payload)

            if response.status_code == 200:
                # 将返回数据解析为字典
                response_dict = json.loads(response.text)
                # 消息ID
                message_id = response_dict['data']['message_id']
                # 向控制台发送消息发送日志
                info_msg = 'ID为{0}的消息发送成功:{1}'.format(str(message_id),
                                                      response.text)
                server.logger.info(info_msg)
        except Exception as e:
            # 若发送异常就向控制台报错
            server.logger.error(e)


@new_thread('FlaskThread')
def run_bot_server():
    """将监听服务器放在新线程运行"""
    BOT_SERVER.run(port=5701)


def on_info(server: ServerInterface, info: Info):
    """插件消息处理函数"""
    send_message(server, info)


@BOT_SERVER.route('/plugin', methods=['POST'])
def on_recv():
    """QQ消息处理函数"""
    try:
        # 将上报的数据解析为字符串
        data = request.get_data().decode('utf-8')
        # 将数据字符串解析为字典
        data_dict = json.loads(data)
        # 判断该数据是否为群消息
        if 'message_type' in data_dict and 'group_id' in data_dict:
            # 判断该消息是否为所监听的群的消息
            if data_dict['group_id'] == GROUP_ID:
                # 原始消息
                raw_msg = data_dict['raw_message']

                # 将特殊消息内容解析
                if not re.search(r'\[CQ:at,qq=.+?]', raw_msg) is None:
                    tmp = raw_msg
                    member_id = re.findall(r'\[CQ:at,qq=.+?]',
                                           tmp)[0].replace('[CQ:at,qq=',
                                                           '').replace(']', '')
                    member_nick = json.loads(
                        requests.post(
                            'http://127.0.0.1:5700/get_group_member_info',
                            data={
                                'group_id': GROUP_ID,
                                'user_id': member_id,
                                'no_cache': True,
                            }).text)['data']['card']
                    raw_msg = re.sub(r'\[CQ:at,qq.+?]',
                                     '§e[@' + member_nick + ']§r', tmp)
                if not re.search(r'\[CQ:image,file=.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:image,file=.+?]', '§e[图片]§r', tmp)
                if not re.search(r'\[CQ:record,.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:record,.+?]', '§e[语音]§r', tmp)
                if not re.search(r'\[CQ:face,.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:face,.+?]', '§e[表情]§r', tmp)
                if not re.search(r'\[CQ:emoji,.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:emoji,.+?]', '§e[表情]§r', tmp)
                if not re.search(r'\[CQ:share,.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:share,.+?]', '§e[分享]§r', tmp)
                if not re.search(r'\[CQ:music,.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:music,.+?]', '§e[音乐]§r', tmp)
                if not re.search(r'\[CQ:xml,.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:xml,.+?]', '§e[XML消息]§r', tmp)
                if not re.search(r'\[CQ:json,.+?]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:json,.+?]', '§e[JSON消息]§r', tmp)

                # 拼接命令
                command = 'tellraw @a "§d[QQ群]§3{0}§r : {1}"'.format(
                    data_dict['sender']['card'], raw_msg)

                # 判断是否要将群消息转发至游戏
                if Q2G_STATUS == 1:
                    # 尝试连接RCON服务器
                    conn = RCON_CONN.connect()
                    # 如果连接成功
                    if conn:
                        # 发送命令并断开连接
                        RCON_CONN.send_command(command)
                        RCON_CONN.disconnect()
    except Exception as e:
        # 若发送异常就向控制台报错
        print('[BOT_SERVER] ' + str(e))
    return ''


@BOT_SERVER.route('/plugin/stop', methods=['POST'])
def on_bot_server_stop():
    """关闭Flask线程"""
    _func = request.environ.get('werkzeug.server.shutdown')
    if _func is None:
        raise RuntimeError
    _func()
    return ''
