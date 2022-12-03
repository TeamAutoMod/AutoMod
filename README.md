![AutoMod Banner](assets/banner.png)
# AutoMod [![discord.py](https://img.shields.io/badge/discord.py-2.0.1-7289da.svg)](https://github.com/Rapptz/discord.py) [![Supportserver](https://discord.com/api/guilds/697814384197632050/embed.png)](https://discord.gg/S9BEBux)
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

### Configuration

#### Bot

>  You can use your local version on your own servers, but please don't make it public.

To run a local version, download or fork this repo and create a ``config.json`` file in the ``backend/bot`` folder filling out the required values as shown in the ``config.json.example`` file. Then run ``pip install -r requirements.txt`` to install the required dependencies. The file you have to run in order to start the bot is ``launch.py`` in the root folder.

#### Website
To use the website, first, configure the ``web_base_url`` field in the ``config.json`` file in ``backend/bot``. Then create a ``.env`` file in the ``backend/web`` directory like it's described in the ``.env.example`` file. Make sure the port is the same as in the config file, meaning if you set ``web_base_url`` to be ``http://localhost:3000`` the ``PORT`` option needs to be ``3000``. After you've set everything, run ``npm run start`` or ``node server.js`` from the terminal (make sure you are in the ``backend/web`` directory -> ``cd backend/web``).

> To have the stats displayed, FIRST start the server and then start the bot afterward.

### 🐋 Dockerized

> You need the latest version of `docker-compose` to run the following containers.

### Configs
You need to setup the bot with the given configs from the local installation for the bot and website.

### Setup
To run the bot and the website just execute `docker-compose up -d` in the root folder of the project. This will start the website first and then the bot. This dependency is needed to post the stats. The stats will now be presented on `your-domain.de:3000` or `your-ip:3000`

### Website with ssl
If you want to run the website with a signed ssl cert you need to setup a let's encrypt instance first. In this example we use a traefik for this. Create a `docker-compose.override.yaml` to setup the needed labels and change `your-domain.de` to your own domain.

```yaml
---
version: '3.8'

services:
  web:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.automod.entrypoints=http"
      - "traefik.http.routers.automod.rule=Host(`your-domain.de`)"
      - "traefik.http.middlewares.automod-https-redirect.redirectscheme.scheme=https"
      - "traefik.http.routers.automod.middlewares=automod-https-redirect"
      - "traefik.http.routers.automod-secure.entrypoints=https"
      - "traefik.http.routers.automod-secure.rule=Host(`your-domain.de`)"
      - "traefik.http.routers.automod-secure.tls=true"
      - "traefik.http.routers.automod-secure.tls.certresolver=http"
      - "traefik.http.routers.automod-secure.service=automod"
      - "traefik.http.services.automod.loadbalancer.server.port=80"
      - "traefik.docker.network=proxy"

networks:
  nginx:
    external: true
```

If you want to limit your bot or website by ressources, just add the following lines to the servicedescription of the override

```yaml
  mem_limit: 512m
  cpus: 0.25
```

## 🔎 Resources
- [Invite the bot](https://automod.xyz/invite)
- [Support server](https://discord.gg/S9BEBux)
- [Vote on Top.gg](https://top.gg/bot/697487580522086431/vote)