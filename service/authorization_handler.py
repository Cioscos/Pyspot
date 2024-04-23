import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse as urlparse


class AuthorizationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the query parameters from the request
        query = urlparse.urlparse(self.path).query
        query_components = urlparse.parse_qs(query)

        # Assuming 'code' is the authorization code
        code = query_components["code"][0] if "code" in query_components else None

        if code:
            # Close the server after capturing the code
            self.server.shutdown()

            # Exchange the code for a token in the main application
            ui_window.exchange_code_for_token(
                code)  # You will need to properly reference your UiMainWindow instance here

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Authorization successful, you can close this window.")