import logging
from gui import main_window
import webbrowser
import urllib.parse as urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%y-%m-%d %H:%M:%S',
    filename='spotipy.log',
    filemode='a'
)


class AuthorizationHandler(BaseHTTPRequestHandler):
    code_received = None

    def do_GET(self):
        global code_received
        query = urlparse.urlparse(self.path).query
        query_components = urlparse.parse_qs(query)
        code = query_components.get("code", [None])[0]

        if code:
            AuthorizationHandler.code_received = code
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Authorization successful, you can close this window.")
            return code
        else:
            self.send_error(400, "Missing 'code' query parameter.")


def wait_for_authorization(handler_class, server_address=('localhost', 3000), timeout=300):
    httpd = HTTPServer(server_address, handler_class)
    httpd.timeout = timeout
    httpd.handle_request()  # Handle a single request then return


def main() -> None:
    main_gui = main_window.UiMainWindow()

    if not main_gui.sp_client.is_session_saved():
        auth_url = main_gui.sp_client.construct_auth_url(scope="user-read-private user-read-email user-top-read playlist-read-private")
        webbrowser.open(auth_url)

        wait_for_authorization(AuthorizationHandler)  # Wait for the authorization code

        if AuthorizationHandler.code_received:
            main_gui.sp_client.exchange_code_for_token(AuthorizationHandler.code_received)
            # Proceed to start the main UI loop
            main_gui.run()
        else:
            logging.error("Authorization was not completed.")
    else:
        # Proceed to start the main UI loop
        main_gui.run()


if __name__ == '__main__':
    main()
