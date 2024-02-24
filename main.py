import discord
import dotenv
import os
import news
import random
from googletrans import Translator

translator = Translator()


def translater(func):
    def wrapper(*args):
        return translator.translate(func(*args), dest="th").text

    return wrapper


def get_data_translate(text, lang="en"):
    text = translator.translate(text, dest=lang).text
    return text


dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True


client = discord.Client(intents=intents)

with open(".tmp", "r") as f:
    data_tmp = f.readline()


def embed_data(channel_lang="en"):
    data = news.get_data_news()
    data = data["articles"][0]

    try:
        data_url = data["author"].replace(" ", "+")
        data_url_icon = data["author"].replace(" ", "+")
    except:
        data_url = "Unknown"
        data_url_icon = "Unknown"
    embed = discord.Embed.from_dict(
        {
            "title": get_data_translate(data["title"], channel_lang),
            "description": get_data_translate(data["description"], channel_lang),
            "color": 1498792,
            "fields": [
                {
                    "name": "content",
                    "value": get_data_translate(data["content"], channel_lang),
                    "inline": True,
                },
                {
                    "name": "published",
                    "value": get_data_translate(data["publishedAt"], channel_lang),
                    "inline": True,
                },
            ],
            "footer": {
                "icon_url": "https://cdn.discordapp.com/attachments/372372440334073859/1100141262205616229/f2c8a1b2-a1a8-43bd-a83e-b50c3bb74ec1.jpg",
                "text": "IT journalist bot#8756",
            },
            "thumbnail": {
                "url": "https://cdn.discordapp.com/attachments/372372440334073859/1100141262205616229/f2c8a1b2-a1a8-43bd-a83e-b50c3bb74ec1.jpg"
            },
            "author": {
                "name": data["author"],
                "url": "https://www.google.com/search?q={}".format(data_url),
                "icon_url": "https://ui-avatars.com/api/?name={}".format(data_url_icon),
            },
            "url": data["url"],
            "image": {"url": data["urlToImage"]},
        }
    )
    with open(".tmp", "w") as f:
        f.write(data["title"])
    return embed


@client.event
async def on_ready():
    try:
        print(f"We have logged in as {client.user}")
        # ActivityType straming
        await client.change_presence(
            activity=discord.Streaming(
                name="Writing a news story......",
                url="https://www.twitch.tv/wk18k",
                type=discord.ActivityType.watching,
            )
        )

        for guild in client.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel) and channel.name not in [
                    "moderator-only",
                    "rules",
                    "exercise-answers",
                ]:
                    data = news.get_data_news()
                    data = data["articles"][0]
                    if data_tmp != data["title"]:
                        await channel.send(
                            embed=embed_data(
                                channel_lang=translator.detect(channel.name).lang
                            )
                        )
                        try:
                            async for message in channel.history(limit=1):
                                print(channel.name, message)
                        except:
                            print(channel.name, "No message")
                        for i in random.sample(
                            list("💻📱🖨🖊📷📺🕹🔌🔋💾💿📀🎞📽🔍🔬💡⏰"), 9
                        ):
                            await message.add_reaction(i)
                    break

        await client.close()
    except Exception as e:
        print(e)
        exit()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


client.run(os.getenv("TOKEN"))
