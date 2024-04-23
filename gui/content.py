import threading
from abc import ABC, abstractmethod
from typing import Callable

import customtkinter as ctk

from ctk_components import CTkLoader


class Content(ABC):
    """
    Abstract base class for all content types in the application.
    Each content class should provide an implementation for initializing and rendering its content.
    """
    def __init__(self, master, navigate_callback: Callable):
        self.master = master
        self.navigate_callback = navigate_callback
        self.frame = ctk.CTkFrame(master)
        self.frame.pack(fill='both', expand=True)
        self.loading_indicator = CTkLoader(master=self.frame, opacity=0.8, width=40, height=40)
        self.loading_indicator.place(relx=0.5, rely=0.5, anchor='center')

    def show_loading_indicator(self):
        self.loading_indicator.place(relx=0.5, rely=0.5, anchor='center')  # Center in the frame
        self.loading_indicator.lift()  # Make sure it's above all other widgets

    def hide_loading_indicator(self):
        self.loading_indicator.place_forget()  # Hide the loader

    def load_and_display(self):
        """
        Loads the necessary data asynchronously and initiates rendering of the content.
        This method should handle both data preparation and the subsequent update of the UI.
        """
        def async_load():
            self.show_loading_indicator()
            # Simulate loading
            self.load_data()
            self.master.after(0, self.finish_loading)

        threading.Thread(target=async_load).start()

    def finish_loading(self):
        self.render()
        self.hide_loading_indicator()

    @abstractmethod
    def load_data(self):
        """ Method to load data required for the content. """
        pass

    @abstractmethod
    def render(self):
        """
        Render the content in the associated frame.
        This method will be called from `load_and_display` once data is ready.
        """
        pass

    def clear(self):
        """
        Clear the content frame.
        This removes all widgets from the frame, useful when refreshing or changing content.
        """
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show(self):
        """
        Show the content frame.
        This method ensures that the frame is visible, typically called after rendering is complete.
        """
        self.frame.pack(fill='both', expand=True)

    def hide(self):
        """
        Hide the content frame.
        This can be used to temporarily remove the frame from view, such as during transitions.
        """
        self.frame.pack_forget()
