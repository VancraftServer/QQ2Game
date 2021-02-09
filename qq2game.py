import requests
import json
import re

from flask import Flask, request

from mcdreforged.api.types import ServerInterface, Info
from mcdreforged.api.command import Literal, Integer
from mcdreforged.api.rcon import RconConnection
from mcdreforged.api.decorator import new_thread

PLUGIN_METADATA = {
    'id': 'q2g',
    'version': '0.0.0',
    'name': 'QQ2Game',
    'description': '群消息与游戏同步插件',
    'author': 'ShootKing233',
    'link': 'https://github.com/VancraftServer/QQ2Game/',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
    },
}

RCON_CONN = RconConnection('127.0.0.1', 25575, '12345678')
GROUP_ID = 1061192531

Q2G_PREFIX = '!!q2g'
G2Q_PREFIX = '!!g2q'

G2Q_STATUS = 0
Q2G_STATUS = 1

BOT_SERVER = Flask(__name__)


def getStatus(target):
    if not isinstance(target, str):
        raise TypeError
    if target not in ['q2g', 'g2q']:
        raise ValueError
    if target == 'q2g':
        if not Q2G_STATUS == 1 and not Q2G_STATUS == 0:
            raise ValueError
        return Q2G_STATUS
    if target == 'g2q':
        if not G2Q_STATUS == 1 and not G2Q_STATUS == 0:
            raise ValueError
        return G2Q_STATUS


def setStatus(target, status):
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


def on_load(server: ServerInterface, prev):
    if prev is not None:
        server.logger.warn('注意！本插件不能热重载，请重启服务器！')
    server.logger.info('QQ2Game正在加载')
    server.register_help_message(
        Q2G_PREFIX,
        '''{0} status -- 查看当前QQ->游戏功能是否打开
        {1} status <0/1> -- 打开/关闭QQ->游戏功能(0:关闭/1:打开)'''.format(Q2G_PREFIX, Q2G_PREFIX)
    )
    server.register_help_message(
        G2Q_PREFIX,
        '''{0} status -- 查看当前QQ<-游戏功能是否打开
        {1} status <0/1> -- 打开/关闭QQ<-游戏功能(0:关闭/1:打开)'''.format(G2Q_PREFIX, G2Q_PREFIX)
    )
    server.register_command(
        Literal(Q2G_PREFIX)
        .then(
            Literal('status')
            .runs(lambda src: src.reply(
                '当前QQ->游戏功能处于{0}状态'.format(
                    '开启' if getStatus('q2g') == 1 else '关闭')))
            .then(
                Integer('statusId')
                .in_range(0, 1)
                .runs(lambda src, ctx: src.reply(
                    '已将QQ->游戏功能设置为{0}状态'.format(
                        '开启' if setStatus('q2g', ctx['statusId']) == 1 else '关闭'))
                      )
            )
        )
    )
    server.register_command(
        Literal(G2Q_PREFIX)
        .then(
            Literal('status')
            .runs(lambda src: src.reply(
                '当前QQ<-游戏功能处于{0}状态'.format(
                    '开启' if getStatus('g2q') == 1 else '关闭')))
            .then(
                Integer('statusId')
                .in_range(0, 1)
                .runs(lambda src, ctx: src.reply(
                    '已将QQ<-游戏功能设置为{0}状态'.format(
                        '开启' if setStatus('g2q', ctx['statusId']) == 1 else '关闭'))
                      )
            )
        )
    )
    runBotServer()
    server.logger.info('QQ2Game加载完成')

    return


def sendMessage(server: ServerInterface, info: Info):
    if (G2Q_STATUS == 1 and not info.content.startswith('!!') and (info.is_player or info.is_from_console)) or (
            G2Q_STATUS == 0 and info.content.startswith('!!send ') and (info.is_player or info.is_from_console)):
        sender = '<{0}> '.format(info.player if info.is_player else 'CONSOLE')
        if info.content.startswith('!!send '):
            msg = sender + info.content[7::]
        else:
            msg = sender + info.content
        payload = {
            'group_id': GROUP_ID,
            'message': msg,
            'auto_escape': False,
        }
        try:
            response = requests.post(
                'http://127.0.0.1:5700/send_group_msg', data=payload)
            if response.status_code == 200:
                responseDict = json.loads(response.text)
                messageId = responseDict['data']['message_id']
                infoMsg = 'ID为' + str(messageId) + '的消息发送成功:' + response.text
                server.logger.info(infoMsg)
        except Exception as e:
            server.logger.error(e)

    return


@new_thread('Flask Thread')
def runBotServer():
    BOT_SERVER.run(port=5701)

    return


def on_info(server: ServerInterface, info: Info):
    sendMessage(server, info)

    return


@BOT_SERVER.route('/plugin', methods=['POST'])
def onRecv():
    try:
        data = request.get_data().decode('utf-8')
        dataDict = json.loads(data)
        if 'message_type' in dataDict:
            if dataDict['group_id'] == GROUP_ID:
                raw_msg = dataDict['raw_message']
                if not re.search(r'\[CQ:at,qq=.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    memberId = re.findall(
                        r'\[CQ:at,qq=.+?\]',
                        tmp)[0].replace(
                        '[CQ:at,qq=',
                        '').replace(
                        ']',
                        '')
                    memberNick = json.loads(
                        requests.post(
                            'http://127.0.0.1:5700/get_group_member_info',
                            data={
                                'group_id': GROUP_ID,
                                'user_id': memberId,
                                'no_cache': True,
                            }).text)['data']['card']
                    raw_msg = re.sub(r'\[CQ:at,qq.+?\]',
                                     '§e[@' + memberNick + ']§r', tmp)
                if not re.search(r'\[CQ:image,file=.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(
                        r'\[CQ:image,file=.+?\]', '§e[图片]§r', tmp)
                if not re.search(r'\[CQ:record,.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:record,.+?\]', '§e[语音]§r', tmp)
                if not re.search(r'\[CQ:face,.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:face,.+?\]', '§e[表情]§r', tmp)
                if not re.search(r'\[CQ:emoji,.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:emoji,.+?\]', '§e[表情]§r', tmp)
                if not re.search(r'\[CQ:share,.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:share,.+?\]', '§e[分享]§r', tmp)
                if not re.search(r'\[CQ:music,.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:music,.+?\]', '§e[音乐]§r', tmp)
                if not re.search(r'\[CQ:xml,.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:xml,.+?\]', '§e[XML消息]§r', tmp)
                if not re.search(r'\[CQ:json,.+?\]', raw_msg) is None:
                    tmp = raw_msg
                    raw_msg = re.sub(r'\[CQ:json,.+?\]', '§e[JSON消息]§r', tmp)
                command = 'tellraw @a "§d[QQ群]§3' + \
                    dataDict['sender']['card'] + '§r : ' + raw_msg + '"'
                if Q2G_STATUS == 1:
                    conn = RCON_CONN.connect()
                    if conn:
                        RCON_CONN.send_command(command)
                        RCON_CONN.disconnect()
    except Exception as e:
        print('[BOT_SERVER] ' + str(e))
    return ''
