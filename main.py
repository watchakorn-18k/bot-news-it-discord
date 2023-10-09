from math import ceil
from os import getenv
from random import sample

import nextcord
from nextcord.ext import commands

from utils import logger, translater, news


@translater
def get_data(text):
    return text

intents = nextcord.Intents.default()

bot = commands.AutoShardedBot(command_prefix="$", intents=intents, help_command=None)
bot.shard_count = ceil(len(bot.guilds) / 1000)


@bot.event
async def on_ready():
    try:
        logger.info(f"We have logged in as {bot.user}")
        # ActivityType straming
        await bot.change_presence(
            activity=nextcord.Streaming(
                name="Writing a news story......",
                url="https://www.twitch.tv/wk18k",
                type=nextcord.ActivityType.watching,
            )
        )

        data = news.get_data()
        data = data["articles"][0]

        try:
            data_url = data["author"].replace(" ", "+")
            data_url_icon = data["author"].replace(" ", "+")
        except Exception:
            data_url = "Unknown"
            data_url_icon = "Unknown"

        embed = nextcord.Embed(
            title=get_data(data["title"]),
            description=get_data(data["description"]),
            color=1498792,
            url=data["url"],
        )
        embed.add_field(
            name="content",
            value=get_data(data["content"]),
            inline=True,
        )
        embed.add_field(
            name="published",
            value=get_data(data["publishedAt"]),
            inline=True,
        )
        embed.set_footer(
            icon_url="https://cdn.discordapp.com/attachments/372372440334073859/1100141262205616229/f2c8a1b2-a1a8-43bd-a83e-b50c3bb74ec1.jpg",
            text="IT journalist bot#8756",
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/372372440334073859/1100141262205616229/f2c8a1b2-a1a8-43bd-a83e-b50c3bb74ec1.jpg",
        )
        embed.set_author(
            name=data["author"],
            url=f"https://www.google.com/search?q={data_url}",
            icon_url=f"https://ui-avatars.com/api/?name={data_url_icon}",
        )
        embed.set_image(url=data["urlToImage"])

        for guild in bot.guilds:
            channel = guild.channels[0]
            if isinstance(channel, nextcord.TextChannel):
                    message = await channel.send(embed=embed)
                    for i in sample(list("💻📱🖨🖊📷📺🕹🔌🔋💾💿📀🎞📽🔍🔬💡⏰"), 9):
                        await message.add_reaction(i)

        await bot.close()
    except Exception as e:
        logger.critical(e)


@bot.slash_command()
async def hello(interaction: nextcord.Interaction):
    await interaction.response.send_message("Hello!")


if __name__ == "__main__":
    bot.run(getenv("TOKEN"))