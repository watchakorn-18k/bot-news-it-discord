import discord
import dotenv
import os
import news
import random

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True


client = discord.Client(intents=intents)

with open(".tmp", "r") as f:
    data_tmp = f.readline()


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    # ActivityType straming
    await client.change_presence(
        activity=discord.Streaming(
            name="Writing a news story......",
            url="https://www.twitch.tv/wk18k",
            type=discord.ActivityType.watching,
        )
    )

    data = news.get_data()
    data = data["articles"][0]

    embed = discord.Embed.from_dict(
        {
            "title": data["title"],
            "description": data["description"],
            "color": 1498792,
            "fields": [
                {"name": "content", "value": data["content"], "inline": True},
                {"name": "published", "value": data["publishedAt"], "inline": True},
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
                "url": "https://www.google.com/search?q={}".format(
                    data["author"].replace(" ", "+")
                ),
                "icon_url": "https://ui-avatars.com/api/?name={}".format(
                    data["author"].replace(" ", "+")
                ),
            },
            "url": data["url"],
            "image": {"url": data["urlToImage"]},
        }
    )
    with open(".tmp", "w") as f:
        f.write(data["title"])

    for guild in client.guilds:
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                if data_tmp != data["title"]:
                    await channel.send(embed=embed)
                    async for message in channel.history(limit=1):
                        msg_old = message
                break
    for i in random.sample(list("💻📱🖨🖊📷📺🕹🔌🔋💾💿📀🎞📽🔍🔬💡⏰"), 9):
        await message.add_reaction(i)

    exit()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


client.run(os.getenv("TOKEN"))
