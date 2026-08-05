import discord
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll a dice with a specified number of sides.")
    async def roll(self, interaction: discord.Interaction, sides: int):
        if sides < 1:
            await interaction.response.send_message("❌ The number of sides must be at least 1.", ephemeral=True)
            return
        
        import random
        result = random.randint(1, sides)
        await interaction.response.send_message(f"🎲 You rolled a {result} on a {sides}-sided dice!", ephemeral=True)

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def coinflip(self, interaction: discord.Interaction):
        import random
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"🪙 The coin landed on **{result}**!", ephemeral=True)

    