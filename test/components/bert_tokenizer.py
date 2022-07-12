import glob
import os
import shutil
from typing import List, Optional, Text, Dict, Any

from transformers import AutoTokenizer
from rasa.shared.nlu.training_data.message import Message
from rasa.nlu.tokenizers.tokenizer import Tokenizer, Token
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER, is_trainable=False
)
class BertTokenizer(Tokenizer):
   
    @staticmethod
    def supported_languages() -> Optional[List[Text]]:
        """Supported languages (see parent class for full docstring)."""
        return ["zh", "en"]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns default config (see parent class for full docstring)."""
        return {
            # Flag to check whether to split intents
            "intent_tokenization_flag": False,            
            # Symbol on which intent should be split
            "intent_split_symbol": "_",    
            # Regular expression to detect tokens
            "token_pattern": None,        
        }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        super(BertTokenizer, self).__init__(component_config)

        self.component_config={
            # name of the language model to load.
            "model_name": component_config['model_name'],
            # Pre-Trained weights to be loaded(string)
            "model_weights": component_config['model_weights'],
            # an optional path to a specific directory to download and cache the pre-trained model weights.
            "cache_dir": component_config.get("cache_dir"),
        }
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.component_config["model_weights"], 
            cache_dir=self.component_config.get("cache_dir"), 
            use_fast=True
        )

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        encoded_input = self.tokenizer(text, return_offsets_mapping=True, add_special_tokens=False)
        token_position_pair = zip(encoded_input.tokens(), encoded_input["offset_mapping"])

        return [Token(text=token_text, start=position[0], end=position[1])
                for token_text, position in token_position_pair]