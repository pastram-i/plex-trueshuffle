#Required packages
from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video, plexapi.audio
import config, random, time, sqlite3
from pprint import pprint

showDB = sqlite3.connect('myShows')
cursor = showDB.cursor()

def serverConnects():
    print('Connecting to servers...')
    provideMilk()
    myAccount = MyPlexAccount(config.username,config.password)
    myServers = []

    for server in config.servers:
        try:
            myServers.append(myAccount.resource(server).connect())
        except:
            print(f"Could not connect to server: {server} :(")
            myServers.append(':(')
            continue
    return myServers
def populateShows(myServers):
    print('Populating shows...')
    provideMilk()
    for server in myServers:
        if server != ':(':
            for playlist in server.playlists():
                for episode in playlist.items():
                    try:
                        cursor.execute('''
                        INSERT INTO shows (Type, Show, Season, Episode, Title, Server, ViewCount)
                        VALUES (?,?,?,?,?,?,?);
                        ''',(str(type(episode)),episode.grandparentTitle, episode.parentTitle, episode.seasonEpisode, episode.title, server.friendlyName, episode.viewCount))
                    except:
                        cursor.execute('''
                        INSERT INTO shows (Type, Show, Season, Episode, Title, Server, ViewCount)
                        VALUES (?,?,?,?,?,?,?);
                        ''',(str(type(episode)),episode.grandparentTitle, episode.parentTitle, episode.index, episode.title, server.friendlyName, episode.viewCount))
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

while True:
    userStart = input('''
    ****************************
    Type "create" to build DB.
     - Note - if one exists it will overwrite it, use to reset as needed.
    Type "update" to refresh DB.
     - Note - will try to find new or missing episodes from your sources.
    Press enter to play media.
     - Note - requires DB to exist.
    Type "quit" to exit.
    ****************************\n''')

    if userStart == 'create':
        cursor.execute(''' DROP TABLE IF EXISTS shows''')
        cursor.execute('''CREATE TABLE shows
        (ID INT PRIMARY KEY, Type TEXT, Show TEXT, Season TEXT, Episode TEXT, Title TEXT, Server TEXT, ViewCount INT)''')
        showDB.commit()
        populateShows(serverConnects())
    elif userStart == 'update':
        pass
    elif userStart == 'quit':
        break
    elif userStart == '':
        plextv_clients = [x for x in MyPlexAccount(config.username,config.password).resources() if "player" in x.provides and x.presence and x.publicAddressMatches]

        toPlay = random.choice(list(myShows))
        i=0

        for episode in myShows[toPlay]:
            if episode.viewCount < i or episode.viewCount == 0:
                nextUp = episode
                i=0
                break
            else:
                i+=1
                continue

        if type(nextUp) == plexapi.video.Episode:
            playEpisode = playVideo(nextUp)
        elif type(nextUp) == plexapi.audio.Track:
            playEpisode = playAudio(nextUp)
        else:
            print('Weird, I don\'t recognize this type of media, sorry :(\nFeel free to submit a bug on github for me to fix!')
            continue
        try:
            client = plextv_clients[0].connect()
            client.playMedia(playEpisode)
        except:
            print('Could not connect to that server :(')
            continue
    else:
        input('Invalid command. Press enter to continue.')
        continue