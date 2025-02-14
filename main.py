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
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from utils.logging_utils import enable_logging, setup_logging, log_message
from sia.sia import Sia

# Load environment variables
load_dotenv()

# Set up logging with more detailed configuration
logger = setup_logging()
logging_enabled = True
enable_logging(logging_enabled)

# Create Flask app
app = Flask(__name__)

# Global flag for graceful shutdown
running = True

@app.route("/")
def home():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message(logger, "info", "Flask", f"Health check endpoint accessed at {current_time}")
    return f"Twitter Agent Bot is running! Last checked: {current_time}"

@app.route("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

async def run_bot():
    try:
        character_name_id = os.getenv("CHARACTER_NAME_ID")
        huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not huggingface_api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is not set!")
        
        log_message(logger, "info", "Bot", "Initializing bot with credentials...")
        
        client_creds = {}
        if os.getenv("TW_API_KEY"):
            client_creds["twitter_creds"] = {
                "api_key": os.getenv("TW_API_KEY"),
                "api_secret_key": os.getenv("TW_API_KEY_SECRET"),
                "access_token": os.getenv("TW_ACCESS_TOKEN"),
                "access_token_secret": os.getenv("TW_ACCESS_TOKEN_SECRET"),
                "bearer_token": os.getenv("TW_BEARER_TOKEN"),
            }
            log_message(logger, "info", "Bot", "Twitter credentials loaded")
            
        if os.getenv("TG_BOT_TOKEN"):
            client_creds["telegram_creds"] = {
                "bot_token": os.getenv("TG_BOT_TOKEN"),
            }
            log_message(logger, "info", "Bot", "Telegram credentials loaded")
        
        sia = Sia(
            character_json_filepath=f"characters/{character_name_id}.json",
            huggingface_api_key=huggingface_api_key,
            **client_creds,
            memory_db_path=os.getenv("DB_PATH"),
            logging_enabled=logging_enabled,
        )
        
        log_message(logger, "info", "Bot", "Bot initialized successfully")
        
        # Run the bot with periodic health checks
        while running:
            try:
                sia.run()
            except Exception as e:
                log_message(logger, "error", "Bot", f"Bot encountered an error: {str(e)}")
                # Wait before retry to prevent rapid cycling
                await asyncio.sleep(5)
                
    except Exception as e:
        log_message(logger, "error", "Bot", f"Failed to initialize bot: {str(e)}")
        raise

def start_bot():
    log_message(logger, "info", "Bot", "Starting bot process...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot())
    except Exception as e:
        log_message(logger, "error", "Bot", f"Bot process error: {str(e)}")
    finally:
        loop.close()

def keep_alive():
    """
    Enhanced keep-alive function with better error handling and logging
    """
    log_message(logger, "info", "KeepAlive", "Starting keep-alive process...")
    
    # Initial delay to allow server startup
    time.sleep(30)
    
    while running:
        try:
            port = int(os.environ.get("PORT", 5000))
            url = f"http://127.0.0.1:{port}/health"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                log_message(logger, "info", "KeepAlive", "Health check successful")
            else:
                log_message(logger, "warning", "KeepAlive", f"Health check returned status code: {response.status_code}")
                
        except requests.RequestException as e:
            log_message(logger, "error", "KeepAlive", f"Health check failed: {str(e)}")
        except Exception as e:
            log_message(logger, "error", "KeepAlive", f"Unexpected error in keep-alive: {str(e)}")
            
        # Sleep for 5 minutes before next check
        time.sleep(300)

def shutdown_handler():
    """Handler for graceful shutdown"""
    global running
    running = False
    log_message(logger, "info", "Shutdown", "Initiating graceful shutdown...")

if __name__ == "__main__":
    try:
        # Register shutdown handler
        import signal
        signal.signal(signal.SIGTERM, lambda signo, frame: shutdown_handler())
        
        log_message(logger, "info", "Main", "Starting application...")
        
        # Start the bot thread
        bot_thread = threading.Thread(target=start_bot, name="BotThread")
        bot_thread.daemon = True
        bot_thread.start()
        log_message(logger, "info", "Main", "Bot thread started")
        
        # Start the keep-alive thread
        keep_alive_thread = threading.Thread(target=keep_alive, name="KeepAliveThread")
        keep_alive_thread.daemon = True
        keep_alive_thread.start()
        log_message(logger, "info", "Main", "Keep-alive thread started")
        
        # Get port from environment
        port = int(os.environ.get("PORT", 10000))
        log_message(logger, "info", "Main", f"Starting Flask server on port {port}")
        
        # Run Flask app
        app.run(host="0.0.0.0", port=port)
        
    except Exception as e:
        log_message(logger, "error", "Main", f"Application failed to start: {str(e)}")
        raise