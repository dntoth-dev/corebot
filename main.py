import discord
from discord.ext import commands
import config
from typing import Optional, Literal

class MyBot(commands.Bot):
    def __init__(self):
        # Initialize default intents (add members intent if tracking counts accurately)
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self):
        # Dynamically load all cogs from the cogs directory
        initial_extensions = [
            "cogs.general",
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


# --- Global Sync Command Setup ---

@bot.command(name="sync")
@commands.is_owner()  # Safeguard: Only the bot owner can call this command
async def sync(ctx: commands.Context, spec: Optional[Literal["global", "clear"]] = None):
    """
    Handles command synchronization.
    Modes:
      !sync          -> Fast-syncs global commands strictly to the current testing server.
      !sync global   -> Syncs commands globally across all servers (takes 10-60 mins).
      !sync clear    -> Wipes all copied commands from the current testing server.
    """
    if spec == "global":
        await ctx.send("Starting global application command sync... (This may take up to an hour to propagate)")
        try:
            synced = await bot.tree.sync()
            await ctx.send(f"Successfully synced {len(synced)} application commands globally.")
        except Exception as e:
            await ctx.send(f"Global sync failed: `{e}`")
            
    elif spec == "clear":
        await ctx.send("Clearing local guild command copies...")
        bot.tree.clear_commands(guild=ctx.guild)
        await bot.tree.sync(guild=ctx.guild)
        await ctx.send("Guild-specific command cache cleared.")
        
    else:
        # Default behavior: Fast-syncs your current global tree directly to this test guild
        await ctx.send("Syncing global commands to this specific server for fast testing...")
        try:
            bot.tree.copy_global_to(guild=ctx.guild)
            synced = await bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"Successfully synced {len(synced)} commands locally to this server.")
        except Exception as e:
            await ctx.send(f"Local guild sync failed: `{e}`")
            

if __name__ == "__main__":
    bot.run(config.TOKEN)