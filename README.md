# Music Share

## What is it?

A flask based web server that allows multiple users on a local area network to add songs to a Spotify queue.


## Note
In order to run this application, the spotipy and flask libraries must be present on the machine. In order to get the Client ID and Secret ID, the owner of the Spotify account must go to https://developer.spotify.com/dashboard/login, create an app and copy over the respective ID's into their spots in server.py. From here, the owner of the Spotify account should click "Edit Settings", type http://(Server IP):(Port the server is running on). Additionally, the server's local IP has to replace HOST IP in both server.py and client.py. The port that the server should connect to the client on should replace PORT.
