![AutoMod Banner](assets/banner.png)
# AutoMod
AutoMod is a Discord moderation and utility bot, made for both small and large communities.

## ℹ️ Features
- Advanced automoderator, with features such as:
  - Anti-Advertising
  - Restrictions for newlines
  - Link filtering
  - Restrictions for emotes
  - Anti-Repetition
  - Malicious file detection
  - Anti-Zalgo
  - Restrictions for mentions
  - Anti-Spam
- Multiple logging options
- Case system for moderation actions
- Custom word filters
- Custom commands for easy replying
- Easy-to-use moderation & utility commands
- Reaction Roles
- And much, much more

## 🛠 Self-hosting/Development
To run a local version, download or fork this repo and create a ``config.json`` file in the ``packages/bot`` folder filling out the required values as shown in the ``config.json.example`` file. Then run ``pip install -r requirements.txt`` to install the required dependencies. The file you have to run in order to start the bot is ``launch.py`` in the root folder. You can use your local version on your own servers, but please don't make it public. 
To use the website, first, configure the ``web_base_url`` field in the ``config.json`` file in ``packages/bot``. Then create a ``.env`` file in the ``packages/web`` directory like it's described in the ``.env.example`` file. Make sure the port is the same as in the config file, meaning if you set ``web_base_url`` to be ``http://localhost:3000`` the ``PORT`` option needs to be ``3000``. After you've set everything, run ``npm run start`` or ``node server.js`` from the terminal (make sure you are in the ``packages/web`` directory -> ``cd packages/web``). TO have the stats displayed, FIRST start the server and then start the bot afterward.

## 🔎 Resources
- [Invite the bot](https://automod.xyz/invite)
- [Support server](https://discord.gg/S9BEBux)
- [Vote on Top.gg](https://top.gg/bot/697487580522086431/vote)