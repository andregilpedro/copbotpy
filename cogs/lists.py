import discord
from discord.ext import commands

from cogs.actions import full_process, unban, note, warn, kick, softban, ban, mute, unmute

from cogs.context import ctx_wrapper

class ListsCog(commands.Cog):
    """
    List related commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='list_infractions', aliases=['infractions', 'listinfractions'])
    async def list_infractions(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command(name='list_bans', aliases=['bans', 'listbans'])
    async def list_bans(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command(name='list_mutes', aliases=['listmutes'])
    async def list_mutes(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command(name='infractions_clear', aliases=['infractionsclear', 'clear_infractions', 'clearinfractions'])
    async def infractions_clear(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command(name='infraction_remove', aliases=['removeinfraction', 'remove_infraction', 'infractionremove'])
    async def remove_infraction(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

def setup(bot):
    bot.add_cog(ListsCog(bot))        


