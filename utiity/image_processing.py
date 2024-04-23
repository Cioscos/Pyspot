from PIL import Image, ImageDraw, ImageOps
from PIL.Image import Resampling


def create_rounded_image(image, size=(100, 100)):
    """
    Creates a rounded (circular) image from the given image path.

    Args:
        size (tuple): The desired size of the output image as (width, height).

    Returns:
        PIL.ImageTk.PhotoImage: The rounded image ready for use with tkinter.
    """

    # Create a mask to crop the image into a circle
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)

    # Apply the mask to the image
    rounded_image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)

    return rounded_image
