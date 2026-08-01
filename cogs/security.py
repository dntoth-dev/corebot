import discord
from discord import app_commands
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Core configuration states
        self.sentry_enabled = False
        self.sentry_channel_id = None
        # self.staff_log_channel_id = 123456789012345678  # Replace with your actual log channel ID

    # ==========================================
    # 1. THE sentry LISTENER
    # ==========================================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots, DMs, or if the system is explicitly turned off
        if message.author.bot or not message.guild or not self.sentry_enabled:
            return

        # Check if a message hit the designated sentry channel
        if self.sentry_channel_id and message.channel.id == self.sentry_channel_id:
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
                    reason="Security Tripwire: Tripped the sentry channel.", 
                    delete_message_days=1
                )
                
                # Immediately unban them for automatic cleanup/recovery access
                await message.guild.unban(
                    target_user, 
                    reason="Core: Automatic unban."
                )
                
                # print(f"[SECURITY] sentry tripped! Purged and ban-cycled {target_user} ({target_user.id}).")
                
            except discord.HTTPException as e:
                print(f"[SECURITY ERROR] Failed to execute ban/unban cycle for {target_user}: {e}")

            """
            # Alert staff in the secure logging channel
            log_channel = message.guild.get_channel(self.staff_log_channel_id)
            if log_channel:
                await log_channel.send(
                    f"🚨 **sentry Triggered & Purged!**\n"
                    f"**User:** {target_user.mention} (`{target_user.id}`)\n"
                    f"**Action:** Executed temporary ban to wipe recent messages, then unbanned."
                )
            """

    # ==========================================
    # 2. MANAGEMENT SLASH COMMANDS
    # ==========================================
    @app_commands.command(name="sentry", description="Toggle or configure the server security sentry system.")
    @app_commands.describe(
        action="Choose to enable, disable, or set the channel for the trap.",
        channel="The text channel to use as the sentry trap (Required if action is 'set')."
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable"),
        app_commands.Choice(name="Set Channel", value="set")
    ])
    @app_commands.default_permissions(administrator=True)
    async def sentry(self, interaction: discord.Interaction, action: str, channel: discord.TextChannel = None):
        # Server owner / Admin permission bypass guard
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.administrator or is_owner):
            await interaction.response.send_message("❌ You do not have permission to manage security settings.", ephemeral=True)
            return

        if action == "enable":
            if not self.sentry_channel_id:
                await interaction.response.send_message("⚠️ Cannot enable sentry: No trap channel has been set yet. Use `/sentry action:Set Channel` first.", ephemeral=True)
                return
            
            self.sentry_enabled = True
            
            # 1. Safe Triple-Quoted String for the Embed Description
            embed = discord.Embed(
                title="🛡️ Security System Active",
                description=(
                "**DO NOT TYPE IN THIS CHANNEL.**\n\n"
                "This channel functions as an automated security tripwire designed to catch "
                "and neutralize compromised accounts, spammers, and malicious user-bots.\n\n"
                "⚠️ **Sending any message here will result in an immediate automated ban.**"
            ),
                color=discord.Color.red()
            )
            embed.set_footer(text="Automated Server Protection System")

            # 2. Robust Channel Retrieval (Handles cache misses)
            sentry_channel = interaction.guild.get_channel(self.sentry_channel_id)
            if not sentry_channel:
                try:
                    sentry_channel = await interaction.guild.fetch_channel(self.sentry_channel_id)
                except discord.HTTPException:
                    await interaction.response.send_message("❌ Error: Could not find or access the configured sentry channel.", ephemeral=True)
                    return
                
            # 3. Send and Pin the Warning
            try:
                warning_message = await sentry_channel.send(embed=embed)
                await warning_message.pin()
            except discord.Forbidden:
                await interaction.response.send_message("❌ Error: Bot lacks permission to send or pin messages in the trip channel.", ephemeral=True)
                return
            
            await interaction.response.send_message(f"🛡️ **Sentry Active:** The security tripwire is now **ON** tracking <#{self.sentry_channel_id}>.", ephemeral=True)

        elif action == "disable":
            self.sentry_enabled = False
            await interaction.response.send_message("🔓 **Sentry Deactivated:** The security tripwire is now **OFF**.", ephemeral=True)

        elif action == "set":
            if not channel:
                await interaction.response.send_message("❌ Error: You must specify a text channel when choosing 'Set Channel'.", ephemeral=True)
                return
            
            self.sentry_channel_id = channel.id
            status_text = "and is currently **ON**" if self.sentry_enabled else "but is currently **OFF** (use `/sentry action:Enable` to activate)"
            await interaction.response.send_message(f"🎯 **Sentry Configuration Updated:** The trap target has been set to {channel.mention} {status_text}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Security(bot))