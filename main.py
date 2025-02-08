from utils.logging_utils import enable_logging, setup_logging
from sia.sia import Sia
import asyncio
import os

from dotenv import load_dotenv

load_dotenv()


logger = setup_logging()
logging_enabled = True
enable_logging(logging_enabled)


async def main():
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
        # knowledge_module_classes=[GoogleNewsModule],
        logging_enabled=logging_enabled,
    )

    sia.run()


if __name__ == "__main__":
    asyncio.run(main())



















# from utils.logging_utils import enable_logging, setup_logging
# from sia.sia import Sia
# import asyncio
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Setup logging
# logger = setup_logging()
# logging_enabled = True
# enable_logging(logging_enabled)

# async def main():
#     # Get character name from environment variables
#     character_name_id = os.getenv("CHARACTER_NAME_ID")
    
#     # Setup client credentials
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
    
#     # Initialize Sia
#     sia = Sia(
#         character_json_filepath=f"characters/{character_name_id}.json",
#         **client_creds,
#         memory_db_path=os.getenv("DB_PATH"),
#         # knowledge_module_classes=[GoogleNewsModule],
#         logging_enabled=logging_enabled,
#     )
    
#     # For debugging
#     print("Available methods:", dir(sia))
#     print("Class type:", type(sia))
    
#     # Run Sia
#     sia.run()

# if __name__ == "__main__":
#     asyncio.run(main())