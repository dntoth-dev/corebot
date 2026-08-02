import discord
from discord import app_commands
from discord.ext import commands
import config
from typing import Union, Optional, Literal

# all dev commands should be ! prefix. Is it neccessary to be ! ? Is it visible in the cmd tree?



class Developer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Custom local check validating Developer Snowflake configurations
    async def is_dev(self, ctx_or_interaction: Union[commands.Context, discord.Interaction]) -> bool:
        # 1. Extract the author/user depending on what type was passed
        if isinstance(ctx_or_interaction, discord.Interaction):
            user = ctx_or_interaction.user
        else:
            user = ctx_or_interaction.author

        # 2. Validate the developer ID
        if user.id == config.DEV_ID:
            return True

        # 3. Send the error message based on the input type
        error_msg = "❌ This command is restricted to developer access only."
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
        else:
            await ctx_or_interaction.send(error_msg)
            
        return False

    
    # ! prefix
    @commands.command(name="clear_slash")
    @commands.is_owner()
    async def clear_slash(self, ctx: commands.Context):
        if not await self.is_dev(ctx):
            return

        # Clear global commands
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync()
        
        # Clear specific guild commands
        for guild in self.bot.guilds:
            try:
                self.bot.tree.clear_commands(guild=guild)
                await self.bot.tree.sync(guild=guild)
            except discord.HTTPException as e:
                print(f"Failed to clear commands for guild {guild.id}: {e}")
        
        await ctx.send("Cleared application commands. System reboot recommended.")

    # ! prefix
    @commands.command(name="devtest")
    @commands.is_owner()
    async def devtest(self, ctx: commands.Context):
        if not await self.is_dev(ctx):
            return

        await ctx.send(
            "devtest check passed. Hello Developer!\n"
            f"`Gateway status: Connected | Session Identity: {self.bot.user}`"
        )

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, spec: Optional[Literal["global", "clear"]] = None):
        """
        Handles command synchronization.
        Modes:
        !sync        -> Fast-syncs global commands strictly to the current testing server.
        !sync global -> Syncs commands globally across all servers (takes 10-60 mins).
        !sync clear  -> Wipes all copied commands from the current testing server.
        """
        if not await self.is_dev(ctx):
            return

        # Global mode doesn't need a guild context
        if spec == "global":
            await ctx.send("Starting global application command sync... (This may take up to an hour to propagate)")
            try:
                synced = await self.bot.tree.sync()
                await ctx.send(f"Successfully synced {len(synced)} application commands globally.")
            except Exception as e:
                await ctx.send(f"Global sync failed: `{e}`")
            return # Exit early

        # Safety check: Local operations require being in a server
        if ctx.guild is None:
            await ctx.send("❌ This synchronization mode can only be used inside a server.")
            return

        if spec == "clear":
            await ctx.send("Clearing local guild command copies...")
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send("Guild-specific command cache cleared.")

        else:
            # Default behavior: Fast-syncs your current global tree directly to this test guild
            await ctx.send("Syncing global commands to this specific server for fast testing...")
            try:
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)
                await ctx.send(f"Successfully synced {len(synced)} commands locally to this server.")
            except Exception as e:
                await ctx.send(f"Local guild sync failed: `{e}`")
                

async def setup(bot: commands.Bot):
    await bot.add_cog(Developer(bot))