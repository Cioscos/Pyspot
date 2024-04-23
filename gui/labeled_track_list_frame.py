from datetime import time

import customtkinter as ctk
from utiity.image_cache import ImageCache


class LabeledTrackListFrame(ctk.CTkFrame):
    def __init__(self, *args, title, track_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracks_frame = None
        self.title = title
        self.track_data = track_data
        self.image_cache = ImageCache()
        self.init_ui()

    def init_ui(self):
        # Title Label
        title_label = ctk.CTkLabel(self, text=self.title, font=('Arial', 14, 'bold'))
        title_label.pack(pady=(10, 20), padx=20)

        # Container Frame for track list
        self.tracks_frame = ctk.CTkFrame(self)
        self.tracks_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.tracks_frame.grid_columnconfigure(0, weight=1)

        # Load tracks
        self.load_tracks()

    def load_tracks(self):
        for index, track in enumerate(self.track_data, start=1):
            self.create_track_row(index, track)

    def create_track_row(self, index, track):
        row_frame = ctk.CTkFrame(self.tracks_frame, corner_radius=5)
        row_frame.grid(row=index - 1, column=0, columnspan=5, padx=5, pady=2, sticky="ew")
        for col in range(5):
            row_frame.grid_columnconfigure(col, weight=1)

        components = [
            self.create_index_frame(row_frame, index),
            self.create_image_frame(row_frame, track['album']["images"][1]),
            self.create_info_frame(row_frame, track),
            self.create_album_frame(row_frame, track),
            self.create_length_frame(row_frame, track)
        ]

        # Bind enter and leave events to change the foreground color
        # row_frame.bind("<Enter>", lambda e: self.on_hover(components))
        # row_frame.bind("<Leave>", lambda e: self.on_leave(components))

    def on_hover(self, components):
        for component in components:
            if isinstance(component, ctk.CTkFrame):
                component.configure(fg_color=self.hover_fg)

    def on_leave(self, components):
        for component in components:
            if isinstance(component, ctk.CTkFrame):
                component.configure(fg_color=self.default_fg)

    def on_label_click(self, track):
        """Handle click events on labels."""
        print(f"Track clicked: {track['name']}")
        # Implement your action here, such as opening a detail view or playing the track

    def create_index_frame(self, parent, index):
        frame = ctk.CTkFrame(parent, width=50, height=30, corner_radius=0)
        frame.grid_propagate(False)
        frame.grid(row=0, column=0, sticky="ew")
        label = ctk.CTkLabel(frame, text=str(index), font=('Arial', 10, 'bold'))
        label.place(relx=0.5, rely=0.5, anchor="center")
        return frame

    def create_image_frame(self, parent, image_data):
        frame = ctk.CTkFrame(parent, width=50, height=50, corner_radius=5)
        frame.grid_propagate(False)
        frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        track_image = self.image_cache.fetch_image(image_data['url'])
        ctk_image = ctk.CTkImage(light_image=track_image, dark_image=track_image, size=(50, 50))
        label = ctk.CTkLabel(frame, image=ctk_image, text='')
        label.place(relwidth=1, relheight=1)
        return frame

    def create_info_frame(self, parent, track):
        """Creates a frame for track information with conditionally clickable labels."""
        frame = ctk.CTkFrame(parent, width=200, height=30, corner_radius=0)
        frame.grid_propagate(False)
        frame.grid(row=0, column=2, sticky="ew", padx=5)

        # Check if the track name should be clickable
        if True:
            track_info_label = ctk.CTkLabel(frame,
                                            text=f"{track['name']}\n{', '.join(artist['name'] for artist in track['artists'])}",
                                            font=('Arial', 10),
                                            cursor="hand2")  # Change cursor to indicate it's clickable
            track_info_label.bind("<Button-1>", lambda e: self.on_label_click(track))  # Bind click event
            track_info_label.bind("<Enter>", lambda e: track_info_label.configure(font=ctk.CTkFont(family='Arial', size=10, underline=True)))
            track_info_label.bind("<Leave>", lambda e: track_info_label.configure(font=ctk.CTkFont(family='Arial', size=10)))
        else:
            track_info_label = ctk.CTkLabel(frame,
                                            text=f"{track['name']}\n{', '.join(artist['name'] for artist in track['artists'])}",
                                            font=('Arial', 10))

        track_info_label.place(relx=0.5, rely=0.5, anchor="center")
        return frame

    def create_album_frame(self, parent, track):
        frame = ctk.CTkFrame(parent, width=200, height=30, corner_radius=0)
        frame.grid_propagate(False)
        frame.grid(row=0, column=3, sticky="ew", padx=5)
        label = ctk.CTkLabel(frame, text=track['album']['name'], font=('Arial', 10))
        label.place(relx=0.5, rely=0.5, anchor="center")
        return frame

    def create_length_frame(self, parent, track):
        frame = ctk.CTkFrame(parent, width=100, height=30, corner_radius=0)
        frame.grid_propagate(False)
        frame.grid(row=0, column=4, sticky="ew", padx=5)
        label = ctk.CTkLabel(frame, text=self._convert_ms_in_timeformat(track['duration_ms']), font=('Arial', 10))
        label.place(relx=0.5, rely=0.5, anchor="center")
        return frame
    # def create_track_row(self, index, track):
    #     row_frame = ctk.CTkFrame(self.tracks_frame, corner_radius=5)
    #     row_frame.grid(row=index - 1, column=0, columnspan=5, padx=5, pady=2, sticky="ew")
    #     for col in range(5):
    #         row_frame.grid_columnconfigure(col, weight=1)
    #
    #     # Progressive Number
    #     index_frame = ctk.CTkFrame(row_frame, width=50, height=30,
    #                                corner_radius=0)  # Fixed size container for the index
    #     index_frame.grid_propagate(False)  # Prevents the frame from resizing to fit its content
    #     index_frame.grid(row=0, column=0, sticky="ew")
    #     index_label = ctk.CTkLabel(index_frame, text=str(index), font=('Arial', 10))
    #     index_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the label within the fixed size frame
    #
    #     # Track Image
    #     image_data = track['album']["images"][1]
    #     image_frame = ctk.CTkFrame(row_frame, width=80, height=80, corner_radius=5)  # Adjusted for image size
    #     image_frame.grid_propagate(False)
    #     image_frame.grid(row=0, column=1, sticky="ew", padx=5)
    #
    #     track_image = self.image_cache.fetch_image(image_data['url'])
    #     ctk_image = ctk.CTkImage(light_image=track_image,
    #                              dark_image=track_image,
    #                              size=(100, 100)
    #                              )
    #     image_label = ctk.CTkLabel(image_frame, image=ctk_image, text='')
    #     image_label.place(relwidth=1, relheight=1)  # Make the label fill the fixed size frame
    #
    #     # Track Info
    #     info_frame = ctk.CTkFrame(row_frame, width=200, height=30, corner_radius=0)  # Adjust width as needed
    #     info_frame.grid_propagate(False)
    #     info_frame.grid(row=0, column=2, sticky="ew", padx=5)
    #     track_info_label = ctk.CTkLabel(info_frame,
    #                                     text=f"{track['name']}\n{', '.join(artist['name'] for artist in track['artists'])}",
    #                                     font=('Arial', 10))
    #     track_info_label.place(relx=0.5, rely=0.5, anchor="center")
    #
    #     # Album Name
    #     album_frame = ctk.CTkFrame(row_frame, width=200, height=30, corner_radius=0)  # Adjust width as needed
    #     album_frame.grid_propagate(False)
    #     album_frame.grid(row=0, column=3, sticky="ew", padx=5)
    #     album_label = ctk.CTkLabel(album_frame, text=track['album']['name'], font=('Arial', 10))
    #     album_label.place(relx=0.5, rely=0.5, anchor="center")
    #
    #     # Track Length
    #     length_frame = ctk.CTkFrame(row_frame, width=100, height=30, corner_radius=0)  # Adjust width as needed
    #     length_frame.grid_propagate(False)
    #     length_frame.grid(row=0, column=4, sticky="ew", padx=5)
    #     length_label = ctk.CTkLabel(length_frame, text=self._convert_ms_in_timeformat(track['duration_ms']),
    #                                 font=('Arial', 10))
    #     length_label.place(relx=0.5, rely=0.5, anchor="center")

    @staticmethod
    def _convert_ms_in_timeformat(ms):
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s = ms // 1000

        formatted_time = f"{h if h != 0 else ''}{':' if h != 0 else ''}{m:02d}:{s:02d}"

        return formatted_time
