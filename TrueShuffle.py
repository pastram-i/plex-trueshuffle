from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video, plexapi.audio
import config, random, sqlite3
from pprint import pprint
from datetime import datetime

pprint([ep.grandparentTitle for ep in [list(set([p.items() for p in connected.playlists()][0]))]])

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
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    MyShows = [[ep.grandparentTitle if ep.type == 'episode' else ep.originalTitle for ep in pla] for pla in connected.playlists()]
    updated = [item for sublist in MyShows for item in sublist]
    return MyShows
def ShowsIFollow(servershows):
    for show in servershows:
        if show not in AllMyShows:
            AllMyShows.append(show)
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
    for server in config.servers:
        connected = ServerConnect(server)
        alleps = [item.episodes() for item in SearchServer(connected, show) if 'Show' in str(type(item))]
        for ep in alleps[0] or []:
            CallDB('''UPDATE shows SET ViewCount = ? WHERE Show = ? AND Episode = ? AND Server = ?''',(ep.viewCount,show,ep.seasonEpisode,server))
            showDB.commit()
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
def AddToDB(show,i, serv):
    try:
        CallDB('''
        INSERT INTO shows (ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length)
        VALUES (?,?,?,?,?,?,?,?,?);
        ''',(i, str(type(show)),show.grandparentTitle, show.parentTitle, show.seasonEpisode, show.title, serv.friendlyName, show.viewCount, show.duration))
    except:
        CallDB('''
        INSERT INTO shows (ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length)
        VALUES (?,?,?,?,?,?,?,?,?);
        ''',(i, str(type(show)),show.originalTitle, show.parentTitle, show.index, show.title, serv.friendlyName, show.viewCount, show.duration))
    showDB.commit()
def RandomShow():
    randShow = c.execute('''
    SELECT Show from shows
    GROUP BY Show
    ORDER BY RANDOM()
    LIMIT 1;
    ''').fetchone()[0]
    print(f'Queueing up: {randShow}, updating view counts real quick though...')
    ViewCountUpdate(randShow)
    showEps = c.execute('''
    SELECT Show, Episode, SUM(ViewCount), Season, Title, Length
    FROM shows
    WHERE Show LIKE ?
    GROUP BY Episode
    ORDER BY Episode, ViewCount;
    ''',('%'+randShow+'%',))
    v=0
    for episode in showEps:
        if episode[2] < v or episode[2] == 0:
            print(f'Queueing up: {episode[1]}')
            return episode
        else:
            v+=1
            continue
def updatedatabase():
    startime = datetime.now()
    dbcount = CallDB('''SELECT COUNT(*) FROM shows''')[0][0]
    ProvideMilk()
    for server in config.servers:
        connected = ServerConnect(server)
        sps = ShowsPerServer(connected)
        ShowsIFollow(sps)
    for show in AllMyShows:
        for server in config.servers:
            connected = ServerConnect(server)
            SearchShow = SearchServer(connected, show)
            for ss in SearchShow:
                if 'Show' in str(type(ss)):
                    alleps = ss.episodes()
                    WhatsInDB = CallDB('''SELECT DISTINCT Show, Episode, Server FROM shows WHERE Show = ? AND Server = ?''',(show,server))
                    for ep in alleps:
                        if (ep.grandparentTitle, ep.seasonEpisode,server) in WhatsInDB:
                            break
                        elif (ep.grandparentTitle, ep.index,server) in WhatsInDB:
                            break
                        else:
                            dbcount+=1
                            AddToDB(ep,dbcount, connected)
                alleps = []
    showDB.commit()
    endtime = datetime.now()
    print(f'DB updated! Time elapsed: {((endtime-startime).seconds)/60} minutes')

print('Welcome to the Plex Queue Shuffle!')

while True:
    Welcome()
    command = input('> ')
    if command.lower() == 'help':
        CommandsInfo()
    elif command.lower() == 'create':
        CallDB(''' DROP TABLE IF EXISTS shows''')
        CallDB('''CREATE TABLE shows
        (ID int, Type TEXT, Show TEXT, Season TEXT, Episode TEXT, Title TEXT, Server TEXT, ViewCount INT, Length INT)''')
        showDB.commit()
        CallDB('''CREATE TABLE shows
        (ID int, Type TEXT, Show TEXT)''')
        for server in config.servers:
            connected = ServerConnect(server)
            ShowsPerServer(connected)
        print('DB created!')
    elif command.lower() == 'update':
        updatedatabase()
    elif command == '':
        plextv_clients = [x for x in MyPlexAccount(config.username,config.password).resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
        upnext = RandomShow()
        for server in config.servers:
            connected = ServerConnect(server)
            epS = [item.episodes() for item in SearchServer(connected, upnext[0]) if 'Show' in str(type(item))]
            for ep in epS[0] or []:
                try:
                    if ep.seasonEpisode == upnext[1]:
                            PlayInfo(ep)
                            client = plextv_clients[0].connect()
                            client.playMedia(ep)
                except:
                    if ep.index == upnext[1]:
                            PlayInfo(ep)
                            client = plextv_clients[0].connect()
                            client.playMedia(ep)
    elif command.lower() in ['exit', 'quit']:
        break
    else:
        input('Invalid command. Press enter to continue.')
        continue