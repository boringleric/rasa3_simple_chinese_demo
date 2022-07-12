# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import logging
import random
import string
from typing import Text
from typing import Dict
from typing import List
from typing import Any

from rasa_sdk import Action
from rasa_sdk import Tracker
from rasa_sdk import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType, AllSlotsReset

from utils.weather_query import get_weather
from utils.neo4j_search import NeoSearch

logger = logging.getLogger(__name__)

class ActionResetAllSlots(Action):
    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):        
        return [AllSlotsReset()]

class ActionWeatherForm(Action):
    def name(self) -> Text:
        return "action_weather_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        slots = tracker.current_slot_values()
        city = slots["city"]
        date = slots["date"]
        ret_weather = get_weather(city, date)
        dispatcher.utter_message(text=ret_weather)
        return []


class ValidateWeatherForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_weather_form"

    @staticmethod
    def get_date_list() -> List[Text]:
        return ["今天", "明天", "后天"]

    def validate_date(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> Dict[Text, Any]:
        if type(slot_value) == list:
            slot_value = slot_value[0]

        if slot_value in self.get_date_list():
            return {"date": slot_value}
        else:
            return {"date": None}


    def validate_city(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> Dict[Text, Any]:
        if type(slot_value) == list:
            slot_value = slot_value[0]

        return {"city": slot_value}


class ActionAskWeatherFormCity(Action):
    def name(self) -> Text:
        return "action_ask_weather_form_city"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        dispatcher.utter_message(text="你想查哪个城市的天气啊？")
        return []


class ActionAskWeatherFormDate(Action):
    def name(self) -> Text:
        return "action_ask_weather_form_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        dispatcher.utter_message(text="你想查哪天的天气啊，只能查三天的，今天、明天、后天。")
        return []


class ActionSongFromForm(Action):
    def __init__(self) -> None:
        super().__init__()
        self.graph = NeoSearch("bolt://localhost:7687", "neo4j", "123456")

    def name(self) -> Text:
        return "action_song_from_form"

    def get_reply(self, dispatcher, style, song=None):
        if not song:
            textlist = [
                '没有啊，是不是记错了？',
                '这个没有啊，要不你再想想。',
                '没有没有没有，别问了！'
            ]
            dispatcher.utter_message(text=random.choice(textlist))
        else:
            textlist = [
                string.Template('找到了找到了，给你找到了$style的$song歌曲。'),
                string.Template('$style的$song，想不到你好这口。'),
                string.Template('来来来看看$style的$song！'),
                string.Template('这个$style的$song没错吧！'),
            ]
            t = random.choice(textlist)
            dispatcher.utter_message(text=t.safe_substitute({'style':style, 'song':song}))

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        slots = tracker.current_slot_values()
        style = slots["style"]
        singer = slots["singer"]
        
        if singer:
            retlist = self.graph.get_music_from_singer(singer)
        elif style:
            retlist = self.graph.get_music_from_style(style)
        
        self.graph.close()

        if not retlist or len(retlist) == 0:
            self.get_reply(dispatcher, style)
        else:
            # 随机选一个歌曲返回
            choose_s1 = random.choice(list(retlist))
            if singer:
                self.get_reply(dispatcher, singer, choose_s1)
            elif style:
                self.get_reply(dispatcher, style, choose_s1)

        return []


class ActionSongQuerywithSong(Action):
    def __init__(self) -> None:
        super().__init__()
        self.graph = NeoSearch("bolt://localhost:7687", "neo4j", "123456")

    def name(self) -> Text:
        return "action_song_query_with_song"

    def get_reply(self, dispatcher, song=None):
        if not song:
            textlist = [
                '没有啊，是不是记错了？',
                '这个没有啊，要不你再想想。',
                '没有没有没有，别问了！'
            ]
            dispatcher.utter_message(text=random.choice(textlist))
        else:
            textlist = [
                string.Template('爷这里有$song这个曲子。'),
                string.Template('$song，想不到你好这口。'),
            ]
            t = random.choice(textlist)
            dispatcher.utter_message(text=t.safe_substitute({'song':song}))

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        slots = tracker.current_slot_values()
        song = slots["song"]
        retlist = self.graph.get_music_from_song(song)
        self.graph.close()

        if len(retlist) == 0:
            self.get_reply(dispatcher)
        else:
            self.get_reply(dispatcher, song)

        return []

class ActionGetRandomSong(Action):
    def __init__(self) -> None:
        super().__init__()
        self.graph = NeoSearch("bolt://localhost:7687", "neo4j", "123456")

    def name(self) -> Text:
        return "action_get_random_song"

    def get_reply(self, dispatcher, song=None):
        textlist = [
            string.Template('古风现代周杰伦费玉清要啥有啥，爷这里有$song这个曲子，给你先听着。'),
            string.Template('各种风格歌曲随便问随便说随便说随便问！$song这个曲子先听着，听着好再来。'),            
            string.Template('咱这有各种风格和歌手的曲子，比如，$song，看看好不好这口。'),
            string.Template('来来来听听看$song，咱这里708090的曲子都有，古今中外随便问随便找随便找随便问。'),
        ]
        t = random.choice(textlist)
        dispatcher.utter_message(text=t.safe_substitute({'song':song}))

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:

        retlist = self.graph.get_rand_music()
        self.graph.close()

        self.get_reply(dispatcher, retlist)

        return []
