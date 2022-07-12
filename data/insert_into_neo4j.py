import json
import time 

from py2neo import Graph, Node, Relationship, NodeMatcher

graph = Graph("bolt://neo4j:123456@127.0.0.1:7687")


with open("./data/songlist_dict_small.json", "r", encoding='utf-8') as f:
    songlist_dict = json.load(f)

with open("./data/song_singer_dict_small.json", "r", encoding='utf-8') as f:
    song_singer_dict = json.load(f)


def add_song_singer_node_relation():
    batch_song = []
    batch_singer = []
    relationlisttmp = []
    # 先插入歌曲-歌手节点，最后插入关系
    for songid in list(song_singer_dict.keys()):
        song = song_singer_dict[songid]['name'][0]
        singerlist = song_singer_dict[songid]['artists']  
        popularity = song_singer_dict[songid]['popularity'][0]
        for singer in singerlist:
            if {"name":song, "songid":songid, "popularity":popularity} not in batch_song:
                batch_song.append({"name":song, "songid":songid, "popularity":popularity})
            if {"name":singer} not in batch_singer:
                batch_singer.append({"name":singer})
            relationlisttmp.append({"songid":songid, "singer":singer})

    starttime = time.time()
    query = "UNWIND $batch as row CREATE (n:song) SET n += row"    
    graph.run(query, batch = batch_song)
    print(time.time()-starttime)

    starttime = time.time()
    query = "UNWIND $batch as row CREATE (n:singer) SET n += row"   
    graph.run(query, batch = batch_singer)
    print(time.time()-starttime)

    starttime = time.time()
    query = 'UNWIND $batch as row    \
             MATCH (p:song) \
             MATCH (q:singer)  \
             WHERE p.songid=row.songid and q.name=row.singer \
             CREATE (q)-[s:sing]->(p)'
    graph.run(query, batch = relationlisttmp)      
    print(time.time()-starttime) 

add_song_singer_node_relation()

def add_song_list_node_relation():
    # 遍历标准组
    songlist_name_list = []
    batch_style_tag_set = set()
    relationlisttmp = []
    tag_list_relation = []
    for songlistname in list(songlist_dict.keys()):
        style = songlist_dict[songlistname][0]['style'] 
        score =  songlist_dict[songlistname][0]['score'][0]
        songlist_name_list.append({"name":songlistname, "score":score})
        for s in style:
            batch_style_tag_set.add(s)
            tag_list_relation.append({"songlist":songlistname, "style":s})

        songlist = songlist_dict[songlistname][0]['songlist']  
        for s in songlist:
            relationlisttmp.append({"songlist":songlistname, "songid":str(s)})

    batch_song_tag_list = [{"name":tagname} for tagname in list(batch_style_tag_set)]

    starttime = time.time()
    query = "UNWIND $batch as row CREATE (n:style) SET n += row"    
    graph.run(query, batch = batch_song_tag_list)
    print(time.time()-starttime) 

    starttime = time.time()
    query = "UNWIND $batch as row CREATE (n:songlist) SET n += row"   
    graph.run(query, batch = songlist_name_list)
    print(time.time()-starttime) 

    starttime = time.time()
    query = 'UNWIND $batch as row    \
             MATCH (p:songlist) \
             MATCH (q:style)  \
             WHERE p.name=row.songlist and q.name=row.style \
             CREATE (p)-[s:havestyle]->(q), (q)-[t:havesongsheet]->(p)'
    graph.run(query, batch = tag_list_relation)       
    print(time.time()-starttime) 

    starttime = time.time()
    query = 'UNWIND $batch as row    \
             MATCH (p:songlist)\
             MATCH (q:song)  \
             WHERE p.name=row.songlist and q.songid=row.songid \
             CREATE (p)-[r:havesong]->(q), (q)-[l:insonglist]->(p)'
    graph.run(query, batch = relationlisttmp)    
    print(time.time()-starttime)    

add_song_list_node_relation()

print("add fin!")