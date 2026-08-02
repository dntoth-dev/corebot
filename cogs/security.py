import discord
from discord import app_commands
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Local configuration states removed! Data is now fetched dynamically per guild via self.bot.db

    # ==========================================
    # 1. THE SENTRY LISTENER
    # ==========================================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots, DMs, or if the guild context is missing
        if message.author.bot or not message.guild:
            return

        # Fetch settings for this specific server from Supabase
        try:
            settings_response = await self.bot.db.client.table("server_settings") \
                .select("sentry_enabled, sentry_channel_id") \
                .eq("guild_id", message.guild.id) \
                .execute()
            
            settings = settings_response.data[0] if settings_response.data else None
                
        except Exception as e:
            print(f"[SECURITY DATABASE ERROR] Failed to fetch settings for guild {message.guild.id}: {e}")
            return

        # If the server hasn't set up the sentry system or it's disabled, ignore
        if not settings or not settings.get("sentry_enabled"):
            return

        sentry_channel_id = settings.get("sentry_channel_id")

        # Check if a message hit the designated sentry channel trap
        if sentry_channel_id and message.channel.id == sentry_channel_id:
            # Instantly delete the triggering message
            try:
                await message.delete()
            except discord.HTTPException:
                pass

            target_user = message.author

            try:
                # Ban the user and purge their recent footprint (last 1 day of messages)
                await message.guild.ban(
                    target_user,
                    reason="Core [Sentry]: User account is suspected as spam or compromised.",
                    delete_message_days=1
                )

                # Immediately unban them for automatic cleanup/recovery access
                await message.guild.unban(
                    target_user,
                    reason="Core [Sentry] @ softban: Automatic message cleanup."
                )
            except discord.HTTPException as e:
                print(f"[SECURITY ERROR] Failed to execute ban/unban cycle for {target_user}: {e}")

    # ==========================================
    # 2. MANAGEMENT SLASH COMMANDS
    # ==========================================
    @app_commands.command(name="sentry", description="Toggle or configure the server security sentry system.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        action="Choose to enable, disable, or set the channel for the trap.",
        channel="The text channel to use as the sentry trap (Required if action is 'set')."
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable"),
        app_commands.Choice(name="Set Channel", value="set")
    ])
    async def sentry(self, interaction: discord.Interaction, action: str, channel: discord.TextChannel = None):
        await interaction.response.defer(ephemeral=True)
        
        # Server owner / Admin permission bypass guard
        is_owner = interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.administrator or is_owner):
            await interaction.followup.send("❌ You do not have permission to manage security settings.", ephemeral=True)
            return

        if interaction.guild:
            # Pull current config state from database for toggle updates
            current_settings_response = await self.bot.db.client.table("server_settings") \
                                            .select("sentry_enabled, sentry_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            current_settings = current_settings_response.data[0] if current_settings_response.data else None
            
            current_channel_id = current_settings.get("sentry_channel_id") if current_settings else None
            current_enabled = current_settings.get("sentry_enabled") if current_settings else False

        if action == "enable":
            if not current_channel_id:
                await interaction.followup.send("⚠️ Cannot enable sentry: No trap channel has been set yet. Use `/sentry action:Set Channel` first.", ephemeral=True)
                return

            # Update DB state to Enabled
            enable_payload = {"guild_id": interaction.guild.id, "sentry_enabled": True, "sentry_channel_id": current_channel_id}
            await self.bot.db.client.table("server_settings").upsert(enable_payload).execute()


            embed = discord.Embed(
                title="🔒 Security System Active",
                description=(
                    "**DO NOT TYPE IN THIS CHANNEL.**\n\n"
                    "This channel functions as an automated security tripwire designed to catch "
                    "and neutralize compromised accounts, spammers, and malicious user-bots.\n\n"
                    "⚠️ **Sending any message here will result in an immediate automated ban.**"
                ),
                color=discord.Color.red()
            )
            embed.set_footer(text="Automated Server Protection System")

            # Robust Channel Retrieval
            sentry_channel = interaction.guild.get_channel(current_channel_id)
            if not sentry_channel:
                try:
                    sentry_channel = await interaction.guild.fetch_channel(current_channel_id)
                except discord.HTTPException:
                    await interaction.followup.send("❌ Error: Could not find or access the configured sentry channel.", ephemeral=True)
                    return

            try:
                warning_message = await sentry_channel.send(embed=embed)
                await warning_message.pin()
            except discord.Forbidden:
                await interaction.followup.send("❌ Error: Bot lacks permission to send or pin messages in the trip channel.", ephemeral=True)
                return

            await interaction.followup.send(f"🔒 **Sentry Active:** The security tripwire is now **ON** tracking <#{current_channel_id}>.", ephemeral=True)

        elif action == "disable":
            # Update DB state to Disabled (passing the current channel ID to preserve it)
            
            disable_payload = {"guild_id": interaction.guild.id, "sentry_enabled": False, "sentry_channel_id": current_channel_id}
            await self.bot.db.client.table("server_settings").upsert(disable_payload).execute()
            
            await interaction.followup.send("🔓 **Sentry Deactivated:** The security tripwire is now **OFF**.", ephemeral=True)

        elif action == "set":
            if not channel:
                await interaction.followup.send("❌ Error: You must specify a text channel when choosing 'Set Channel'.", ephemeral=True)
                return

            # Upsert new channel ID to Supabase while keeping current enabled state
            set_payload = {"guild_id": interaction.guild.id, "sentry_enabled": current_enabled, "sentry_channel_id": channel.id}
            await self.bot.db.client.table("server_settings").upsert(set_payload).execute()
            
            status_text = "and is currently **ON**" if current_enabled else "but is currently **OFF** (use `/sentry action:Enable` to activate)"
            await interaction.followup.send(f"🎯 **Sentry Configuration Updated:** The trap channel has been set to {channel.mention} {status_text}.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Security(bot))