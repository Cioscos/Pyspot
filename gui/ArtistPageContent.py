from typing import Dict, Any, Optional, List, Callable
import customtkinter as ctk

from gui.content import Content
from gui.labeled_artist_cards_frame import LabeledArtistCardsFrame
from gui.labeled_playlist_cards_frame import LabeledPlaylistCardsFrame
from gui.labeled_track_list_frame import LabeledTrackListFrame
from gui.profile_info_component import ProfileInfoComponent
from service.config_reader import ConfigReader
from service.spotify_client import SpotifyClient
from utiity.image_cache import ImageCache
from utiity.image_processing import create_rounded_image


class ArtistPageContent(Content):
    def __init__(self,
                 master: ctk.CTkFrame,
                 spotify_client: SpotifyClient,
                 config: ConfigReader,
                 current_profile: Dict[str, Any],
                 image_cache: ImageCache,
                 data: Any,
                 navigate_callback: Optional[Callable] = None,
                 ):
        super().__init__(master, navigate_callback)

        self.sp_client = spotify_client
        self.config = config
        self.current_profile = current_profile
        self.image_cache = image_cache
        self.artist_data = data

        self.albums: List[Dict[str, Any]] = []
        self.singles: List[Dict[str, Any]] = []
        self.appears_on: List[Dict[str, Any]] = []
        self.top_tracks: List[Dict[str, Any]] = []
        self.related_artists: List[Dict[str, Any]] = []

    def load_data(self):
        self._fetch_data()

    def _fetch_data(self):
        # Perform all data fetching operations
        self.albums = self.sp_client.get(
            self.config.get_config_value('api.endpoints.artist.get_albums').format(self.artist_data['id']),
            params={'include_groups': 'album', 'limit': 9}
        )['items']

        self.singles = self.sp_client.get(
            self.config.get_config_value('api.endpoints.artist.get_albums').format(self.artist_data['id']),
            params={'include_groups': 'single', 'limit': 9}
        )['items']

        self.appears_on = self.sp_client.get(
            self.config.get_config_value('api.endpoints.artist.get_albums').format(self.artist_data['id']),
            params={'include_groups': 'appears_on', 'limit': 9}
        )['items']

        self.top_tracks = self.sp_client.get(
            self.config.get_config_value('api.endpoints.artist.top_tracks').format(self.artist_data['id'])
        )['tracks']

        self.related_artists = self.sp_client.get(
            self.config.get_config_value('api.endpoints.artist.related_artists').format(self.artist_data['id'])
        )['artists']

    def render(self):
        # Left Column - Profile Image and Artist Details
        self.left_frame = ctk.CTkFrame(self.frame)
        self.left_frame.pack(side='left', fill='y', padx=(20, 10), pady=20)

        # artist profile image
        if 'images' in self.artist_data and self.artist_data['images']:
            largest_image = max(self.artist_data['images'], key=lambda image: image["width"] * image["height"])
            image_url = largest_image["url"]
            profile_image = self.image_cache.fetch_image(image_url)
            profile_image = create_rounded_image(profile_image, (largest_image["width"], largest_image["height"]))
            ctk_image = ctk.CTkImage(light_image=profile_image, dark_image=profile_image,
                                     size=(largest_image["width"], largest_image["height"]))
            profile_image_label = ctk.CTkLabel(self.left_frame, image=ctk_image, text='')
            profile_image_label.image = ctk_image
            profile_image_label.pack(padx=10, pady=10)

        # Profile info components
        ProfileInfoComponent(self.left_frame,
                             "Followers",
                             self.artist_data.get("followers").get("total", 'N/A'),
                             ).pack(fill='x', pady=2, padx=5)
        ProfileInfoComponent(self.left_frame,
                             "Genres:",
                             ', '.join(self.artist_data.get("genres", "N/A"))
                             ).pack(fill='x', pady=2, padx=5)

        # Right columns - Artist albums and tracks
        self.right_frame = ctk.CTkFrame(self.frame)
        self.right_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.right_frame,
                     text=self.artist_data['name'],
                     font=ctk.CTkFont(family='Helvetica', size=40, weight='bold')
                     ).pack(fill='x', pady=10, padx=5)

        # Scrollable Frame for Top Artists and Tracks
        scroll_frame = ctk.CTkScrollableFrame(self.right_frame)
        scroll_frame.pack(fill='both', expand=True)

        # Top tracks
        LabeledTrackListFrame(scroll_frame,
                              title='The top tracks!',
                              track_data=self.top_tracks
                              ).pack(fill='both', expand=True, pady=10)

        # Albums
        if self.albums:
            LabeledPlaylistCardsFrame(scroll_frame,
                                      title='Album',
                                      data=self.albums,
                                      size=(200, 250),
                                      image_size=(200, 200),
                                      navigate_callback=self.navigate_callback
                                      ).pack(fill='both', expand=True, pady=10)

        # Singles
        if self.singles:
            LabeledPlaylistCardsFrame(scroll_frame,
                                      title='Singles and EP',
                                      data=self.singles,
                                      size=(200, 250),
                                      image_size=(200, 200),
                                      navigate_callback=self.navigate_callback
                                      ).pack(fill='both', expand=True, pady=10)

        # Appears on
        if self.appears_on:
            LabeledPlaylistCardsFrame(scroll_frame,
                                      title='Appears on',
                                      data=self.appears_on,
                                      size=(200, 250),
                                      image_size=(200, 200),
                                      navigate_callback=self.navigate_callback
                                      ).pack(fill='both', expand=True, pady=10)

        # Related artists
        if self.related_artists:
            LabeledArtistCardsFrame(scroll_frame,
                                    title='The top artists of this month',
                                    data=self.related_artists,
                                    size=(100, 150),
                                    image_size=(80, 80),
                                    navigate_callback=self.navigate_callback
                                    ).pack(fill='both', expand=True, pady=10)
