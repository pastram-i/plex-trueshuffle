from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.client import PlexClient
import config, random, re, time

myAccount = MyPlexAccount(config.username,config.password)
myServers = []

for server in config.servers:
    myServers.append(myAccount.resource(server).connect())

myShows = {}
myQueue = []

for server in myServers:
    for playlist in server.playlists():
        for episode in playlist.items():
            if episode.grandparentTitle not in myShows.keys():
                myShows[episode.grandparentTitle] = []
            if episode not in myShows[episode.grandparentTitle]:
                myShows[episode.grandparentTitle].append(episode)

for show in myShows.keys():
    myShows[show].sort(key=lambda x: re.sub(r'Episode:.+?-s', '',str(x)))

while len(myQueue) < 100:
    i=0
    toAdd = random.choice(list(myShows))
    for episode in myShows[toAdd]:
        if episode.viewCount <= i and episode not in myQueue:
            myQueue.append(episode)
            break
        else:
            i+=1
            continue

for playEpisode in myQueue:
    print(
        '''----------------------------
        Now playing:            {}
        Season:                 {}
        Episode:                {}
        Full Name:              {}
        Length (HH:MM:SS:MMMM): {}'''
        .format(playEpisode.grandparentTitle,playEpisode.parentTitle,playEpisode.title,str(playEpisode),millisecondToHumanstr(playEpisode.duration))
        )

    plex = myAccount.resource(config.servers[myServers.index(playEpisode._server)]).connect()
    
    print(plex.clients())
    for client in plex.clients():
        print(client.title)

    client = plex.client(config.client)
    try:
        device_url = client.url("/")
    except plexapi.exceptions.BadRequest:
        device_url = "127.0.0.1"
    if "127.0.0.1" in device_url:
        client.proxyThroughServer()

    client.playMedia(playEpisode)

    time.sleep(playEpisode.duration/1000)

    while client.isPlayingMedia():
        time.sleep(10000)