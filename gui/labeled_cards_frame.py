from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Callable, Optional

import customtkinter as ctk


class LabeledCardsFrame(ctk.CTkFrame, ABC):
    def __init__(self, *args,
                 title: str,
                 data: List[Dict[str, Any]],
                 size: Tuple = (150, 200),
                 image_size: Tuple = (100, 100),
                 navigate_callback: Optional[Callable] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.data = data
        self.size = size
        self.image_size = image_size
        self.cards = []
        self.navigate_callback = navigate_callback
        self.init_ui()

    def init_ui(self):
        title_label = ctk.CTkLabel(self, text=self.title, font=('Arial', 14, 'bold'))
        title_label.pack(pady=(10, 20), padx=20)

        cards_frame = ctk.CTkFrame(self)
        cards_frame.pack(fill='both', expand=True)

        for item in self.data:
            image = None
            if item['images'] and item['images'][0]['width']:
                image = max(item["images"], key=lambda img: img["width"] * img["height"])
            elif item['images']:
                image = item["images"][0]

            card = self.create_card(
                container=cards_frame,
                image_url=image['url'] if image else image,
                name=item['name'],
                additional_info=self.get_additional_info(item),
                card_size=self.size,
                image_size=self.image_size,
                navigate_callback=self.navigate_callback,
                data=item
            )
            self.cards.append(card)

        self.bind("<Configure>", self.adjust_layout)

    @abstractmethod
    def create_card(self, container, image_url, name, additional_info, card_size, image_size, navigate_callback, data):
        pass

    @abstractmethod
    def get_additional_info(self, item):
        pass

    def adjust_layout(self, event=None):
        card_width = 150
        padding = 5
        container_width = self.winfo_width()

        cards_per_row = max(1, container_width // (card_width + (2 * padding)))

        row, column = 0, 0
        for card in self.cards:
            card.grid_forget()
            card.grid(row=row, column=column, padx=padding, pady=padding)
            column += 1
            if column >= cards_per_row:
                column = 0
                row += 1
