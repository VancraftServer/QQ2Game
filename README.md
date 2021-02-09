# QQ2Game
An MCDR plugin that synchronizes QQ messages to the game.

# **!!DO NOT RELOAD THIS PLUGIN WHILE THE SERVER IS STILL RUNNING!!**

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
2. Fill in your RCON port and password at line 24 at  `qq2game.py`.
3. Fill in your QQ group id at line 25 at `qq2game.py`.
4. Copy `qq2game.py` into your MCDR plugins folder and start the server.
5. Run OneBot Kotlin.

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

##### Command prefix

You can change the prefix of the command at line 27 & 28 at `qq2game.py`.

##### Default status

You can change the default status of game to QQ and QQ to game at line 30 & 31 at `qq2game.py`.

P.S. 0 stands for off and 1 stands for on.