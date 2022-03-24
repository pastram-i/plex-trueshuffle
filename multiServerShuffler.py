#Required packages
from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.library import Library, Hub
import config, random, time

myAccount = MyPlexAccount(config.username,config.password)
plextv_clients = [x for x in myAccount.resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
myServers = [myAccount.resource(server).connect() for server in config.servers]

myShows = {}
myQueue = []

#Pulls shows from playlists on each server
for server in myServers:
    for playlist in server.playlists():
        for episode in playlist.items():
            if episode.grandparentTitle not in myShows.keys():
                myShows[episode.grandparentTitle] = [] #Will add all unique show names from all servers
            if episode not in myShows[episode.grandparentTitle]:
                myShows[episode.grandparentTitle].append(episode) #Will add all unique episodes from all servers

'''if config.includePodcasts:
    plex = myAccount.resource()'''


#Organizing shows by 's##e##' value in the Episode object.
#Can use index for audiobooks too!
for value in myShows.values():
    try:
        value.sort(key=lambda x: x.seasonEpisode)
    except:
        value.sort(key=lambda x: x.index)

#Adds a queue of 100 episodes to play
while len(myQueue) < 100:
    i=0
    toAdd = random.choice(list(myShows))
    for episode in myShows[toAdd]:
        if episode.viewCount <= i and episode not in myQueue:
            myQueue.append(episode)
            i=0
            break
        else:
            i+=1
            continue

#Starts to play queue, using the PlexServer attribute in the Episode object
while myQueue:
    userCom = input('To start, skip, or play next when episode is done, hit enter. You can also type "quit" to exit.\n')
    if userCom == '':
        playEpisode = myQueue.pop(0)
        print(
        '''----------------------------
        Now playing:            {} {}
        Season:                 {}
        Episode:                {}
        Length (HH:MM:SS:MMMM): {}
        '''.format(playEpisode.grandparentTitle,playEpisode.seasonEpisode, playEpisode.parentTitle,playEpisode.title,millisecondToHumanstr(playEpisode.duration))
        )

        client = plextv_clients[0].connect()
        client.playMedia(playEpisode)
        continue
    elif userCom == 'quit':
        break
    else:
        input('Invalid command. Press enter to continue.')
        continue

#An old way, saving while I trial the new way
'''for playEpisode in myQueue:
    print(
        ----------------------------
        Now playing:            {} {}
        Season:                 {}
        Episode:                {}
        Length (HH:MM:SS:MMMM): {}
        .format(playEpisode.grandparentTitle,playEpisode.seasonEpisode, playEpisode.parentTitle,playEpisode.title,str(playEpisode),millisecondToHumanstr(playEpisode.duration))
        )

    client = plextv_clients[0].connect()
    client.playMedia(playEpisode)
    print(f'Sleeping for: {(playEpisode.duration / 1000)+30} seconds')
    time.sleep((playEpisode.duration/1000)+30)
    while client.isPlayingMedia():
        time.sleep(60)'''