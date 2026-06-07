import os
import logging
import asyncio
from datetime import datetime, time
import discord
from discord import File, Intents, Embed, Activity, ActivityType, Status
from discord.app_commands import CommandTree
from discord.ext import tasks

import fii_dii_data
import generate_oi_image
import generate_gross_io_image

# Configuration
TOKEN = os.environ.get('DISCORD_TOKEN')
OUTPUT_DIR = os.environ.get("BOT_OUTPUT_DIR", "/tmp/discord_nse_data_bot")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class NSEBot(discord.Client):
    def __init__(self):
        intents = Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = CommandTree(self)
        self.last_processed_date = None

    async def setup_hook(self):
        self.data_scheduler.start()

    @tasks.loop(minutes=15)
    async def data_scheduler(self):
        now = datetime.now()
        # Weekdays only (0-4 are Mon-Fri)
        if now.weekday() > 4:
            return

        # Time window 19:00 to 23:00
        start_time = time(19, 0)
        end_time = time(23, 0)
        current_time = now.time()

        if not (start_time <= current_time <= end_time):
            return

        today_str = now.strftime("%d-%m-%Y")
        if self.last_processed_date == today_str:
            logger.debug(f"Data for {today_str} already processed today.")
            return

        logger.info(f"Checking for new NSE data... (Current time: {now.strftime('%H:%M:%S')})")

        try:
            # Check for dates
            dates = generate_oi_image.get_dates()
            if not dates:
                logger.warning("Could not retrieve dates from NSE.")
                return

            latest_nse_date = dates[2][0] # Format: "07 Jun 2026" or similar from dates.py

            # If the latest date from NSE is today (or the most recent market day)
            # and we haven't processed it yet.
            # Note: NSE usually updates in the evening.

            logger.info(f"Latest data available on NSE: {latest_nse_date}")

            oi_data = generate_oi_image.get_oi_data(dates)
            if oi_data:
                # Participant Wise OI
                oi_change = generate_oi_image.calculate_oi_change(oi_data)
                generate_oi_image.save_img(oi_change)
                generate_oi_image.add_isb_link()

                # Gross OI
                oi_gross, change_oi_list = generate_gross_io_image.calculations(oi_data)
                generate_gross_io_image.generate_image(oi_gross, change_oi_list, latest_nse_date)

                self.last_processed_date = today_str
                logger.info(f"Successfully processed and updated data for {today_str}")
            else:
                logger.info("New data not yet available on NSE.")

        except Exception as e:
            logger.error(f"Error in data scheduler: {e}", exc_info=True)

    @data_scheduler.before_loop
    async def before_data_scheduler(self):
        await self.wait_until_ready()

client = NSEBot()

@client.tree.command(name="bot_info", description="Stock Market Data Bot")
async def bot_info(interaction: discord.Interaction):
    detailsEmbed = Embed(
        title="Stock Market Data Bot",
        description="Open Source Stock Market Data Bot",
        color=0x002366,
    )
    detailsEmbed.set_author(
        name="SiriusBrightstar",
        url="https://github.com/siriusbrightstar",
        icon_url="https://avatars.githubusercontent.com/u/62252266?v=4",
    )
    await interaction.response.send_message(embed=detailsEmbed)

@client.tree.command(name="get_oi_change", description="Get Participant wise OI")
async def oi(interaction: discord.Interaction):
    path = os.path.join(OUTPUT_DIR, "Participant_Wise_OI_Data.png")
    if not os.path.exists(path):
        await interaction.response.send_message("OI Data image not yet generated. Please wait for the next update.", ephemeral=True)
        return

    dataEmbed = Embed(
        title="Participant Wise OI Data",
        description="Disclaimer: Don't use this data to make investments",
        color=0x002366,
    )
    file = File(path, filename="image.png")
    dataEmbed.set_image(url="attachment://image.png")
    await interaction.response.send_message(file=file, embed=dataEmbed)

@client.tree.command(name="get_gross_fut_oi", description="Get Outstanding Futures OI")
async def gross_oi(interaction: discord.Interaction):
    path = os.path.join(OUTPUT_DIR, "Gross_OI.png")
    if not os.path.exists(path):
        await interaction.response.send_message("Gross OI image not yet generated. Please wait for the next update.", ephemeral=True)
        return

    dataEmbed = Embed(
        title="Outstanding Futures OI",
        color=0x002366,
    )
    file = File(path, filename="image.png")
    dataEmbed.set_image(url="attachment://image.png")
    await interaction.response.send_message(file=file, embed=dataEmbed)

@client.tree.command(name="fii_dii", description="Get FII & DII Data")
async def fii_dii(interaction: discord.Interaction):
    try:
        data = fii_dii_data.get_fii_dii_data()
        detailsEmbed = Embed(title="FII DII Data",
                             description=data[0], color=data[1])
        await interaction.response.send_message(embed=detailsEmbed)
    except Exception as e:
        logger.error(f"Error fetching FII/DII data: {e}")
        await interaction.response.send_message("Error fetching FII/DII data.", ephemeral=True)

@client.event
async def on_ready():
    await client.tree.sync()
    await client.change_presence(
        activity=Activity(type=ActivityType.watching,
                          name="Market Participants"),
        status=Status.online,
    )
    logger.info(f"Bot has logged in as {client.user}")

if __name__ == "__main__":
    if not TOKEN:
        logger.error("DISCORD_TOKEN environment variable not set.")
    else:
        client.run(TOKEN)
