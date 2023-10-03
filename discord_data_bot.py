from discord import File
from discord import Intents
from discord import Embed
from discord import Client
from discord.app_commands import CommandTree
from discord import Activity
from discord import ActivityType
from discord import Status
from dotenv import dotenv_values

cred = dotenv_values('.env')

intents = Intents.default()
intents.members = True
embed = Embed()
client = Client(intents=intents)
tree = CommandTree(client)


@tree.command(name="bot_info", description="Stock Market Data Bot")
async def first_command(interaction):
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


@tree.command(name="get_oi_change", description="Get Participant wise OI")
async def oi(interaction):
    dataEmbed = Embed(
        title="Participant Wise OI Data",
        description="Disclaimer: Don't use this data to make investments",
        color=0x002366,
    )
    file = File("plot1.png", filename="image.png")
    dataEmbed.set_image(url="attachment://image.png")
    await interaction.response.send_message(file=file, embed=dataEmbed)


if __name__ == "__main__":

    @client.event
    async def on_ready():
        await tree.sync()
        await client.change_presence(
            activity=Activity(type=ActivityType.watching, name="Market Participants"),
            status=Status.online,
        )
        print("Bot has logged in as {0.user}".format(client))

    client.run(cred['TOKEN'])
