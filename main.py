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
from flask import Flask
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
    return {"status": "healthy", "timestamp": time.time()}

async def run_bot():
    while True:  # Add outer loop for reconnection
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
            
            await sia.run()  # Changed to await since run() is likely async
            
        except Exception as e:
            logger.error(f"Bot encountered an error: {e}")
            logger.info("Attempting to restart bot in 60 seconds...")
            await asyncio.sleep(60)  # Wait before retry

def start_bot():
    asyncio.run(run_bot())

def run_background_bot():
    while True:  # Add outer loop for persistence
        try:
            start_bot()
        except Exception as e:
            logger.error(f"Background bot thread crashed: {e}")
            time.sleep(60)  # Wait before restarting the bot

def keep_alive():
    """
    Periodically pings the local Flask server to prevent Render from considering 
    the service idle. Includes error handling and retry logic.
    """
    time.sleep(30)  # Initial delay to allow Flask server to start
    
    while True:
        try:
            port = int(os.environ.get("PORT", 5000))
            url = f"http://127.0.0.1:{port}/health"  # Use health check endpoint
            response = requests.get(url, timeout=10)  # Add timeout
            logger.info(f"Keep-alive ping successful - Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive request failed: {e}")
        finally:
            time.sleep(300)  # Always wait 5 minutes between pings

if __name__ == "__main__":
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_background_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Start the keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    # Start the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)