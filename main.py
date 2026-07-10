import discord
from discord.ext import commands
import config

class MyBot(commands.Bot):
    def __init__(self):
        # Initialize default intents (add members intent if tracking counts accurately)
        intents = discord.Intents.default()
        intents.members = True 
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Dynamically load all cogs from the cogs directory
        initial_extensions = [
            "cogs.general",
            "cogs.youtube",
            "cogs.moderation",
            "cogs.records",
            "cogs.developer"
        ]
        
        for ext in initial_extensions:
            await self.load_extension(ext)
            print(f"Loaded extension: {ext}")
            
bot = MyBot()

@bot.event
async def on_ready():
    print('------')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    # WARNING: Do not place command sync functions in on_ready, because Discord rate-limits command syncing globally, which could deactivate the bot.
    
@bot.event
async def on_guild_join(guild):
    # Copy global commands to the newly joined server, then sync
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"Synced commands to new guild: {guild.name}")

if __name__ == "__main__":
    bot.run(config.TOKEN)