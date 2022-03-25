#Required packages
from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import plexapi.video
import config, random, time

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

myAccount = MyPlexAccount(config.username,config.password)
plextv_clients = [x for x in myAccount.resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
myServers = []

for server in config.servers:
    try:
        myServers.append(myAccount.resource(server).connect())
    except:
        print(f"Could not connect to server: {server} :(")
        myServers.append(':(')
        continue

myShows = {}

#Pulls shows from playlists on each server
for server in myServers:
    if server != ':(':
        for playlist in server.playlists():
            for episode in playlist.items():
                if type(episode) == plexapi.video.Episode:
                    if episode.grandparentTitle not in myShows.keys():
                        myShows[episode.grandparentTitle] = [] #Will add all unique show names from all servers
                    if episode not in myShows[episode.grandparentTitle]:
                        myShows[episode.grandparentTitle].append(episode) #Will add all unique episodes from all servers

#Organizing shows by 's##e##' value in the Episode object.
#Can use index for audiobooks too!
for value in myShows.values():
    try:
        value.sort(key=lambda x: x.seasonEpisode)
    except:
        value.sort(key=lambda x: x.index)

#Starts to play queue, using the PlexServer attribute in the Episode object
while myShows:
    i=0
    userCom = input('''
    ****************************
    To start, skip, or play next when episode is done, hit enter.
    You can also type "quit" to exit.
    ****************************\n''')
    if userCom == '':
        toPlay = random.choice(list(myShows))
        for episode in myShows[toPlay]:
            if episode.viewCount <= i:
                playEpisode = episode
                i=0
                break
            else:
                i+=1
                continue
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