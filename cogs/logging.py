import asyncio
import logging

import discord
from discord.ext import commands

from cogs.context import ctx_wrapper

ATTACHMENTS_UPLOAD_CHANNEL_ID = 123

async def save_attachments(bot: 'ctx_wrapper', message: discord.Message):
    if len(message.attachments) >= 1:
        attachments_upload_channel = bot.get_channel(ATTACHMENTS_UPLOAD_CHANNEL_ID)
        saved_attachments_files = []
        attachments_unsaved_urls = []
        total_files = len(message.attachments)
        saved_files = 0
        for i, attachment in enumerate(message.attachments):
            file = io.BytesIO()
            attachment: discord.Attachment
            try:
                await attachment.save(file, seek_begin=True, use_cached=True)  # Works most of the time
            except discord.HTTPException:
                try:
                    await attachment.save(file, seek_begin=True, use_cached=False)  # Almost never works, but worth a try!
                except discord.HTTPException:
                    attachments_unsaved_urls.append(attachment.url)
                    break  # Couldn't save
            saved_files += 1
            saved_attachments_files.append(discord.File(fp=file, filename=attachment.filename))
        if saved_files >= 0:
            try:
                saved = await attachments_upload_channel.send(
                    content=f"`[{saved_files}/{total_files}]` - Attachment(s) for message {message.id} on channel `[{message.channel.id}]` #{message.channel.name}, in guild `[{message.guild.id}]` {message.guild.name}",
                    files=saved_attachments_files)
            except discord.HTTPException:
                # Too large for the bot
                return [], [a.url for a in message.attachments]

            attachments_saved_urls = [a.url for a in saved.attachments]
        else:
            attachments_saved_urls = []
    else:
        return [], []

    return attachments_saved_urls, attachments_unsaved_urls


class Logging(commands.Cog):
    """
    Logging events. """

    def __init__(self, bot):
        self.bot = bot

    async def perms_okay(self, channel: discord.TextChannel):
        pass

    async def get_logging_channel(self, guild: discord.Guild, pref: str):
        pass

