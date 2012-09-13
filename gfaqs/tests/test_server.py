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

EXAMPLE_DIR = "file://%s/examples" % os.path.dirname(__file__)

class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


class TestRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        def die():
            self.send_response(404)
            self.end_headers()
            return

        path = self.path
        if not path:
            die()

        pr = urlparse.urlparse(path)
        if not pr.path: 
            die()
        base_path = pr.path.split("/")
        board_name = base_path[0]
        topic_name = ""
        if len(base_path) == 2:
            topic_name = base_path[1]


        if pr.query:
            query = urlparse.parse_qs(pr.query)
            page = query.get("page", 0)
        else:
            page = 0

        try:
            # ce/p0/topics
            # ce/p0/123312-0
            # ce/p0/123312-1
            if topic_name:
                fpath = "%s/%s/p%s/%s-%s" % (EXAMPLE_DIR,board_name,page,topic_name)
            else:
                fpath = "%s/%s/p%s/topics" % (EXAMPLE_DIR,board_name,page)
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
