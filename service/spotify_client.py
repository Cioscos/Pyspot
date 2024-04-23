import json
import os

import httpx
import base64
import hashlib
import secrets
import time
import logging
from .config_reader import ConfigReader

logger = logging.getLogger(__name__)


class SpotifyClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        access_token, refresh_token, token_expiration = self.read_saved_tokens_locally()
        self.access_token = access_token if access_token else None
        self.refresh_token = refresh_token if refresh_token else None
        self.token_expires = token_expiration if token_expiration else None

        # initialize config reader instance
        self.config = ConfigReader("config.yaml")

        self.code_verifier = self.generate_code_verifier()
        self.code_challenge = self.generate_code_challenge(self.code_verifier)
        self.client = httpx.Client()  # Persistent HTTP client instance

    @staticmethod
    def generate_code_verifier(length=64):
        """Generate a high-entropy cryptographic random string as code verifier."""
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def generate_code_challenge(code_verifier):
        """Transform the code verifier to a code challenge."""
        digest = hashlib.sha256(code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().replace('=', '')

    def construct_auth_url(self, scope):
        """Construct the URL for user authorization."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.config.get_config_value("api.redirect_uri"),
            "code_challenge_method": "S256",
            "code_challenge": self.code_challenge,
            "scope": scope
        }
        return f"{self.config.get_config_value("api.auth_url")}?{httpx.QueryParams(params)}"

    def exchange_code_for_token(self, code):
        """Exchange authorization code for an access token."""
        data = {
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.get_config_value("api.redirect_uri"),
            "code_verifier": self.code_verifier
        }
        response = self.client.post(self.config.get_config_value("api.access_token_url"),
                                    data=data,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                                    )
        if response.status_code == 200:
            json_response = response.json()
            self.access_token = json_response["access_token"]
            self.refresh_token = json_response["refresh_token"]
            # Set the expiration time (current time + expires_in - a small leeway)
            self.token_expires = time.time() + json_response["expires_in"] - 60
            self.save_tokens_locally()
        else:
            raise Exception(f"Failed to retrieve access token: {response.status_code}")

    def ensure_token_validity(self):
        """Ensure that the access token is valid, refreshing it if necessary."""
        if time.time() >= self.token_expires:
            self.refresh_access_token()

    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = self.client.post(self.config.get_config_value("api.access_token_url"),
                                    data=data,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                                    )
        if response.status_code == 200:
            json_response = response.json()
            self.access_token = json_response["access_token"]
            # Optionally update the refresh token if a new one is provided
            self.refresh_token = json_response.get("refresh_token", self.refresh_token)
            # Reset the expiration time
            self.token_expires = time.time() + json_response["expires_in"] - 60
            self.save_tokens_locally()
        else:
            raise Exception(f"Failed to refresh access token: {response.status_code}")

    def save_tokens_locally(self):
        os.makedirs('data', exist_ok=True)

        dictionary = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expires": self.token_expires
        }

        with open('data/tokens.json', 'w') as f:
            f.write(json.dumps(dictionary))

    def read_saved_tokens_locally(self):
        """Reads saved tokens from a local JSON file and returns the access, refresh tokens, and token expiry.

        Returns:
            tuple: A tuple containing the access token, refresh token, and token expiry. Returns (None, None, None) if the file doesn't exist or the content is invalid.
        """
        # Define the file path
        file_path = 'data/tokens.json'

        # Check if the file exists
        if os.path.exists(file_path):
            try:
                # Open and directly load the JSON content into a dictionary
                with open(file_path, 'r') as f:
                    dictionary = json.load(f)

                # Extract tokens and expiry, checking for their existence
                access_token = dictionary.get("access_token")
                refresh_token = dictionary.get("refresh_token")
                token_expires = dictionary.get("token_expires")

                # Ensure all tokens are present, else return None values
                if not all([access_token, refresh_token, token_expires]):
                    return None, None, None

                return access_token, refresh_token, token_expires
            except json.JSONDecodeError:
                # Handle case where file content is not valid JSON
                return None, None, None

        # Return None values if file doesn't exist
        return None, None, None

    def is_session_saved(self):
        return self.access_token is not None

    def get(self, url, params=None, **kwargs):
        """Perform a GET request with optional query parameters.

        Args:
            url (str): The URL for the GET request.
            params (dict, optional): A dictionary of query parameters.
            **kwargs: Additional keyword arguments to be passed to the request.

        Returns:
            The response from the GET request as a JSON object.
        """
        self.ensure_token_validity()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"

        # Include query params in the request. If `params` is None, this is effectively ignored.
        response = self.client.get(url, headers=headers, params=params, **kwargs)

        # Logging the response
        logger.info("Response received")
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response text: {response.text}")

        # Return the JSON response, assuming the request was successful and the response is in JSON format
        return response.json()

    def post(self, url, data=None, json=None, **kwargs):
        """Perform a POST request."""
        self.ensure_token_validity()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        response = self.client.post(url, headers=headers, data=data, json=json, **kwargs)
        logger.info("Response received")
        logger.info("Status code: {}".format(response.status_code))
        logger.info("Response text: {}".format(response.text))
        return response.json()

    def put(self, url, data=None, **kwargs):
        """Perform a PUT request."""
        self.ensure_token_validity()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        response = self.client.put(url, headers=headers, data=data, **kwargs)
        logger.info("Response received")
        logger.info("Status code: {}".format(response.status_code))
        logger.info("Response text: {}".format(response.text))
        return response.json()

    def delete(self, url, **kwargs):
        """Perform a DELETE request."""
        self.ensure_token_validity()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        response = self.client.delete(url, headers=headers, **kwargs)
        logger.info("Response received")
        logger.info("Status code: {}".format(response.status_code))
        logger.info("Response text: {}".format(response.text))
        return response.json()
