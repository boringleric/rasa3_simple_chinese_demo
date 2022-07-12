from neo4j import GraphDatabase
import random

class NeoSearch:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # 风格查歌
    def get_music_from_style(self, style):
        with self.driver.session() as session:
            ret_style = session.write_transaction(self._get_music_from_style, style)
            if len(ret_style) == 0:
                return None
            
            songlist_name =  random.choice(list(ret_style))[0]._properties['name']

            ret_style = session.write_transaction(self._get_music_from_songlist, songlist_name)

            musiclist = []
            for g in ret_style:
                musiclist.append(g[0]._properties['name'])

            return musiclist

    @staticmethod
    def _get_music_from_style(tx, message):
        result = tx.run("MATCH (p:style)-[]-(s:songlist) WHERE p.name=$message RETURN s LIMIT 25", message=message)
        return result.values()

    @staticmethod
    def _get_music_from_songlist(tx, message):
        result = tx.run("MATCH (p:songlist)-[]-(s:song) WHERE p.name=$message RETURN s LIMIT 100", message=message)
        return result.values()
        
    # 歌手查歌
    def get_music_from_singer(self, singer):
        with self.driver.session() as session:
            ret_singer = session.write_transaction(self._get_music_from_singer, singer)
            musiclist = []
            for g in ret_singer:
                musiclist.append(g[0]._properties['name'])
            return musiclist

    @staticmethod
    def _get_music_from_singer(tx, message):
        result = tx.run("MATCH (p:singer)-[]-(s:song) WHERE p.name=$message RETURN s ORDER BY s.popularity DESC LIMIT 100", message=message)
        return result.values()
        
    # 歌名查歌
    def get_music_from_song(self, song):
        with self.driver.session() as session:
            ret_song = session.write_transaction(self._get_music_from_song, song)
            musiclist = []
            for g in ret_song:
                musiclist.append(g[0]._properties['name'])
            return musiclist

    @staticmethod
    def _get_music_from_song(tx, message):
        result = tx.run("MATCH (p:song) WHERE p.name=$message RETURN s LIMIT 10", message=message)
        return result.values()

    # 随机曲子
    def get_rand_music(self):
        with self.driver.session() as session:
            ret_song = session.write_transaction(self._get_rand_music)
            musiclist = []
            for g in ret_song:
                musiclist.append(g[0]._properties['name'])
            return musiclist

    @staticmethod
    def _get_rand_music(tx):
        result = tx.run("MATCH (p:song) RETURN p LIMIT 100")
        return result.values()
