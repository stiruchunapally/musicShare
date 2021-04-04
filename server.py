import spotipy
from spotipy import SpotifyException
from Song import Song
from spotipy.oauth2 import SpotifyOAuth
import socket
import pickle
from _thread import *

scope = "user-modify-playback-state"  # The scope of Spotify permissions that are required
SPOTIFY_CLIENT_ID = "CLIENTID"  # The Client ID of the App (Add your own)
SPOTIFY_SECRET_ID = "SECRETID" # The Secret ID of the App (Add your own)
REDIRECT_URI = "http://10.192.54.210:5000/"  # The redirect URL in case of failed authentication

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_SECRET_ID,
                                               redirect_uri=REDIRECT_URI,  scope=scope))

ServerSocket = socket.socket()
host = '10.192.54.210'  # The Host IP
port = 1233  # The port the web server is hosted on
ThreadCount = 0

# Binds socket to the port
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

# Waits for client connection
print('Waiting for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection):
    """
    Accepts commands from the Client

    :param: The connection between the Server and Client
    """

    while True:
        data = pickle.loads(connection.recv(2048))
        read_command(data, connection)
        if not data:
            break
    connection.close()


def read_command(command, connection):
    """
    Processes the command from the client

    :param command: The command received from the Client
    :param: The connection between the Server and Client
    """

    if command[0] == "GET":
        if command[1] == "Song":
            reply = pickle.dumps(search(command[2]))
            connection.send(reply)
        elif command[1] == "Current":
            reply = pickle.dumps(get_now_playing())
            connection.send(reply)
    elif command[0] == "POST":
        if command[1] == "Song":
            reply = pickle.dumps(add_song_to_queue(command[2]))
            connection.send(reply)
        elif command[1] == "SongID":
            reply = pickle.dumps(add_song_to_queue_from_id(command[2]))
            connection.send(reply)


def search(song_name):
    """
    Searches for a song and processes the data received from the Spotify API into a new Song object. The Song
    objects found are added to a list.

    :param song_name: The connection between the Server and Client
    :return: The list of songs received from the Spotify API
    """

    results = sp.search(q=song_name, limit=20)
    newSongList = []
    for i in range(len(results['tracks']['items'])):
        newSongName = results['tracks']['items'][i]['name']
        newSongArtist = results['tracks']['items'][i]['album']['artists'][0]['name']
        newSongAlbum = results['tracks']['items'][i]['album']['name']
        newSongId = results['tracks']['items'][i]['id']
        newSongAlbumArt = results['tracks']['items'][i]['album']['images'][0]['url']
        newSong = Song(newSongName, newSongArtist, newSongAlbum, newSongId, newSongAlbumArt)
        newSongList.append(newSong)

    return newSongList


def add_song_to_queue(song):
    """
    Adds a song to the queue given a Song object

    :param song: The song object that should be added to the queue
    :return: A success or error message
    """

    songID = song.id
    try:
        message = sp.add_to_queue(songID)
    except SpotifyException:
        message = "Error - No Active Device"
    return message


def add_song_to_queue_from_id(song_id):
    """
    Adds a song to the queue given a Song ID

    :param song_id: The ID of the song that should be added to the queue
    :return: A success or error message
    """

    try:
        message = sp.add_to_queue(song_id)
    except SpotifyException:
        message = "Error - No Active Device"
    return message


def get_now_playing():
    """
    Gets the currently playing song

    :return: The Song object of the song that is currently playing
    """

    results = sp.currently_playing()
    if results != None:
        currentSongName = results['item']['name']
        currentSongArtist = results['item']['album']['artists'][0]['name']
        currentSongAlbum = results['item']['album']['name']
        currentSongId = results['item']['id']
        currentSongAlbumArt = results['item']['album']['images'][0]['url']
        currentSong = Song(currentSongName, currentSongArtist, currentSongAlbum, currentSongId, currentSongAlbumArt)
        return currentSong
    else:
        return "No Song Playing"


# After client connection, keeps the connection open, prints the address of the client and creates a new thread
while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
