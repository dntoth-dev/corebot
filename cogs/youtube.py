import discord
from discord import app_commands
from discord.ext import commands
import config

class YouTube(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="recentvids", description="Get recent videos of Shadow!")
    @app_commands.describe(amount="Number of recent videos to fetch (max 5).")
    async def recentvids(self, interaction: discord.Interaction, amount: int):
        if not config.youtube:
            await interaction.response.send_message("❌ YouTube API client is not configured.", ephemeral=True)
            return

        if amount > 5 or amount < 1:
            await interaction.response.send_message("The number of videos must be between 1 and 5!", ephemeral=True)
            return

        await interaction.response.defer() # Defers to allow slower API response processing

        try:
            uploads_playlist_id = f"UU{config.SM_CH_ID[2:]}"
            request = config.youtube.playlistItems().list(
                playlistId=uploads_playlist_id,
                part="snippet",
                maxResults=amount
            )
            response = request.execute()

            if not response.get('items'):
                await interaction.followup.send("No videos found for this channel.")
                return

            await interaction.followup.send(f"🎥 Recent {amount} videos from Shadow's YouTube channel:")
            
            for item in response['items']:
                video_data = item['snippet']
                video_title = video_data['title']
                video_id = video_data['resourceId']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                await interaction.followup.send(f"🎬 **{video_title}**\n{video_url}")

        except Exception as e:
            await interaction.followup.send("❌ Error fetching YouTube feeds.")
            print(f"Error fetching latest video: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(YouTube(bot))