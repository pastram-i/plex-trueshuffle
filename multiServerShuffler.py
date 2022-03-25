#Required packages
from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video, plexapi.audio
import config, random, time

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

print('''
Some really quick reminders:
 - Add new shows to your playlist(s)!
 - Add new episodes to your playlist(s)!
 - Depending on the amount of servers/shows/episodes - give me a minute or so to get started............

    Take a milk while you wait
            _____
           j_____j
          /_____/_\\
          |_(~)_| |
          | )"( | |
          |(@_@)| |  
          |_____|,'
''')

print('Logging in to Plex...')
myAccount = MyPlexAccount(config.username,config.password)
plextv_clients = [x for x in myAccount.resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
myServers = []
print('Adding servers...')
for server in config.servers:
    try:
        myServers.append(myAccount.resource(server).connect())
    except:
        print(f"Could not connect to server: {server} :(")
        myServers.append(':(')
        continue

myShows = {}
print('Adding shows...')
#Pulls shows from playlists on each server
for server in myServers:
    if server != ':(':
        for playlist in server.playlists():
            for episode in playlist.items():
                if episode.grandparentTitle not in myShows.keys():
                    myShows[episode.grandparentTitle] = [] #Will add all unique show names from all servers
                if type(episode) == plexapi.video.Episode:
                    if episode.seasonEpisode not in(x.seasonEpisode for x in myShows[episode.grandparentTitle]):
                        myShows[episode.grandparentTitle].append(episode)
                elif type(episode) == plexapi.audio.Track:
                    if episode.index not in(x.index for x in myShows[episode.grandparentTitle]):
                        myShows[episode.grandparentTitle].append(episode)

print('Organizing shows...')
#Organizing shows by 's##e##' value in the Episode object.
#Can use index for audiobooks too!
for value in myShows.values():
    try:
        value.sort(key=lambda x: x.seasonEpisode)
        for ep in value:
            if value[0].seasonEpisode.startswith('s00'):
                value.append(value.pop(ep))
    except:
        value.sort(key=lambda x: x.index)

#Starts to play queue, using the PlexServer attribute in the Episode object
print('Ready!')

while myShows:
    userCom = input('''
    ****************************
    To start, skip, or play next when episode is done, hit enter.
    You can also type "quit" to exit.
    ****************************\n''')
    if userCom == '':
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
        continue
    elif userCom == 'quit':
        break
    else:
        input('Invalid command. Press enter to continue.')
        continue