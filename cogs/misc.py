import typing
import logging
import json
from datetime import datetime

import discord
from discord.ext import commands

from cogs.checks import HierarchyError, NotStrongEnough
from cogs.context import ctx_wrapper


db_name = "db.json"

def converter(o):
    if isinstance(o, datetime):
        return o.timestamp()

def save_to_db(db):
    with open(db_name, 'w') as json_file:
        json.dump(db, json_file, default=converter)

def read_from_db():
    with open(db_name) as json_file:
        return json.load(json_file)

def load_bans(db):
    return 1

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)

            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")

        return entity

class LikeUser:
    def __init__(self, did: int, name: str, guild: discord.Guild, discriminator: str = '0000',
                 avatar_url="https://cdn.discordapp.com/embed/avatars/1.png", bot=False,
                 do_not_update=True):

        self.id = did
        self.name = name
        self.guild = guild
        self.discriminator = discriminator
        self.avatar_url = avatar_url
        self.default_avatar_url = avatar_url
        self.do_not_update = do_not_update
        self.bot = bot

    def avatar_url_as(self, *args, **kwargs):
        return self.avatar_url


class FakeMember:
    def __init__(self, user: discord.User, guild: discord.Guild):
        self._user = user
        self.guild = guild

    def __getattr__(self, item):
        return getattr(self._user, item)     

class ForcedMember(commands.Converter):
    def __init__(self, may_be_banned=True, inferior_rank=False):
        super().__init__()
        self.may_be_banned = may_be_banned
        self.inferior_rank = inferior_rank

    async def convert(self, ctx, argument) -> typing.Union[discord.Member, FakeMember, LikeUser]:
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
            if self.inferior_rank:
                if m != ctx.guild.owner and ctx.author.top_role > m.top_role or ctx.author == ctx.guild.owner and ctx.author != m:
                    if m.top_role > ctx.guild.me.top_role:
                        raise NotStrongEnough(f'You cannot do this action on this user due to role hierarchy between the bot and {m.name}.')
                    return m
                else:
                    raise HierarchyError('You cannot do this action on this user due to role hierarchy.')
            return m
        except commands.BadArgument:
            try:
                did = int(argument, base=10)
                if did < 10 * 15:  # Minimum 21154535154122752 (17 digits, but we are never too safe)
                    raise commands.BadArgument(f"The discord ID {argument} provided is too small to be a real discord user-ID. Please check your input and try again.")

                if not self.may_be_banned:
                    if discord.utils.find(lambda u: u.user.id == did, await ctx.guild.bans()):
                        raise commands.BadArgument(f"The member {argument} is already banned.")

                try:
                    u = ctx.bot.get_user(did)
                    if u:
                        return FakeMember(u, ctx.guild)

                    else:
                        u = await ctx.bot.fetch_user(did)
                        return FakeMember(u, ctx.guild)
                except:
                    ctx.logger.exception("An error happened trying to convert a discord ID to a User instance. "
                                         "Relying on a LikeUser")
                    return LikeUser(did=int(argument, base=10), name="Unknown member", guild=ctx.guild)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        except Exception as e:
            raise

def get_top_role(user):
    if user == user.guild.owner:
        return 10000
    top_role = 0
    for role in user.roles:
        if role.postition > top_role:
            top_role = role.postition
    return top_role