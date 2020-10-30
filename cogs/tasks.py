import discord
from discord.ext import tasks, commands
import json
from cogs.misc import save_to_db
from cogs.context import ctx_wrapper

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_bans.start()
        self.save_db.start()

    # Check for unbans/unmutes
    @tasks.loop(seconds=1.0)
    async def check_bans(self):
        pass

    # Save DB to file
    @tasks.loop(minutes=5)
    async def save_db(self):
        save_to_db(self.bot.db)
        print("saved DB") 

    @save_db.before_loop
    @check_bans.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()     

def setup(bot):
    bot.add_cog(TasksCog(bot))        