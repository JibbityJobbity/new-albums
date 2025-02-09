import random

import config
from services.get_spotify import get_spotify
from rich import print

import json


spotify = get_spotify()
reject_fields = [
    "available_markets",
    "external_urls",
    "href",
    "images",
    "album_type",
    "release_date_precision",
    "uri",
    "type",
]


def get_spotify_songs_from_playlist(
    playlistId, desired_quantity, skip_recents=None, name=""
):

    """
    This function will return a list of track ids from a playlist.
    I'm not sure we'll need it for this program, but it's been very useful in the past.
    """

    playlist = {"id": playlistId, "quantity": desired_quantity}

    print(
        f"\n - returning {desired_quantity} SPOTIFY track IDs for the spotify playlist '{name}' with ID: {playlistId}"
    )
    # print(spotify)

    # get the results for every song in the playlist
    results = spotify.user_playlist_tracks(config.SPOTIFY_USER, playlist["id"])
    # print(results)
    tracks = results["items"]
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])

    # pprint(tracks[:2])

    track_ids = []
    for x in tracks:
        track = x["track"]
        if track is None:
            print("TRACK IS NONE!")
            continue
        try:
            id = track["id"]
        except:
            print(track)
        track_ids.append(id)
    # # extract the trackids for every song in the playlist from results
    # [x["track"]["id"] for x in tracks]
    # # print(len(track_ids))

    # If you've passed a list of recently played track ids to skip
    if skip_recents != None:
        track_ids = [x for x in track_ids if x not in skip_recents]
    print(len(track_ids))

    # If there are still more track ids than you want to pull from this playlist,
    # take a random sample.
    if len(track_ids) > desired_quantity:
        track_ids = random.sample(track_ids, int(desired_quantity))

    # if name == "sparks":

    # print(track_ids)
    # exit()

    return track_ids


def get_new_album_ids(limit=50):
    """
    Get all the album ids from the last x new albums. It doesn't include single-only releases OR any genres you've marked as reject.
    """
    new = spotify.new_releases(limit=limit, country="US")["albums"]["items"]

    new.sort(key=lambda x: x["release_date"], reverse=True)

    # Remove any albums that are single-only
    new_albums = [x for x in new if x["album_type"] == "album"]
    # print(new)

    # Remove any fields that we don't for the rest of the script
    for x in new_albums:
        for f in reject_fields:
            x.pop(f, None)

    new_albums = remove_reject_genres(new_albums)

    return [x["id"] for x in new_albums]


def remove_reject_genres(new_albums):
    """
    remove any albums whose first artist's first genre is in reject_genres
    """
    with open("reject_genres.json") as f:
        reject_genres = json.load(f)

    albums = []
    for album in new_albums:
        main_artist = album["artists"][0]
        artist_name = main_artist["name"]
        main_artist = spotify.artist(main_artist["id"])

        artist_genres = main_artist["genres"]
        # print(artist_name, genres)

        if contains_reject_genre(reject_genres, artist_name, artist_genres):
            continue
        else:
            albums.append(album)

    return albums


def contains_reject_genre(reject_genres, artist_name, artist_genres):
    try:
        artist_genre = artist_genres[0]
    except:
        print(f"{artist_name} has no genres")
        return False

    for reject_genre in reject_genres:
        if (
            reject_genre["genre"] in artist_genre
            and artist_name not in reject_genre["exceptions"]
        ):
            print(f"{artist_name}'s first genre is a reject genre: {artist_genre}")
            return True

    print(f"{artist_name}'s first genre is not a reject genres: {artist_genres}")


def get_track_ids_for_album(album_id):
    """
    Get the track ids for a single album.
    """
    # print(f"getting track ids for album {album_id}")
    album = spotify.album(album_id)

    # print(track_ids)
    return [x["id"] for x in album["tracks"]["items"]]


def main():

    print("new_albums.setup main...")

    new_album_ids = get_new_album_ids()
    # print(new_album_ids)
    # exit()

    #

    track_ids = []

    for album_id in new_album_ids:
        # print(album_id)
        track_ids.extend(get_track_ids_for_album(album_id))

        # print(track_ids)

    # TODO:
    # accomodate a request of more than 100 tracks
    if len(track_ids) > 100:
        track_ids = track_ids[:100]

    print("updating spotify playlist")
    result = spotify.user_playlist_replace_tracks(
        config.SPOTIFY_USER, config.PLAYLIST_ID, track_ids
    )
    print(result)

    # # change the playlist description to a random fact
    # post_description(job)
