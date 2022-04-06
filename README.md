# Multi (Or single) server shuffle for plex
The goal is to watch episodes in order, but shuffle between shows after each play.

Allows the user to create a small sqlite database file of their shows, and all episodes that can be found on all their servers for those shows.

This means it will -
 - Create DB file
	- This pulls shows from your playlists (playlist name does not matter)
	- Go through each show, and search each server for show
	- Collect all episodes for all shows
**Also includes audiobooks if they are in the playlist**

When you select to `play`, the script will roll a random show.

Before it is played, your servers will be searched to update View Counts for any changes.
- This also allows any new or missing episodes to be added to your DB

Then the script will look for the lowest episode number, with the least view count (regardless of server - view counts a summed across all servers).

**Note: episodes with 's00' generally means they are specials. I move those to the end of the list, to watch after the series.**

Once an episode has been chosen, it will scan your servers for the appropriate file and play.Information on what's being played will show in your console.

## Requirements:
Need to have python 3.6 or higher, and pip.
Navigate to the directory of this file, and run `pip install -r requirements.txt` which will grab:
```
plexapi
config
random
time
sqlite3
datetime
```
You should have most of these already, as they come with python.

Download [plex media server](https://www.plex.tv/media-server-downloads/#plex-app) and run. Right click on the icon in your task bar, and select `Open`. This will open the plex app in your browser for a client to use.

## Config.py:
- `username` should be a string of your plex account name
- `password` should be a string of your plex account password
- `servers` should be a list of strings
	- Should only include server(s) name
	- **Should Not** include account name of the server owner
- 'audioLang' should be your preferred audio language
- 'subLang' should be your preferred subtitle language

**Note: audioLang and subLang will attempt to set the media when playing to this language if one is found. If one is not, it will select the default.**

## To run:
Open a `terminal` or `cmd` depending on your OS. Navigate to the file using `cd` and run:

`python plex-multi_server_queue_shuffle.py`

You can also:

`python <path>/<to>/<file>/multiServerShuffler.py`

**Note: Depending on how you manage python, you may have to use `python3` command instead of `python`**

**Commands:**
 - `help` will display all commands
 - `create` will build a DB file. This is required on first run, and can be  - used later to reset from a blank slate.
 - `Update` will run a scan of all servers, to add all episodes for your shows to the DB. **Note: this will take a while. It is also not necessary before playing, as each show is updated when chosen to be played. Nothing wrong with hitting this on your first run though for an initial setup.**
 - You can hit enter to submit an empty string. This will shuffle shows, and play the next episode. **Note: This can be done at any point, to skip what is currently playing, when your show ends, etc.**
 - 'quit' or 'exit' will exit the script.

## Things to add:
 - Movies, this may even work now? idk haven't tested
 - Podcast episodes
 - I wonder if I can make this into a browser extension...