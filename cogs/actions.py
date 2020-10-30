import asyncio
import datetime
import typing
import pytz

import discord
from discord import Color

from cogs.misc import LikeUser, FakeMember

colours = {'unban': Color.green(),
           'unmute': Color.dark_green(),
           'note': Color.light_grey(),
           'warn': Color.orange(),
           'mute': Color.dark_purple(),
           'kick': Color.dark_orange(),
           'softban': Color.red(),
           'ban': Color.dark_red()
           }


async def ban(victim: discord.Member, reason: str = None):
    await victim.guild.ban(victim, reason=reason)


async def softban(victim: discord.Member, reason: str = None):
    await victim.guild.ban(victim, reason=reason)
    await victim.guild.unban(victim, reason=reason)


async def kick(victim: discord.Member, reason: str = None):
    await victim.guild.kick(victim, reason=reason)


async def mute(victim: discord.Member, reason: str = None):
    muted_role = discord.utils.get(victim.guild.roles, name="Muted")
    await victim.add_roles(muted_role, reason=reason)


async def unmute(victim: discord.Member, reason: str = None):
    muted_role = discord.utils.get(victim.guild.roles, name="Muted")
    await victim.remove_roles(muted_role, reason=reason)


async def warn(victim: discord.Member, reason: str = None):
    pass


async def note(victim: discord.Member, reason: str = None):
    pass


async def unban(victim: discord.Member, reason: str = None):
    await victim.guild.unban(victim, reason=reason)

async def get_action_log_embed(bot: 'ctx_wrapper', case_number: int, action_type: str, victim: discord.Member, moderator: discord.Member, reason: str = None,
                               attachement_url: str = None):
    embed = discord.Embed()
    if attachement_url:
        embed.set_image(url=attachement_url)

    embed.colour = colours[action_type]
    embed.title = f"{action_type.title()} | Case #{case_number}"
    embed.description = reason[:1000]

    embed.add_field(name="Moderator", value=f"{moderator.name}#{moderator.discriminator}", inline=True)
    embed.add_field(name="Victim", value=f"{victim.name}#{victim.discriminator} ({victim.id})", inline=True)

    embed.set_author(name=bot.user.name)

    embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Lisbon'))

    return embed

async def full_process(bot, action_coroutine: typing.Callable[[discord.Member, str], typing.Awaitable], victim: typing.Union[discord.Member, FakeMember],
                       moderator: typing.Union[discord.Member, LikeUser], reason: str = None, attachement_url: str = None, duration: time.FutureTime = None):

    action_type = action_coroutine.__name__
    case_number = 123


    #ban DM
    quoted_reason = '> '.join(('> ' + reason).splitlines(True))
    victim_message = f"You have received a {action_type}, with the following reason\n" \
                     f"{quoted_reason}\n\n" \
                     f"For more info, please see"
    victim_message += "\n"

    invite = bot.settings["invite_link"]

    if invite and action_type in ['kick', 'unban', 'ban', 'softban']:
        victim_message += f"You can rejoin the server: {invite}\n"

    if action_type in ['warn', 'kick', 'ban', 'mute']:
        victim_message += f"You can appeal this with the moderator of your choice."

    try:
        asyncio.ensure_future(victim.send(victim_message))
    except AttributeError:
        # LikeUser dosen't have a send attr
        pass
    await action_coroutine(victim, reason[:510])

        #log action to DB here
    #new_infraction(victim, case_number, action_type, moderator.id, reason,  )

    # Log this to #mod-log or whatever
    if bot.settings["mod_logs"]:
        # Beware to see if the channel id is actually in the same server (to compare, we will see if the current server
        # owner is the same as the one in the target channel). If yes, even if it's not the same server, we will allow
        # logging there

        channel_id = bot.settings["mod_logs_channel_id"]

        if channel_id != 0:
            channel = bot.get_channel(channel_id)
            bot.logger.debug(f"B Getting logging channel for {victim.guild}, logs_channel_id, channel_id={channel_id}, channel={channel}")

            if not channel:
                bot.logger.warning(f"There is something fishy going on with guild={victim.guild.id}! "
                                   f"Their logs_channel_id={channel_id} can't be found!")
            elif not channel.guild.owner == victim.guild.owner:
                bot.logger.warning(f"There is something fishy going on with guild={victim.guild.id}! "
                                   f"Their logs_channel_id={channel_id} don't belong to them!")
            else:
                if bot.settings["logs_as_embed"]:
                    embed = await get_action_log_embed(bot,
                                                       case_number,
                                                       action_type,
                                                       victim,
                                                       moderator,
                                                       reason=reason,
                                                       attachement_url=attachement_url)

                    # With ensure future we can send the message on background
                    # This way the logger does not limit thresholds to discord ratelimits
                    async def send(embed):
                        try:
                            await channel.send(embed=embed)
                        except discord.errors.Forbidden:
                            pass

                    asyncio.ensure_future(send(embed))
                else:
                    textual_log = f"**{action_type}** #{case_number} " \
                                  f"on {victim.name}#{victim.discriminator} (`{victim.id}`)\n" \
                                  f"**Reason**: {reason}\n" \
                                  f"**Moderator**: {moderator.name}#{moderator.discriminator} (`{moderator.id}`)"

                    async def send(log):
                        try:
                            await channel.send(log)
                        except discord.errors.Forbidden:
                            pass

                    asyncio.ensure_future(send(textual_log))

    return {"user_informed": None,
            "case_number": case_number}