import asyncio
from datetime import datetime, timedelta, timezone
import os
import random
import threading
import time
from datetime import timezone
from uuid import uuid4
import requests
from typing import List, Optional
import logging

from sia.character import SiaCharacter
from sia.clients.telegram.telegram_client_aiogram import SiaTelegram
from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial
from sia.memory.memory import SiaMemory
from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
from utils.etc_utils import generate_image_dalle, save_image_from_url
from utils.logging_utils import enable_logging, log_message, setup_logging

class HuggingFaceAPI:
    def __init__(self, api_key: str, model_id: str = "google/flan-t5-small", logger=None):
        """
        Initialize HuggingFace API client with a lightweight model.
        Using flan-t5-small as default - it's efficient and has good performance for general tasks.
        """
        self.api_key = api_key
        self.model_id = model_id
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.logger = logger or logging.getLogger("HuggingFaceAPI")
        
    async def generate(self, prompt: str, max_length: int = 100) -> str:
        """
        Generate text using the HuggingFace API with rate limiting consideration
        """
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
                await asyncio.sleep(60)  # Wait for 1 minute before retrying
                return await self.generate(prompt, max_length)
                
            if response.status_code != 200:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
            return response.json()[0]["generated_text"]
            
        except Exception as e:
            log_message(self.logger, "error", self, f"Error generating text: {str(e)}")
            return None, []

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
        
        # Initialize HuggingFace API client
        self.llm = HuggingFaceAPI(
            api_key=huggingface_api_key,
            model_id="google/flan-t5-small"  # Lightweight model good for free tier
        )
        
        self.twitter = (
            SiaTwitterOfficial(sia=self, **twitter_creds, testing=self.testing)
            if twitter_creds
            else None
        )
        self.telegram = (
            SiaTelegram(
                sia=self,
                **telegram_creds,
                chat_id=self.character.platform_settings.get("telegram", {}).get(
                    "chat_id", None
                ),
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
        
        self.run_all_modules()

    def run_all_modules(self):
        """
        Run all the knowledge or plugin modules if they have a 'run' method.
        Modify this implementation as needed for your use case.
        """
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
                        KnowledgeModuleSettingsModel.character_name_id
                        == self.character.name_id,
                        KnowledgeModuleSettingsModel.module_name == module.module_name,
                    )
                    .all()
                )
                log_message(
                    self.logger, "info", self, f"Module settings: {module_settings}"
                )
                modules_settings[module.module_name] = module_settings[
                    0
                ].module_settings
            return modules_settings
        finally:
            session.close()


    def get_plugin(self, time_of_day="afternoon"):
        modules_settings = self.get_modules_settings()

        for module in self.knowledge_modules:
            log_message(
                self.logger,
                "info",
                self,
                f"Module: {module.module_name}",
            )
            for plugin_name, plugin in module.plugins.items():
                log_message(self.logger, "info", self, f"Plugin: {plugin_name}")
                log_message(
                    self.logger,
                    "info",
                    self,
                    f"Usage condition: {modules_settings[module.module_name].get('plugins', {}).get(plugin_name, {}).get('usage_condition', {}).get('time_of_day')}",
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

    async def generate_post(
        self, 
        platform="twitter", 
        author=None, 
        character=None, 
        time_of_day=None, 
        conversation_id=None
        ):
        # Get plugin (if any) based on the current time of day.
        plugin = self.get_plugin(time_of_day=self.character.current_time_of_day())
        plugin_prompt = plugin.get_instructions_and_knowledge() if plugin else ""


        # Build the prompt for generating a post.
        prompt = f"""
        System: {self.character.prompts.get('you_are')}
    
        Previous posts examples:
        {self.character.get_post_examples('general', time_of_day=time_of_day, random_pick=7)}
    
        Your post must be unique and different from previous posts.
        Platform: {platform}
        {plugin_prompt}
    
        Core objective: {self.character.core_objective}
        Means for achieving core objective: {self.character.means_for_achieving_core_objective}
    
        Generate a {platform} post (10-30 words) that is either thought-provoking, controversial, funny, philosophical, inspirational, or action-oriented.
        """

        try:
            # Call the Hugging Face API to generate text.
            result = await self.llm.generate(prompt, max_length=50)
            # If result is a tuple or list, extract the first element.
            if isinstance(result, (list, tuple)):
                post_content = result[0]
            else:
                post_content = result

            # Validate that the generated text is a valid string.
            if not post_content or not isinstance(post_content, str):
                log_message(self.logger, "error", self, "Generated post content is not a valid string.")
                return None, []
                
            image_filepaths = []

            # Image generation logic remains the same.
            if random.random() < self.character.plugins_settings.get("dalle", {}).get("probability_of_posting", 0):
                image_url = generate_image_dalle(post_content[0:900])
                if image_url:
                    image_filepath = f"media/{uuid4()}.png"
                    save_image_from_url(image_url, image_filepath)
                    image_filepaths.append(image_filepath)

            # Create a schema for the generated post.
            generated_post_schema = SiaMessageGeneratedSchema(
                content=post_content,
                platform=platform,
                author=author,
                conversation_id=conversation_id
            )

            # Update plugin settings if a plugin is used.
            if plugin:
                plugin.update_settings(
                    next_use_after=datetime.now(timezone.utc) + timedelta(hours=1)
                )

            return generated_post_schema, image_filepaths
        
        except Exception as e:
            # Log the exception using the string representation of e.
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
        """Generate a response to a message using HuggingFace API"""
        if not self.character.responding.get("enabled", True):
            return None

        if not conversation:
            conversation = self.twitter.get_conversation(
                conversation_id=message.conversation_id
            )
            conversation_first_message = self.memory.get_messages(
                id=message.conversation_id, platform=platform
            )
            conversation = conversation_first_message + conversation[-20:]
            conversation_str = "\n".join(
                [f"[{msg.wen_posted}] {msg.author}: {msg.content}"
                 for msg in conversation]
            )
        else:
            conversation_str = conversation

        message_to_respond_str = (
            f"[{message.wen_posted}] {message.author}: {message.content}"
        )

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

        response_prompt = f"""
        System: {self.character.prompts.get('you_are')}
        {self.character.prompts.get('communication_requirements')}
        
        Platform: {platform}
        {social_memory_str}
        
        Message to respond to:
        {message_to_respond_str}
        
        Conversation:
        {conversation_str}
        
        Core objective: {self.character.core_objective}
        Means: {self.character.means_for_achieving_core_objective}
        
        Generate a natural, unique response (max 30 words).
        """

        try:
            response_content = await self.llm.generate(response_prompt, max_length=50)
            
            if not response_content:
                return None
                
            generated_response_schema = SiaMessageGeneratedSchema(
                content=response_content,
                platform=message.platform,
                author=self.character.platform_settings.get(message.platform, {}).get(
                    "username", self.character.name
                ),
                response_to=message.id,
                conversation_id=message.conversation_id,
            )

            # Update social memory
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
        """Run all clients concurrently using threads"""
        threads = []
        
        if self.telegram:
            def run_telegram():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.telegram.run())
                except Exception as e:
                    print(f"Telegram error: {e}")
                finally:
                    loop.close()
                    
            telegram_thread = threading.Thread(
                target=run_telegram,
                name="telegram_thread"
            )
            threads.append(telegram_thread)
            
        if self.twitter:
            def run_twitter():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.twitter.run())
                except Exception as e:
                    print(f"Twitter error: {e}")
                finally:
                    loop.close()
                    
            twitter_thread = threading.Thread(
                target=run_twitter,
                name="twitter_thread"
            )
            threads.append(twitter_thread)
            
        for thread in threads:
            thread.daemon = True
            thread.start()
            
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    




















# import asyncio
# import datetime
# import os
# import random
# import threading
# import time
# from datetime import timezone
# from uuid import uuid4

# from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
# from langchain.prompts import ChatPromptTemplate

# from plugins.imgflip_meme_generator import ImgflipMemeGenerator
# from sia.character import SiaCharacter
# from sia.clients.telegram.telegram_client_aiogram import SiaTelegram
# from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial
# from sia.memory.memory import SiaMemory
# from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
# from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
# from sia.schemas.schemas import ResponseFilteringResultLLMSchema
# from utils.etc_utils import generate_image_dalle, save_image_from_url
# from utils.logging_utils import enable_logging, log_message, setup_logging

# from sia.clients.client_interface import SiaClientInterface




# class OpenSourceLLMWrapper:
#     def __init__(self, model_name='TinyLlama/TinyLlama-1.1B-Chat-v1.0', max_length=1024):
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.model = AutoModelForCausalLM.from_pretrained(model_name)
#         self.generator = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer)
#         self.max_length = max_length

#     def generate(self, prompt, temperature=0.7):
#         try:
#             generation_kwargs = {
#                 "max_length": self.max_length,
#                 "do_sample": True,           # Enables sampling (randomness)
#                 "temperature": temperature,  # Controls randomness
#                 "truncation": True,          # Explicitly enable truncation if needed
#                 "num_return_sequences": 1
#             }
#             # The pipeline will automatically use the tokenizer's settings when needed.
#             outputs = self.generator(prompt, **generation_kwargs)
#             return outputs[0]['generated_text']
#         except Exception as e:
#             log_message(None, "error", None, f"OpenSource LLM generation error: {e}")
#             return None

# class Sia:
#     def __init__(
#         self,
#         character_json_filepath: str,
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
        
#         # Initialize Open Source LLM
#         self.llm = OpenSourceLLMWrapper()
        
#         self.run_all_modules()

#     def run_all_modules(self):
#         import threading

#         def run_module(module):
#             module.run()

#         threads = []
#         for module in self.knowledge_modules:
#             thread = threading.Thread(target=run_module, args=(module,))
#             threads.append(thread)
#             thread.start()

#         for thread in threads:
#             thread.join()

    # def get_modules_settings(self):
    #     session = self.memory.Session()

    #     try:
    #         modules_settings = {}
    #         for module in self.knowledge_modules:
    #             module_settings = (
    #                 session.query(KnowledgeModuleSettingsModel)
    #                 .filter(
    #                     KnowledgeModuleSettingsModel.character_name_id
    #                     == self.character.name_id,
    #                     KnowledgeModuleSettingsModel.module_name == module.module_name,
    #                 )
    #                 .all()
    #             )
    #             log_message(
    #                 self.logger, "info", self, f"Module settings: {module_settings}"
    #             )
    #             modules_settings[module.module_name] = module_settings[
    #                 0
    #             ].module_settings
    #         return modules_settings
    #     finally:
    #         session.close()

    # def get_plugin(self, time_of_day="afternoon"):
    #     modules_settings = self.get_modules_settings()

    #     for module in self.knowledge_modules:
    #         log_message(
    #             self.logger,
    #             "info",
    #             self,
    #             f"Module: {module.module_name}",
    #         )
    #         for plugin_name, plugin in module.plugins.items():
    #             log_message(self.logger, "info", self, f"Plugin: {plugin_name}")
    #             log_message(
    #                 self.logger,
    #                 "info",
    #                 self,
    #                 f"Usage condition: {modules_settings[module.module_name].get('plugins', {}).get(plugin_name, {}).get('usage_condition', {}).get('time_of_day')}",
    #             )
    #             log_message(self.logger, "info", self, f"Time of day: {time_of_day}")
    #             if (
    #                 modules_settings[module.module_name]
    #                 .get("plugins", {})
    #                 .get(plugin_name, {})
    #                 .get("usage_condition", {})
    #                 .get("time_of_day")
    #                 == time_of_day
    #             ):
    #                 return plugin

    #     return None

#     def generate_post(
#         self, platform="twitter", author=None, character=None, time_of_day=None, conversation_id=None
#     ):
#         plugin = self.get_plugin(time_of_day=self.character.current_time_of_day())
#         plugin_prompt = ""
#         if plugin:
#             plugin_prompt = plugin.get_instructions_and_knowledge()
#             log_message(self.logger, "info", self, f"Plugin prompt: {plugin_prompt}")
#         else:
#             log_message(self.logger, "info", self, f"No plugin found")

#         full_prompt = f"""
#         {self.character.prompts.get('you_are', '')}
#         Platform: {platform}
#         Plugin Instructions: {plugin_prompt}
        
#         Post Requirements:
#         - Topic: {random.choice(['thought provoking', 'controversial', 'philosophical', 'inspirational'])}
#         - Length: {random.choice(['1-5', '10-15', '20-30'])} words
#         - No hashtags
        
#         Core Objective: {self.character.core_objective}
#         Means of Achieving Objective: {self.character.means_for_achieving_core_objective}
        
#         Generate a unique, creative post that follows these guidelines.
#         Previous Posts Examples:
#         {chr(10).join(self.character.get_post_examples('general', time_of_day=time_of_day, random_pick=7))}
#         """

#         generated_post_content = self.llm.generate(full_prompt, temperature=0.7)

#         image_filepaths = []
        
#         # Retain original image generation logic
#         if random.random() < self.character.plugins_settings.get("dalle", {}).get(
#             "probability_of_posting", 0
#         ):
#             image_url = generate_image_dalle(generated_post_content[0:900])
#             if image_url:
#                 image_filepath = f"media/{uuid4()}.png"
#                 save_image_from_url(image_url, image_filepath)
#                 image_filepaths.append(image_filepath)

#         imgflip_meme_generator = ImgflipMemeGenerator(
#             os.getenv("IMGFLIP_USERNAME"), os.getenv("IMGFLIP_PASSWORD")
#         )
#         if random.random() < self.character.plugins_settings.get("imgflip", {}).get(
#             "probability_of_posting", 0
#         ):
#             image_url = imgflip_meme_generator.generate_ai_meme(
#                 prefix_text=generated_post_content
#             )
#             if image_url:
#                 os.makedirs("media/imgflip_memes", exist_ok=True)
#                 image_filepath = f"media/imgflip_memes/{uuid4()}.png"
#                 save_image_from_url(image_url, image_filepath)
#                 image_filepaths.append(image_filepath)

#         generated_post_schema = SiaMessageGeneratedSchema(
#             content=generated_post_content,
#             platform=platform,
#             author=author,
#             conversation_id=conversation_id
#         )

#         if plugin:
#             log_message(
#                 self.logger,
#                 "info",
#                 self,
#                 f"Updating settings for {plugin.plugin_name}",
#             )
#             plugin.update_settings(
#                 next_use_after=datetime.datetime.now(timezone.utc)
#                 + datetime.timedelta(hours=1)
#             )
#         else:
#             log_message(self.logger, "info", self, f"No plugin found")

#         return generated_post_schema, image_filepaths

#     def generate_response(
#         self,
#         message: SiaMessageSchema,
#         platform="twitter",
#         time_of_day=None,
#         conversation=None,
#         previous_messages: str = None,
#         use_filtering_rules: str = True,
#     ) -> SiaMessageGeneratedSchema | None:
#         # Disable response if responding is not enabled
#         if not self.character.responding.get("enabled", True):
#             return None

#         # Prepare conversation context
#         if not conversation:
#             conversation = self.twitter.get_conversation(
#                 conversation_id=message.conversation_id
#             )
#             conversation_first_message = self.memory.get_messages(
#                 id=message.conversation_id, platform=platform
#             )
#             conversation = conversation_first_message + conversation[-20:]
        
#         conversation_str = "\n".join(
#             [f"[{msg.wen_posted}] {msg.author}: {msg.content}" for msg in conversation]
#         )
#         log_message(self.logger, "info", self, f"Conversation: {conversation_str.replace('\n', ' ')}")

#         message_to_respond_str = f"[{message.wen_posted}] {message.author}: {message.content}"
#         log_message(
#             self.logger, "info", self, f"Message to respond (id {message.id}): {message_to_respond_str.replace('\n', ' ')}"
#         )

#         # Prevent responding to own messages
#         if message.author == self.character.platform_settings.get(platform, {}).get("username"):
#             return None

#         # Apply filtering rules if enabled
#         if self.character.responding.get("filtering_rules") and use_filtering_rules:
#             log_message(
#                 self.logger,
#                 "info",
#                 self,
#                 f"Checking response against filtering rules: {self.character.responding.get('filtering_rules')}",
#             )

#             try:
#                 # Use OpenSourceLLMWrapper for filtering
#                 filtering_prompt = f"""
#                 You are a message filtering AI. Determine if the following message passes these filtering rules:
                
#                 Filtering Rules: {self.character.responding.get('filtering_rules')}
                
#                 Conversation Context:
#                 {conversation_str}
                
#                 Message to Evaluate:
#                 {message_to_respond_str}
                
#                 Respond with ONLY 'True' or 'False'. True means the message passes the filtering rules. 
#                 False means the message violates the filtering rules.
#                 """

#                 filtering_result = self.llm.generate(filtering_prompt, temperature=0.0)
#                 filtering_result = filtering_result.strip().lower()
                
#                 log_message(
#                     self.logger,
#                     "info",
#                     self,
#                     f"Response filtering result: {filtering_result}",
#                 )

#                 if filtering_result not in ['true', 'false']:
#                     log_message(
#                         self.logger,
#                         "warning",
#                         self,
#                         f"Invalid filtering result: {filtering_result}. Defaulting to False."
#                     )
#                     return None

#                 if filtering_result != 'true':
#                     return None

#             except Exception as e:
#                 log_message(
#                     self.logger, "error", self, f"Error getting filtering result: {e}"
#                 )
#                 return None

#         else:
#             log_message(self.logger, "info", self, "No filtering rules found.")

#         # Determine time of day
#         time_of_day = time_of_day if time_of_day else self.character.current_time_of_day()
#         platform = message.platform
        
#         # Retrieve and prepare social memory
#         social_memory = self.memory.get_social_memory(message.author, platform)
#         social_memory_str = ""
#         if social_memory:
#             social_memory_str = f"""
#                 Your social memory about {message.author}:
#                 Last interaction: {social_memory.last_interaction}
#                 Number of interactions: {social_memory.interaction_count}
#                 Your opinion: {social_memory.opinion}
                
#                 Recent conversation history:
#                 {chr(10).join([f"{msg['role']}: {msg['content']}" for msg in social_memory.conversation_history[-5:]])}
#             """

#         # Construct comprehensive response generation prompt
#         full_prompt = f"""
#         Character Context: {self.character.prompts.get('you_are', '')}
#         Platform: {platform}
#         Communication Requirements: {self.character.prompts.get('communication_requirements', '')}

#         Conversation Context:
#         {conversation_str}

#         Current Message:
#         {message_to_respond_str}

#         Social Memory:
#         {social_memory_str}

#         Previous Messages:
#         {previous_messages or ''}

#         Core Objective: {self.character.core_objective}
#         Means of Achieving Objective: {self.character.means_for_achieving_core_objective}

#         Response Requirements:
#         - Create a unique, creative response
#         - Length: Under 30 words
#         - Natural conversation continuation
#         - Reflect character's distinctive personality
#         - Align with core objective
#         - Avoid repeating previous message patterns

#         Generate a response following these strict guidelines.
#         """

#         try:
#             # Generate response using OpenSourceLLMWrapper
#             generated_response_content = self.llm.generate(full_prompt, temperature=0.7)

#             if not generated_response_content:
#                 raise Exception("LLM generation failed")

#             # Create response schema
#             generated_response_schema = SiaMessageGeneratedSchema(
#                 content=generated_response_content,
#                 platform=message.platform,
#                 author=self.character.platform_settings.get(message.platform, {}).get(
#                     "username", self.character.name
#                 ),
#                 response_to=message.id,
#                 conversation_id=message.conversation_id,
#             )

#             # Update social memory
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
#             log_message(
#                 self.logger, "error", self, f"Error generating response: {e}"
#         )
#         return None

#     def run(self):
#         """Run all clients concurrently using threads"""
#         threads = []
        
#         # Add Telegram thread if enabled
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
            
#         # Add Twitter thread if enabled    
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
            
#         # Start all threads
#         for thread in threads:
#             thread.daemon = True
#             thread.start()
            
#         try:
#             # Keep main thread alive
#             while True:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print("Shutting down...")