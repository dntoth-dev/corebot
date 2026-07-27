import discord
from discord import app_commands
from discord.ext import commands
import config

# all dev commands should be ! prefix. Is it neccessary to be ! ? Is it visible in the cmd tree?

class Developer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Custom local check validating Developer Snowflake configurations
    async def is_dev(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == config.DEV_ID:
            return True
        await interaction.response.send_message("❌ This command is restricted to developer access only.", ephemeral=True)
        return False

    # Should be ! prefix
    @app_commands.command(name="clear_slash", description="Clear all slash commands in case of a bug.")
    async def clear_slash(self, interaction: discord.Interaction):
        if not await self.is_dev(interaction):
            return

        self.bot.tree.clear_commands(guild=None)
        self.bot.tree.clear_commands(guild=config.GUILD_OBJ)
        await self.bot.tree.sync()
        await self.bot.tree.sync(guild=config.GUILD_OBJ)
        await interaction.response.send_message("Cleared application commands. System reboot recommended.")

    # Should be ! prefix
    @app_commands.command(name="devtest", description="Bot status test command.")
    async def devtest(self, interaction: discord.Interaction):
        if not await self.is_dev(interaction):
            return

        await interaction.response.send_message(
            "devtest check passed. Hello Developer!\n"
            f"`Gateway status: Connected | Session Identity: {self.bot.user}`"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Developer(bot))