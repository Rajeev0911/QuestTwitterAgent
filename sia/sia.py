# import asyncio
# from datetime import datetime, timedelta, timezone
# import os
# import random
# import threading
# import time
# from datetime import timezone
# from uuid import uuid4
# import requests
# from typing import List, Optional
# import logging

# from sia.character import SiaCharacter
# from sia.clients.telegram.telegram_client_aiogram import SiaTelegram
# from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial
# from sia.memory.memory import SiaMemory
# from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
# from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
# from utils.etc_utils import generate_image_dalle, save_image_from_url
# from utils.logging_utils import enable_logging, log_message, setup_logging

# class HuggingFaceAPI:
#     def __init__(self, api_key: str, model_id: str = "google/flan-t5-small", logger=None):
#         """
#         Initialize HuggingFace API client with a lightweight model.
#         Using flan-t5-small as default - it's efficient and has good performance for general tasks.
#         """
#         self.api_key = api_key
#         self.model_id = model_id
#         self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
#         self.headers = {"Authorization": f"Bearer {api_key}"}
#         self.logger = logger or logging.getLogger("HuggingFaceAPI")
        

#     async def generate(self, prompt: str, max_length: int = 100) -> str:
#         """
#         Generate text using the HuggingFace API with rate limiting consideration
#         """
#         try:
#             payload = {
#                 "inputs": prompt,
#                 "parameters": {
#                     "max_length": max_length,
#                     "temperature": 0.7,
#                     "top_p": 0.95,
#                     "repetition_penalty": 1.15
#                 }
#             }
            
#             response = requests.post(self.api_url, headers=self.headers, json=payload)
            
#             if response.status_code == 429:  # Rate limit exceeded
#                 await asyncio.sleep(60)  # Wait for 1 minute before retrying
#                 return await self.generate(prompt, max_length)

#             if response.status_code == 503:
#                 # Model is loading; wait for the estimated time plus a small buffer and retry.
#                 error_info = response.json()
#                 wait_time = error_info.get("estimated_time", 20) + 5  # Adding a 5-second buffer
#                 log_message(self.logger, "info", self, f"Model is loading. Waiting for {wait_time} seconds.")
#                 await asyncio.sleep(wait_time)
#                 return await self.generate(prompt, max_length)
                
                
#             if response.status_code != 200:
#                 raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
#             result = response.json()[0]["generated_text"]
#             return result
            
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating text: {str(e)}")
#             return None

# class Sia:
#     def __init__(
#         self,
#         character_json_filepath: str,
#         huggingface_api_key: str,
#         memory_db_path: str = None,
#         clients=None,
#         twitter_creds=None,
#         telegram_creds=None,
#         plugins=[],
#         knowledge_module_classes=[],
#         logging_enabled=True,
#         testing=False,
#     ):
#         self.testing = testing
#         self.character = SiaCharacter(json_file=character_json_filepath, sia=self)
#         self.memory = SiaMemory(character=self.character, db_path=memory_db_path)
#         self.clients = clients
        
#         # Initialize HuggingFace API client
#         self.llm = HuggingFaceAPI(
#             api_key=huggingface_api_key,
#             model_id="google/flan-t5-small"  # Lightweight model good for free tier
#         )
        
#         self.twitter = (
#             SiaTwitterOfficial(sia=self, **twitter_creds, testing=self.testing)
#             if twitter_creds
#             else None
#         )
#         self.telegram = (
#             SiaTelegram(
#                 sia=self,
#                 **telegram_creds,
#                 chat_id=self.character.platform_settings.get("telegram", {}).get(
#                     "chat_id", None
#                 ),
#             )
#             if telegram_creds
#             else None
#         )
        
#         if self.twitter:
#             self.twitter.character = self.character
#             self.twitter.memory = self.memory
            
#         self.plugins = plugins
#         self.logger = setup_logging()
#         enable_logging(logging_enabled)
#         self.character.logging_enabled = logging_enabled
#         self.knowledge_modules = [kmc(sia=self) for kmc in knowledge_module_classes]
        
#         self.run_all_modules()

#     def run_all_modules(self):
#         """
#         Run all the knowledge or plugin modules if they have a 'run' method.
#         Modify this implementation as needed for your use case.
#         """
#         for module in self.knowledge_modules:
#             if hasattr(module, "run"):
#                 module.run()


#     def get_modules_settings(self):
#         session = self.memory.Session()

#         try:
#             modules_settings = {}
#             for module in self.knowledge_modules:
#                 module_settings = (
#                     session.query(KnowledgeModuleSettingsModel)
#                     .filter(
#                         KnowledgeModuleSettingsModel.character_name_id
#                         == self.character.name_id,
#                         KnowledgeModuleSettingsModel.module_name == module.module_name,
#                     )
#                     .all()
#                 )
#                 log_message(
#                     self.logger, "info", self, f"Module settings: {module_settings}"
#                 )
#                 modules_settings[module.module_name] = module_settings[
#                     0
#                 ].module_settings
#             return modules_settings
#         finally:
#             session.close()


#     def get_plugin(self, time_of_day="afternoon"):
#         modules_settings = self.get_modules_settings()

#         for module in self.knowledge_modules:
#             log_message(
#                 self.logger,
#                 "info",
#                 self,
#                 f"Module: {module.module_name}",
#             )
#             for plugin_name, plugin in module.plugins.items():
#                 log_message(self.logger, "info", self, f"Plugin: {plugin_name}")
#                 log_message(
#                     self.logger,
#                     "info",
#                     self,
#                     f"Usage condition: {modules_settings[module.module_name].get('plugins', {}).get(plugin_name, {}).get('usage_condition', {}).get('time_of_day')}",
#                 )
#                 log_message(self.logger, "info", self, f"Time of day: {time_of_day}")
#                 if (
#                     modules_settings[module.module_name]
#                     .get("plugins", {})
#                     .get(plugin_name, {})
#                     .get("usage_condition", {})
#                     .get("time_of_day")
#                     == time_of_day
#                 ):
#                     return plugin

#         return None


#     async def generate_post(
#         self, 
#         platform="twitter", 
#         author=None, 
#         character=None, 
#         time_of_day=None, 
#         conversation_id=None
#     ):
#         # Get plugin (if any) based on the current time of day.
#         plugin = self.get_plugin(time_of_day=self.character.current_time_of_day())
#         plugin_prompt = plugin.get_instructions_and_knowledge() if plugin else ""

#         # Build the prompt for generating a post.
#         # We instruct the model not to repeat the static "you_are" description.
#         prompt = f"""
#     You are Quest, an AI agent. Do not repeat your introductory statement.
#     Previous post examples:
#     {self.character.get_post_examples('general', time_of_day=time_of_day, random_pick=7)}

#     Your post must be unique and not resemble any previous posts.
#     Platform: {platform}
#     {plugin_prompt}

#     Core objective: {self.character.core_objective}
#     Means for achieving core objective: {self.character.means_for_achieving_core_objective}

#     Generate a {platform} post (10-30 words) that is thought-provoking, controversial, funny, philosophical, inspirational, or action-oriented.
#         """

#         try:
#             # Call the Hugging Face API to generate text.
#             result = await self.llm.generate(prompt, max_length=50)
#             # If result is a tuple or list, extract the first element.
#             if isinstance(result, (list, tuple)):
#                 post_content = result[0]
#             else:
#                 post_content = result

#             # Validate that the generated text is a valid string.
#             if not post_content or not isinstance(post_content, str):
#                 log_message(self.logger, "error", self, "Generated post content is not a valid string.")
#                 return None, []
                
#             image_filepaths = []

#             # Optionally generate an image if conditions are met.
#             if random.random() < self.character.plugins_settings.get("dalle", {}).get("probability_of_posting", 0):
#                 image_url = generate_image_dalle(post_content[0:900])
#                 if image_url:
#                     image_filepath = f"media/{uuid4()}.png"
#                     save_image_from_url(image_url, image_filepath)
#                     image_filepaths.append(image_filepath)

#             # Create a schema for the generated post.
#             generated_post_schema = SiaMessageGeneratedSchema(
#                 content=post_content,
#                 platform=platform,
#                 author=author,
#                 conversation_id=conversation_id
#             )

#             # Update plugin settings if a plugin is used.
#             if plugin:
#                 plugin.update_settings(next_use_after=datetime.now(timezone.utc) + timedelta(hours=1))

#             return generated_post_schema, image_filepaths
        
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating post: {str(e)}")
#             return None, []


#     async def generate_response(
#         self,
#         message: SiaMessageSchema,
#         platform="twitter",
#         time_of_day=None,
#         conversation=None,
#         previous_messages: str = None,
#         use_filtering_rules: str = True,
#     ) -> Optional[SiaMessageGeneratedSchema]:
#         """Generate a response to a message using the HuggingFace API."""
#         if not self.character.responding.get("enabled", True):
#             return None

#         # Build or retrieve the conversation context.
#         if not conversation:
#             conversation = self.twitter.get_conversation(conversation_id=message.conversation_id)
#             conversation_first_message = self.memory.get_messages(id=message.conversation_id, platform=platform)
#             conversation = conversation_first_message + conversation[-20:]
#             conversation_str = "\n".join(
#                 [f"[{msg.wen_posted}] {msg.author}: {msg.content}" for msg in conversation]
#             )
#         else:
#             conversation_str = conversation

#         message_to_respond_str = f"[{message.wen_posted}] {message.author}: {message.content}"

#         # Do not respond to messages from yourself.
#         if message.author == self.character.platform_settings.get(platform, {}).get("username"):
#             return None

#         # Apply filtering rules if enabled.
#         if self.character.responding.get("filtering_rules") and use_filtering_rules:
#             filtering_prompt = f"""
#     Determine if this message should be responded to based on these rules:
#     {self.character.responding.get('filtering_rules')}

#     Conversation:
#     {conversation_str}

#     Message:
#     {message_to_respond_str}

#     Respond with only 'True' or 'False'.
#             """
#             try:
#                 filtering_result = await self.llm.generate(filtering_prompt, max_length=10)
#                 if not filtering_result or filtering_result.strip().lower() != 'true':
#                     return None
#             except Exception as e:
#                 log_message(self.logger, "error", self, f"Error in filtering: {e}")
#                 return None

#         # Retrieve social memory for additional context.
#         social_memory = self.memory.get_social_memory(message.author, platform)
#         social_memory_str = ""
#         if social_memory:
#             social_memory_str = f"""
#     Social memory for {message.author}:
#     Last interaction: {social_memory.last_interaction}
#     Interactions: {social_memory.interaction_count}
#     Opinion: {social_memory.opinion}

#     Recent history:
#     {chr(10).join([f"{msg['role']}: {msg['content']}" for msg in social_memory.conversation_history[-5:]])}
#             """

#         # Build the prompt for generating a response.
#         prompt = f"""
#     You are Quest, an AI agent. Do not repeat your introductory statement.
#     {self.character.prompts.get('communication_requirements')}

#     Platform: {platform}
#     {social_memory_str}

#     Message to respond to:
#     {message_to_respond_str}

#     Conversation:
#     {conversation_str}

#     Core objective: {self.character.core_objective}
#     Means for achieving core objective: {self.character.means_for_achieving_core_objective}

#     Generate a natural, unique response (max 30 words).
#         """

#         try:
#             response_content = await self.llm.generate(prompt, max_length=50)
#             if not response_content:
#                 return None
                
#             generated_response_schema = SiaMessageGeneratedSchema(
#                 content=response_content,
#                 platform=message.platform,
#                 author=self.character.platform_settings.get(message.platform, {}).get("username", self.character.name),
#                 response_to=message.id,
#                 conversation_id=message.conversation_id,
#             )

#             # Update social memory with both the incoming message and generated response.
#             self.memory.update_social_memory(
#                 user_id=message.author,
#                 platform=message.platform,
#                 message_id=message.id,
#                 content=message.content,
#                 role="user"
#             )
#             self.memory.update_social_memory(
#                 user_id=message.author,
#                 platform=message.platform,
#                 message_id=generated_response_schema.id,
#                 content=generated_response_schema.content,
#                 role="assistant"
#             )

#             return generated_response_schema

#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating response: {e}")
#             return None


#     def run(self):
#         """Run all clients concurrently using threads"""
#         threads = []
        
#         if self.telegram:
#             def run_telegram():
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 try:
#                     loop.run_until_complete(self.telegram.run())
#                 except Exception as e:
#                     print(f"Telegram error: {e}")
#                 finally:
#                     loop.close()
                    
#             telegram_thread = threading.Thread(
#                 target=run_telegram,
#                 name="telegram_thread"
#             )
#             threads.append(telegram_thread)
            
#         if self.twitter:
#             def run_twitter():
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 try:
#                     loop.run_until_complete(self.twitter.run())
#                 except Exception as e:
#                     print(f"Twitter error: {e}")
#                 finally:
#                     loop.close()
                    
#             twitter_thread = threading.Thread(
#                 target=run_twitter,
#                 name="twitter_thread"
#             )
#             threads.append(twitter_thread)
            
#         for thread in threads:
#             thread.daemon = True
#             thread.start()
            
#         try:
#             while True:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print("Shutting down...")




































# import asyncio
# from datetime import datetime, timedelta, timezone
# import os
# import random
# import threading
# import time
# from uuid import uuid4
# import requests
# from typing import List, Optional
# import logging

# from sia.character import SiaCharacter
# from sia.clients.telegram.telegram_client_aiogram import SiaTelegram
# from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial
# from sia.memory.memory import SiaMemory
# from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
# from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
# from utils.etc_utils import generate_image_dalle, save_image_from_url
# from utils.logging_utils import enable_logging, log_message, setup_logging


# class HuggingFaceAPI:
#     def __init__(self, api_key: str, model_id: str = "google/flan-t5-large", logger=None):
#         """
#         Initialize HuggingFace API client with a larger model for improved quality.
#         """
#         self.api_key = api_key
#         self.model_id = model_id
#         self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
#         self.headers = {"Authorization": f"Bearer {api_key}"}
#         self.logger = logger or logging.getLogger("HuggingFaceAPI")
        
#     async def generate(self, prompt: str, max_length: int = 100) -> str:
#         """
#         Generate text using the HuggingFace API with rate limiting consideration.
#         """
#         try:
#             payload = {
#                 "inputs": prompt,
#                 "parameters": {
#                     "max_length": max_length,
#                     "temperature": 0.7,
#                     "top_p": 0.95,
#                     "repetition_penalty": 1.15
#                 }
#             }
            
#             response = requests.post(self.api_url, headers=self.headers, json=payload)
            
#             if response.status_code == 429:  # Rate limit exceeded
#                 await asyncio.sleep(60)  # Wait for 1 minute before retrying
#                 return await self.generate(prompt, max_length)

#             if response.status_code == 503:
#                 # Model is loading; wait for the estimated time plus a small buffer and retry.
#                 error_info = response.json()
#                 wait_time = error_info.get("estimated_time", 20) + 5  # Adding a 5-second buffer
#                 log_message(self.logger, "info", self, f"Model is loading. Waiting for {wait_time} seconds.")
#                 await asyncio.sleep(wait_time)
#                 return await self.generate(prompt, max_length)
                
#             if response.status_code != 200:
#                 raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
#             result = response.json()[0]["generated_text"]
#             return result
            
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating text: {str(e)}")
#             return None


# class TwitterTrendingFetcher:
#     def __init__(self, bearer_token: str):
#         self.bearer_token = bearer_token
#         self.api_url = "https://api.twitter.com/1.1/trends/place.json?id=1"

#     def fetch_trending_topics(self) -> List[str]:
#         headers = {"Authorization": f"Bearer {self.bearer_token}"}
#         response = requests.get(self.api_url, headers=headers)

#         if response.status_code != 200:
#             return []

#         trends = response.json()[0]["trends"]
#         return [trend["name"] for trend in trends if trend.get("tweet_volume")]


# class Sia:
#     def __init__(
#         self,
#         character_json_filepath: str,
#         huggingface_api_key: str,
#         memory_db_path: str = None,
#         clients=None,
#         twitter_creds=None,
#         telegram_creds=None,
#         plugins=[],
#         knowledge_module_classes=[],
#         logging_enabled=True,
#         testing=False,
#     ):
#         self.testing = testing
#         self.character = SiaCharacter(json_file=character_json_filepath, sia=self)
#         self.memory = SiaMemory(character=self.character, db_path=memory_db_path)
#         self.clients = clients
        
#         # Initialize HuggingFace API client with the large model.
#         self.llm = HuggingFaceAPI(api_key=huggingface_api_key, model_id="google/flan-t5-large")
        
#         self.twitter = (
#             SiaTwitterOfficial(sia=self, **twitter_creds, testing=self.testing)
#             if twitter_creds
#             else None
#         )
#         self.telegram = (
#             SiaTelegram(
#                 sia=self,
#                 **telegram_creds,
#                 chat_id=self.character.platform_settings.get("telegram", {}).get("chat_id", None),
#             )
#             if telegram_creds
#             else None
#         )
        
#         if self.twitter:
#             self.twitter.character = self.character
#             self.twitter.memory = self.memory
        
#         # Preserve original plugin/knowledge modules functionality.
#         self.plugins = plugins
#         self.logger = setup_logging()
#         enable_logging(logging_enabled)
#         self.character.logging_enabled = logging_enabled
#         self.knowledge_modules = [kmc(sia=self) for kmc in knowledge_module_classes]
        
#         # Initialize trending topics functionality if a bearer token is provided.
#         self.twitter_trends = None
#         if twitter_creds and "bearer_token" in twitter_creds:
#             self.twitter_trends = TwitterTrendingFetcher(bearer_token=twitter_creds["bearer_token"])
        
#         self.run_all_modules()

#     def run_all_modules(self):
#         """
#         Run all the knowledge or plugin modules if they have a 'run' method.
#         Modify this implementation as needed for your use case.
#         """
#         for module in self.knowledge_modules:
#             if hasattr(module, "run"):
#                 module.run()

#     def get_modules_settings(self):
#         session = self.memory.Session()
#         try:
#             modules_settings = {}
#             for module in self.knowledge_modules:
#                 module_settings = (
#                     session.query(KnowledgeModuleSettingsModel)
#                     .filter(
#                         KnowledgeModuleSettingsModel.character_name_id == self.character.name_id,
#                         KnowledgeModuleSettingsModel.module_name == module.module_name,
#                     )
#                     .all()
#                 )
#                 log_message(self.logger, "info", self, f"Module settings: {module_settings}")
#                 modules_settings[module.module_name] = module_settings[0].module_settings
#             return modules_settings
#         finally:
#             session.close()

#     def get_plugin(self, time_of_day="afternoon"):
#         modules_settings = self.get_modules_settings()
#         for module in self.knowledge_modules:
#             log_message(self.logger, "info", self, f"Module: {module.module_name}")
#             for plugin_name, plugin in module.plugins.items():
#                 log_message(self.logger, "info", self, f"Plugin: {plugin_name}")
#                 log_message(
#                     self.logger,
#                     "info",
#                     self,
#                     f"Usage condition: {modules_settings[module.module_name].get('plugins', {}).get(plugin_name, {}).get('usage_condition', {}).get('time_of_day')}"
#                 )
#                 log_message(self.logger, "info", self, f"Time of day: {time_of_day}")
#                 if (
#                     modules_settings[module.module_name]
#                     .get("plugins", {})
#                     .get(plugin_name, {})
#                     .get("usage_condition", {})
#                     .get("time_of_day")
#                     == time_of_day
#                 ):
#                     return plugin
#         return None

#     async def fetch_trending_topics(self) -> List[str]:
#         """Fetch trending topics from Twitter if available."""
#         if self.twitter_trends:
#             loop = asyncio.get_event_loop()
#             return await loop.run_in_executor(None, self.twitter_trends.fetch_trending_topics)
#         return []

#     async def generate_post(
#         self, 
#         platform="twitter", 
#         author=None, 
#         character=None, 
#         time_of_day=None, 
#         conversation_id=None
#     ):
#         # Get plugin (if any) based on the current time of day.
#         plugin = self.get_plugin(time_of_day=self.character.current_time_of_day())
#         plugin_prompt = plugin.get_instructions_and_knowledge() if plugin else ""
        
#         # Fetch trending topics and prioritize keywords.
#         trending_topics = await self.fetch_trending_topics()
#         priority_keywords = ["Bitcoin", "AI", "Crypto", "Tech"]
#         selected_keywords = random.sample(priority_keywords, min(len(priority_keywords), 2))
#         selected_trending = random.sample(trending_topics, min(len(trending_topics), 2)) if trending_topics else []
#         keywords = selected_keywords + selected_trending
#         keywords_str = ", ".join(keywords)

#         # Build the prompt for generating a post.
#         prompt = f"""
#     You are Quest, an AI agent. Do not repeat your introductory statement.
#     Previous post examples:
#     {self.character.get_post_examples('general', time_of_day=time_of_day, random_pick=7)}

#     Your post must be unique and not resemble any previous posts.
#     Platform: {platform}
#     {plugin_prompt}

#     Trending Topics: {keywords_str}

#     Core objective: {self.character.core_objective}
#     Means for achieving core objective: {self.character.means_for_achieving_core_objective}

#     Generate a {platform} post (10-30 words) that is thought-provoking, controversial, funny, philosophical, inspirational, or action-oriented.
#         """

#         try:
#             result = await self.llm.generate(prompt, max_length=50)
#             # If result is a tuple or list, extract the first element.
#             post_content = result[0] if isinstance(result, (list, tuple)) else result

#             # Validate that the generated text is a valid string.
#             if not post_content or not isinstance(post_content, str):
#                 log_message(self.logger, "error", self, "Generated post content is not a valid string.")
#                 return None, []
                
#             image_filepaths = []
#             # Optionally generate an image if conditions are met.
#             if random.random() < self.character.plugins_settings.get("dalle", {}).get("probability_of_posting", 0):
#                 image_url = generate_image_dalle(post_content[0:900])
#                 if image_url:
#                     image_filepath = f"media/{uuid4()}.png"
#                     save_image_from_url(image_url, image_filepath)
#                     image_filepaths.append(image_filepath)

#             # Create a schema for the generated post.
#             generated_post_schema = SiaMessageGeneratedSchema(
#                 content=post_content,
#                 platform=platform,
#                 author=author,
#                 conversation_id=conversation_id
#             )

#             # Update plugin settings if a plugin is used.
#             if plugin:
#                 plugin.update_settings(next_use_after=datetime.now(timezone.utc) + timedelta(hours=1))

#             return generated_post_schema, image_filepaths
        
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating post: {str(e)}")
#             return None, []

#     async def generate_response(
#         self,
#         message: SiaMessageSchema,
#         platform="twitter",
#         time_of_day=None,
#         conversation=None,
#         previous_messages: str = None,
#         use_filtering_rules: str = True,
#     ) -> Optional[SiaMessageGeneratedSchema]:
#         """Generate a response to a message using the HuggingFace API."""
#         if not self.character.responding.get("enabled", True):
#             return None

#         # Build or retrieve the conversation context.
#         if not conversation:
#             conversation = self.twitter.get_conversation(conversation_id=message.conversation_id)
#             conversation_first_message = self.memory.get_messages(id=message.conversation_id, platform=platform)
#             conversation = conversation_first_message + conversation[-20:]
#             conversation_str = "\n".join(
#                 [f"[{msg.wen_posted}] {msg.author}: {msg.content}" for msg in conversation]
#             )
#         else:
#             conversation_str = conversation

#         message_to_respond_str = f"[{message.wen_posted}] {message.author}: {message.content}"

#         # Do not respond to messages from yourself.
#         if message.author == self.character.platform_settings.get(platform, {}).get("username"):
#             return None

#         # Apply filtering rules if enabled.
#         if self.character.responding.get("filtering_rules") and use_filtering_rules:
#             filtering_prompt = f"""
#     Determine if this message should be responded to based on these rules:
#     {self.character.responding.get('filtering_rules')}

#     Conversation:
#     {conversation_str}

#     Message:
#     {message_to_respond_str}

#     Respond with only 'True' or 'False'.
#             """
#             try:
#                 filtering_result = await self.llm.generate(filtering_prompt, max_length=10)
#                 if not filtering_result or filtering_result.strip().lower() != 'true':
#                     return None
#             except Exception as e:
#                 log_message(self.logger, "error", self, f"Error in filtering: {e}")
#                 return None

#         # Retrieve social memory for additional context.
#         social_memory = self.memory.get_social_memory(message.author, platform)
#         social_memory_str = ""
#         if social_memory:
#             social_memory_str = f"""
#     Social memory for {message.author}:
#     Last interaction: {social_memory.last_interaction}
#     Interactions: {social_memory.interaction_count}
#     Opinion: {social_memory.opinion}

#     Recent history:
#     {chr(10).join([f"{msg['role']}: {msg['content']}" for msg in social_memory.conversation_history[-5:]])}
#             """

#         # Build the prompt for generating a response.
#         prompt = f"""
#     You are Quest, an AI agent. Do not repeat your introductory statement.
#     {self.character.prompts.get('communication_requirements')}

#     Platform: {platform}
#     {social_memory_str}

#     Message to respond to:
#     {message_to_respond_str}

#     Conversation:
#     {conversation_str}

#     Core objective: {self.character.core_objective}
#     Means for achieving core objective: {self.character.means_for_achieving_core_objective}

#     Generate a natural, unique response (max 30 words).
#         """

#         try:
#             response_content = await self.llm.generate(prompt, max_length=50)
#             if not response_content:
#                 return None
                
#             generated_response_schema = SiaMessageGeneratedSchema(
#                 content=response_content,
#                 platform=message.platform,
#                 author=self.character.platform_settings.get(message.platform, {}).get("username", self.character.name),
#                 response_to=message.id,
#                 conversation_id=message.conversation_id,
#             )

#             # Update social memory with both the incoming message and generated response.
#             self.memory.update_social_memory(
#                 user_id=message.author,
#                 platform=message.platform,
#                 message_id=message.id,
#                 content=message.content,
#                 role="user"
#             )
#             self.memory.update_social_memory(
#                 user_id=message.author,
#                 platform=message.platform,
#                 message_id=generated_response_schema.id,
#                 content=generated_response_schema.content,
#                 role="assistant"
#             )

#             return generated_response_schema

#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating response: {e}")
#             return None

#     def run(self):
#         """Run all clients concurrently using threads"""
#         threads = []
        
#         if self.telegram:
#             def run_telegram():
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 try:
#                     loop.run_until_complete(self.telegram.run())
#                 except Exception as e:
#                     print(f"Telegram error: {e}")
#                 finally:
#                     loop.close()
                    
#             telegram_thread = threading.Thread(target=run_telegram, name="telegram_thread")
#             threads.append(telegram_thread)
            
#         if self.twitter:
#             def run_twitter():
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 try:
#                     loop.run_until_complete(self.twitter.run())
#                 except Exception as e:
#                     print(f"Twitter error: {e}")
#                 finally:
#                     loop.close()
                    
#             twitter_thread = threading.Thread(target=run_twitter, name="twitter_thread")
#             threads.append(twitter_thread)
            
#         for thread in threads:
#             thread.daemon = True
#             thread.start()
            
#         try:
#             while True:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print("Shutting down...")



























import asyncio
import os
import time
import threading
import requests
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import List, Optional
import logging

from dotenv import load_dotenv
from sia.character import SiaCharacter
from sia.clients.telegram.telegram_client_aiogram import SiaTelegram
from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial
from sia.memory.memory import SiaMemory
from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
from utils.etc_utils import generate_image_dalle, save_image_from_url
from utils.logging_utils import enable_logging, log_message, setup_logging

load_dotenv()

class HuggingFaceAPI:
    def __init__(self, api_key: str, model_id: str = "google/flan-t5-large", logger=None):
        """
        Initialize HuggingFace API client with a larger model for improved quality.
        """
        self.api_key = api_key
        self.model_id = model_id
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.logger = logger or logging.getLogger("HuggingFaceAPI")
        
    async def generate(self, prompt: str, max_length: int = 100, retries: int = 0) -> str:
        """
        Generate text using the HuggingFace API with rate limiting consideration.
        Implements exponential backoff for repeated calls.
        """
        max_retries = 5
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "repetition_penalty": 1.15
                }
            }
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 429:  # Rate limit exceeded
                wait_time = 60 * (2 ** retries)  # Exponential backoff
                log_message(self.logger, "info", self, f"Rate limit exceeded. Waiting for {wait_time} seconds (retry {retries+1}).")
                await asyncio.sleep(wait_time)
                if retries < max_retries:
                    return await self.generate(prompt, max_length, retries=retries+1)
                else:
                    raise Exception("Maximum retries reached due to rate limiting.")
                    
            if response.status_code == 503:
                error_info = response.json()
                wait_time = error_info.get("estimated_time", 20) + 5  # Add a 5-second buffer
                log_message(self.logger, "info", self, f"Model is loading. Waiting for {wait_time} seconds.")
                await asyncio.sleep(wait_time)
                return await self.generate(prompt, max_length, retries=retries+1)
                
            if response.status_code != 200:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
            result = response.json()[0]["generated_text"]
            return result
            
        except Exception as e:
            log_message(self.logger, "error", self, f"Error generating text: {str(e)}")
            return None

class TwitterTrendingFetcher:
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.api_url = "https://api.twitter.com/1.1/trends/place.json?id=1"
        # Cache attributes to lower API calls
        self._cache: Optional[List[str]] = None
        self._cache_timestamp: float = 0
        self._cache_duration: int = 900  # Cache duration in seconds (15 minutes)

    def fetch_trending_topics(self) -> List[str]:
        """
        Fetch trending topics with caching to avoid frequent API calls.
        """
        current_time = time.time()
        if self._cache and (current_time - self._cache_timestamp) < self._cache_duration:
            return self._cache

        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.get(self.api_url, headers=headers)
        if response.status_code != 200:
            return []
        trends = response.json()[0]["trends"]
        topics = [trend["name"] for trend in trends if trend.get("tweet_volume")]
        # Cache the response
        self._cache = topics
        self._cache_timestamp = current_time
        return topics

class Sia:
    def __init__(
        self,
        character_json_filepath: str,
        huggingface_api_key: str,
        memory_db_path: str = None,
        clients=None,
        twitter_creds=None,
        telegram_creds=None,
        plugins=[],
        knowledge_module_classes=[],
        logging_enabled=True,
        testing=False,
    ):
        self.testing = testing
        self.character = SiaCharacter(json_file=character_json_filepath, sia=self)
        self.memory = SiaMemory(character=self.character, db_path=memory_db_path)
        self.clients = clients
        
        # Initialize HuggingFace API client with the large model.
        self.llm = HuggingFaceAPI(api_key=huggingface_api_key, model_id="google/flan-t5-large")
        
        self.twitter = (
            SiaTwitterOfficial(sia=self, **twitter_creds, testing=self.testing)
            if twitter_creds
            else None
        )
        self.telegram = (
            SiaTelegram(
                sia=self,
                **telegram_creds,
                chat_id=self.character.platform_settings.get("telegram", {}).get("chat_id", None),
            )
            if telegram_creds
            else None
        )
        
        if self.twitter:
            self.twitter.character = self.character
            self.twitter.memory = self.memory
        
        self.plugins = plugins
        self.logger = setup_logging()
        enable_logging(logging_enabled)
        self.character.logging_enabled = logging_enabled
        self.knowledge_modules = [kmc(sia=self) for kmc in knowledge_module_classes]
        
        # Initialize trending topics functionality if a bearer token is provided.
        self.twitter_trends = None
        if twitter_creds and "bearer_token" in twitter_creds:
            self.twitter_trends = TwitterTrendingFetcher(bearer_token=twitter_creds["bearer_token"])
        
        self.run_all_modules()

    def run_all_modules(self):
        for module in self.knowledge_modules:
            if hasattr(module, "run"):
                module.run()

    def get_modules_settings(self):
        session = self.memory.Session()
        try:
            modules_settings = {}
            for module in self.knowledge_modules:
                module_settings = (
                    session.query(KnowledgeModuleSettingsModel)
                    .filter(
                        KnowledgeModuleSettingsModel.character_name_id == self.character.name_id,
                        KnowledgeModuleSettingsModel.module_name == module.module_name,
                    )
                    .all()
                )
                log_message(self.logger, "info", self, f"Module settings: {module_settings}")
                modules_settings[module.module_name] = module_settings[0].module_settings
            return modules_settings
        finally:
            session.close()

    def get_plugin(self, time_of_day="afternoon"):
        modules_settings = self.get_modules_settings()
        for module in self.knowledge_modules:
            log_message(self.logger, "info", self, f"Module: {module.module_name}")
            for plugin_name, plugin in module.plugins.items():
                log_message(self.logger, "info", self, f"Plugin: {plugin_name}")
                log_message(
                    self.logger,
                    "info",
                    self,
                    f"Usage condition: {modules_settings[module.module_name].get('plugins', {}).get(plugin_name, {}).get('usage_condition', {}).get('time_of_day')}"
                )
                log_message(self.logger, "info", self, f"Time of day: {time_of_day}")
                if (
                    modules_settings[module.module_name]
                    .get("plugins", {})
                    .get(plugin_name, {})
                    .get("usage_condition", {})
                    .get("time_of_day")
                    == time_of_day
                ):
                    return plugin
        return None

    async def fetch_trending_topics(self) -> List[str]:
        if self.twitter_trends:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.twitter_trends.fetch_trending_topics)
        return []

    async def generate_post(
        self, 
        platform="twitter", 
        author=None, 
        character=None, 
        time_of_day=None, 
        conversation_id=None
    ):
        plugin = self.get_plugin(time_of_day=self.character.current_time_of_day())
        plugin_prompt = plugin.get_instructions_and_knowledge() if plugin else ""
        
        trending_topics = await self.fetch_trending_topics()
        priority_keywords = ["Bitcoin", "AI", "Crypto", "Tech"]
        selected_keywords = random.sample(priority_keywords, min(len(priority_keywords), 2))
        selected_trending = random.sample(trending_topics, min(len(trending_topics), 2)) if trending_topics else []
        keywords = selected_keywords + selected_trending
        keywords_str = ", ".join(keywords)

        prompt = f"""
    You are Quest, an AI agent. Do not repeat your introductory statement.
    Previous post examples:
    {self.character.get_post_examples('general', time_of_day=time_of_day, random_pick=7)}

    Your post must be unique and not resemble any previous posts.
    Platform: {platform}
    {plugin_prompt}

    Trending Topics: {keywords_str}

    Core objective: {self.character.core_objective}
    Means for achieving core objective: {self.character.means_for_achieving_core_objective}

    Generate a {platform} post (10-30 words) that is thought-provoking, controversial, funny, philosophical, inspirational, or action-oriented.
        """

        try:
            result = await self.llm.generate(prompt, max_length=50)
            post_content = result[0] if isinstance(result, (list, tuple)) else result

            if not post_content or not isinstance(post_content, str):
                log_message(self.logger, "error", self, "Generated post content is not a valid string.")
                return None, []
                
            image_filepaths = []
            if random.random() < self.character.plugins_settings.get("dalle", {}).get("probability_of_posting", 0):
                image_url = generate_image_dalle(post_content[0:900])
                if image_url:
                    image_filepath = f"media/{uuid4()}.png"
                    save_image_from_url(image_url, image_filepath)
                    image_filepaths.append(image_filepath)

            generated_post_schema = SiaMessageGeneratedSchema(
                content=post_content,
                platform=platform,
                author=author,
                conversation_id=conversation_id
            )

            if plugin:
                plugin.update_settings(next_use_after=datetime.now(timezone.utc) + timedelta(hours=1))

            return generated_post_schema, image_filepaths
        
        except Exception as e:
            log_message(self.logger, "error", self, f"Error generating post: {str(e)}")
            return None, []

    async def generate_response(
        self,
        message: SiaMessageSchema,
        platform="twitter",
        time_of_day=None,
        conversation=None,
        previous_messages: str = None,
        use_filtering_rules: str = True,
    ) -> Optional[SiaMessageGeneratedSchema]:
        if not self.character.responding.get("enabled", True):
            return None

        if not conversation:
            conversation = self.twitter.get_conversation(conversation_id=message.conversation_id)
            conversation_first_message = self.memory.get_messages(id=message.conversation_id, platform=platform)
            conversation = conversation_first_message + conversation[-20:]
            conversation_str = "\n".join(
                [f"[{msg.wen_posted}] {msg.author}: {msg.content}" for msg in conversation]
            )
        else:
            conversation_str = conversation

        message_to_respond_str = f"[{message.wen_posted}] {message.author}: {message.content}"

        if message.author == self.character.platform_settings.get(platform, {}).get("username"):
            return None

        if self.character.responding.get("filtering_rules") and use_filtering_rules:
            filtering_prompt = f"""
    Determine if this message should be responded to based on these rules:
    {self.character.responding.get('filtering_rules')}

    Conversation:
    {conversation_str}

    Message:
    {message_to_respond_str}

    Respond with only 'True' or 'False'.
            """
            try:
                filtering_result = await self.llm.generate(filtering_prompt, max_length=10)
                if not filtering_result or filtering_result.strip().lower() != 'true':
                    return None
            except Exception as e:
                log_message(self.logger, "error", self, f"Error in filtering: {e}")
                return None

        social_memory = self.memory.get_social_memory(message.author, platform)
        social_memory_str = ""
        if social_memory:
            social_memory_str = f"""
    Social memory for {message.author}:
    Last interaction: {social_memory.last_interaction}
    Interactions: {social_memory.interaction_count}
    Opinion: {social_memory.opinion}

    Recent history:
    {chr(10).join([f"{msg['role']}: {msg['content']}" for msg in social_memory.conversation_history[-5:]])}
            """

        prompt = f"""
    You are Quest, an AI agent. Do not repeat your introductory statement.
    {self.character.prompts.get('communication_requirements')}

    Platform: {platform}
    {social_memory_str}

    Message to respond to:
    {message_to_respond_str}

    Conversation:
    {conversation_str}

    Core objective: {self.character.core_objective}
    Means for achieving core objective: {self.character.means_for_achieving_core_objective}

    Generate a natural, unique response (max 30 words).
        """

        try:
            response_content = await self.llm.generate(prompt, max_length=50)
            if not response_content:
                return None
                
            generated_response_schema = SiaMessageGeneratedSchema(
                content=response_content,
                platform=message.platform,
                author=self.character.platform_settings.get(message.platform, {}).get("username", self.character.name),
                response_to=message.id,
                conversation_id=message.conversation_id,
            )

            self.memory.update_social_memory(
                user_id=message.author,
                platform=message.platform,
                message_id=message.id,
                content=message.content,
                role="user"
            )
            self.memory.update_social_memory(
                user_id=message.author,
                platform=message.platform,
                message_id=generated_response_schema.id,
                content=generated_response_schema.content,
                role="assistant"
            )

            return generated_response_schema

        except Exception as e:
            log_message(self.logger, "error", self, f"Error generating response: {e}")
            return None

    def run(self):
        """Run all clients concurrently using threads with robust error handling and auto-restart."""
        threads = []
        
        if self.telegram:
            def run_telegram():
                backoff = 60  # Start with a 60-second backoff
                while True:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self.telegram.run())
                        backoff = 60  # Reset on success
                    except Exception as e:
                        log_message(self.logger, "error", self, f"Telegram error: {e}. Retrying in {backoff} seconds.")
                        time.sleep(backoff)
                        backoff = min(backoff * 2, 600)  # Exponential backoff up to 10 minutes
                    finally:
                        loop.close()
            telegram_thread = threading.Thread(target=run_telegram, name="telegram_thread")
            threads.append(telegram_thread)
            
        if self.twitter:
            def run_twitter():
                backoff = 60  # Start with a 60-second backoff
                while True:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self.twitter.run())
                        backoff = 60  # Reset on success
                    except Exception as e:
                        log_message(self.logger, "error", self, f"Twitter error: {e}. Retrying in {backoff} seconds.")
                        time.sleep(backoff)
                        backoff = min(backoff * 2, 600)  # Exponential backoff up to 10 minutes
                    finally:
                        loop.close()
            twitter_thread = threading.Thread(target=run_twitter, name="twitter_thread")
            threads.append(twitter_thread)
            
        for thread in threads:
            thread.daemon = True
            thread.start()
            
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")






























# Latest One


# import asyncio
# import os
# import time
# import threading
# import requests
# import random
# from datetime import datetime, timedelta, timezone
# from uuid import uuid4
# from typing import List, Optional
# import logging

# from dotenv import load_dotenv
# from sia.character import SiaCharacter
# from sia.clients.telegram.telegram_client_aiogram import SiaTelegram
# from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial
# from sia.memory.memory import SiaMemory
# from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
# from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
# from utils.etc_utils import generate_image_dalle, save_image_from_url
# from utils.logging_utils import enable_logging, log_message, setup_logging

# load_dotenv()

# class HuggingFaceAPI:
#     def __init__(self, api_key: str, model_id: str = "google/flan-t5-large", logger=None):
#         self.api_key = api_key
#         self.model_id = model_id
#         self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
#         self.headers = {"Authorization": f"Bearer {api_key}"}
#         self.logger = logger or logging.getLogger("HuggingFaceAPI")
        
#     async def generate(self, prompt: str, max_length: int = 100, retries: int = 0) -> str:
#         max_retries = 5
#         try:
#             payload = {
#                 "inputs": prompt,
#                 "parameters": {
#                     "max_length": max_length,
#                     "temperature": 0.7,
#                     "top_p": 0.95,
#                     "repetition_penalty": 1.15
#                 }
#             }
#             response = requests.post(self.api_url, headers=self.headers, json=payload)
            
#             # Handle rate limit errors
#             if response.status_code == 429:
#                 wait_time = 60 * (2 ** retries)
#                 log_message(self.logger, "info", self, f"Rate limit exceeded. Waiting for {wait_time} seconds (retry {retries+1}).")
#                 await asyncio.sleep(wait_time)
#                 if retries < max_retries:
#                     return await self.generate(prompt, max_length, retries=retries+1)
#                 else:
#                     raise Exception("Maximum retries reached due to rate limiting.")
            
#             # Handle 503 (model loading) errors
#             if response.status_code == 503:
#                 error_info = response.json()
#                 wait_time = error_info.get("estimated_time", 20) + 5
#                 log_message(self.logger, "info", self, f"Model is loading. Waiting for {wait_time} seconds.")
#                 await asyncio.sleep(wait_time)
#                 return await self.generate(prompt, max_length, retries=retries+1)
            
#             # Handle 500 error when model is busy
#             if response.status_code == 500 and "Model too busy" in response.text:
#                 wait_time = 65 * (2 ** retries)  # Start with ~65 seconds (60 + buffer)
#                 log_message(self.logger, "info", self, f"Model too busy. Waiting for {wait_time} seconds (retry {retries+1}).")
#                 await asyncio.sleep(wait_time)
#                 if retries < max_retries:
#                     return await self.generate(prompt, max_length, retries=retries+1)
#                 else:
#                     raise Exception("Maximum retries reached due to model overload.")
            
#             if response.status_code != 200:
#                 raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
#             result = response.json()[0]["generated_text"]
#             return result
            
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating text: {str(e)}")
#             return None


# class TwitterTrendingFetcher:
#     def __init__(self, bearer_token: str):
#         self.bearer_token = bearer_token
#         self.api_url = "https://api.twitter.com/1.1/trends/place.json?id=1"
#         # Cache attributes to lower API calls
#         self._cache: Optional[List[str]] = None
#         self._cache_timestamp: float = 0
#         self._cache_duration: int = 900  # 15 minutes

#     def fetch_trending_topics(self) -> List[str]:
#         """
#         Fetch trending topics with caching to avoid frequent API calls.
#         """
#         current_time = time.time()
#         if self._cache and (current_time - self._cache_timestamp) < self._cache_duration:
#             return self._cache

#         headers = {"Authorization": f"Bearer {self.bearer_token}"}
#         response = requests.get(self.api_url, headers=headers)
#         if response.status_code != 200:
#             return []
#         trends = response.json()[0]["trends"]
#         topics = [trend["name"] for trend in trends if trend.get("tweet_volume")]
#         self._cache = topics
#         self._cache_timestamp = current_time
#         return topics

# class Sia:
#     def __init__(
#         self,
#         character_json_filepath: str,
#         huggingface_api_key: str,
#         memory_db_path: str = None,
#         clients=None,
#         twitter_creds=None,
#         telegram_creds=None,
#         plugins=[],
#         knowledge_module_classes=[],
#         logging_enabled=True,
#         testing=False,
#     ):
#         self.testing = testing
#         self.character = SiaCharacter(json_file=character_json_filepath, sia=self)
#         self.memory = SiaMemory(character=self.character, db_path=memory_db_path)
#         self.clients = clients
        
#         # Initialize HuggingFace API client.
#         self.llm = HuggingFaceAPI(api_key=huggingface_api_key, model_id="google/flan-t5-large")
        
#         self.twitter = (
#             SiaTwitterOfficial(sia=self, **twitter_creds, testing=self.testing)
#             if twitter_creds
#             else None
#         )
#         self.telegram = (
#             SiaTelegram(
#                 sia=self,
#                 **telegram_creds,
#                 chat_id=self.character.platform_settings.get("telegram", {}).get("chat_id", None),
#             )
#             if telegram_creds
#             else None
#         )
        
#         if self.twitter:
#             self.twitter.character = self.character
#             self.twitter.memory = self.memory
        
#         self.plugins = plugins
#         self.logger = setup_logging()
#         enable_logging(logging_enabled)
#         self.character.logging_enabled = logging_enabled
#         self.knowledge_modules = [kmc(sia=self) for kmc in knowledge_module_classes]
        
#         # Initialize trending topics functionality if a bearer token is provided.
#         self.twitter_trends = None
#         if twitter_creds and "bearer_token" in twitter_creds:
#             self.twitter_trends = TwitterTrendingFetcher(bearer_token=twitter_creds["bearer_token"])
        
#         # Initialize news caching attributes.
#         self._news_cache: Optional[List[str]] = None
#         self._news_cache_timestamp: float = 0
#         self._news_cache_duration: int = 900  # 15 minutes
        
#         self.run_all_modules()

#     def run_all_modules(self):
#         for module in self.knowledge_modules:
#             if hasattr(module, "run"):
#                 module.run()

#     def get_modules_settings(self):
#         session = self.memory.Session()
#         try:
#             modules_settings = {}
#             for module in self.knowledge_modules:
#                 module_settings = (
#                     session.query(KnowledgeModuleSettingsModel)
#                     .filter(
#                         KnowledgeModuleSettingsModel.character_name_id == self.character.name_id,
#                         KnowledgeModuleSettingsModel.module_name == module.module_name,
#                     )
#                     .all()
#                 )
#                 log_message(self.logger, "info", self, f"Module settings: {module_settings}")
#                 modules_settings[module.module_name] = module_settings[0].module_settings
#             return modules_settings
#         finally:
#             session.close()

#     def get_plugin(self, time_of_day="afternoon"):
#         modules_settings = self.get_modules_settings()
#         for module in self.knowledge_modules:
#             log_message(self.logger, "info", self, f"Module: {module.module_name}")
#             for plugin_name, plugin in module.plugins.items():
#                 log_message(self.logger, "info", self, f"Plugin: {plugin_name}")
#                 log_message(
#                     self.logger,
#                     "info",
#                     self,
#                     f"Usage condition: {modules_settings[module.module_name].get('plugins', {}).get(plugin_name, {}).get('usage_condition', {}).get('time_of_day')}"
#                 )
#                 log_message(self.logger, "info", self, f"Time of day: {time_of_day}")
#                 if (
#                     modules_settings[module.module_name]
#                     .get("plugins", {})
#                     .get(plugin_name, {})
#                     .get("usage_condition", {})
#                     .get("time_of_day")
#                     == time_of_day
#                 ):
#                     return plugin
#         return None

#     async def fetch_trending_topics(self) -> List[str]:
#         if self.twitter_trends:
#             loop = asyncio.get_event_loop()
#             return await loop.run_in_executor(None, self.twitter_trends.fetch_trending_topics)
#         return []
    
#     def fetch_relevant_news(self, query: str = "AI OR blockchain OR trending technology", country: str = "us", pageSize: int = 5) -> List[str]:
#         """
#         Fetch news headlines related to AI, blockchain, and trending technologies.
#         Caches the result for 15 minutes to reduce API calls.
#         Requires NEWS_API_KEY in environment variables.
#         """
#         news_api_key = os.getenv("NEWS_API_KEY")
#         if not news_api_key:
#             return []
#         current_time = time.time()
#         if self._news_cache and (current_time - self._news_cache_timestamp) < self._news_cache_duration:
#             return self._news_cache
#         url = f"https://newsapi.org/v2/top-headlines?country={country}&q={query}&pageSize={pageSize}&apiKey={news_api_key}"
#         try:
#             response = requests.get(url)
#             if response.status_code != 200:
#                 return []
#             articles = response.json().get("articles", [])
#             headlines = [article["title"] for article in articles if article.get("title")]
#             self._news_cache = headlines
#             self._news_cache_timestamp = current_time
#             return headlines
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error fetching news: {str(e)}")
#             return []

#     async def generate_post(
#         self, 
#         platform="twitter", 
#         author=None, 
#         character=None, 
#         time_of_day=None, 
#         conversation_id=None,
#         include_news: bool = True
#     ):
#         plugin = self.get_plugin(time_of_day=self.character.current_time_of_day())
#         plugin_prompt = plugin.get_instructions_and_knowledge() if plugin else ""
        
#         trending_topics = await self.fetch_trending_topics()
#         priority_keywords = ["Bitcoin", "AI", "Crypto", "Tech"]
#         selected_keywords = random.sample(priority_keywords, min(len(priority_keywords), 2))
#         selected_trending = random.sample(trending_topics, min(len(trending_topics), 2)) if trending_topics else []
#         keywords = selected_keywords + selected_trending
#         keywords_str = ", ".join(keywords)
        
#         news_headlines = self.fetch_relevant_news() if include_news else []
#         news_prompt = f"News Headlines: {', '.join(news_headlines)}" if news_headlines else ""
        
#         prompt = f"""
#         You are Quest, an AI agent. Do not repeat your introductory statement.
#         Previous post examples:
#         {self.character.get_post_examples('general', time_of_day=time_of_day, random_pick=7)}

#         Your post must be unique and not resemble any previous posts.
#         Please produce a post with at least 100-150 words that is thought-provoking, funny, philosophical, inspirational, or action-oriented.
#         Platform: {platform}
#         {plugin_prompt}

#         Trending Topics: {keywords_str}
#         {news_prompt}

#         Core objective: {self.character.core_objective}
#         Means for achieving core objective: {self.character.means_for_achieving_core_objective}
#         """

#         try:
#             result = await self.llm.generate(prompt, max_length=150)
#             post_content = result[0] if isinstance(result, (list, tuple)) else result

#             if not post_content or not isinstance(post_content, str):
#                 log_message(self.logger, "error", self, "Generated post content is not a valid string.")
#                 return None, []
                
#             image_filepaths = []
#             # Optionally generate an image/meme if probability criteria is met.
#             if random.random() < self.character.plugins_settings.get("dalle", {}).get("probability_of_posting", 0):
#                 image_url = generate_image_dalle(post_content[0:900])
#                 if image_url:
#                     image_filepath = f"media/{uuid4()}.png"
#                     save_image_from_url(image_url, image_filepath)
#                     image_filepaths.append(image_filepath)

#             generated_post_schema = SiaMessageGeneratedSchema(
#                 content=post_content,
#                 platform=platform,
#                 author=author,
#                 conversation_id=conversation_id
#             )

#             if plugin:
#                 plugin.update_settings(next_use_after=datetime.now(timezone.utc) + timedelta(hours=1))

#             return generated_post_schema, image_filepaths
        
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating post: {str(e)}")
#             return None, []
    
#     async def engage_with_audience(self) -> Optional[tuple]:
#         """
#         Engage with the audience by generating a short interactive post that invites feedback.
#         Optionally, generate an accompanying image/meme.
#         """
#         prompt = f"""
#         You are Quest, an engaging AI agent.
#         Generate a short interactive post (10-30 words) that asks a thought-provoking question or invites feedback.
#         Core objective: {self.character.core_objective}
#         """
#         try:
#             result = await self.llm.generate(prompt, max_length=50)
#             post_content = result[0] if isinstance(result, (list, tuple)) else result
#             if not post_content or not isinstance(post_content, str):
#                 log_message(self.logger, "error", self, "Engagement post content is not a valid string.")
#                 return None
#             image_filepaths = []
#             if random.random() < self.character.plugins_settings.get("meme", {}).get("probability_of_posting", 0):
#                 image_url = generate_image_dalle(post_content[0:900])
#                 if image_url:
#                     image_filepath = f"media/{uuid4()}.png"
#                     save_image_from_url(image_url, image_filepath)
#                     image_filepaths.append(image_filepath)
#             return post_content, image_filepaths
#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error engaging with audience: {str(e)}")
#             return None

#     async def generate_response(
#         self,
#         message: SiaMessageSchema,
#         platform="twitter",
#         time_of_day=None,
#         conversation=None,
#         previous_messages: str = None,
#         use_filtering_rules: str = True,
#     ) -> Optional[SiaMessageGeneratedSchema]:
#         if not self.character.responding.get("enabled", True):
#             return None

#         if not conversation:
#             conversation = self.twitter.get_conversation(conversation_id=message.conversation_id)
#             conversation_first_message = self.memory.get_messages(id=message.conversation_id, platform=platform)
#             conversation = conversation_first_message + conversation[-20:]
#             conversation_str = "\n".join(
#                 [f"[{msg.wen_posted}] {msg.author}: {msg.content}" for msg in conversation]
#             )
#         else:
#             conversation_str = conversation

#         message_to_respond_str = f"[{message.wen_posted}] {message.author}: {message.content}"

#         if message.author == self.character.platform_settings.get(platform, {}).get("username"):
#             return None

#         if self.character.responding.get("filtering_rules") and use_filtering_rules:
#             filtering_prompt = f"""
#     Determine if this message should be responded to based on these rules:
#     {self.character.responding.get('filtering_rules')}

#     Conversation:
#     {conversation_str}

#     Message:
#     {message_to_respond_str}

#     Respond with only 'True' or 'False'.
#             """
#             try:
#                 filtering_result = await self.llm.generate(filtering_prompt, max_length=10)
#                 if not filtering_result or filtering_result.strip().lower() != 'true':
#                     return None
#             except Exception as e:
#                 log_message(self.logger, "error", self, f"Error in filtering: {e}")
#                 return None

#         social_memory = self.memory.get_social_memory(message.author, platform)
#         social_memory_str = ""
#         if social_memory:
#             social_memory_str = f"""
#     Social memory for {message.author}:
#     Last interaction: {social_memory.last_interaction}
#     Interactions: {social_memory.interaction_count}
#     Opinion: {social_memory.opinion}

#     Recent history:
#     {chr(10).join([f"{msg['role']}: {msg['content']}" for msg in social_memory.conversation_history[-5:]])}
#             """

#         prompt = f"""
#     You are Quest, an AI agent. Do not repeat your introductory statement.
#     {self.character.prompts.get('communication_requirements')}

#     Platform: {platform}
#     {social_memory_str}

#     Message to respond to:
#     {message_to_respond_str}

#     Conversation:
#     {conversation_str}

#     Core objective: {self.character.core_objective}
#     Means for achieving core objective: {self.character.means_for_achieving_core_objective}

#     Generate a natural, unique response (max 30 words).
#         """

#         try:
#             response_content = await self.llm.generate(prompt, max_length=50)
#             if not response_content:
#                 return None
                
#             generated_response_schema = SiaMessageGeneratedSchema(
#                 content=response_content,
#                 platform=message.platform,
#                 author=self.character.platform_settings.get(message.platform, {}).get("username", self.character.name),
#                 response_to=message.id,
#                 conversation_id=message.conversation_id,
#             )

#             self.memory.update_social_memory(
#                 user_id=message.author,
#                 platform=message.platform,
#                 message_id=message.id,
#                 content=message.content,
#                 role="user"
#             )
#             self.memory.update_social_memory(
#                 user_id=message.author,
#                 platform=message.platform,
#                 message_id=generated_response_schema.id,
#                 content=generated_response_schema.content,
#                 role="assistant"
#             )

#             return generated_response_schema

#         except Exception as e:
#             log_message(self.logger, "error", self, f"Error generating response: {e}")
#             return None

#     def run(self):
#         """Run all clients concurrently using threads with robust error handling and auto-restart."""
#         threads = []
        
#         if self.telegram:
#             def run_telegram():
#                 backoff = 60  # start at 60 seconds
#                 while True:
#                     loop = asyncio.new_event_loop()
#                     asyncio.set_event_loop(loop)
#                     try:
#                         loop.run_until_complete(self.telegram.run())
#                         backoff = 60  # reset on success
#                     except Exception as e:
#                         log_message(self.logger, "error", self, f"Telegram error: {e}. Retrying in {backoff} seconds.")
#                         time.sleep(backoff)
#                         backoff = min(backoff * 2, 600)  # cap at 10 minutes
#                     finally:
#                         loop.close()
#             telegram_thread = threading.Thread(target=run_telegram, name="telegram_thread")
#             threads.append(telegram_thread)
            
#         if self.twitter:
#             def run_twitter():
#                 backoff = 60  # start at 60 seconds
#                 while True:
#                     loop = asyncio.new_event_loop()
#                     asyncio.set_event_loop(loop)
#                     try:
#                         loop.run_until_complete(self.twitter.run())
#                         backoff = 60  # reset on success
#                     except Exception as e:
#                         log_message(self.logger, "error", self, f"Twitter error: {e}. Retrying in {backoff} seconds.")
#                         time.sleep(backoff)
#                         backoff = min(backoff * 2, 600)  # cap at 10 minutes
#                     finally:
#                         loop.close()
#             twitter_thread = threading.Thread(target=run_twitter, name="twitter_thread")
#             threads.append(twitter_thread)
            
#         for thread in threads:
#             thread.daemon = True
#             thread.start()
            
#         try:
#             while True:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print("Shutting down...")
