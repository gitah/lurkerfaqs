import os
import urlparse
import threading
import BaseHTTPServer
import SocketServer

"""
Implements a webserver that emulates a gamefaqs GET request for testing
"""
HOSTNAME="localhost"
PORT_NUMBER= 9999

if __name__ != "__main__":
    EXAMPLE_DIR = "%s/examples" % os.path.dirname(__file__)
else:
    EXAMPLE_DIR = "%s/examples" % os.getcwd()

BOARDS_DIR = "boards"
TOPICS_DIR = "topics"

class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


class TestRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        def die():
            self.send_response(404)
            self.end_headers()
            return

        path = self.path
        pr = urlparse.urlparse(path)

        base_path = pr.path.split("/")
        board_name = topic_name = ""
        if len(base_path) == 3:
            # Case 1: we're dealing with a board
            board_name = base_path[2]
        elif len(base_path) == 4:
            # Case 2: we're dealing with a topic
            board_name = base_path[2]
            topic_name = base_path[3]
        else:
            # Case 3: invalid dealing with a topic
            die()

        if pr.query:
            query = urlparse.parse_qs(pr.query)
            page = query.get("page", [0])[0]
        else:
            page = 0

        try:
            if topic_name:
                fpath = "%s/%s/%s-%s" % (EXAMPLE_DIR,TOPICS_DIR,topic_name,page)
            else:
                fpath = "%s/%s/%s-%s" % (EXAMPLE_DIR,BOARDS_DIR,board_name,page)

            with open(fpath) as fp:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                for l in fp:
                    self.wfile.write(l)
        except IOError:
            die()


class TestServerThread(threading.Thread):
    def __init__(self, port, hostname="localhost"):
        super(TestServerThread,self).__init__()
        self.port=port
        self.hostname=hostname
        self.server = ThreadingHTTPServer(
            (self.hostname, self.port), TestRequestHandler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

def start_server(port, hostname="localhost"):
    th = TestServerThread(port,hostname)
    th.start()
    return th

if __name__ == "__main__":
    start_server(9999)
