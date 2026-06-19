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

        # Copy global tree commands to target guild layout and sync
        self.tree.copy_global_to(guild=config.GUILD_OBJ)
        await self.tree.sync(guild=config.GUILD_OBJ)
        print(f"Synced commands to Guild ID: {config.SHADOW_GUILD_ID}")

bot = MyBot()

@bot.event
async def on_ready():
    print('------')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

if __name__ == "__main__":
    bot.run(config.TOKEN)