from flask import Flask, render_template, request, redirect, flash
import socket
import pickle


clientSocket = socket.socket()  # Creates a socket object for the client
host = '10.192.54.210'  # The host IP
port = 1233  # The port the web server is hosted on

# Tries to connect to the server
print('Waiting for connection')
try:
    clientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

app = Flask(__name__)
app.secret_key = 'secret'


def get_searched_songs(song_name):
    """
    Sends a message to the server and receives the list of songs that are found through the search

    :param song_name: The name of the song that is searched for (User input)
    :return: The list of songs that are found through the search
    """

    command = ["GET", "Song", song_name]
    clientSocket.send(pickle.dumps(command))
    response = clientSocket.recv(4096)
    found_songs = pickle.loads(response)
    return found_songs


def queue(song):
    """
    Sends a Song object to the server to be added to the queue.

    :param song: The song object that should be added to the queue
    :return: A success or error message from the server
    """

    command = ["POST", "Song", song]
    clientSocket.send(pickle.dumps(command))
    response = clientSocket.recv(4096)
    message = pickle.loads(response)
    return message


def queue_from_id(song_id):
    """
    Sends a Song ID to the server to be added to the queue.

    :param song_id: The id of the song that should be added to the queue
    :return: A success or error message from the server
    """

    command = ["POST", "SongID", song_id]
    clientSocket.send(pickle.dumps(command))
    response = clientSocket.recv(4096)
    message = pickle.loads(response)
    return message


def song_to_array(song):
    """
    Converts a Song object into an array

    :param song: The Song object that should be converted to an array
    :return: The converted song array
    """

    if song != "No Song Playing":
        song_array = [song.albumArt, song.name, song.artist, song.album, song.id]
        return song_array
    else:
        return "None"


def format_songs_list(songs_list):
    """
    Converts a List of Song objects into a nested array

    :param songs_list: List of Song objects
    :return: The converted nested array of songs
    """

    formatted_song_list = []
    for song in songs_list:
        formatted_song_list.append(song_to_array(song))
    return formatted_song_list


def get_current_song():
    """
    Sends a message to the server and receives the currently playing song

    :return: The current Song object
    """

    command = ["GET", "Current"]
    clientSocket.send(pickle.dumps(command))
    response = clientSocket.recv(4615)
    message = pickle.loads(response)
    return message


@app.route("/", methods=["GET", "POST"])
def home():
    """
    Shows the home page

    :return: Renders the Home template and sends the current song to be processed in the HTML
    """
    songs = ""
    current_song = song_to_array(get_current_song())
    return render_template('index.html', songsList=songs, len=len(songs), currentSong=current_song)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    Catches the POST request sent by the HTML after a search request, sends the name of the song to the server to be
    processed and sends the received list of songs and the length of the list to the HTML. If there are no found songs
    the user is shown a "No Songs Found" message

    :return: Renders the HTML and sends the list of songs to be processed in the HTML
    """
    songs = []
    if request.method == "POST":
        if "songName" not in request.form:
            return redirect(request.url)
        songName = request.form['songName']
        songs = format_songs_list(get_searched_songs(songName))
        if len(songs) == 0:
            flash("No Songs Found")

    return render_template('index.html', songsList=songs, len=len(songs), currentSong="None")


@app.route("/addToQueue", methods=["GET", "POST"])
def queue_button_handler():
    """
    Catches the POST request sent by the HTML after a queue request, sends the song id to the server to be processed and
    added to the queue. If there is no active device the user is shown a "Error - No Active Device" message

    :return: Redirects the user to the home page
    """
    if request.method == "POST":
        songToAdd = request.form['songId']
        message = queue_from_id(songToAdd)
        if message == "Error - No Active Device":
            flash(message)
    return redirect("/")


if __name__ == "__main__":
    # Runs the web server
    app.run(debug=False, threaded=True, host=host)
