from typing import Callable

import customtkinter as ctk
from .content import Content


class HomePageContent(Content):
    def __init__(self,
                 master: ctk.CTkFrame,
                 navigate_callback: Callable = None):
        super().__init__(master, navigate_callback)

    def load_data(self):
        return

    def render(self):
        label = ctk.CTkLabel(self.frame, text="This is the Home Page")
        label.pack(pady=20)
