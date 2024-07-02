import telebot
import time
import tweepy
import requests
# Telegram API token
API_TOKEN = 'YOURBOTTOKEN'
CHANNEL_ID = ''  # or the channel ID, e.g., -1001234567890
TWITTER_API_KEY = ''
TWITTER_API_SECRET_KEY = ''
TWITTER_ACCESS_TOKEN = ''
TWITTER_ACCESS_TOKEN_SECRET = ''
TWITTER_BEARER_TOKEN = ''

# Initialize the Telegram bot
bot = telebot.TeleBot(API_TOKEN)

# Initialize the Twitter API client for v2
client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET_KEY,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

# Function to send a message with a delay
def send_message_with_delay(channel_id, text, delay, photo=None):
    time.sleep(delay)
    if photo:
        bot.send_photo(channel_id, photo, caption=text)
    else:
        bot.send_message(channel_id, text)
    post_to_twitter(text)

# Function to post a message to Twitter
def upload_media_to_twitter(image_path):
    url = "https://upload.twitter.com/1.1/media/upload.json"

    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    files = {
        'media': open(image_path, 'rb')
    }

    response = requests.post(url, headers=headers, files=files)
    media_id = response.json()['media_id']
    return media_id

def post_to_twitter(text, image_path=None):
    try:
        if image_path:
            media_id = upload_media_to_twitter(image_path)
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            response = client.create_tweet(text=text)

        print(f"Tweet posted successfully: {response}")
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
# Handler for the /delay command
@bot.message_handler(commands=['delay'])
def handle_delay_command(message):
    try:
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message, "Неверный формат команды. Используйте: /delay <seconds> <message>")
            return

        delay = int(command_parts[1])
        text = command_parts[2]

        # Check for photo in the replied message
        if message.reply_to_message and message.reply_to_message.photo:
            photo = message.reply_to_message.photo[-1].file_id
        else:
            photo = None

        bot.reply_to(message, f"Сообщение будет отправлено через {delay} секунд.")
        send_message_with_delay(CHANNEL_ID, text, delay, photo)
    except ValueError:
        bot.reply_to(message, "Ошибка: задержка должна быть числом.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке команды: {e}")

# Start the bot
bot.polling(none_stop=True)
