import customtkinter as ctk
from PIL import Image
from utiity.image_cache import ImageCache


class HeaderBar(ctk.CTkFrame):
    """
    A header bar component that displays a list of clickable buttons, a clickable image,
    and navigation buttons.

    Attributes:
        master (ctk.CTk): The parent widget.
        buttons (list): A list of strings representing the button labels.
        image_path (str): The file path to the header image.
        on_button_click (function): A callback function for button click events.
        navigate_back (function): A callback function for the back navigation button.
        navigate_forward (function): A callback function for the forward navigation button.
    """

    def __init__(self, master, buttons, image_path, on_button_click, navigate_back, navigate_forward, **kwargs):
        super().__init__(master, height=80, **kwargs)
        self.pack_propagate(False)
        self.master = master
        self.buttons = buttons
        self.image_path = image_path
        self.on_button_click = on_button_click
        self.navigate_back = navigate_back
        self.navigate_forward = navigate_forward

        self.image_cache = ImageCache()

        self.create_widgets()

    def create_widgets(self):
        """Creates and packs the navigation and functional buttons along with a clickable image into the header bar."""

        # Back and Forward navigation buttons
        btn_back_image = Image.open('./icons/back.png')
        btn_back_image_ctk = ctk.CTkImage(light_image=btn_back_image, dark_image=btn_back_image)
        btn_back = ctk.CTkButton(self, command=self.navigate_back, image=btn_back_image_ctk, text='')
        btn_back.pack(side='left', padx=2)

        btn_forward_image = Image.open('./icons/next.png')
        btn_forward_image_ctk = ctk.CTkImage(light_image=btn_forward_image, dark_image=btn_forward_image)
        btn_forward = ctk.CTkButton(self, command=self.navigate_forward, image=btn_forward_image_ctk, text='')
        btn_forward.pack(side='left', padx=2)

        # Functional buttons
        for button_label in self.buttons:
            button = ctk.CTkButton(self, text=button_label,
                                   command=lambda b=button_label: self.on_button_click(b))
            button.pack(side='left', padx=10)

        # Profile image button
        profile_image = self.image_cache.fetch_image(self.image_path)
        image = ctk.CTkImage(light_image=profile_image,
                                  dark_image=profile_image)
        image_button = ctk.CTkButton(self, image=image,
                                     command=lambda b="Profile": self.on_button_click(b), text='Profile')
        image_button.pack(side='right', padx=10)
