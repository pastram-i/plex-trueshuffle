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
    if server != ':(':
        print(f'Searching for {search} on {server.friendlyName}...')
        return server.search(search)
    else:
        return []
def ShowsPerServer(server):
    if server != ':(':
        print(f'Getting shows from playlist(s) on {server.friendlyName}...')
    ### Need to add movies to this list, potentially other types of media.
        MyShows = [[ep.grandparentTitle if ep.type == 'episode' else ep.originalTitle for ep in pla] for pla in server.playlists()]
        return list({item for sublist in MyShows for item in sublist})
    else:
        return []
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
    for serv in conservs:
            if serv != ':(':
                i = CallDB('''SELECT COUNT(ID) FROM episodes''')[0][0]
                alleps = [item.episodes() for item in SearchServer(serv, show) if 'Show' in str(type(item))]
                if alleps:
                    alreadyin = CallDB('''SELECT Show, Episode, Server FROM episodes WHERE Show = ? AND Server = ?''',(show,serv.friendlyName))
                    for ep in alleps[0]:
                        if ep.type=='episode':
                            if [ep.grandparentTitle, ep.seasonEpisode, serv.friendlyName] not in alreadyin:
                                if ep.seasonEpisode[:3] == 's00' and ep.parentTitle.lower() == 'specials':
                                    seasonEpisode = 's99'+ep.seasonEpisode[3:]
                                else:
                                    seasonEpisode = ep.seasonEpisode
                                CallDB('''INSERT INTO episodes (ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length) VALUES (?,?,?,?,?,?,?,?,?)''',(i,ep.type,ep.grandparentTitle,ep.parentTitle,seasonEpisode,ep.title,serv.friendlyName,ep.viewCount,ep.duration))
                                i+=1
                            else:
                                CallDB('''UPDATE episodes SET ViewCount = ? WHERE Show = ? AND Server = ? AND Episode = ?''',(ep.viewCount, show,serv.friendlyName,ep.seasonEpisode))
                        elif ep.type=='track':
                            if [ep.originalTitle, ep.index, serv.friendlyName] not in alreadyin:
                                CallDB('''INSERT INTO episodes (ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length) VALUES (?,?,?,?,?,?,?,?,?)''',(i,ep.type,ep.originalTitle,ep.parentTitle,ep.index,ep.title,serv.friendlyName,ep.viewCount,ep.duration))
                                i+=1
                            else:
                                CallDB('''UPDATE episodes SET ViewCount = ? WHERE Show = ? AND Server = ? AND Episode = ?''',(ep.viewCount, show,serv.friendlyName,ep.index))
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
print('Connected to your servers real quick...')
conservs = [ServerConnect(server) for server in config.servers]

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
        for serv in conservs:
            if serv != ':(':
                ShowsIFollow(ShowsPerServer(serv))
            showDB.commit()
        endtime = datetime.now()
        print(f'DB created! Time elapsed: {((endtime-startime).seconds)/60} minutes')
    elif command.lower() == 'update':
        ProvideMilk()
        startime = datetime.now()
        showlist = CallDB('''SELECT Show FROM shows''')
        for show in showlist:
            ViewCountUpdate(show[0])
            showDB.commit()
        endtime = datetime.now()
        print(f'DB updated! Time elapsed: {((endtime-startime).seconds)/60} minutes')
    elif command == '':
        plextv_clients = [x for x in myAccount.resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
        upnext = RandomShow()
        for serv in conservs:
            if serv != ':(':
                try:
                    epS = [ep for ep in [item.episodes() for item in SearchServer(serv, upnext[0]) if 'Show' in str(type(item))][0] if upnext[1] in ep.seasonEpisode]
                    PlayInfo(epS[0])
                    client = plextv_clients[0].connect()
                    client.playMedia(epS[0])
                    break
                except:
                    continue
    elif command.lower() in ['exit', 'quit']:
        break
    else:
        input('Invalid command. Press enter to continue.')
        continue