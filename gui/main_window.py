import logging
from typing import Optional, Any

import customtkinter as ctk

from gui.ArtistPageContent import ArtistPageContent
from gui.ProfilePageContent import ProfilePageContent
from gui.HomePageContent import HomePageContent
from gui.ArtistsPageContent import ArtistsPageContent
from service.config_reader import ConfigReader
from service.spotify_client import SpotifyClient
from gui.header_bar import HeaderBar
from utiity.image_cache import ImageCache


logger = logging.getLogger(__name__)


class UiMainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme('theme.json')

        logger.info("Welcome to Spotipy!\nLogging in...")

        # initialize config reader instance
        self.config = ConfigReader("config.yaml")
        self.current_profile = {}

        api_access_data = self.config.get_config_value('api')

        self.sp_client = SpotifyClient(
            api_access_data['client_id'],
            api_access_data['client_secret']
        )

        # Frame which contains the content of the page based on the pressed header button
        self.content_frame = None
        self.bottom_bar = None
        self.current_content_name = None
        self.page_history = []
        self.forward_history = []

        # Stores the current content shown in the content_frame
        self.current_content = None

        self.image_cache = ImageCache()

    def init_ui(self):
        """
        Initializes the user interface for the main window.
        """
        self.title("Pyspot")
        self.geometry("1280x1200")

        # User profile retrieval
        self.current_profile = self.sp_client.get(
            self.config.get_config_value("api.endpoints.users.current_user_profile"))
        profile_image_url = self.current_profile["images"][0]["url"] if self.current_profile["images"] else None

        # Header bar with navigation and function buttons
        header_bar = HeaderBar(self, ["Home", "Artists"], profile_image_url,
                               self.on_header_button_click, self.navigate_back, self.navigate_forward)
        header_bar.pack(side='top', fill='x')

        # Main content frame setup
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(side='top', fill='both', expand=True)

        # Bottom bar setup
        self.init_bottom_bar()

    def init_bottom_bar(self):
        """
        Initializes the bottom bar and adds it to the main window.
        """
        self.bottom_bar = ctk.CTkFrame(self, height=100)
        self.bottom_bar.pack(side='bottom', fill='x')
        self.bottom_bar.configure(bg_color='grey', fg_color='black', corner_radius=0)

    def update_content(self, content_type_identifier: str = 'Home', data: Optional[Any] = None):
        """
        Updates the content of the main window based on a unique content identifier and associated data.
        """
        base_content_type = content_type_identifier.split(':')[0]  # Extract the base content type

        if hasattr(self, 'current_content') and self.current_content is not None:
            self.current_content.clear()
            self.current_content.hide()

        if not self.page_history or (self.page_history[-1][0] != content_type_identifier):
            self.page_history.append((content_type_identifier, data))
            self.forward_history.clear()

        # Instantiate and render the appropriate content object
        if base_content_type == "Home":
            self.current_content = HomePageContent(self.content_frame)
        elif base_content_type == "Profile":
            self.current_content = ProfilePageContent(self.content_frame,
                                                      self.sp_client,
                                                      self.config,
                                                      self.current_profile,
                                                      self.image_cache,
                                                      navigate_callback=self.update_content
                                                      )
        elif base_content_type == "Artists":
            self.current_content = ArtistsPageContent(self.content_frame)
        elif base_content_type == "Artist":
            self.current_content = ArtistPageContent(self.content_frame,
                                                     self.sp_client,
                                                     self.config,
                                                     self.current_profile,
                                                     self.image_cache,
                                                     navigate_callback=self.update_content,
                                                     data=data
                                                     )

        self.current_content.load_and_display()

    def on_header_button_click(self, txt: str):
        print(f"Header button clicked: {txt}")
        # Determine the content type based on the button text
        if txt == "Home":
            self.update_content("Home")
        elif txt == "Artists":
            self.update_content("Artists")
        elif txt == "Profile":
            self.update_content("Profile")

    def navigate_back(self):
        """
        Navigate to the previous page stored in the history stack.
        """
        if len(self.page_history) > 1:
            self.forward_history.append(self.page_history.pop())
            previous_content_type, previous_data = self.page_history[-1]
            self.update_content(previous_content_type, previous_data)

    def navigate_forward(self):
        """
        Navigate forward to the next page in the forward history stack, including the associated data.
        """
        if self.forward_history:
            next_content_type, next_data = self.forward_history.pop()
            self.update_content(next_content_type, next_data)
            self.page_history.append((next_content_type, next_data))

    def run(self):
        """
        Starts the tkinter main loop
        """
        self.init_ui()
        self.update_content("Home")
        self.mainloop()
