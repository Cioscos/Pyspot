import hashlib
import os
import httpx
from PIL import Image
from io import BytesIO


class ImageCache:
    """
    A simple caching system for images fetched from URLs.
    """

    def __init__(self, cache_dir="image_cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()

    def ensure_cache_dir(self):
        """Ensures the cache directory exists."""
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_image_hash(self, url):
        """Returns a SHA-256 hash of the URL."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def get_cached_image_path(self, url):
        """Returns the path to the cached image, if it exists."""
        filename = self.get_image_hash(url) + ".png"
        return os.path.join(self.cache_dir, filename)

    def fetch_image(self, url):
        """Fetches an image from the URL or cache and returns a PIL.Image.Image object."""
        cached_path = self.get_cached_image_path(url)
        if os.path.exists(cached_path):
            # Load from cache
            return Image.open(cached_path)
        else:
            # Download and cache
            response = httpx.get(url)
            img = Image.open(BytesIO(response.content))
            img.save(cached_path)  # Cache the image
            return img
