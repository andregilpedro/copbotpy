import logging

import discord
from discord.ext import commands
import json
import sys, traceback
from cogs.misc import read_from_db, load_bans
from cogs.context import ctx_wrapper
from cogs import checks

def get_prefix(bot, message):
    """Pre process Prefix"""

    prefixes = ['!']

    return commands.when_mentioned_or(*prefixes)(bot, message)


# Cogs
cogs = ['cogs.tasks',
        'cogs.moderation']


intents = discord.Intents.default()
intents.members = True        

bot = commands.Bot(command_prefix=get_prefix, description='A moderation bot', intents=intents)

base_logger = logging.getLogger('copbot')
base_logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(channelname)s - %(userid)s | %(username)s -> %(message)s')
fh.setFormatter(fh_formatter)
base_logger.addHandler(fh)
bot.logger = logging.LoggerAdapter(base_logger, {"channelname": "#SYSTEM", "userid": "<", "username": ">"})
bot.base_logger = base_logger
bot.logger.debug("teste")

#bot.db_name = "db.json"
#bot.hastebins_servers = ["https://wastebin.travitia.xyz/", "https://hastebin.com/", "https://del.dog/", "https://mystb.in/"]
bot.admin_channels = [123]

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in cogs:
        bot.load_extension(extension)

bot.db = read_from_db()
bot.temp_bans = load_bans(bot.db)

@bot.event
async def on_ready():
    """on ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    #print(bot.db)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='stuff'))
    print(f'Successfully logged in...!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # ignore messages from other bots

    ctx = await bot.get_context(message, cls=ctx_wrapper)
    if ctx.prefix is not None:
        await bot.invoke(ctx)    

@bot.event
async def on_command_error(ctx, exception):
    if isinstance(exception, discord.ext.commands.errors.CommandNotFound):
        return
    ctx.logger.debug(f"Error during processing: {exception} ({repr(exception)})")
    if isinstance(exception, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send_to(f":no_entry_sign: A required argument is missing.\nUse it like : `{ctx.prefix}{ctx.command.signature}`", delete_after=60)
        await ctx.message.delete(delay=60)
        return
    elif isinstance(exception, discord.ext.commands.errors.MissingPermissions):
        await ctx.send_to(f":no_entry_sign: You don't have the required permissions to run this command! ", delete_after=60)
        await ctx.message.delete(delay=60)
        return
    elif isinstance(exception, checks.NoPermissionsError):
        await ctx.send_to(f":no_entry_sign: Oof, there was a problem! "
                              f"The bot need more permissions to work. Please see a server admin about that. "
                              f"If you are an admin, please type {ctx.prefix}bot_permissions_check to see what permissions are missing. "
                              f"Remember to check for channel overwrites")
        return
    elif isinstance(exception, checks.PermissionsError):
        if exception.sendErr:
            await ctx.send_to(f":no_entry_sign: You don't have the required permissions to run this command! ", delete_after=60)
            await ctx.message.delete(delay=60)
        return
    # elif isinstance(exception, discord.ext.commands.errors.CheckFailure):
    #       return
    elif isinstance(exception, discord.ext.commands.errors.ConversionError):
        if isinstance(exception.original, checks.NotStrongEnough):
            await ctx.send_to(f":no_entry_sign: You have the required level to run this command, but I can't do this "
                                  f"as your target is higher in the hierarchy than me. To fix this, move my role "
                                  f"to the top of the list in this server roles list"
                                  f"```{exception.original}```")
            return
        elif isinstance(exception.original, checks.HierarchyError):
            await ctx.send_to(f":no_entry_sign: Even if you have the required level to run this command, you can't target "
                                  f"someone with a higher/equal level than you :("
                                  f"```{exception.original}```", delete_after=60)
            await ctx.message.delete(delay=60)
            return            

    elif isinstance(exception, discord.ext.commands.errors.BadArgument):
        await ctx.send_to(f":no_entry_sign: An argument provided is incorrect: \n"
                              f"**{exception}**", delete_after=60)
        await ctx.message.delete(delay=60)
        return
    elif isinstance(exception, discord.ext.commands.errors.ArgumentParsingError):
        await ctx.send_to(f":no_entry_sign: There was a problem parsing your command, please ensure all quotes are correct: \n"
                              f"**{exception}**", delete_after=60)
        await ctx.message.delete(delay=60)
        return
    elif isinstance(exception, discord.ext.commands.errors.BadUnionArgument):
        await ctx.send_to(f":no_entry_sign: There was a problem parsing your arguments, please ensure the are the correct type: \n"
                              f"**{exception}**", delete_after=60)
        await ctx.message.delete(delay=60)
        return
    elif isinstance(exception, discord.ext.commands.errors.CommandOnCooldown):
        if ctx.message.author.id in [138751484517941259]:
            await ctx.reinvoke()
            return
        else:
            await ctx.send_to("You are on cooldown :(, try again in {seconds} seconds".format(
                seconds=round(exception.retry_after, 1)), delete_after=60)
            return
    elif isinstance(exception, discord.ext.commands.errors.TooManyArguments):
        await ctx.send_to(f":no_entry_sign: You gave me to many arguments. You may want to use quotes.\nUse the command like : `{ctx.prefix}{ctx.command.signature}`", delete_after=60)
        await ctx.message.delete(delay=60)
        return
    elif isinstance(exception, discord.ext.commands.NoPrivateMessage):
        await ctx.send_to('This command cannot be used in private messages.')
        return
    elif isinstance(exception, discord.ext.commands.errors.CommandInvokeError):
        await ctx.author.send(f"Sorry, an error happened processing your command. "
                                  f"Please review the bot permissions and try again. To report a bug, please give the support staff the following: ```py\n{exception}\n{''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}\n```", delete_after=3600)
        await ctx.message.delete(delay=3600)
        return
    elif isinstance(exception, discord.ext.commands.errors.NotOwner):
        return  # Jsk uses this
    elif isinstance(exception, discord.ext.commands.errors.MaxConcurrencyReached):
        await ctx.send_to(str(exception),
                                  delete_after=3600)
        await ctx.message.delete(delay=3600)
    else:
        bot.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        bot.logger.error("".join(traceback.format_exception(type(exception), exception, exception.__traceback__)))

bot.run('TOKEN', bot=True, reconnect=True)