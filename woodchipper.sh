#!/bin/sh
export DISCORD_TOKEN=`cat .discord-token`
poetry run python3 bot.py
