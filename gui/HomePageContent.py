from typing import Callable, Optional, Any

import customtkinter as ctk

from .content import Content


class HomePageContent(Content):
    def __init__(self,
                 master: ctk.CTkFrame,
                 navigate_callback: Callable = None,
                 data: Optional[Any] = None):
        super().__init__(master, navigate_callback, data)

    def update_ui_with_new_data(self, data):
        pass

    def setup_ui(self):
        pass

    def load_data(self):
        return

    def render(self):
        label = ctk.CTkLabel(self.frame, text="This is the Home Page")
        label.pack(pady=20)
