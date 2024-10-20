import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyPlayer:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.scope = 'user-read-playback-state user-modify-playback-state'
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=self.scope
        ))

    def play_song(self, track_uri, device_id=None):
        """Start playing a song given its Spotify URI."""
        self.sp.start_playback(device_id=device_id, uris=[track_uri])

    def pause(self, device_id=None):
        """Pause the current playback."""
        self.sp.pause_playback(device_id=device_id)

    def resume(self, device_id=None):
        """Resume playback."""
        self.sp.start_playback(device_id=device_id)

    def stop(self, device_id=None):
        """Stop playback by pausing and seeking to the beginning."""
        self.pause(device_id)
        self.sp.seek_track(position_ms=0, device_id=device_id)

    def get_current_track(self):
        """Get information about the currently playing track."""
        return self.sp.current_playback()

    def set_volume(self, volume_percent, device_id=None):
        """Set the volume (0 to 100)."""
        self.sp.volume(volume_percent, device_id=device_id)

    def get_devices(self):
        """List available playback devices."""
        devices = self.sp.devices()
        return devices.get('devices', [])
    
    def get_track_uris(self, artist_song_list):
        """
        Takes a lisst of (artist_name, song_name) tuples and returns a list of Spotify track URIs.
        
        Parameters:
            artist_song_list (list of tuples): Each tuple contains (artist_name, song_name).
        
        Returns:
            list: A list of Spotify track URIs.
        """
        track_uris = []
        for artist, song in artist_song_list:
            query = f"artist:{artist} track:{song}"
            try:
                results = self.sp.search(q=query, type='track', limit=1)
                tracks = results['tracks']['items']
                if tracks:
                    track_uri = tracks[0]['uri']
                    track_uris.append(track_uri)
                else:
                    print(f"Track not found for {artist} - {song}")
                    track_uris.append(None)
            except Exception as e:
                print(f"An error occurred while searching for {artist} - {song}: {e}")
                track_uris.append(None)
        return track_uris
    
    def create_playlist(self, playlist_name, track_uris, public=False):
        """
        Creates a new playlist with the given name and adds the provided track URIs.

        Parameters:
            playlist_name (str): The name of the new playlist.
            track_uris (list): A list of Spotify track URIs to add to the playlist.
            public (bool): Whether the playlist should be public. Defaults to False.

        Returns:
            dict: The newly created playlist's details.
        """
        try:
            # Get the current user's ID
            user_id = self.sp.current_user()['id']

            # Create a new playlist
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=playlist_name,
                public=public
            )
            playlist_id = playlist['id']

            # Add tracks to the playlist in batches of 100
            for i in range(0, len(track_uris), 100):
                self.sp.user_playlist_add_tracks(
                    user=user_id,
                    playlist_id=playlist_id,
                    tracks=track_uris[i:i + 100]
                )
            print(f"Playlist '{playlist_name}' created successfully.")
            return playlist
        except Exception as e:
            print(f"An error occurred while creating the playlist: {e}")
            return None
    

if __name__ == '__main__':
    # Initialize the SpotifyPlayer
    player = SpotifyPlayer(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    # Get available devices and select one
    devices = player.get_devices()
    if devices:
        device_id = devices[0]['id']  # Select the first available device
    else:
        print("No devices available.")
        exit()

    # Play a specific song
    track_uri = 'spotify:track:443NlczMsHNzZuTX3cTQtz'
    player.play_song(track_uri, device_id=device_id)

    # Pause playback
    player.pause(device_id=device_id)

    # Resume playback
    player.resume(device_id=device_id)

    # Stop playback
    player.stop(device_id=device_id)

    # Set volume to 50%
    player.set_volume(50, device_id=device_id)

    # Get current track info
    current_track = player.get_current_track()
    if current_track and current_track['is_playing']:
        print(f"Currently playing: {current_track['item']['name']} by {current_track['item']['artists'][0]['name']}")
    else:
        print("No track is currently playing.")