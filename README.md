# rasa3_simple_chinese_demo

这个项目是之前学习研究rasa代码的副产品，混乱不堪，大概率不会更新了罢！

配合的简单博客是这里：https://tedious.life/posts/36364.html

由于rasa功能更新频繁，仅保证此次使用环境下没有大问题。此次使用环境为：Rasa 3.2.1， Python 3.9，Neo4j 4.4.8， 不使用GPU

功能有一些简单的聊天，然后两个简单功能，一个是neo4j的查歌曲，歌曲是从https://github.com/jiejie1993/music_recommendation_2018/blob/master/数据集 获取的网易云数据集，项目内就截取了前200条，定义了4类节点，5类关系，大约2w左右的歌曲，5w的边，数据和插入方式都在/data/insert_into_neo4j.py中；另一个功能就是抄的https://github.com/Ailln/rasa-guotie 的查天气，用的和风天气api，对上述两作者贡献表示感谢！

test就是创建的rasa聊天文件夹，在源码中使用run_action可以启动action server, 使用run_train_and_test，更改trainflag，可以训练rasa模型，加载rasa模型。

对了， neo4j插入大批量数据节点速度倒还可以，但是创建边真的太慢太慢太慢了，推荐试一试Nebula Graph，虽然也没快了多少，可能我玩的还不够深，还需要继续研究。

最后，记住match (n) detach delete n，对neo4j真有效。