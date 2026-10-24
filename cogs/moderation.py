import discord
import datetime
from discord import app_commands
from discord.ext import commands
import config
import datetime


# ==========================================
# 1. THE MODAL WINDOWS (Form Popups)
# ==========================================

class TimeoutModal(discord.ui.Modal, title="🛡️ Core: Timeout member"):
    duration = discord.ui.TextInput(label="Duration (in minutes)", placeholder="e.g., 5, 60, 1440", required=True, max_length=5)
    reason = discord.ui.TextInput(label="Reason", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, target_member: discord.Member, bot):
        super().__init__()
        self.target_member = target_member
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Check permissions at execution time to ensure safety
        if not interaction.user.guild_permissions.mute_members:
            await interaction.followup.send("❌ You no longer have permission to timeout members.", ephemeral=True)
            return

        if interaction.guild.me.top_role <= self.target_member.top_role:
            await interaction.followup.send("❌ Cannot timeout this user. My role hierarchy position is too low.", ephemeral=True)
            return
        
        try:
            minutes = int(self.duration.value)
            timeout_duration = datetime.timedelta(minutes=minutes)
            await self.target_member.timeout(timeout_duration, reason=self.reason.value or "No reason provided.")
            
            # --- Timeout confirm ---
            confirmation_embed = discord.Embed(title="⚡ Action Executed: Timeout", color=0xFF9900)
            confirmation_embed.add_field(name="Target", value=f"{self.target_member.mention}", inline=True)
            confirmation_embed.add_field(name="Duration", value=f"`{minutes} Mins`", inline=True)
            confirmation_embed.add_field(name="Reason", value=self.reason.value or "`None specified`", inline=False)
            await interaction.followup.send(embed=confirmation_embed, ephemeral=True)
            
            # region logging
            logging_config = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            logging_settings = logging_config.data[0] if logging_config.data else None
            if logging_settings is not None:
                logging_enabled = logging_settings.get("logging_enabled")
                if logging_enabled:
                    logging_channel_id = logging_settings.get("logging_channel_id")
                    log_embed = discord.Embed(
                                title=f"{self.target_member.name} was muted.",
                                description=(
                                    f"**Mute duration:** {minutes} minutes\n"
                                    f"**Reason:** {self.reason.value}\n\n"
                                    f"Member ID: {self.target_member.id}\n"
                                    f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                ),
                                color=discord.Color.dark_grey()
                            )
                    log_embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Robust Channel Retrieval
                    logging_channel = interaction.guild.get_channel(logging_channel_id)
                    if not logging_channel:
                        try:
                            logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                        except discord.HTTPException:
                            await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                            return
                    try:
                        log = await logging_channel.send(embed=log_embed)
                    except discord.Forbidden:
                        await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                        return
                else: return
            else: return
            # endregion
        except ValueError:
            await interaction.followup.send("❌ Duration must be a valid number.", ephemeral=True)
        except Exception as e:
            print(f"Failed to timeout member with /moderate. Error: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class BanModal(discord.ui.Modal, title="🛡️ Core: Ban member"):
    reason = discord.ui.TextInput(label="Reason for Ban", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, target_member: discord.Member, bot):
        super().__init__()
        self.target_member = target_member
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        if not interaction.user.guild_permissions.ban_members:
            await interaction.followup.send("❌ You no longer have permission to ban members.", ephemeral=True)
            return

        if interaction.guild.me.top_role <= self.target_member.top_role:
            await interaction.followup.send("❌ Cannot ban this user. My role hierarchy position is too low.", ephemeral=True)
            return
        try:
            await interaction.guild.ban(self.target_member, reason=self.reason.value or "No reason provided.", delete_message_seconds=86400)
            
            confirmation_embed = discord.Embed(title="⚡ Action Executed: Ban Purge", color=0xFF0000)
            confirmation_embed.add_field(name="Target", value=f"{self.target_member.name}", inline=True)
            confirmation_embed.add_field(name="Reason", value=self.reason.value or "`None specified`", inline=False)
            await interaction.followup.send(embed=confirmation_embed, ephemeral=True)
            
            # region logging
            logging_config = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            logging_settings = logging_config.data[0] if logging_config.data else None
            if logging_settings is not None:
                logging_enabled = logging_settings.get("logging_enabled")
                if logging_enabled:
                    logging_channel_id = logging_settings.get("logging_channel_id")
                    log_embed = discord.Embed(
                                title=f"{self.target_member.name} was banned.",
                                description=(
                                    f"**Reason:** {self.reason.value}\n\n"
                                    f"Member ID: {self.target_member.id}\n"
                                    f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                ),
                                color=discord.Color.dark_grey()
                            )
                    log_embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Robust Channel Retrieval
                    logging_channel = interaction.guild.get_channel(logging_channel_id)
                    if not logging_channel:
                        try:
                            logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                        except discord.HTTPException:
                            await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                            return
                    try:
                        log = await logging_channel.send(embed=log_embed)
                    except discord.Forbidden:
                        await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                        return
                else: return
            else: return
            # endregion
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class KickModal(discord.ui.Modal, title="🛡️ Core: Kick member"):
    reason = discord.ui.TextInput(label="Reason for Kick", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, target_member: discord.Member, bot):
        super().__init__()
        self.target_member = target_member
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.guild_permissions.kick_members:
            await interaction.followup.send("❌ You no longer have permission to kick members.", ephemeral=True)
            return

        if interaction.guild.me.top_role <= self.target_member.top_role:
            await interaction.followup.send("❌ Cannot kick this user. My role hierarchy position is too low.", ephemeral=True)
            return

        try:
            await self.target_member.kick(reason=self.reason.value or "No reason provided.")
            
            confirmation_embed = discord.Embed(title="⚡ Action Executed: Member Kick", color=0x3498DB)
            confirmation_embed.add_field(name="Target", value=f"{self.target_member.name}", inline=True)
            confirmation_embed.add_field(name="Reason", value=self.reason.value or "`None specified`", inline=False)
            await interaction.followup.send(embed=confirmation_embed, ephemeral=True)
            
            # region logging
            logging_config = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            logging_settings = logging_config.data[0] if logging_config.data else None
            if logging_settings is not None:
                logging_enabled = logging_settings.get("logging_enabled")
                if logging_enabled:
                    logging_channel_id = logging_settings.get("logging_channel_id")
                    log_embed = discord.Embed(
                                title=f"{self.target_member.name} was kicked.",
                                description=(
                                    f"**Reason:** {self.reason.value}\n\n"
                                    f"Member ID: {self.target_member.id}\n"
                                    f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                ),
                                color=discord.Color.dark_grey()
                            )
                    log_embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Robust Channel Retrieval
                    logging_channel = interaction.guild.get_channel(logging_channel_id)
                    if not logging_channel:
                        try:
                            logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                        except discord.HTTPException:
                            await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                            return
                    try:
                        log = await logging_channel.send(embed=log_embed)
                    except discord.Forbidden:
                        await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                        return
                else: return
            else: return
            # endregion
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class WarnModal(discord.ui.Modal, title="🛡️ Core: Issue warning"):
    reason = discord.ui.TextInput(label="Reason for the warning", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self, target_member: discord.Member, bot):
        super().__init__()
        self.target_member = target_member
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.followup.send("❌ You no longer have permission to moderate members.", ephemeral=True)
            return
        
        # TODO: Hook this up to JSON/SQLite database later for persistent tracking!
        confirmation_embed = discord.Embed(title="⚡ Action Executed: Written Warning", color=0xE74C3C)
        confirmation_embed.add_field(name="Target", value=f"{self.target_member.mention}", inline=True)
        confirmation_embed.add_field(name="Reason", value=self.reason.value, inline=False)
        await interaction.followup.send(embed=confirmation_embed, ephemeral=True)
        
        # region DATABASE STORING
        warn_payload = {"guild_id": interaction.guild.id, "created_at": datetime.datetime.now(datetime.timezone.utc), "user_id": self.target_member.id, "moderator_id": interaction.user.id, "reason": self.reason.value}
        await self.bot.db.client.table("warnings").upsert(warn_payload).execute()
        # endregion
        
        
        # region logging
        logging_config = await self.bot.db.client.table("server_settings") \
                                        .select("logging_enabled, logging_channel_id") \
                                        .eq("guild_id", interaction.guild.id) \
                                        .execute()
                                        
        logging_settings = logging_config.data[0] if logging_config.data else None
        if logging_settings is not None:
            logging_enabled = logging_settings.get("logging_enabled")
            if logging_enabled:
                logging_channel_id = logging_settings.get("logging_channel_id")
                embed = discord.Embed(
                            title=f"{self.target_member.name} was warned.",
                            description=(
                                f"**Reason:** {self.reason.value}\n\n"
                                f"Member ID: {self.target_member.id}\n"
                                f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                            ),
                            color=discord.Color.dark_grey()
                        )
                embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                
                # Robust Channel Retrieval
                logging_channel = interaction.guild.get_channel(logging_channel_id)
                if not logging_channel:
                    try:
                        logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                    except discord.HTTPException:
                        await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                        return
                try:
                    log = await logging_channel.send(embed=embed)
                except discord.Forbidden:
                    await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                    return
            else: return
        else: return
        # endregion


# ==========================================
# 2. THE CHASSIS DROPDOWN AND CENTRAL VIEW
# ==========================================

class ModerateDropdown(discord.ui.Select):
    def __init__(self, interaction:discord.Interaction, target_member: discord.Member, bot):
        self.target_member = target_member
        self.bot = bot
        options = []

        user_permissions = interaction.permissions
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        
        # Build options dynamically based on native server permissions
        if user_permissions.moderate_members or is_owner:
            options.append(discord.SelectOption(label="Issue a warning", value="warn", description="Issue a written warning to a user", emoji="⚠️"))
            
        if user_permissions.mute_members or is_owner:
            options.append(discord.SelectOption(label="Apply Timeout", value="timeout", description="Temporarily restrict communication access", emoji="⏳"))
            
        if user_permissions.kick_members or is_owner:
            options.append(discord.SelectOption(label="Remove member (Kick)", value="kick", description="Remove user from the server", emoji="🥾"))
            
        if user_permissions.ban_members or is_owner:
            options.append(discord.SelectOption(label="Purge Member (Ban)", value="ban", description="Permanently remove user from the server", emoji="🚫"))

        # Fallback if the user has no permissions and is not the owner
        if not options:
            options.append(discord.SelectOption(label="No Actions Available", value="none", description="You lack administrative permissions.", emoji="❌"))

        super().__init__(placeholder="Select administrative enforcement action...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]

        if selection == "none":
            await interaction.response.send_message("❌ You do not have permissions to perform any actions.", ephemeral=True)
            return

        # Double check hierarchy before opening form input overlays
        if selection in ["timeout", "kick", "ban"]:
            if interaction.guild.me.top_role <= self.target_member.top_role:
                await interaction.response.send_message("❌ Cannot execute action: This user's role hierarchy matches or exceeds mine.", ephemeral=True)
                return

        if selection == "warn":
            await interaction.response.send_modal(WarnModal(self.target_member, self.bot))
        elif selection == "timeout":
            await interaction.response.send_modal(TimeoutModal(self.target_member, self.bot))
        elif selection == "kick":
            await interaction.response.send_modal(KickModal(self.target_member, self.bot))
        elif selection == "ban":
            await interaction.response.send_modal(BanModal(self.target_member, self.bot))


class ModerateView(discord.ui.View):
    def __init__(self, interaction:discord.Interaction, target_member: discord.Member, bot):
        super().__init__(timeout=60.0)
        # Pass permissions right down into the dropdown component
        self.add_item(ModerateDropdown(interaction, target_member, bot))

# --- | Moderation Class | ---
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # /moderate command
    @app_commands.command(name="moderate", description="Launches Core's central all-in-one administrative terminal panel.")
    @app_commands.default_permissions(moderate_members=True)
    async def moderate_command(self, interaction: discord.Interaction, target: discord.Member):
        
        if not interaction.guild:
            return
        
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.moderate_members or is_owner):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return
        
        panel_embed = discord.Embed(
            title="🛡️ Core System | Administration Console",
            description=(
                f"Target Member Locked: {target.mention} (`{target.id}`)\n\n"
                "Select an administrative command from the dropdown matrix below. "
                "Choosing an action will launch a secure parameter input form."
            ),
            color=0x2F3136
        )
        panel_embed.set_footer(text="Advanced Moderation Protocol")
        
        # Pull permissions directly from the interaction environment
        view = ModerateView(interaction, target, self.bot)
        await interaction.response.send_message(embed=panel_embed, view=view, ephemeral=True)

    @moderate_command.error
    async def moderate_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message("❌ I do not have permission to mute members. Please check my server roles.", ephemeral=True)
        else:
            print(f"An error occurred in /moderate: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ An unexpected error occurred.", ephemeral=True)












    
    # Single-action moderation commands below...
    
    # warn..
    
    @app_commands.command(name="mute", description="Timeout a member (mute).")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided."):
        
        if not interaction.guild:
            return
        
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.moderate_members or is_owner):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        duration = datetime.timedelta(minutes=float(minutes))
        if interaction.guild.me.top_role > member.top_role:
            await member.timeout(duration, reason=reason)
            await interaction.response.send_message(f"### Timeout successful!\n**User:** {member.name} (ID: {member.id})\n**Duration:** {minutes} minutes\n**Reason:** {reason}")
            # region logging
            logging_config = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            logging_settings = logging_config.data[0] if logging_config.data else None
            if logging_settings is not None:
                logging_enabled = logging_settings.get("logging_enabled")
                if logging_enabled:
                    logging_channel_id = logging_settings.get("logging_channel_id")
                    embed = discord.Embed(
                                title=f"{member.name} was muted.",
                                description=(
                                    f"**Mute duration:** {minutes} minutes\n"
                                    f"**Reason:** {reason}\n\n"
                                    f"Member ID: {member.id}\n"
                                    f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                ),
                                color=discord.Color.dark_grey()
                            )
                    embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Robust Channel Retrieval
                    logging_channel = interaction.guild.get_channel(logging_channel_id)
                    if not logging_channel:
                        try:
                            logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                        except discord.HTTPException:
                            await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                            return
                    try:
                        log = await logging_channel.send(embed=embed)
                    except discord.Forbidden:
                        await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                        return
                else: return
            else: return
            # endregion
        else:
            await interaction.response.send_message("Failed to timeout because my role hierarchy position is too low.", ephemeral=True)

    @mute.error
    async def mute_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message("❌ I do not have permission to mute members. Please check my server roles.", ephemeral=True)
        else:
            print(f"An error occurred in /mute: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ An unexpected error occurred. Check permissions.", ephemeral=True)












    @app_commands.command(name="unmute", description="Remove timeout from a member (unmute).")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
        
        if not interaction.guild:
            return
        
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.moderate_members or is_owner):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        if interaction.guild.me.top_role > member.top_role:
            await member.timeout(None, reason=reason)
            await interaction.response.send_message(f"### Untimeout successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
            
            # region logging
            logging_config = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            logging_settings = logging_config.data[0] if logging_config.data else None
            if logging_settings is not None:
                logging_enabled = logging_settings.get("logging_enabled")
                if logging_enabled:
                    logging_channel_id = logging_settings.get("logging_channel_id")
                    embed = discord.Embed(
                                title=f"{member.name} was unmuted.",
                                description=(
                                    f"**Reason:** {reason}\n\n"
                                    f"Member ID: {member.id}\n"
                                    f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                ),
                                color=discord.Color.dark_grey()
                            )
                    embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Robust Channel Retrieval
                    logging_channel = interaction.guild.get_channel(logging_channel_id)
                    if not logging_channel:
                        try:
                            logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                        except discord.HTTPException:
                            await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                            return
                    try:
                        log = await logging_channel.send(embed=embed)
                    except discord.Forbidden:
                        await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                        return
                else: return
            else: return
            # endregion
        else:
            await interaction.response.send_message("Failed to untimeout because my role hierarchy position is too low.", ephemeral=True)

    @unmute.error
    async def unmute_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message("❌ I do not have permission to unmute members. Please check my server roles.", ephemeral=True)
        else:
            print(f"An error occurred in /unmute: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ An unexpected error occurred. Check permissions.", ephemeral=True)















    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
        
        if not interaction.guild:
            return
        
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.kick_members or is_owner):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        if interaction.guild.me.top_role > member.top_role:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"### Kick successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
            
            # region logging
            logging_config = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            logging_settings = logging_config.data[0] if logging_config.data else None
            if logging_settings is not None:
                logging_enabled = logging_settings.get("logging_enabled")
                if logging_enabled:
                    logging_channel_id = logging_settings.get("logging_channel_id")
                    embed = discord.Embed(
                                title=f"{member.name} was kicked.",
                                description=(
                                    f"**Reason:** {reason}\n\n"
                                    f"Member ID: {member.id}\n"
                                    f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                ),
                                color=discord.Color.dark_grey()
                            )
                    embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Robust Channel Retrieval
                    logging_channel = interaction.guild.get_channel(logging_channel_id)
                    if not logging_channel:
                        try:
                            logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                        except discord.HTTPException:
                            await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                            return
                    try:
                        log = await logging_channel.send(embed=embed)
                    except discord.Forbidden:
                        await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                        return
                else: return
            else: return
            # endregion
        else:
            await interaction.response.send_message("Failed to kick because my role hierarchy position is too low.", ephemeral=True)

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message("❌ I do not have permission to kick members. Please check my server roles.", ephemeral=True)
        else:
            print(f"An error occurred in /kick: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ An unexpected error occurred. Check permissions.", ephemeral=True)















    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
        
        if not interaction.guild:
            return
        
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.ban_members or is_owner):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        if interaction.guild.me.top_role > member.top_role:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"### Ban successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
            
            # region logging
            logging_config = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            logging_settings = logging_config.data[0] if logging_config.data else None
            if logging_settings is not None:
                logging_enabled = logging_settings.get("logging_enabled")
                if logging_enabled:
                    logging_channel_id = logging_settings.get("logging_channel_id")
                    embed = discord.Embed(
                                title=f"{member.name} was banned.",
                                description=(
                                    f"**Reason:** {reason}\n\n"
                                    f"Member ID: {member.id}\n"
                                    f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                ),
                                color=discord.Color.dark_grey()
                            )
                    embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Robust Channel Retrieval
                    logging_channel = interaction.guild.get_channel(logging_channel_id)
                    if not logging_channel:
                        try:
                            logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                        except discord.HTTPException:
                            await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                            return
                    try:
                        log = await logging_channel.send(embed=embed)
                    except discord.Forbidden:
                        await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                        return
                else: return
            else: return
            # endregion
        else:
            await interaction.response.send_message("Failed to ban because my role hierarchy position is too low.", ephemeral=True)

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message("❌ I do not have permission to ban members. Please check my server roles.", ephemeral=True)
        else:
            print(f"An error occurred in /ban: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ An unexpected error occurred. Check permissions.", ephemeral=True)















    @app_commands.command(name="unban", description="Unban a member from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided."):
        
        if not interaction.guild:
            return
        
        is_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
        if not (interaction.permissions.ban_members or is_owner):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        handled = False
        async for ban_entry in interaction.guild.bans():
            if ban_entry.user.id == user.id:
                await interaction.guild.unban(user, reason=reason)
                await interaction.response.send_message(f"### Unban successful!\n**User:** {user.name} (ID: {user.id})\n**Reason:** {reason}")
                handled = True
                
                # region logging
                logging_config = await self.bot.db.client.table("server_settings") \
                                                .select("logging_enabled, logging_channel_id") \
                                                .eq("guild_id", interaction.guild.id) \
                                                .execute()
                                                
                logging_settings = logging_config.data[0] if logging_config.data else None
                if logging_settings is not None:
                    logging_enabled = logging_settings.get("logging_enabled")
                    if logging_enabled:
                        logging_channel_id = logging_settings.get("logging_channel_id")
                        embed = discord.Embed(
                                    title=f"{user.name} was unbanned.",
                                    description=(
                                        f"**Reason:** {reason}\n\n"
                                        f"Member ID: {user.id}\n"
                                        f"Moderator: {interaction.user} (ID: {interaction.user.id})"
                                    ),
                                    color=discord.Color.dark_grey()
                                )
                        embed.set_footer(text=f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                        
                        # Robust Channel Retrieval
                        logging_channel = interaction.guild.get_channel(logging_channel_id)
                        if not logging_channel:
                            try:
                                logging_channel = await interaction.guild.fetch_channel(logging_channel_id)
                            except discord.HTTPException:
                                await interaction.followup.send("⚠️ Logging error: Could not find or access the configured logging channel.\n""-# If the channel does not exist anymore, reconfigure or disable logging with the `/logging` command.", ephemeral=True)
                                return
                        try:
                            log = await logging_channel.send(embed=embed)
                        except discord.Forbidden:
                            await interaction.followup.send("⚠️ Logging error: Bot lacks permission to send or pin messages in the logging channel.\n""-# Ensure that the bot has permissions to type in the channel and that the channel type is not forum, rules or announcements.", ephemeral=True)
                            return
                    else: return
                else: return
                # endregion
                
                break
        if not handled:
            await interaction.response.send_message("User not found in ban list.", ephemeral=True)

    @unban.error
    async def unban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message("❌ I do not have permission to unban members. Please check my server roles.", ephemeral=True)
        else:
            print(f"An error occurred in /unban: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ An unexpected error occurred. Check permissions.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))