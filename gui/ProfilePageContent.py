from typing import Dict, Any, Optional, List, Callable
import customtkinter as ctk

from service.config_reader import ConfigReader
from service.spotify_client import SpotifyClient
from utiity.image_cache import ImageCache
from .content import Content
from utiity.image_processing import create_rounded_image
from gui.labeled_artist_cards_frame import LabeledArtistCardsFrame
from gui.labeled_track_list_frame import LabeledTrackListFrame
from gui.profile_info_component import ProfileInfoComponent
from gui.labeled_playlist_cards_frame import LabeledPlaylistCardsFrame


class ProfilePageContent(Content):
    def __init__(self,
                 master: ctk.CTkFrame,
                 spotify_client: SpotifyClient,
                 config: ConfigReader,
                 current_profile: Dict[str, Any],
                 image_cache: ImageCache,
                 navigate_callback: Callable = None):
        super().__init__(master, navigate_callback)

        self.sp_client = spotify_client
        self.config = config
        self.current_profile = current_profile
        self.image_cache = image_cache

        # initialize responses variables
        self.top_artists: Optional[List[Dict[str, Any]]] = None
        self.top_tracks: Optional[List[Dict[str, Any]]] = None
        self.user_public_playlists = []

        # Initialize frame variables
        self.left_frame = None
        self.right_frame = None

    def load_data(self):
        self._fetch_data()

    def _fetch_data(self):
        # Perform all data fetching operations
        # This runs in a background thread
        self.top_artists = self.sp_client.get(self.config.get_config_value("api.endpoints.users.user_top_item_artists"),
                                              params={'time_range': 'short_term', 'limit': 8})['items']

        self.top_tracks = self.sp_client.get(self.config.get_config_value("api.endpoints.users.user_top_item_tracks"),
                                             params={'time_range': 'short_term', 'limit': 10})['items']

        user_playlist = self.sp_client.get(self.config.get_config_value("api.endpoints.users.current_user_playlists"),
                                           params={'limit': 10})

        self.user_public_playlists.clear()  # Clear existing data
        for playlist in user_playlist['items']:
            if playlist['public']:
                self.user_public_playlists.append({
                    'href': playlist['href'],
                    'name': playlist['name'],
                    'owner_name': playlist['owner']['display_name'],
                    'images': playlist['images']
                })

    def render(self):
        """
        Renders the profile content into the provided master frame.
        """

        # Left Column - Profile Image and User Details
        self.left_frame = ctk.CTkFrame(self.frame)
        self.left_frame.pack(side='left', fill='y', padx=(20, 10), pady=20)

        if "images" in self.current_profile and self.current_profile["images"]:
            largest_image = max(self.current_profile["images"], key=lambda img: img["width"] * img["height"])
            image_url = largest_image["url"]
            profile_image = self.image_cache.fetch_image(image_url)
            profile_image = create_rounded_image(profile_image, (largest_image["width"], largest_image["height"]))
            ctk_image = ctk.CTkImage(light_image=profile_image, dark_image=profile_image,
                                     size=(largest_image["width"], largest_image["height"]))
            profile_image_label = ctk.CTkLabel(self.left_frame, image=ctk_image, text='')
            profile_image_label.image = ctk_image  # keep a reference
            profile_image_label.pack(padx=10, pady=10)

        # Profile Info Components
        ProfileInfoComponent(self.left_frame,
                             "Display Name:",
                             self.current_profile.get("display_name", "N/A")
                             ).pack(fill='x', pady=2, padx=5)
        ProfileInfoComponent(self.left_frame,
                             "Email:",
                             self.current_profile.get("email", "N/A")
                             ).pack(fill='x', pady=2, padx=5)
        ProfileInfoComponent(self.left_frame,
                             "Country:",
                             self.current_profile.get("country", "N/A")
                             ).pack(fill='x', pady=2, padx=5)
        followers = str(self.current_profile.get("followers", {}).get("total", "N/A"))
        ProfileInfoComponent(self.left_frame, "Followers:", followers).pack(fill='x', pady=2, padx=5)

        # Right Column - Top Artists and Tracks
        self.right_frame = ctk.CTkFrame(self.frame)
        self.right_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)

        # Scrollable Frame for Top Artists and Tracks
        scroll_frame = ctk.CTkScrollableFrame(self.right_frame)
        scroll_frame.pack(fill='both', expand=True)

        # Top Artists
        top_artists_frame = LabeledArtistCardsFrame(scroll_frame,
                                                    title='The top artists of this month',
                                                    data=self.top_artists,
                                                    size=(200, 250),
                                                    image_size=(200, 200),
                                                    navigate_callback=self.navigate_callback)
        top_artists_frame.pack(fill='both', expand=True, pady=10)

        # Top Tracks
        top_tracks_frame = LabeledTrackListFrame(scroll_frame,
                                                 title='The top tracks!',
                                                 track_data=self.top_tracks)
        top_tracks_frame.pack(fill='both', expand=True, pady=10)

        # Public playlist
        public_playlist_frame = LabeledPlaylistCardsFrame(scroll_frame,
                                                          title='Public playlists',
                                                          data=self.user_public_playlists,
                                                          size=(150, 200),
                                                          image_size=(130, 130),
                                                          navigate_callback=self.navigate_callback)
        public_playlist_frame.pack(fill='both', expand=True, pady=10)
