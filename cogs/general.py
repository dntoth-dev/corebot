import discord
from discord import app_commands
from discord.ext import commands
import config


# region Elements of the /help command
class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Core System", value="general", description="System configurations", emoji="🔳"),
            discord.SelectOption(label="Moderation Suite", value="moderation", description="Administrative tools", emoji="🛡️"),
            discord.SelectOption(label="YouTube Tracker", value="youtube", description="Notification engines", emoji="📺"),
            discord.SelectOption(label="Entertainment", value="fun", description="Community games", emoji="🎲")
        ]
        super().__init__(placeholder="Select a module engine to inspect...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        
        cog_mapping = {
            "general": "General",
            "moderation": "Moderation",
            "youtube": "YouTube",
            "fun": "Fun"
        }
        
        # Look up the true class name, fallback to title-case if not found
        cog_name = cog_mapping.get(selection, selection.title())
        
        # Fetch the active instance from the bot tree
        target_cog = self.bot.get_cog(cog_name)
        
        updated_embed = discord.Embed(color=0x2F3136)
        updated_embed.set_footer(text="Core™ • Dynamic Documentation • Powered by QuantumStrike")

        # 2. If the cog isn't loaded yet, show a clean loading/fallback message
        if not target_cog:
            updated_embed.title = f"⚠️ {cog_name} Module Offline"
            updated_embed.description = "This engine cluster is currently not initialized or loaded."
            return await interaction.response.edit_message(embed=updated_embed, view=self.view)

        # 3. Dynamic Generation: Pull descriptions straight from your code!
        updated_embed.title = f"📦 {cog_name} Commands"
        updated_embed.description = target_cog.__doc__ or "Available sub-system routines:"

        # 4. Loop through every command registered inside that specific Cog automatically
        # Works perfectly for standard slash commands (app_commands)
        for command in target_cog.get_app_commands():
            # Dynamically format signature layout: /command_name [param1] [param2]
            param_list = " ".join([f"[{param.name}]" for param in command.parameters])
            command_signature = f"`/{command.name} {param_list}`".strip()
            
            # Extract the actual description you wrote in the command's decorator!
            command_description = command.description or "No documentation provided."
            
            updated_embed.add_field(
                name=command_signature, 
                value=command_description, 
                inline=False
            )

        await interaction.response.edit_message(embed=updated_embed, view=self.view)
class HelpMenuView(discord.ui.View):
    def __init__(self, bot:commands.Bot):
        super().__init__(timeout=120.0) # Active for 2 minutes
        self.add_item(HelpDropdown(bot))
        
        # Keep your clean URL button linking to your worker address
        self.add_item(discord.ui.Button(
            label="Launch Core Control Panel", 
            url="https://core-bot.pages.dev/", 
            style=discord.ButtonStyle.link,
            emoji="🚀"
        ))

    async def on_timeout(self):
        # Prevent "interaction failed" issues by cleanly disabling the dropdown when inactive
        for item in self.children:
            if isinstance(item, discord.ui.Select):
                item.disabled = True
        # If the message still exists, this keeps the UI clean without leaving broken selectors
        pass
# endregion

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Open the interactive bot menu.")
    async def help_command(self, interaction: discord.Interaction):
        # Build the initial aesthetically pleasing Embed
        embed = discord.Embed(
            title="🔐 Welcome to Core.",
            description="Control your entire community dashboard natively inside the chat window. Select a category below to get started.",
            color=0x2F3136 # Sleek, near-invisible dark mode background color
        )
        
        # Add visual components like images, thumbnails, and footers
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Powered by QuantumStrike™")
        
        # Initialize our custom button/dropdown layout
        view = HelpMenuView(self.bot)
        
        # Send the beautiful integrated layout back to the user
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="hello", description="Says hello to the user.")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hello, {interaction.user.mention}!')

    @app_commands.command(name="pingsb", description="Returns the bot's latency.")
    async def pingsb(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Pong! {int(self.bot.latency * 1000)}ms')

    @app_commands.command(name="am_i_shadow", description="Returns if the user matches target configuration.")
    async def am_i_shadow(self, interaction: discord.Interaction):
        if str(interaction.user.id) == config.SHADOW_ID:
            await interaction.response.send_message(f'Yes, you are {config.SHADOW}.')
        else:
            await interaction.response.send_message(f"You ain't {config.SHADOW} :(")

    @app_commands.command(name="membercount", description="Returns the number of members on the server.")
    async def membercount(self, interaction: discord.Interaction):
        if interaction.guild:
            await interaction.response.send_message(f'The server has {interaction.guild.member_count} members!')
        else:
            await interaction.response.send_message("This command must be run within a server.", ephemeral=True)

    @app_commands.command(name='commands', description='View the current available commands of the bot')
    async def commands_list(self, interaction: discord.Interaction):
        commands_objs = self.bot.tree.get_commands(guild=config.GUILD_OBJ)
        command_list = "\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in commands_objs])
        await interaction.response.send_message(f"### Current Commands:\n{command_list}")



        
async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))