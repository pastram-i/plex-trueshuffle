from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video, plexapi.audio
import config, sqlite3
from datetime import datetime
from pprint import pprint

showDB = sqlite3.connect('myShows.db')
c = showDB.cursor()
myAccount = MyPlexAccount(config.username,config.password)

def CallDB (query, args=()):
    return c.execute(query, args).fetchall()
def ServerConnect(server):
    print(f'Connecting to {server}...')
    try:
        serv = myAccount.resource(server).connect()
    except:
        print(f"Could not connect to server: {server} :(")
        serv = ':('
    return serv
def SearchServer(server, search):
    print(f'Searching for {search} on {server.friendlyName}...')
    return server.search(search)
def ShowsPerServer(server):
    print(f'Getting shows from playlist(s) on {server.friendlyName}...')
    ### Need to add movies to this list, potentially other types of media.
    MyShows = [[ep.grandparentTitle if ep.type == 'episode' else ep.originalTitle for ep in pla] for pla in connected.playlists()]
    return list({item for sublist in MyShows for item in sublist})
def ShowsIFollow(servershows):
    for show in servershows:
        CallDB('''INSERT INTO shows (Show) SELECT ? WHERE NOT EXISTS(SELECT 1 FROM shows WHERE Show = ?)''',(show,show))
def Welcome():
    print('Type "help" for a list of commands.')
def PlayInfo(play):
    try:
        print(
    '''
----------------------------
Now playing:            {} {}
Season:                 {}
Episode:                {}
Length (HH:MM:SS:MMMM): {}
----------------------------
    '''.format(play.grandparentTitle,play.seasonEpisode, play.parentTitle,play.title,millisecondToHumanstr(play.duration))
    )
        if play.audioStreams:
            p=0
            for audio in play.audioStreams():
                if config.audioLang in audio.language:
                    play.audioStreams()[p].select()
                    break
                else:
                    p+=1
                    continue
        if play.subtitleStreams:
            p=0
            for sub in play.subtitleStreams():
                if config.subLang in sub.language:
                    play.subtitleStreams()[p].select()
                    break
                else:
                    p+=1
                    continue
    except:
        print(
    '''
----------------------------
Now playing:            {}
Album/Book:             {}
Track/Chapter:          {}
Length (HH:MM:SS:MMMM): {}
----------------------------
    '''.format(play.originalTitle,play.parentTitle,play.title,millisecondToHumanstr(play.duration))
    )
def ViewCountUpdate(show):
    i = CallDB('''SELECT COUNT(ID) FROM episodes''')[0][0]
    for server in config.servers:
        connected = ServerConnect(server)
        if alleps := [
            item.episodes()
            for item in SearchServer(connected, show)
            if 'Show' in str(type(item))
        ][0]:
            for ep in alleps:
                if ep.type=='episode':
                    pprint((i,ep.type,ep.grandparentTitle,ep.parentTitle,ep.seasonEpisode,ep.title,server,ep.viewCount,ep.duration,ep.grandparentTitle,ep.seasonEpisode,server,))
                    CallDB('''INSERT INTO episodes(ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length) SELECT ?, ?, ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS(SELECT * FROM episodes WHERE Show = ? AND Episode = ? AND Server = ?)''',(i,ep.type,ep.grandparentTitle,ep.parentTitle,ep.seasonEpisode,ep.title,server,ep.viewCount,ep.duration,ep.grandparentTitle,ep.seasonEpisode,server,))
                    showDB.commit()
                    CallDB('''UPDATE episodes SET ViewCount = ? WHERE Show = ? AND Episode = ? AND Server = ?''',(ep.viewCount,ep.grandparentTitle,ep.index,server,))
                    showDB.commit()
                elif ep.type=='track':
                    CallDB('''INSERT INTO episodes(ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length) SELECT ?, ?, ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS(SELECT * FROM episodes WHERE Show = ? AND Episode = ? AND Server = ?)''',(i,ep.type,ep.originalTitle,ep.parentTitle,ep.index,ep.title,server,ep.viewCount,ep.duration,ep.originalTitle,ep.index,server,))
                    showDB.commit()
                    CallDB('''UPDATE episodes SET ViewCount = ? WHERE Show = ? AND Episode = ? AND Server = ?''',(ep.viewCount,ep.grandparentTitle,ep.index,server,))
                    showDB.commit()
            i+=1
def CommandsInfo():
    print('''
    ****************************
Type "help" for this list of commands
Type "create" to build DB
    - If one exists it will overwrite it; use to reset as needed.
    - Must run "update" after to populate.
Type "update" to refresh DB
    - Will try to find new or missing episodes, for shows in your DB, from your sources.
Press enter to play media
    - Requires DB to exist, will randomly choose a show and play the next episode.
Type "quit" to exit
    ****************************\n''')
def ProvideMilk():
    print('''
This make take a little while....

    Take a milk while you wait
            _____
           j_____j
          /_____/_\\
          |_(~)_| |
          | )"( | |
          |(@_@)| |  
          |_____|,'
''')
def RandomShow():
    randShow = c.execute('''SELECT Show from shows GROUP BY Show ORDER BY RANDOM() LIMIT 1;''').fetchone()[0]
    print(f'Queueing up: {randShow}, updating view counts real quick though...')
    ViewCountUpdate(randShow)
    showEps = c.execute('''SELECT Show, Episode, SUM(ViewCount), Season Title, Length FROM episodes WHERE Show LIKE ? GROUP BY Episode ORDER BY Episode, ViewCount;''',('%'+randShow+'%',))
    v=0
    for episode in showEps:
        if episode[2] < v or episode[2] == 0:
            print(f'Queueing up: {episode[1]}')
            return episode
        else:
            v+=1
            continue

print('Welcome to the Plex Queue Shuffle!')

while True:
    Welcome()
    command = input('> ')
    if command.lower() == 'help':
        CommandsInfo()
    elif command.lower() == 'create':
        startime = datetime.now()
        CallDB(''' DROP TABLE IF EXISTS shows''')
        CallDB(''' DROP TABLE IF EXISTS episodes''')
        CallDB('''CREATE TABLE episodes
        (ID int, Type TEXT, Show TEXT, Season TEXT, Episode TEXT, Title TEXT, Server TEXT, ViewCount INT, Length INT)''')
        CallDB('''CREATE TABLE shows
        (Type TEXT, Show TEXT)''')
        for server in config.servers:
            connected = ServerConnect(server)
            ShowsIFollow(ShowsPerServer(connected))
        showDB.commit()
        endtime = datetime.now()
        print(f'DB created! Time elapsed: {((endtime-startime).seconds)/60} minutes')
    elif command.lower() == 'update':
        ProvideMilk
        startime = datetime.now()
        showlist = CallDB('''SELECT Show FROM shows''')[0]
        for show in showlist:
            ViewCountUpdate(show)
        endtime = datetime.now()
        print(f'DB updated! Time elapsed: {((endtime-startime).seconds)/60} minutes')
    elif command == '':
        plextv_clients = [x for x in MyPlexAccount(config.username,config.password).resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
        upnext = RandomShow()
        ViewCountUpdate(upnext[0])
        for server in config.servers:
            connected = ServerConnect(server)
            if epS := [item.episodes() for item in SearchServer(connected, upnext[0]) if 'Show' in str(type(item))][0]:
                for ep in epS:
                    ### Need to add movies to this list, potentially other types of media.
                    if ep.seasonEpisode == upnext[1]:
                        PlayInfo(ep)
                        client = plextv_clients[0].connect()
                        client.playMedia(ep)
                    elif ep.index == upnext[1]:
                        PlayInfo(ep)
                        client = plextv_clients[0].connect()
                        client.playMedia(ep)
    elif command.lower() in ['exit', 'quit']:
        break
    else:
        input('Invalid command. Press enter to continue.')
        continue