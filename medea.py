#!/usr/bin/python3
import asyncio #Comes with discord.py
import json #Base
import base64 #Base
from chatbot import BotClient # Included

bc = BotClient()

botinfo = open("chatbot/AI.json", "r")
rawinfo = botinfo.read()
BOTDATA = json.loads(rawinfo)
botinfo.close()
inp = ""
while inp != "quit" and inp != "exit":
    inp = input("User> ")
    print("%s> %s"%(BOTDATA["name"], 
bc.chat(inp)))
