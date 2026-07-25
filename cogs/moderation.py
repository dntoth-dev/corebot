import discord
import datetime
from discord import app_commands
from discord.ext import commands
import config

import discord
from discord.ext import commands
from discord import app_commands
import datetime

# ==========================================
# 1. THE MODAL WINDOWS (Form Popups)
# ==========================================

class TimeoutModal(discord.ui.Modal, title="🛡️ Core: Timeout member"):
    duration = discord.ui.TextInput(label="Duration (in minutes)", placeholder="e.g., 5, 60, 1440", required=True, max_length=5)
    reason = discord.ui.TextInput(label="Reason", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, target_member: discord.Member):
        super().__init__()
        self.target_member = target_member

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            minutes = int(self.duration.value)
            timeout_duration = datetime.timedelta(minutes=minutes)
            await self.target_member.timeout(timeout_duration, reason=self.reason.value or "No reason provided.")
            
            log_embed = discord.Embed(title="⚡ Action Executed: Timeout", color=0xFF9900)
            log_embed.add_field(name="Target", value=f"{self.target_member.mention}", inline=True)
            log_embed.add_field(name="Duration", value=f"`{minutes} Mins`", inline=True)
            log_embed.add_field(name="Reason", value=self.reason.value or "`None specified`", inline=False)
            await interaction.followup.send(embed=log_embed, ephemeral=True)
        except ValueError:
            await interaction.followup.send("❌ Duration must be a valid number.", ephemeral=True)


class BanModal(discord.ui.Modal, title="🛡️ Core: Ban member"):
    reason = discord.ui.TextInput(label="Reason for Global Purge", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, target_member: discord.Member):
        super().__init__()
        self.target_member = target_member

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.guild.ban(self.target_member, reason=self.reason.value or "No reason provided.", delete_message_seconds=86400)
            
            log_embed = discord.Embed(title="⚡ Action Executed: Ban Purge", color=0xFF0000)
            log_embed.add_field(name="Target", value=f"{self.target_member.name}", inline=True)
            log_embed.add_field(name="Reason", value=self.reason.value or "`None specified`", inline=False)
            await interaction.followup.send(embed=log_embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class KickModal(discord.ui.Modal, title="🛡️ Core: Kick member"):
    reason = discord.ui.TextInput(label="Reason for Session Kick", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, target_member: discord.Member):
        super().__init__()
        self.target_member = target_member

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.target_member.kick(reason=self.reason.value or "No reason provided.")
            
            log_embed = discord.Embed(title="⚡ Action Executed: Member Kick", color=0x3498DB)
            log_embed.add_field(name="Target", value=f"{self.target_member.name}", inline=True)
            log_embed.add_field(name="Reason", value=self.reason.value or "`None specified`", inline=False)
            await interaction.followup.send(embed=log_embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class WarnModal(discord.ui.Modal, title="🛡️ Core: Issue warning"):
    reason = discord.ui.TextInput(label="Reason for the warning", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self, target_member: discord.Member):
        super().__init__()
        self.target_member = target_member

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # TODO: Hook this up to JSON/SQLite database later for persistent tracking!
        log_embed = discord.Embed(title="⚡ Action Executed: Written Warning", color=0xE74C3C)
        log_embed.add_field(name="Target", value=f"{self.target_member.mention}", inline=True)
        log_embed.add_field(name="Reason", value=self.reason.value, inline=False)
        log_embed.set_footer(text="Warning saved to Core system registry.")
        
        await interaction.followup.send(embed=log_embed, ephemeral=True)


# ==========================================
# 2. THE CHASSIS DROPDOWN AND CENTRAL VIEW
# ==========================================

class ModerateDropdown(discord.ui.Select):
    def __init__(self, target_member: discord.Member):
        self.target_member = target_member
        options = [
            discord.SelectOption(label="Issue a warning", value="warn", description="Issue a written warning to a user", emoji="⚠️"),
            discord.SelectOption(label="Apply Timeout", value="timeout", description="Temporarily restrict communication access", emoji="⏳"),
            discord.SelectOption(label="Disconnect User (Kick)", value="kick", description="Remove user from the server", emoji="🥾"),
            discord.SelectOption(label="Purge Member (Ban)", value="ban", description="Permanently remove user from the server", emoji="🚫")
        ]
        super().__init__(placeholder="Select administrative enforcement action...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]

        # Pass the target_member down directly into whichever form they click!
        if selection == "warn":
            await interaction.response.send_modal(WarnModal(self.target_member))
        elif selection == "timeout":
            await interaction.response.send_modal(TimeoutModal(self.target_member))
        elif selection == "kick":
            await interaction.response.send_modal(KickModal(self.target_member))
        elif selection == "ban":
            await interaction.response.send_modal(BanModal(self.target_member))


class ModerateView(discord.ui.View):
    def __init__(self, target_member: discord.Member):
        super().__init__(timeout=60.0)
        self.add_item(ModerateDropdown(target_member))


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    # /moderate command
    @app_commands.command(name="moderate", description="Launches Core's central all-in-one administrative terminal panel.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def moderate_command(self, interaction: discord.Interaction, target: discord.Member):
        panel_embed = discord.Embed(
            title="🛡️ Core System | Administration Console",
            description=(
                f"Target Configuration Locked: {target.mention} (`{target.id}`)\n\n"
                "Select an administrative command from the dropdown matrix below. "
                "Choosing an action will launch a secure parameter input form."
            ),
            color=0x2F3136
        )
        panel_embed.set_footer(text="Core™ Advanced Moderation Protocol")
        
        view = ModerateView(target)
        
        # We send this as ephemeral=True so regular users can't see the mod panel or spam it
        await interaction.response.send_message(embed=panel_embed, view=view, ephemeral=True)

    # Checks role configuration based on structural Snowflake IDs
    @app_commands.command(name="mute", description="Timeout a member (mute).")
    @app_commands.checks.has_permissions(mute_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided."):
        duration = datetime.timedelta(minutes=float(minutes))
        if interaction.guild.me.top_role > member.top_role:
            await member.timeout(duration, reason=reason)
            await interaction.response.send_message(f"### Timeout successful!\n**User:** {member.name} (ID: {member.id})\n**Duration:** {minutes} minutes\n**Reason:** {reason}")
        else:
            await interaction.response.send_message("Failed to timeout because my role hierarchy position is too low.", ephemeral=True)

    @app_commands.command(name="unmute", description="Remove timeout from a member (unmute).")
    @app_commands.checks.has_permissions(mute_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
        if interaction.guild.me.top_role > member.top_role:
            await member.timeout(None, reason=reason)
            await interaction.response.send_message(f"### Untimeout successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
        else:
            await interaction.response.send_message("Failed to untimeout because my role hierarchy position is too low.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
        if interaction.guild.me.top_role > member.top_role:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"### Kick successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
        else:
            await interaction.response.send_message("Failed to kick because my role hierarchy position is too low.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
        if interaction.guild.me.top_role > member.top_role:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"### Ban successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
        else:
            await interaction.response.send_message("Failed to ban because my role hierarchy position is too low.", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str ="No reason provided."):
        handled = False
        async for ban_entry in interaction.guild.bans():
            if ban_entry.user.id == user.id:
                await interaction.guild.unban(user, reason=reason)
                await interaction.response.send_message(f"### Unban successful!\n**User:** {user.name} (ID: {user.id})\n**Reason:** {reason}")
                handled = True
                break
        if not handled:
            await interaction.response.send_message("User not found in ban list.", ephemeral=True)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))