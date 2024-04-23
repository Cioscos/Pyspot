from .card import Card
from .labeled_cards_frame import LabeledCardsFrame


class LabeledArtistCardsFrame(LabeledCardsFrame):
    def create_card(self, container, image_url, name, additional_info, card_size, image_size, navigate_callback, data):
        return Card(container,
                    image_url=image_url,
                    name=name,
                    subtitle='Artist',
                    role='Artist',
                    card_size=card_size,
                    image_size=image_size,
                    rounded=True,
                    navigate_callback=self.navigate_callback,
                    data=data
                    )

    def get_additional_info(self, item):
        # No additional info required for artists in this scenario
        return None
