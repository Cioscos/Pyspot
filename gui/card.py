import threading
from typing import Tuple, Optional, Callable, Any
from PIL import Image
import logging

import customtkinter as ctk

from utiity.image_cache import ImageCache
from utiity.image_processing import create_rounded_image

logger = logging.getLogger(__name__)


class Card(ctk.CTkFrame):
    DEFAULT_LOGOS = {
        'Playlist': './default_images/playlist.webp'
    }

    """
    A custom component that displays an item's image, name, and labels them as "Artist" in a card format.

    Attributes:
        master (ctk.CTk): The parent widget.
        image_url (str): The URL of the artist's image.
        artist_name (str): The name of the artist.
    """

    def __init__(self,
                 *args,
                 image_url: str,
                 image_size: Tuple[int, int],
                 name: str,
                 subtitle: str,
                 role: str,
                 card_size: Tuple = (150, 200),
                 rounded: bool = False,
                 navigate_callback: Optional[Callable] = None,
                 data: Optional[Any] = None,
                 **kwargs):
        super().__init__(*args, width=card_size[0], height=card_size[1], corner_radius=10, **kwargs)

        self.image_url = image_url
        self.artist_name = name
        self.subtitle = subtitle
        self.role = role
        self.image_size = image_size
        self.card_size = card_size
        self.rounded = rounded
        self.image_cache = ImageCache()
        self.image_label = None
        self.action_button = None
        self.navigate_callback = navigate_callback
        self.data = data

        self.action_button_x = image_size[0] - 50
        self.action_button_y = image_size[1] - 30

        self.debounce_job = None
        self.button_visible = False

        # Creation of content type identifier for the next artist called page
        self.content_type_identifier = f'Artist:{self.artist_name}'

        self.init_ui()
        self.bind_events()

    def init_ui(self):
        """Initializes the UI components of the ArtistCard."""
        # Fetch and display the artist's image
        self.image_label = ctk.CTkLabel(self, text='')
        self.image_label.pack(pady=10, padx=10)
        self.load_image()

        # Use tkinter font metrics to truncate text if necessary
        font = ctk.CTkFont(family="Arial", size=10, weight="bold")
        truncated_name = self._truncate_text_to_fit(self.artist_name, font, self.card_size[0] - 20)
        name_label = ctk.CTkLabel(self, text=truncated_name, font=font)
        name_label.pack()

        # subtitle Label ("Artist")
        subtitle_label = ctk.CTkLabel(self, text=self.subtitle, font=('Arial', 9))
        subtitle_label.pack(pady=(0, 5))

        # Position action button in the bottom right corner of the image
        self.action_button = ctk.CTkButton(self.image_label,
                                           text='',
                                           corner_radius=15 if self.rounded else 0,
                                           width=30,
                                           height=30
                                           )

    def _go_to(self):
        if self.navigate_callback:
            self.navigate_callback(self.content_type_identifier, self.data)

    def bind_events(self):
        """Binds necessary events for the card while ensuring no redundant triggers."""
        self.bind("<Enter>", lambda event: self.show_button(), add="+")
        self.bind("<Leave>", lambda event: self.hide_button(), add="+")
        self.bind("<Button-1>", self._go_to, add="+")
        # For child widgets, make sure to stop the propagation of events.
        for widget in self.winfo_children():
            widget.bind("<Enter>", lambda event: event.widget.master.show_button(), add="+")
            widget.bind("<Leave>", lambda event: event.widget.master.hide_button(), add="+")
            widget.bind("<Button-1>", lambda event: self._go_to())

    def show_button(self, event=None):
        """Show the action button if it's not visible and cancel any pending hide requests."""
        if self.debounce_job is not None:
            self.after_cancel(self.debounce_job)
            self.debounce_job = None

        if not self.button_visible:
            self.button_visible = True
            self.action_button.place(x=self.action_button_x, y=self.action_button_y)

    def hide_button(self, event=None):
        """Debounce the hiding of the button."""
        if self.debounce_job is not None:
            return  # Do not schedule another job if one is already pending

        self.debounce_job = self.after(100, self._hide_button)  # Adjust the time as needed for your use case

    def _hide_button(self):
        """Actually hide the button, checking the hover state."""
        x, y = self.winfo_pointerxy()
        card_x1 = self.winfo_rootx()
        card_y1 = self.winfo_rooty()
        card_x2 = card_x1 + self.winfo_width()
        card_y2 = card_y1 + self.winfo_height()

        if not (card_x1 <= x <= card_x2 and card_y1 <= y <= card_y2):
            self.action_button.place_forget()
            self.button_visible = False

        self.debounce_job = None

    def load_image(self):
        """Loads the artist's image from the given URL and updates the label asynchronously."""
        def update_image_on_ui(photo_image):
            if self.image_label.winfo_exists():  # Check if widget still exists before updating
                self.image_label.configure(image=photo_image)
                self.image_label.image = photo_image  # Keep a reference!

        def fetch_and_apply_image():
            try:
                if self.image_url:
                    image = self.image_cache.fetch_image(self.image_url)
                else:
                    image = Image.open(self.DEFAULT_LOGOS[self.role])

                if self.rounded:
                    image = create_rounded_image(image, self.image_size)

                photo_image = ctk.CTkImage(light_image=image,
                                           dark_image=image,
                                           size=self.image_size)
                self.image_label.after(0, update_image_on_ui, photo_image)

            except Exception as e:
                logger.error(f"Error loading artist image: {e}")
                # Load default image if error
                default_image = Image.open(self.DEFAULT_LOGOS[self.role])
                photo_image = ctk.CTkImage(light_image=default_image,
                                           dark_image=default_image,
                                           size=self.image_size)
                self.image_label.after(0, update_image_on_ui, photo_image)

        # Start the image loading in a separate thread
        thread = threading.Thread(target=fetch_and_apply_image)
        thread.start()

    def _truncate_text_to_fit(self, text, font, max_width):
        """
        Truncates text to fit within the specified width with an ellipsis if necessary using tkinter font metrics.
        """
        text_width = font.measure(text)
        while text_width > max_width:
            text = text[:-1]
            text_width = font.measure(text + '...')
        return text + '...' if text != self.artist_name else text
