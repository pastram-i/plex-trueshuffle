#Required packages
from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video, plexapi.audio
import config, random, time, sqlite3
from pprint import pprint
import pandas as pd

showDB = sqlite3.connect('myShows.db')
c = showDB.cursor()
myAccount = MyPlexAccount(config.username,config.password)

def serverConnect(server):
    print(f'Connecting to {server}...')
    try:
        serv = myAccount.resource(server).connect()
        print('Done!')
    except:
        print(f"Could not connect to server: {server} :(")
        serv = ':('
    return serv
def populateShows(server):
    print('Populating shows db...')
    if server != ':(':
        myShows = []
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
            if show not in myShows:
                myShows.append(show)
        return (myShows, server)
def scanForUpdates(shows,i):
    #if type(shows[1]) == str:
    #    server = shows[1]
    #    shows[1] = serverConnect(server)
    for show in shows[0]:
        print(f'Scanning for updates for {show}...')
        #source = serverConnect(shows[1])
        search = shows[1].search(show)
        for sh in search:
            if 'Show' in str(type(sh)):
                eps = sh.episodes()
        epSources = c.execute('''
        SELECT Show, Episode, Server
        FROM shows
        WHERE Show LIKE ? AND Server LIKE ?;
        ''',('%'+show+'%','%'+shows[1].friendlyName+'%')).fetchall()
        for ep in eps:
            if ((ep.grandparentTitle and shows[1].friendlyName and ep.seasonEpisode)not in epSources) or ((ep.grandparentTitle and shows[1].friendlyName and ep.originalTitle)not in epSources) or (not epSources):
                try:
                    c.execute('''
                    INSERT INTO shows (ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length)
                    VALUES (?,?,?,?,?,?,?,?,?);
                    ''',(i, str(type(ep)),ep.grandparentTitle, ep.parentTitle, ep.seasonEpisode, ep.title, shows[1].friendlyName, ep.viewCount, ep.duration))
                except:
                    c.execute('''
                    INSERT INTO shows (ID, Type, Show, Season, Episode, Title, Server, ViewCount, Length)
                    VALUES (?,?,?,?,?,?,?,?,?);
                    ''',(i, str(type(ep)),ep.originalTitle, ep.parentTitle, ep.index, ep.title, shows[1].friendlyName, ep.viewCount, ep.duration))
                showDB.commit()
        i+=1
    print('Done!')
def provideMilk():
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
def playVideo(playEpisode):
    print(
    '''
----------------------------
Now playing:            {} {}
Season:                 {}
Episode:                {}
Length (HH:MM:SS:MMMM): {}
----------------------------
    '''.format(playEpisode.grandparentTitle,playEpisode.seasonEpisode, playEpisode.parentTitle,playEpisode.title,millisecondToHumanstr(playEpisode.duration))
    )

    if playEpisode.audioStreams:
        i=0
        for audio in playEpisode.audioStreams():
            if config.audioLang in audio.language:
                playEpisode.audioStreams()[i].select()
                break
            else:
                i+=1
                continue
    if playEpisode.subtitleStreams:
        i=0
        for sub in playEpisode.subtitleStreams():
            if config.subLang in sub.language:
                playEpisode.subtitleStreams()[i].select()
                break
            else:
                i+=1
                continue

    return playEpisode
def playAudio(playTrack):
    print(
    '''
----------------------------
Now playing:            {}
Album/Book:             {}
Track/Chapter:          {}
Length (HH:MM:SS:MMMM): {}
----------------------------
    '''.format(playTrack.originalTitle,playTrack.parentTitle,playTrack.title,millisecondToHumanstr(playTrack.duration))
    )
    return playTrack
def pullDB():
    print('Connecting to DB...')

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
    i=0
    for episode in showEps:
        print(f'Queueing up: {episode[0]}, updating view counts real quick though...')
        viewCountUpdate([episode[0], episode[1], episode[3], episode[4], episode[5]])
        if episode[2] < i or episode[2] == 0:
            print(f'Queueing up: {episode[1]}')
            return [episode[0], episode[1], episode[3], episode[4], episode[5]]
        else:
            i+=1
            continue
def upnext(episode):
    epSources = c.execute('''
    SELECT Show, Episode, Server, Title
    FROM shows
    WHERE Show LIKE ? AND Episode LIKE ?;
    ''',('%'+episode[0]+'%','%'+episode[1]+'%'))
    for source in epSources:
        try:
            trySource = serverConnect(source[2])
            episode = trySource.search(source[3])[0]
            return [episode[0], episode[1], episode[3], episode[4], episode[5]]
        except:
            print(f'Could not connect to {source[2]} server, trying next...')
            continue

    print('I wasn\'t able to connect to any servers for this episode...')
def viewCountUpdate(episode):
    epSources = c.execute('''
    SELECT Show, Episode, Server, Title
    FROM shows
    WHERE Show LIKE ? AND Episode LIKE ?;
    ''',('%'+episode[0]+'%','%'+episode[1]+'%'))
    for source in epSources:
        try:
            c.execute('''
            UPDATE shows
            SET ViewCount = ?
            WHERE Show = ? AND Episode = ? AND Title = ? AND Server = ?;
            ''', (myAccount.resource(source[0][2]).connect().search(source[0][3])[0].viewCount, episode[0], episode[1], episode[3], episode[2]))
            showDB.commit()
        except:
            pass

while True:
    userStart = input('''
    ****************************
Type "create" to build DB
    - Note: if one exists it will overwrite it; use to reset as needed.
Type "update" to refresh DB
    - Note: will try to find new or missing episodes, for shows in your DB, from your sources.
Press enter to play media
    - Note: requires DB to exist, will randomly choose a show and play the next episode.
Type "quit" to exit.
    ****************************\n''')

    if userStart == 'create':
        c.execute(''' DROP TABLE IF EXISTS shows''')
        c.execute('''CREATE TABLE shows
        (ID int, Type TEXT, Show TEXT, Season TEXT, Episode TEXT, Title TEXT, Server TEXT, ViewCount INT, Length INT)''')
        showDB.commit()
        provideMilk()
        i=1
        for server in config.servers:
            connected = serverConnect(server)
            readyshows = populateShows(connected)
            scanForUpdates(readyshows,i)
        print('All done!')
    elif userStart == 'update':
        MyShows = c.execute('''
        SELECT Show, Server
        FROM shows
        GROUP BY Server;
        ''').fetchall()
        pprint(MyShows)
        scanForUpdates(MyShows, i=0)
    elif userStart == 'quit':
        break
    elif userStart == '':
        plextv_clients = [x for x in MyPlexAccount(config.username,config.password).resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
        dbready = pullDB()
        nextUp = upnext(dbready)
        if type(nextUp) == plexapi.video.Episode:
            playEpisode = playVideo(nextUp)
        elif type(nextUp) == plexapi.audio.Track:
            playEpisode = playAudio(nextUp)
        else:
            print('Weird, I don\'t recognize this type of media, sorry :(\nFeel free to submit a bug on github for me to fix!')
            continue
        client = plextv_clients[0].connect()
        client.playMedia(playEpisode)
    else:
        input('Invalid command. Press enter to continue.')
        continue