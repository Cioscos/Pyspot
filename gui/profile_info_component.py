import customtkinter as ctk


class ProfileInfoComponent(ctk.CTkFrame):
    """
    A custom component for displaying a piece of profile information within a ctk.CTkFrame.

    Attributes:
        label_text (str): The text for the label part of the information (e.g., "Display Name").
        value_text (str): The actual value to display (e.g., the user's name).
    """

    def __init__(self, master, label_text, value_text, **kwargs):
        super().__init__(master, **kwargs)
        self.label_text = label_text
        self.value_text = value_text
        self.init_ui()

    def init_ui(self):
        """Initializes the UI components of the ProfileInfoComponent."""
        label = ctk.CTkLabel(self, text=self.label_text, anchor="w", font=('Arial', 15, 'bold'))
        label.pack(fill='x', padx=10, pady=(5, 0))

        value = ctk.CTkLabel(self, text=self.value_text, anchor="w", font=('Arial', 12))
        value.pack(fill='x', padx=10, pady=(0, 5))
