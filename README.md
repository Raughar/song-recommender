# Song Recomendation

With this project, I aim to create a song recomendation system. To do that, I have scraped the Billboard Top 100 list of songs and got som data from Spotify about song features, to create clusters. The original idea was to cluster the songs by genre, but the Spotify API has some limitaitions for genres and can only give genre recomendation seeds, which are not sufficient. For now, the project will function as follows:

- First, we ask the user to input a song or artist

- Then, we will check if the song or artist is present in the Billboard Top 100 list.

- If so, we will recommend a song from that list if the user gave a song name, and a song from the artist if the input was the artist name.

- If the song/artist is not present in the input from the user, we will then ask for a specific song of the artist from the input if that was the orignal input.

- We will use the Spotipy library to get the song features of the song.

- The next step will be to run those features through the KMeans algorithm to assign it a cluster.

- Then, we will recommend a song from that cluster that is not the same song.

- We will ask the user if he wants a new song recomendation if so, we will recommend a new song, until the user wants to end the process.

As of the last version, I have created a GUI using PySImpleGUI and a Streamlit app, that you can check here: https://song-recommender-samuel.streamlit.app/
In the future, I want to improve the GUI by creating a .EXE file and give the Streamlit app a new look.

You can check the code for the Stremlit app here: https://github.com/Raughar/streamlit-song

The tools used to make this project were:
- Python
- Spotipy library ( https://spotipy.readthedocs.io/en/2.22.1/# )
- Scikit-learn KMeans model for clustering
- PySimpleGUI ( https://www.pysimplegui.com/ )
- Streamlit ( https://streamlit.io/ )
