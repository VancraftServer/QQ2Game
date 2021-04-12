# QQ2Game
[English](README.md) | **中文**

一个将QQ消息与游戏同步的MCDR插件。

# **!!请不要在服务器运行时频繁重载该插件!!**

# 用法

### 安装

##### 依赖

1. Flask   `pip3 install flask`
2. Requests `pip3 install request`
3. MCDReforged >= 1.0.0 `pip3 install mcdreforged`
4. [OneBot Kotlin](https://github.com/yyuueexxiinngg/onebot-kotlin)

##### 配置 OneBot Kotlin

编辑你的 `setting.yml` (通常位于`.../config/OneBot/settings.yml`) 到如下样式

```yaml
proxy: ''
bots: 
  123456789: 
    http: 
      enable: true
      host: 127.0.0.1
      port: 5700
      accessToken: ''
      postUrl: 'http://127.0.0.1:5701/plugin'
      postMessageFormat: string
      secret: ''
      timeout: 0
    
```

##### 安装插件

1. 编辑你的 `server.properties` 并打开RCON。
2. 在 `qq2game.py` 的 `CONFIGURES` 变量中配置好RCON密码和要监听的QQ群号。
3. 将 `qq2game.py` 复制到你的MCDR插件文件夹并开启服务器。
4. 运行OneBot Kotlin。

##### Enjoy

***

### 命令

##### !!q2g

- 使用 `!!q2g status` 获取当前QQ到游戏功能状态。

- 使用 `!!q2g status <0/1>` 设置当前QQ到游戏功能状态。
##### !!g2q
- 使用 `!!g2q status` 获取当前游戏到QQ功能状态。
- 使用 `!!g2q status <0/1>` 设置当前游戏到QQ功能状态。
***

### 配置

你可以在 `qq2game.py` 的 `CONFIGURES` 变量中配置默认的命令前缀和默认的QQ到游戏功能状态和游戏到QQ功能状态。

注： 0 代表关闭，1 代表开启。

------

### 许可

此插件按照 [GNU General Public License](LICENSE) 分发。