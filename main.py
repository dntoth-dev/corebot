import discord
from discord.ext import commands
import config
from database import SupabaseManager
import logging

logger = logging.getLogger("corebot")


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
    # 1. Register guild to database at join
    guild_data = {"guild_name": guild.name, "guild_id": str(guild.id)}
    if bot.db.client:
        try: 
            await bot.db.client.table("server_settings").upsert(guild_data, on_conflict="guild_id").execute()
            logger.info(f"Registered guild {guild.name} ({guild.id}) in database.")
        except Exception as e:
            logger.error(f"Failed to insert guild {guild.id} into database: {e}")
            
    # 2. Get top role safely
    top_role_name = guild.me.top_role.name if guild.me and guild.me.top_role else "Core"
            

    # Send a message to the server about role hiererarchy requirements
    msg = (
        f"👋 **Thanks for inviting me to {guild.name}!**\n\n"
        f"⚠️ **Important Setup Action Required:**\n"
        f"To allow me to effectively moderate or manage users, my integration role (**{top_role_name}**) "
        f"must be moved to the **very top** of your server's role settings hierarchy.\n\n"
        f"**How to fix:**\n"
        f"1. Go to **Server Settings** > **Roles**.\n"
        f"2. Locate the **{top_role_name}** role.\n"
        f"3. Click and drag it above your staff/moderator roles.\n"
        f"4. Click **Save Changes**.\n"
        f"For other information and commands, use the `/help` command, where you can also join my support server!"
    )
        
    # 3. Resolve server owner safely
    owner = guild.owner
    if owner is None:
        try:
            owner = await guild.fetch_member(guild.owner_id)
        except Exception:
            owner = None

    # 4. Attempt to DM owner or fall back to system/text channel
    dm_sent = False
    if owner:
        try:
            await owner.send(msg)
            dm_sent = True
        except discord.Forbidden:
            dm_sent = False

    if not dm_sent:
        owner_mention = owner.mention if owner else "Server Owner"
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(f"⚠️ **Notice to {owner_mention}:**\n\n{msg}")
                    break
                except discord.Forbidden:
                    continue

@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    # Only update the database if server name changes
    if before.name != after.name:
        payload = {
            "guild_id": str(after.id),
            "guild_name": after.name
        }
        if bot.db.client:
            try:
                await bot.db.client.table("server_settings").upsert(payload, on_conflict="guild_id").execute()
            except Exception as e:
                logger.error(f"Failed to update guild name for {after.id}: {e}")


if __name__ == "__main__":
    bot.run(config.TOKEN)