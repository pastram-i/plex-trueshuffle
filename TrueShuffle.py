from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video, plexapi.audio
import config, random, time, sqlite3

showDB = sqlite3.connect('myShows.db')
c = showDB.cursor()
myAccount = MyPlexAccount(config.username,config.password)
AllMyShows = []

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
    MyShows = []
    for playlist in server.playlists():
        pshows = []
        for ep in playlist.items():
            try:
                epT = ep.grandparentTitle
            except:
                epT = ep.originalTitle
            if epT not in pshows:
                pshows.append(epT)
    for show in pshows:
        if show not in MyShows:
            MyShows.append(show)
    return MyShows
def ShowsIFollow(servershows):
    for show in servershows:
        if show not in AllMyShows:
            AllMyShows.append(show)
def Welcome():
    print('Welcome to the Plex Queue Shuffle!')
    print('Type "help" for a list of commands.')
def PlayInfo():
    pass
def viewCountUpdate():
    pass
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
def AddToDB(show):
    try:
        CallDB('''
        INSERT INTO shows (Type, Show, Season, Episode, Title, Server, ViewCount, Length)
        VALUES (?,?,?,?,?,?,?,?);
        ''',(str(type(show)),show.grandparentTitle, show.parentTitle, show.seasonEpisode, show.title, show[2].friendlyName, show.viewCount, show.duration))
    except:
        CallDB('''
        INSERT INTO shows (Type, Show, Season, Episode, Title, Server, ViewCount, Length)
        VALUES (?,?,?,?,?,?,?,?);
        ''',(str(type(show)),show.originalTitle, show.parentTitle, show.index, show.title, show[2].friendlyName, show.viewCount, show.duration))
    showDB.commit()
def RandomShow():
    randShow = c.execute('''
    SELECT Show from shows
    GROUP BY Show
    ORDER BY RANDOM()
    LIMIT 1;
    ''').fetchone()[0]
    showEps = c.execute('''
    SELECT Show, Episode, SUM(ViewCount), Season, Title, Length
    FROM shows
    WHERE Show LIKE ?
    GROUP BY Episode
    ORDER BY Episode, ViewCount;
    ''',('%'+randShow+'%',))
    v=0
    for episode in showEps:
        print(f'Queueing up: {episode[0]}, updating view counts real quick though...')
        viewCountUpdate(episode)
        if episode[2] < i or episode[2] == 0:
            print(f'Queueing up: {episode[1]}')
            return episode
        else:
            v+=1
            continue

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
    elif command.lower() == 'update':
        ProvideMilk()
        for server in config.servers:
            connected = ServerConnect(server)
            sps = ShowsPerServer(connected)
            ShowsIFollow(sps)
        for show in AllMyShows:
            for server in config.servers:
                connected = ServerConnect(server)
                alleps = []
                #IM SOMEWHERE HERE ~~~~~~~~~~~~~~~~~~~~~~~~~~
                SearchShow = SearchServer(connected, show)
                for ss in SearchShow:
                    if 'Show' in str(type(ss)):
                        alleps = ss.episodes()
                WhatsInDB = CallDB('''SELECT DISTINCT Show, Episode, Server FROM shows WHERE Show = ? AND Server = ?''',(show,server))
                for ep in alleps:
                    for dbline in WhatsInDB:
                        try:
                            if dbline != [
                                ep.grandparentTitle,
                                ep.seasonEpisode,
                                connected.friendlyName,
                            ]:
                                AddToDB(ep)
                        except:
                            if dbline != [
                                ep.originalTitle,
                                ep.seasonEpisode,
                                connected.friendlyName,
                            ]:
                                AddToDB(ep)
    elif command == '':
        plextv_clients = [x for x in MyPlexAccount(config.username,config.password).resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
        upnext = RandomShow()
        connected = ServerConnect(upnext[3])
        epObject = SearchServer(connected, (upnext[0], upnext[1]))
        #STILL HAVE TO FINISH THIS THOUGH ~~~~~~~~~~~~~~~~~~~~~~~~~~
        #UPDATE VIEW COUNTS MISSING FROM THIS VERSION TOO ~~~~~~~~~~
    elif command.lower() == 'exit':
        break
    else:
        input('Invalid command. Press enter to continue.')
        continue