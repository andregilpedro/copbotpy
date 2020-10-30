import logging

import discord
from discord.ext import commands

from cogs.context import ctx_wrapper

#move this to bot.settings
staff_id = 123
guild_ids = [123]

class NoPermissionsError(commands.CheckFailure):
    pass

class PermissionsError(commands.CheckFailure):
    def __init__(self, sendErr):
        self.sendErr = sendErr

class NoPrivateMessages(commands.CommandError):
    pass

class GuildNotAllowed(commands.CommandError):
    pass

class NoStaff(commands.CommandError):
    pass

class NotStrongEnough(Exception):
    pass

class HierarchyError(Exception):
    pass


def guild_only(guild_id):
    async def predicate(ctx: 'ctx_wrapper'):
        if ctx.guild is None:
            raise NoPrivateMessages('no DMs')
        if not ctx.guild.id in guild_id:
            raise GuildNotAllowed('guild not allowed')
        return True       
    return commands.check(predicate)

def is_staff(admin: bool = False):
    async def predicate(ctx: 'ctx_wrapper'):
        role = discord.utils.get(ctx.guild.roles, id=staff_id)
        if not ctx.author.guild_permissions.administrator:
            if not role in ctx.author.roles:
                raise PermissionsError(False)
            elif admin:
                raise PermissionsError(True)
        return True
    return commands.check(predicate)

def bot_have_permissions():
    async def predicate(ctx: 'ctx_wrapper') -> bool:
        await ctx.bot.wait_until_ready()
        current_permissions = ctx.message.guild.me.permissions_in(ctx.channel)
        wanted_permissions = discord.permissions.Permissions.none()
        wanted_permissions.update(
            kick_members=True,
            ban_members=True,
            read_messages=True,
            send_messages=True,
            manage_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            external_emojis=True,
            change_nickname=True,
            add_reactions=True
        )

        cond = current_permissions >= wanted_permissions

        ctx.logger.debug(f"Check for permissions required returned {cond}")

        if cond:
            return True
        else:
            raise NoPermissionsError()

    return commands.check(predicate)    

class ChecksCog(commands.Cog):
    """
    Moderation commands for the bot.
    Here you'll find, commands to ban, kick, warn and add notes to members.
    """

    def __init__(self, bot):
        self.bot = bot    

    async def bot_check(self, ctx):
        if ctx.author.bot:
            return False
        if ctx.guild is None:
            raise NoPrivateMessages()
        if not ctx.guild.id in guild_ids:
            raise GuildNotAllowed()
        return True  

def setup(bot):
    bot.add_cog(ChecksCog(bot))