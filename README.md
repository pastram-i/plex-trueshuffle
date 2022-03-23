#Multi (Or single) server shuffle for plex
The goal is to watch shows in order, but shuffle between shows after each plays

Allows users to create an off platform queue of Episodes. This queue will -

 - Be created from shows in playlists
 	- Personally I create a playlist on each server
 		- Go through shows and just click `Add to => Playlist`
 	- You can do just an episode, or the whole show
 	- Playlist name **does not** matter.
 - Play the next episode in order for that show
 - Only persist if the script is running
 	- Usually I'll just run it starting my day
 	- It may take a few minutes to start depending on the number of servers/shows you follow
 - Display information on an episode as it sends the request to play it

## Requirements:
 - Python
 	- Comes with `config`, `random`, `re`, and `time`
 		- These are required if you managed to skip them somehow
 - pip
 - [PlexAPI](https://github.com/pkkid/python-plexapi)

## Config:
- In `config.py` you'll have to update four items -
	- `username` should be a string of your plex account name
	- `password` should be a string of your plex account password
	- `servers` should be a list of strings of the server(s) name
		- **Not** server provider account name
	- ~~`client` should be a string of your client to send requests~~
        - `client` is no longer needed, the script will use your most recent connected client in `Plex=>Authorized Devices`
            - If the desired client isn't the most recent, just reconnect/refresh and it's value will be updated allowing the script to grab the (correct) first

## To run:
Open a `terminal` or `cmd` depending on your OS. Navigate to the file using `cd` and/or run using 

`python <path>/<to>/<file>/multiServerShuffler.py`

## Things to add:
 - Movies
 - Podcast episodes
