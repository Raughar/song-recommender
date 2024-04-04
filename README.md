# Song Recomendation

With this project, I aim to create a song recomendation system. To do that, I have scraped the Billboard Top 100 list of songs and got som data from Spotify about song features, to create clusters. The original idea was to cluster the songs by genre, but the Spotify API has some limitaitions for genres and can only give genre recomendation seeds, which are not sufficient. For now, the project will function as follows:

- First, we ask the user to input a song or artist

- Then, we will check if the song or artist is present in the Billboard Top 100 list.

- If so, we will recommend a song from that list if the user gave a song name, and a song from the artist if the input was the artist name.

- If the song/artist is not present in the input from the user, we will then ask for a specific song of the artist from the input if that was the orignal input.

- We will use the Spotipy library to get the song features of the song.

- The next step will be to run those features through the KMeans algorithm to assign it a cluster.

- Then, we will recommend a song from that cluster that is no the same song.

- We will ask the user if he wants a new song recomendation if so, we will give a new song, that is not the same as the two before, by creating a list of the songs given, until the user wants to end the process.

The tools used to make this project were:
- Python
- Spotipy library ( https://spotipy.readthedocs.io/en/2.22.1/# )
- Scikit-learn KMeans model for clustering

In the future, I want to work upon this project and further improve it, by creating a GUI and new functions.
