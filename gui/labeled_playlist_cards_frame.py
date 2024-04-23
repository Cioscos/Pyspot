from .card import Card
from .labeled_cards_frame import LabeledCardsFrame


class LabeledPlaylistCardsFrame(LabeledCardsFrame):
    def create_card(self, container, image_url, name, additional_info, card_size, image_size, navigate_callback, data):
        return Card(container,
                    image_url=image_url,
                    name=name,
                    subtitle=additional_info,
                    role='Playlist',
                    card_size=card_size,
                    image_size=image_size,
                    navigate_callback=self.navigate_callback,
                    data=data
                    )

    def get_additional_info(self, item):
        return f"By {item.get('owner_name', '')}"  # The role information is more detailed for playlists
