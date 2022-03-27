#Required packages
from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video, plexapi.audio
import config, random, time, sqlite3

showDB = sqlite3.connect('myShows')
c = showDB.cursor()
myAccount = MyPlexAccount(config.username,config.password)

def serverConnect(server):
    print(f'Connecting to {server}...')
    try:
        serv = myAccount.resource(server).connect()
    except:
        print(f"Could not connect to server: {server} :(")
        serv = ':('
    return serv
def populateShows(server):
    print('Populating shows db...')
    if server != ':(':
        i=0
        for playlist in server.playlists():
            for episode in playlist.items():
                try:
                    c.execute('''
                    INSERT INTO shows (ID, Type, Show, Season, Episode, Title, Server, ViewCount)
                    VALUES (?,?,?,?,?,?,?,?);
                    ''',(i, str(type(episode)),episode.grandparentTitle, episode.parentTitle, episode.seasonEpisode, episode.title, server.friendlyName, episode.viewCount))
                except:
                    c.execute('''
                    INSERT INTO shows (ID, Type, Show, Season, Episode, Title, Server, ViewCount)
                    VALUES (?,?,?,?,?,?,?,?);
                    ''',(i, str(type(episode)),episode.grandparentTitle, episode.parentTitle, episode.index, episode.title, server.friendlyName, episode.viewCount))
                i+=1
        showDB.commit()
def scanForUpdates(myServers):
    pass
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
    '''.format(playTrack.grandparentTitle,playTrack.parentTitle,playTrack.title,millisecondToHumanstr(playTrack.duration))
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
    SELECT Show, Episode, SUM(ViewCount)
    FROM shows
    WHERE Show LIKE ?
    GROUP BY Episode
    ORDER BY Episode, ViewCount;
    ''',('%'+randShow+'%',))
    i=0
    for episode in showEps:
        if episode[2] < i or episode[2] == 0:
            return episode[0], episode[1]
        else:
            i+=1
            continue
def upnext(db):
    pass


    

while True:
    userStart = input('''
    ****************************
    Type "create" to build DB.
     - Note: if one exists it will overwrite it; use to reset as needed.
    Type "update" to refresh DB.
     - Note: will try to find new or missing episodes from your sources.
    Press enter to play media.
     - Note: requires DB to exist.
    Type "quit" to exit.
    ****************************\n''')

    if userStart == 'create':
        c.execute(''' DROP TABLE IF EXISTS shows''')
        c.execute('''CREATE TABLE shows
        (ID int, Type TEXT, Show TEXT, Season TEXT, Episode TEXT, Title TEXT, Server TEXT, ViewCount INT)''')
        showDB.commit()
        provideMilk()
        for server in config.servers:
            populateShows(serverConnect(server))
        print('All done!')
    elif userStart == 'update':
        pass
    elif userStart == 'quit':
        break
    elif userStart == '':
        plextv_clients = [x for x in MyPlexAccount(config.username,config.password).resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
        playEpisode = upnext(pullDB())
        try:
            client = plextv_clients[0].connect()
            client.playMedia(playEpisode)
        except:
            print('Could not connect to that server :(')
            continue
    else:
        input('Invalid command. Press enter to continue.')
        continue