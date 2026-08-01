import discord
from discord.ext import commands
import config
from typing import Optional, Literal
from database import SupabaseManager

class MyBot(commands.Bot):
    def __init__(self):
        # Initialize default intents (add members intent if tracking counts accurately)
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)
        self.db = SupabaseManager()

        
    async def setup_hook(self):
        # Dynamically load all cogs from the cogs directory
        
        await self.db.initialize()
        
        initial_extensions = [
            "cogs.general",
            "cogs.moderation",
            "cogs.records",
            "cogs.developer",
            "cogs.security"
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
    
    bot_role = guild.me.top_role
    
    # Check if there are dangerous configurations (e.g., administrator roles above the bot)
    # Or simply check if it's sitting near the bottom of the list
    roles_above_bot = [role for role in guild.roles if role > bot_role and not role.is_default()]
    
    if roles_above_bot:
        # Construct a helpful notice for the owner
        msg = (
            f"👋 **Thanks for inviting me to {guild.name}!**\n\n"
            f"⚠️ **Important Setup Action Required:**\n"
            f"To allow me to effectively moderate or manage users, my integration role (**{bot_role.name}**) "
            f"must be moved to the **very top** of your server's role settings hierarchy.\n\n"
            f"**How to fix:**\n"
            f"1. Go to **Server Settings** > **Roles**.\n"
            f"2. Locate the **{bot_role.name}** role.\n"
            f"3. Click and drag it above your staff/moderator roles.\n"
            f"4. Click **Save Changes**."
        )
        
        # Attempt to DM the server owner
        try:
            await guild.owner.send(msg)
        except discord.Forbidden:
            # Fallback: Find the first available system or text channel to alert staff
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(f"⚠️ **Notice to Server Owner ({guild.owner.mention}):**\n\n{msg}")
                    break


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