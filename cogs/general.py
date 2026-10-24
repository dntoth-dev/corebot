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
            label="Launch Core Website", 
            url=config.WEB_URL, 
            style=discord.ButtonStyle.link,
            emoji="🚀"
        ))
        
        self.add_item(discord.ui.Button(
            label="Join Support Server",
            url="https://discord.gg/RUyAChCBc6",
            style=discord.ButtonStyle.link,
            emoji="📢"
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
    def __init__(self, bot):
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
    
    # Useless
    @app_commands.command(name="hello", description="Says hello to the user.")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hello, {interaction.user.mention}!')

    @app_commands.command(name="pingcore", description="Returns the bot's latency.")
    async def pingcore(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'🏓 Pong! {int(self.bot.latency * 1000)}ms')

    @app_commands.command(name="membercount", description="Returns the number of members on the server.")
    async def membercount(self, interaction: discord.Interaction):
        if interaction.guild:
            await interaction.response.send_message(f'The server has {interaction.guild.member_count} members!')
        else:
            await interaction.response.send_message("This command must be run within a server.", ephemeral=True)



    @app_commands.command(name="logging", description="Edit action logging settings.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        action="Choose to enable, disable, or set the logging feature",
        channel="The text channel to use for logging (Required if action is 'set')."
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable"),
        app_commands.Choice(name="Set Channel", value="set")
    ])
    async def logging(self, interaction: discord.Interaction, action: str, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        
        # Server owner / Admin permission bypass guard
        if interaction.guild:
            is_owner = interaction.guild.owner_id == interaction.user.id
            if not (interaction.permissions.administrator or is_owner):
                await interaction.followup.send("❌ You do not have permission to manage logging settings.", ephemeral=True)
                return

            # Pull current config state from database for toggle updates
            current_settings_response = await self.bot.db.client.table("server_settings") \
                                            .select("logging_enabled, logging_channel_id") \
                                            .eq("guild_id", interaction.guild.id) \
                                            .execute()
                                            
            current_settings = current_settings_response.data[0] if current_settings_response.data else None
            
            current_channel_id = current_settings.get("logging_channel_id") if current_settings else None
            current_enabled = current_settings.get("logging_enabled") if current_settings else False

            if action == "enable":
                if not current_channel_id:
                    await interaction.followup.send("⚠️ Cannot enable logging: No channel for logging has been set yet. Use `/logging action:Set Channel` first.", ephemeral=True)
                    return

                # Update DB state to Enabled
                enable_payload = {"guild_id": interaction.guild.id, "logging_enabled": True, "logging_channel_id": current_channel_id}
                await self.bot.db.client.table("server_settings").upsert(enable_payload).execute()


                embed = discord.Embed(
                    title="📝 Logging was set to this channel.",
                    description=(
                        "**The logging feature was turned on and set to this channel.**\n\n"
                        "The bot logs user warnings, timeouts (mutes), kicks and bans. "
                        "`INFORMATION: In the current implementation, it is not possible to change what the bot logs.`\n\n"
                        "⚠️ **To turn off future logging, use the `/logging action:Disable` command, and follow the instructions.**"
                    ),
                    color=discord.Color.yellow()
                )
                embed.set_footer(text="Automated Server Surveillance System")

                # Robust Channel Retrieval
                logging_channel = interaction.guild.get_channel(current_channel_id)
                if not logging_channel:
                    try:
                        logging_channel = await interaction.guild.fetch_channel(current_channel_id)
                    except discord.HTTPException:
                        await interaction.followup.send("❌ Error: Could not find or access the configured logging channel.", ephemeral=True)
                        return

                try:
                    confirmation_embed = await logging_channel.send(embed=embed)
                    await confirmation_embed.pin()
                except discord.Forbidden:
                    await interaction.followup.send("❌ Error: Bot lacks permission to send or pin messages in the trip channel.", ephemeral=True)
                    return

                await interaction.followup.send(f"📝 **Logging Active:** Logging is now **ON** and set to <#{current_channel_id}>.", ephemeral=True)

            elif action == "disable":
                # Update DB state to Disabled (passing the current channel ID to preserve it)
                
                disable_payload = {"guild_id": interaction.guild.id, "logging_enabled": False, "logging_channel_id": current_channel_id}
                await self.bot.db.client.table("server_settings").upsert(disable_payload).execute()
                
                await interaction.followup.send("❗ **Logging Deactivated:** Logging is now **OFF**.", ephemeral=True)

            elif action == "set":
                if not channel:
                    await interaction.followup.send("❌ Error: You must specify a text channel when choosing 'Set Channel'.", ephemeral=True)
                    return

                # Upsert new channel ID to Supabase while keeping current enabled state
                set_payload = {"guild_id": interaction.guild.id, "logging_enabled": current_enabled, "logging_channel_id": channel.id}
                await self.bot.db.client.table("server_settings").upsert(set_payload).execute()
                
                status_text = "and is currently **ON**" if current_enabled else "but is currently **OFF** (use `/logging action:Enable` to activate)"
                await interaction.followup.send(f"📝 **Logging Configuration Updated:** Logging has been set to {channel.mention} {status_text}.", ephemeral=True)
        else: return


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))