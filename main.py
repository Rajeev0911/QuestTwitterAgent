# from utils.logging_utils import enable_logging, setup_logging
# from sia.sia import Sia
# import asyncio
# import os

# from dotenv import load_dotenv

# load_dotenv()


# logger = setup_logging()
# logging_enabled = True
# enable_logging(logging_enabled)


# async def main():
#     character_name_id = os.getenv("CHARACTER_NAME_ID")

#     huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
#     if not huggingface_api_key:
#         raise ValueError("HUGGINGFACE_API_KEY environment variable is not set!")

#     client_creds = {}
#     if os.getenv("TW_API_KEY"):
#         client_creds["twitter_creds"] = {
#             "api_key": os.getenv("TW_API_KEY"),
#             "api_secret_key": os.getenv("TW_API_KEY_SECRET"),
#             "access_token": os.getenv("TW_ACCESS_TOKEN"),
#             "access_token_secret": os.getenv("TW_ACCESS_TOKEN_SECRET"),
#             "bearer_token": os.getenv("TW_BEARER_TOKEN"),
#         }
#     if os.getenv("TG_BOT_TOKEN"):
#         client_creds["telegram_creds"] = {
#             "bot_token": os.getenv("TG_BOT_TOKEN"),
#         }

#     sia = Sia(
#         character_json_filepath=f"characters/{character_name_id}.json",
#         huggingface_api_key=huggingface_api_key,
#         **client_creds,
#         memory_db_path=os.getenv("DB_PATH"),
#         # knowledge_module_classes=[GoogleNewsModule],
#         logging_enabled=logging_enabled,
#     )

#     sia.run()


# if __name__ == "__main__":
#     asyncio.run(main())







# import asyncio
# import os
# import threading
# from dotenv import load_dotenv
# from flask import Flask

# from utils.logging_utils import enable_logging, setup_logging
# from sia.sia import Sia

# # Load environment variables
# load_dotenv()

# # Set up logging
# logger = setup_logging()
# logging_enabled = True
# enable_logging(logging_enabled)

# # Create a minimal Flask app
# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Twitter Agent Bot is running!"

# async def run_bot():
#     character_name_id = os.getenv("CHARACTER_NAME_ID")

#     huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
#     if not huggingface_api_key:
#         raise ValueError("HUGGINGFACE_API_KEY environment variable is not set!")

#     client_creds = {}
#     if os.getenv("TW_API_KEY"):
#         client_creds["twitter_creds"] = {
#             "api_key": os.getenv("TW_API_KEY"),
#             "api_secret_key": os.getenv("TW_API_KEY_SECRET"),
#             "access_token": os.getenv("TW_ACCESS_TOKEN"),
#             "access_token_secret": os.getenv("TW_ACCESS_TOKEN_SECRET"),
#             "bearer_token": os.getenv("TW_BEARER_TOKEN"),
#         }
#     if os.getenv("TG_BOT_TOKEN"):
#         client_creds["telegram_creds"] = {
#             "bot_token": os.getenv("TG_BOT_TOKEN"),
#         }

#     sia = Sia(
#         character_json_filepath=f"characters/{character_name_id}.json",
#         huggingface_api_key=huggingface_api_key,
#         **client_creds,
#         memory_db_path=os.getenv("DB_PATH"),
#         # knowledge_module_classes=[GoogleNewsModule],
#         logging_enabled=logging_enabled,
#     )

#     # Start your bot (blocking call)
#     sia.run()

# def start_bot():
#     asyncio.run(run_bot())

# def run_background_bot():
#     start_bot()

# if __name__ == "__main__":
#     # Start the bot in a background thread
#     bot_thread = threading.Thread(target=run_background_bot)
#     bot_thread.daemon = True
#     bot_thread.start()

#     # Start the Flask app, binding to the port Render provides (or default to 5000)
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)





# import asyncio
# import os
# import threading
# import time
# import requests
# from dotenv import load_dotenv
# from flask import Flask

# from utils.logging_utils import enable_logging, setup_logging
# from sia.sia import Sia

# # Load environment variables
# load_dotenv()

# # Set up logging
# logger = setup_logging()
# logging_enabled = True
# enable_logging(logging_enabled)

# # Create a minimal Flask app
# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Twitter Agent Bot is running!"

# async def run_bot():
#     character_name_id = os.getenv("CHARACTER_NAME_ID")

#     huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
#     if not huggingface_api_key:
#         raise ValueError("HUGGINGFACE_API_KEY environment variable is not set!")

#     client_creds = {}
#     if os.getenv("TW_API_KEY"):
#         client_creds["twitter_creds"] = {
#             "api_key": os.getenv("TW_API_KEY"),
#             "api_secret_key": os.getenv("TW_API_KEY_SECRET"),
#             "access_token": os.getenv("TW_ACCESS_TOKEN"),
#             "access_token_secret": os.getenv("TW_ACCESS_TOKEN_SECRET"),
#             "bearer_token": os.getenv("TW_BEARER_TOKEN"),
#         }
#     if os.getenv("TG_BOT_TOKEN"):
#         client_creds["telegram_creds"] = {
#             "bot_token": os.getenv("TG_BOT_TOKEN"),
#         }

#     sia = Sia(
#         character_json_filepath=f"characters/{character_name_id}.json",
#         huggingface_api_key=huggingface_api_key,
#         **client_creds,
#         memory_db_path=os.getenv("DB_PATH"),
#         # knowledge_module_classes=[GoogleNewsModule],
#         logging_enabled=logging_enabled,
#     )

#     # Start your bot (blocking call)
#     sia.run()

# def start_bot():
#     asyncio.run(run_bot())

# def run_background_bot():
#     start_bot()

# def keep_alive():
#     """
#     Waits for the server to start, then periodically pings the local Flask server
#     to prevent Render from considering the service idle.
#     """
#     # Wait 10 seconds to allow the Flask server to start
#     time.sleep(30)
#     while True:
#         try:
#             port = int(os.environ.get("PORT", 5000))
#             url = f"http://127.0.0.1:{port}/"
#             response = requests.get(url)
#             logger.info(f"Keep-alive ping to {url} - Status Code: {response.status_code}")
#         except Exception as e:
#             logger.error(f"Keep-alive request failed: {e}")
#         time.sleep(300)  # Wait 5 minutes (300 seconds) before next ping

# if __name__ == "__main__":
#     # Start the bot in a background thread
#     bot_thread = threading.Thread(target=run_background_bot)
#     bot_thread.daemon = True
#     bot_thread.start()

#     # Start the keep-alive thread
#     keep_alive_thread = threading.Thread(target=keep_alive)
#     keep_alive_thread.daemon = True
#     keep_alive_thread.start()

#     # Start the Flask app; Render will bind this to the PORT environment variable (default 5000)
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)







import asyncio
import os
import threading
import time
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from utils.logging_utils import enable_logging, setup_logging
from sia.sia import Sia

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logging()
logging_enabled = True
enable_logging(logging_enabled)

# Create a minimal Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Twitter Agent Bot is running!"

@app.route("/health")
def health_check():
    """Additional endpoint for health checks"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

class TwitterRateManager:
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 30  # 30 seconds between requests
        self.lock = threading.Lock()

    async def wait_if_needed(self):
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_request_time = time.time()

async def run_bot():
    while True:
        try:
            character_name_id = os.getenv("CHARACTER_NAME_ID")
            huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
            
            if not huggingface_api_key:
                raise ValueError("HUGGINGFACE_API_KEY environment variable is not set!")

            client_creds = {}
            if os.getenv("TW_API_KEY"):
                client_creds["twitter_creds"] = {
                    "api_key": os.getenv("TW_API_KEY"),
                    "api_secret_key": os.getenv("TW_API_KEY_SECRET"),
                    "access_token": os.getenv("TW_ACCESS_TOKEN"),
                    "access_token_secret": os.getenv("TW_ACCESS_TOKEN_SECRET"),
                    "bearer_token": os.getenv("TW_BEARER_TOKEN"),
                }

            if os.getenv("TG_BOT_TOKEN"):
                client_creds["telegram_creds"] = {
                    "bot_token": os.getenv("TG_BOT_TOKEN"),
                }

            sia = Sia(
                character_json_filepath=f"characters/{character_name_id}.json",
                huggingface_api_key=huggingface_api_key,
                **client_creds,
                memory_db_path=os.getenv("DB_PATH"),
                logging_enabled=logging_enabled,
            )
            
            # Add rate manager to twitter client if it exists
            if sia.twitter:
                sia.twitter.rate_manager = TwitterRateManager()
                
                # Monkey patch the post method to include rate limiting
                original_post = sia.twitter.post
                async def rate_limited_post(*args, **kwargs):
                    await sia.twitter.rate_manager.wait_if_needed()
                    return await original_post(*args, **kwargs)
                sia.twitter.post = rate_limited_post
                
                # Monkey patch the reply method to include rate limiting
                original_reply = sia.twitter.reply
                async def rate_limited_reply(*args, **kwargs):
                    await sia.twitter.rate_manager.wait_if_needed()
                    return await original_reply(*args, **kwargs)
                sia.twitter.reply = rate_limited_reply
            
            await sia.run()
            
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                wait_time = 300  # 5 minutes
                logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Bot encountered an error: {e}")
                logger.info("Attempting to restart bot in 60 seconds...")
                await asyncio.sleep(60)

def start_bot():
    asyncio.run(run_bot())

def run_background_bot():
    while True:
        try:
            start_bot()
        except Exception as e:
            logger.error(f"Background bot thread crashed: {e}")
            time.sleep(60)

def keep_alive():
    time.sleep(30)
    while True:
        try:
            port = int(os.environ.get("PORT", 10000))  # Changed to match your port
            url = f"http://127.0.0.1:{port}/health"
            response = requests.get(url, timeout=10)
            logger.info(f"Keep-alive ping successful - Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive request failed: {e}")
        finally:
            time.sleep(300)

if __name__ == "__main__":
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_background_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Start the keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    # Start the Flask app with the correct port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)