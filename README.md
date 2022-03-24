# Multi (Or single) server shuffle for plex
The goal is to watch episodes in order, but shuffle between shows after each plays

Allows users to create an off platform queue of Episodes. This queue will -

 - Be created from shows in playlists
 	# Create a playlist on each server
 		- Go through shows in server library and just click `Add to => Playlist`
 	# It's best to do this on a show level, to add all episodes
 	# Playlist name **does not** matter.
 - Play the next episode in order for that show
 - Only persist if the script is running
 	- It may take a few minutes to start depending on the number of servers/shows you follow
 - Display information on an episode as it sends the request to play it
 - Set audio and subtitles

## Requirements:
```bash
pip install -r requirements.txt
```
To grab:
```
plexapi
config
random
time
```

Download [plex media server](https://www.plex.tv/media-server-downloads/#plex-app) and run. Right click on the icon in your task bar, and select `Open`. This will open the plex app in your browser for a client to use.

## Config:
In `config.py` you'll have to update these items
- `username` should be a string of your plex account name
- `password` should be a string of your plex account password
- `servers` should be a list of strings
	- Should only include server(s) name
	- **Should Not** include account name of server owner
- 'audioLang' should be your preferred audio language
- 'subLang' should be your preferred subtitle language

## To run:
Open a `terminal` or `cmd` depending on your OS. Navigate to the file using `cd` and run:

`python plex-multi_server_queue_shuffle.py`

You can also:

`python <path>/<to>/<file>/multiServerShuffler.py`

**Note: Depending on how you manage python, you may have to use `python3` command instead of `python`**

## Things to add:
 - Movies, this may even work now? idk haven't tested
 - Podcast episodes
 - I wonder if I can make this into a browser extension...
 - A loca SQLlite db could probably cut down the time to load
	- Probably just reload db button to do on command
 - Querying new episodes for all shows, from all servers
 - Scan for missing episodes from other servers
 - Implement tracks for audiobooks