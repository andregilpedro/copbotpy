import logging
import typing
import random
import aiohttp
import json

import discord
from discord.ext import commands

#upload to a random wastebin
hastebins_servers = ["https://wastebin.travitia.xyz/", "https://hastebin.com/", "https://del.dog/", "https://mystb.in/"]
async def upload_text(text: str) -> str:
    servers = hastebins_servers[:]
    random.shuffle(servers)  # In-place

    async with aiohttp.ClientSession() as cs:
        for server in servers:
            try:
                async with cs.post(server + "documents", data=text) as r:
                    res = await r.json()
                    print(f"Pasted on {server} with key {res['key']} - {server}/{res['key']} ")
                    return server + res["key"]
            except Exception as e:
                print(f"{server} - Can't paste: error- {e} ({type(e)}), code- {r.status}")
                continue
    raise IOError("No paste servers available :(")

class ctx_wrapper(commands.Context):

    def __init__(self, **attrs):
        super().__init__(**attrs)

    @property
    def logger(self):
        # Copy that to log
        if self.channel:
            cname = self.channel.name
        else:
            cname = "PRIVATE_MESSAGE"

        extra = {"channelname": f"#{cname}", "userid": f"{self.author.id}", "username": f"{self.author.name}#{self.author.discriminator}"}
        logger = logging.LoggerAdapter(self.bot.base_logger, extra)
        return logger

    async def send_to(self, message: str, user: typing.Optional[discord.User] = None, **kwargs):
        if user is None:
            user = self.author

        if len(message) > 1900 and kwargs.get("embed", None) is None:
            message = await upload_text(message.strip("`"))

        message = f"{user.mention} {message}"

        if self.channel.id in self.bot.admin_channels:
            return await self.send(message, **kwargs)
        else:
            await self.message.delete()
            return await user.send(message, **kwargs)