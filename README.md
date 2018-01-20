# PUGBot
Bot for organising CSGO 10 mans in a discord
Create a csv with the headings:
owner,bans_channel,voice_channel,botID,serverName

[owner unique discord ID],[text channel unique ID],[voice channel unique ID],[bot user secret],[Name of server for which it is configured]

run using the command
python3.5 bot.py my_config.csv

If you don't include my_config.csv as an argument, it will default to searching for config.csv, i.e. if you want multiple configs for different bots you can feed it a different config.

You will need to create a bot and a bot user here: https://discordapp.com/developers/applications/me
