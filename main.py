import discord
import dotenv
import os
import news
import random
from googletrans import Translator

try:
    from textblob import TextBlob
    SENTIMENT_ENABLED = True
except ImportError:
    SENTIMENT_ENABLED = False
    print("⚠️  TextBlob not installed. Sentiment analysis disabled.")
    print("   Install with: pip install textblob")

try:
    import edge_tts
    TTS_ENABLED = True
except ImportError:
    print("   Install with: pip install gTTS")
    
try:
    from bs4 import BeautifulSoup
    BS4_ENABLED = True
except ImportError:
    BS4_ENABLED = False
    print("⚠️  BeautifulSoup4 not installed. HTML cleaning fallback to regex.")

from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException


def translater(func):
    def wrapper(*args):
        text_to_translate = func(*args)
        try:
            return GoogleTranslator(source='en', target="th").translate(text_to_translate)
        except:
            return text_to_translate

    return wrapper


def get_data_translate(text, lang="en"):
    if not text:
        return ""
    try:
        # deep-translator usage (Specify source='en' for better accuracy with news)
        translated = GoogleTranslator(source='en', target=lang).translate(text)
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return text


def analyze_sentiment(text):
    """
    วิเคราะห์ความรู้สึกของข้อความด้วย AI
    Returns: dict with sentiment info (polarity, emoji, color, label)
    
    ตัวอย่าง:
    - Positive (>0.2): "Company reports record profits" → 🟢 สีเขียว
    - Negative (<-0.2): "Security breach exposes data" → 🔴 สีแดง  
    - Neutral: "New product released" → 🟡 สีส้ม
    """
    if not SENTIMENT_ENABLED:
        # Fallback to default if TextBlob not available
        return {
            "polarity": 0,
            "emoji": "📰",
            "color": 0x16d8c8,  # Teal (original color)
            "label": "News",
            "label_th": "ข่าว"
        }
    
    try:
        # Analyze sentiment using TextBlob
        blob = TextBlob(str(text))  # Ensure text is string
        polarity = blob.sentiment.polarity  # Range: -1 (negative) to 1 (positive)
        
        # Categorize sentiment
        if polarity > 0.2:
            return {
                "polarity": polarity,
                "emoji": "🟢",
                "color": 0x00d26a,  # Green
                "label": "Positive",
                "label_th": "ข่าวดี"
            }
        elif polarity < -0.2:
            return {
                "polarity": polarity,
                "emoji": "🔴",
                "color": 0xff4757,  # Red
                "label": "Negative",
                "label_th": "ข่าวไม่ดี"
            }
        else:
            return {
                "polarity": polarity,
                "emoji": "🟡",
                "color": 0xffa502,  # Orange
                "label": "Neutral",
                "label_th": "ข่าวทั่วไป"
            }
    except Exception as e:
        print(f"⚠️  Sentiment analysis error: {e}")
        # Default to neutral on error
        return {
            "polarity": 0,
            "emoji": "📰",
            "color": 0x16d8c8,
            "label": "News",
            "label_th": "ข่าว"
        }


async def create_audio_file(text, lang="en"):
    """
    สร้างไฟล์เสียงจากข้อความด้วย Edge TTS (เสียงดีกว่า + ไฟล์เล็ก)
    Returns: ชื่อไฟล์ที่สร้าง หรือ None ถ้ามี error
    """
    if not TTS_ENABLED:
        return None
    
    try:
        # Select voice based on language
        if lang == 'th':
            voice = "th-TH-PremwadeeNeural"
        elif lang == 'ja':
            voice = "ja-JP-NanamiNeural"
        elif lang.startswith('zh'):
            voice = "zh-CN-XiaoxiaoNeural"
        elif lang == 'ko':
            voice = "ko-KR-SunHiNeural"
        elif lang == 'fr':
            voice = "fr-FR-DeniseNeural"
        elif lang == 'de':
            voice = "de-DE-KatjaNeural"
        elif lang == 'es':
            voice = "es-ES-ElviraNeural"
        else:
            voice = "en-US-AriaNeural" # Default to English
        
        communicate = edge_tts.Communicate(text, voice)
        filename = f".tmp_audio_{lang}.mp3"
        
        await communicate.save(filename)
        return filename
    except Exception as e:
        print(f"TTS Error: {e}")
        return None


def create_reading_progress_bar(text):
    """
    สร้าง Progress Bar ตามความยาวของข่าว
    Short (<100 words): [■□□□□]
    Medium (100-300 words): [■■■□□]
    Long (>500 words): [■■■■■]
    """
    if not text:
        return "[□□□□□]"
    
    word_count = len(text.split())
    
    # Determine level (1-5)
    if word_count < 50:
        level = 1
    elif word_count < 150:
        level = 2
    elif word_count < 300:
        level = 3
    elif word_count < 500:
        level = 4
    else:
        level = 5
        
    # Create bar
    bar = "■" * level + "□" * (5 - level)
    
    # Calculate estimated reading time (avg 200 wpm)
    reading_time = max(1, round(word_count / 200))
    
    return f"[{bar}] ({word_count} words, ~{reading_time} min read)"


dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True


client = discord.Client(intents=intents)

with open(".tmp", "r") as f:
    data_tmp = f.readline()


with open(".tmp", "r") as f:
    data_tmp = f.readline()


def clean_html_tags(text):
    """ลบ HTML tags ออกจากข้อความ"""
    if not text:
        return ""
    
    if BS4_ENABLED:
        try:
            soup = BeautifulSoup(text, "html.parser")
            return soup.get_text(separator=" ", strip=True)
        except Exception as e:
            print(f"BS4 Error: {e}")
            
    # Fallback to regex if BS4 fails or not installed
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


# Global variable to store the fetched article for this run
current_article_data = None

def fetch_article_once():
    """สุ่มดึงข่าวครั้งเดียว แล้วเก็บไว้ใช้กับทุกห้อง"""
    global current_article_data
    
    # Randomly choose between NewsAPI and RSS Feeds (50/50 chance)
    use_rss = random.choice([True, False])
    article_data = {}
    
    if use_rss:
        try:
            print("📡 Fetching from RSS Feeds...")
            rss_news = news.fetch_from_multiple_sources()
            if rss_news:
                # Pick a random article from RSS results
                raw_data = random.choice(rss_news)
                
                # Map RSS data to our format
                article_data = {
                    "title": raw_data.get("title"),
                    "description": clean_html_tags(raw_data.get("summary", "")),
                    "content": clean_html_tags(raw_data.get("summary", "")),
                    "publishedAt": raw_data.get("published", "Unknown"),
                    "author": raw_data.get("source", "Unknown Source"),
                    "url": raw_data.get("link"),
                    "urlToImage": None
                }
            else:
                use_rss = False # Fallback
        except Exception as e:
            print(f"RSS Error: {e}")
            use_rss = False

    if not use_rss:
        print("📰 Fetching from NewsAPI...")
        data = news.get_data_news()
        raw_data = data["articles"][0]
        # Clean content from NewsAPI too
        raw_data["description"] = clean_html_tags(raw_data.get("description", ""))
        raw_data["content"] = clean_html_tags(raw_data.get("content", ""))
        article_data = raw_data

    current_article_data = article_data
    return article_data


def embed_data(channel_lang="en"):
    # Use the globally fetched article
    global current_article_data
    if not current_article_data:
        fetch_article_once()
    
    data = current_article_data

    try:
        data_url = data.get("author", "Unknown").replace(" ", "+") if data.get("author") else "Unknown"
        data_url_icon = data.get("author", "Unknown").replace(" ", "+") if data.get("author") else "Unknown"
    except:
        data_url = "Unknown"
        data_url_icon = "Unknown"
    
    # 🧠 Analyze sentiment of the article
    article_text = f"{data.get('title', '')} {data.get('description', '')} {data.get('content', '')}"
    sentiment = analyze_sentiment(article_text)
    
    # 📊 Create Reading Progress Bar
    reading_bar = create_reading_progress_bar(article_text)
    
    # Translate and add emoji to title
    translated_title = get_data_translate(data["title"], channel_lang)
    title_with_sentiment = f"{sentiment['emoji']} {translated_title}"
    
    # Build fields with sentiment info
    fields = []
    
    # Add sentiment field (only if sentiment analysis is enabled)
    if SENTIMENT_ENABLED:
        sentiment_label = sentiment['label_th'] if channel_lang == 'th' else sentiment['label']
        fields.append({
            "name": "📊 Sentiment Analysis",
            "value": f"{sentiment_label} (Score: {sentiment['polarity']:.2f})",
            "inline": True,
        })
    
    fields.extend([
        {
            "name": "📄 Content",
            "value": get_data_translate(data.get("content", "No content"), channel_lang)[:150] + "...",
            "inline": False,
        },
        {
            "name": "📏 Length",
            "value": reading_bar,
            "inline": True,
        },
        {
            "name": "📅 Published",
            "value": get_data_translate(data.get("publishedAt", "Unknown"), channel_lang),
            "inline": True,
        },
    ])
    
    # Footer text with or without AI mention
    footer_text = "IT journalist bot#8756"
    if SENTIMENT_ENABLED:
        footer_text += " | 🧠 AI Sentiment Analysis"
    
    embed = discord.Embed.from_dict(
        {
            "title": title_with_sentiment,
            "description": get_data_translate(data.get("description", ""), channel_lang),
            "color": sentiment["color"],  # 🎨 Dynamic color based on sentiment!
            "fields": fields,
            "footer": {
                "icon_url": "https://cdn.discordapp.com/attachments/372372440334073859/1100141262205616229/f2c8a1b2-a1a8-43bd-a83e-b50c3bb74ec1.jpg",
                "text": footer_text,
            },
            "thumbnail": {
                "url": "https://cdn.discordapp.com/attachments/372372440334073859/1100141262205616229/f2c8a1b2-a1a8-43bd-a83e-b50c3bb74ec1.jpg"
            },
            "author": {
                "name": data.get("author", "Unknown"),
                "url": "https://www.google.com/search?q={}".format(data_url),
                "icon_url": "https://ui-avatars.com/api/?name={}".format(data_url_icon),
            },
            "url": data.get("url", ""),
            "image": {"url": data.get("urlToImage", "")},
        }
    )
    
    with open(".tmp", "w") as f:
        f.write(data.get("title", ""))
    
    return embed


@client.event
async def on_ready():
    try:
        print(f"We have logged in as {client.user}")
        
        # Check Dev Mode
        is_dev_mode = os.getenv("MODE_DEV") == "TRUE"
        target_dev_channel_id = 1204096924374794290
        
        if is_dev_mode:
            # Show "Under Construction" status in Dev Mode
            await client.change_presence(
                activity=discord.Game(name="🚧 Under Construction 🚧")
            )
            print("🔧 Dev Mode Enabled: Sending only to target channel.")
        else:
            # Normal status
            await client.change_presence(
                activity=discord.Streaming(
                    name="Writing a news story......",
                    url="https://www.twitch.tv/wk18k",
                    type=discord.ActivityType.watching,
                )
            )

        # Fetch article once before looping through guilds
        fetch_article_once()

        for guild in client.guilds:
            for channel in guild.channels:
                # Dev Mode Logic: Only allow specific channel
                if is_dev_mode and channel.id != target_dev_channel_id:
                    continue

                if isinstance(channel, discord.TextChannel) and channel.name not in [
                    "moderator-only",
                    "rules",
                    "exercise-answers",
                ]:
                    # Use the pre-fetched data
                    data = current_article_data
                    
                    if data_tmp != data["title"]:
                        # Detect language based on channel name using langdetect
                        try:
                            # Clean channel name (remove emojis, numbers) for better detection
                            clean_name = ''.join(c for c in channel.name if c.isalpha() or c.isspace())
                            if not clean_name.strip():
                                lang = 'en' # Default if name is only emojis/numbers
                            else:
                                lang = detect(clean_name)
                        except LangDetectException:
                            lang = 'en' # Default to English on error
                        except Exception as e:
                            print(f"Language detection error: {e}")
                            lang = 'en'
                            
                        print(f"   🗣️  Detected language for '{channel.name}': {lang}")
                        
                        # Prepare Embed
                        embed = embed_data(channel_lang=lang)
                        
                        # Prepare Audio (TTS)
                        audio_file = None
                        files_to_send = []
                        
                        if TTS_ENABLED:
                            # Create audio from Title + Description + Content (Summary)
                            title_text = get_data_translate(data.get("title", ""), lang)
                            desc_text = get_data_translate(data.get("description", ""), lang)
                            content_text = get_data_translate(data.get("content", ""), lang)
                            
                            # Combine text
                            full_text = f"{title_text}. {desc_text}. {content_text}"
                            
                            # Limit length to ~800 chars (approx 1.5 - 2 mins) to keep file small
                            if len(full_text) > 800:
                                full_text = full_text[:800] + "... (อ่านต่อในข่าว)"
                                
                            audio_filename = await create_audio_file(full_text, lang)
                            
                            if audio_filename:
                                audio_file = discord.File(audio_filename, filename="news_audio.mp3")
                                files_to_send.append(audio_file)
                        
                        # Send Message with Embed and Audio
                        try:
                            await channel.send(embed=embed, files=files_to_send)
                        except discord.errors.Forbidden:
                            # If permission missing (likely Attach Files), try sending only embed
                            print(f"⚠️  Missing 'Attach Files' permission in {channel.name}. Sending embed only.")
                            await channel.send(embed=embed)
                        except Exception as e:
                            print(f"❌ Error sending to {channel.name}: {e}")
                        
                        # Cleanup audio file
                        if audio_filename and os.path.exists(audio_filename):
                            os.remove(audio_filename)

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
