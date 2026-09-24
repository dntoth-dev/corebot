import discord
from discord.ext import commands
import config
from database import SupabaseManager

class MyBot(commands.Bot):
    def __init__(self):
        # Initialize default intents (add members intent if tracking counts accurately)
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        
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
            "cogs.security",
            "cogs.fun"
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
async def on_guild_join(guild: discord.Guild):
    # Copy global commands to the newly joined server, then sync
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"Synced commands to new guild: {guild.name}")

    # Register guild to database at join
    guild_data = {"guild_name": guild.name, "guild_id": guild.id}
    if bot.db.client:
        bot.db.client.table("server_settings").upsert(guild_data).execute()

    # Send a message to the server about role hiererarchy requirements
    msg = (
        f"👋 **Thanks for inviting me to {guild.name}!**\n\n"
        f"⚠️ **Important Setup Action Required:**\n"
        f"To allow me to effectively moderate or manage users, my integration role (**{guild.me.top_role.name}**) "
        f"must be moved to the **very top** of your server's role settings hierarchy.\n\n"
        f"**How to fix:**\n"
        f"1. Go to **Server Settings** > **Roles**.\n"
        f"2. Locate the **{guild.me.top_role.name}** role.\n"
        f"3. Click and drag it above your staff/moderator roles.\n"
        f"4. Click **Save Changes**.\n"
        f"For other information and commands, use the `/help` command, where you can also join my support server!"
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

@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    # Only update the database if the name itself was modified
    if before.name != after.name:
        payload = {
            "guild_id": after.id,
            "guild_name": after.name
        }
        if bot.db.client:
            bot.db.client.table("server_settings").upsert(payload).execute()
 

if __name__ == "__main__":
    bot.run(config.TOKEN)