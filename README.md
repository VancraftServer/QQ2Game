# QQ2Game
**English** | [中文](README_CN.md)

An MCDR plugin that synchronizes QQ messages to the game.

# **!!DO NOT RELOAD THIS PLUGIN VERY OFTEN WHILE THE SERVER IS STILL RUNNING!!**

# Usages

### Installation

##### Requirements

1. Flask   `pip3 install flask`
2. Requests `pip3 install request`
3. MCDReforged >= 1.0.0 `pip3 install mcdreforged`
4. [OneBot Kotlin](https://github.com/yyuueexxiinngg/onebot-kotlin)

##### Configure OneBot Kotlin

Edit you `setting.yml`(usually at `.../config/OneBot/settings.yml`) like this

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

##### Install the plugin

1. Edit your `server.properties`  to turn on RCON.
2. Config your RCON password and listening group id in the dictionary variable `CONFIGURES` at `qq2game.py`.
3. Copy `qq2game.py` into your MCDR plugins folder and start the server.
4. Run OneBot Kotlin.

##### Enjoy

***

### Commands

##### !!q2g

- Use `!!q2g status` to get current status of QQ to game.

- Use `!!q2g status <0/1>` to set current status of QQ to game.
##### !!g2q
- Use `!!g2q status` to get current status of game to QQ.
- Use `!!g2q status <0/1>` to set current status of game to QQ.
***

### Config

You can change the prefix of the command and the default status of game to QQ and QQ to game in the dictionary variable `CONFIGURES` at `qq2game.py`.

P.S. 0 stands for off and 1 stands for on.

------

### License

This plugin is licensed under the [GNU General Public License](LICENSE).