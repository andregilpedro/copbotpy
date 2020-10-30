import typing
import datetime
import pytz

import discord
from discord.ext import commands

#from cogs.actions import full_process, unban, note, warn, kick, softban, ban, mute, unmute
from cogs.misc import BannedMember, FakeMember, LikeUser, ForcedMember, get_top_role
from cogs.context import ctx_wrapper
from cogs import checks
from cogs import time

#finish the commands
class ModerationCog(commands.Cog):
    """
    Moderation commands for the bot.
    Here you'll find, commands to ban, kick, warn and add notes to members.
    """

    def __init__(self, bot: 'ctx_wrapper'):
        self.bot = bot

    async def run_actions(self, ctx: 'ctx_wrapper', user: typing.Union[discord.Member, discord.User, ForcedMember, LikeUser], reason: str,
                          attachments_saved_url: str, action: typing.Callable[[discord.Member, str], typing.Awaitable], duration: time.FutureTime = None):

        if get_top_role(ctx.author) <= get_top_role(user):
            pass

        cases_urls = []

        if duration:
            reason = reason + f"\n🕰️ Duration: {time.human_timedelta(duration.dt, source=datetime.datetime.now(pytz.timezone('Europe/Lisbon')))}"

        #act = await full_process(ctx.bot, action, user, ctx.author, reason, attachement_url=attachments_saved_url)
#
        #cases_urls.append(act['url'])
        #if duration:
        #    if action is mute:
        #        await self.api.create_task("unmute", arguments={"target": user.id, "guild": ctx.guild.id, "reason": f"Time is up | See case #{act['case_number']} for details"},
        #                                   execute_at=duration.dt)
        #    elif action is ban:
        #        await self.api.create_task("unban", arguments={"target": user.id, "guild": ctx.guild.id, "reason": f"Time is up | See case #{act['case_number']} for details"}, execute_at=duration.dt)
#
        #await ctx.send(f":ok_hand: - See {', '.join(cases_urls)} for details")

    @commands.command()
    @checks.bot_have_permissions()
    @checks.is_staff(admin=True)
    async def ban(self, ctx: 'ctx_wrapper', user: ForcedMember(may_be_banned=False, inferior_rank=True), duration: typing.Optional[time.FutureTime], *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        """ Ban user """
        print("user:",user,"duration:",duration,"reason:",reason)
        pass

    @commands.command()
    @checks.bot_have_permissions()
    @checks.is_staff(admin=True)
    async def unban(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command()
    @checks.bot_have_permissions()
    @checks.is_staff()
    async def mute(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command()
    @checks.bot_have_permissions()
    @checks.is_staff()
    async def unmute(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command()
    @checks.bot_have_permissions()
    @checks.is_staff()
    async def warn(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

    @commands.command()
    @checks.bot_have_permissions()
    @checks.is_staff()
    async def note(self, ctx, duration, user, *, reason: commands.clean_content(fix_channel_mentions=True, use_nicknames=False) = ""):
        pass

def setup(bot):
    bot.add_cog(ModerationCog(bot))        


