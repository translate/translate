import json
import os
import shutil
import tempfile
import threading
from urllib.request import urlopen

from cheroot.wsgi import Server
from pytest import mark

from translate.services.tmserver import TMServer


class TestTMServer:
    @staticmethod
    def create_server(*args, **kwargs):
        test_dir = tempfile.mkdtemp()
        po_file = os.path.join(test_dir, "test.po")
        with open(po_file, "w") as handle:
            handle.write(
                """
msgid "Hello"
msgstr "Ahoj"
"""
            )
        test_file = os.path.join(test_dir, "test.tmdb")
        application = TMServer(
            test_file, tmfiles=[po_file], source_lang="en", target_lang="cs", **kwargs
        )
        return test_dir, application

    @staticmethod
    def cleanup(test_dir, application):
        application.tmdb.connection.close()
        shutil.rmtree(test_dir)

    def test_import(self):
        """Test importing strings into tmdb"""
        test_dir, application = self.create_server()
        assert application.tmdb.preload_db() == 1
        self.cleanup(test_dir, application)

    @mark.skipif(os.name == "nt", reason="can not delete non closed files")
    def test_server(self):
        """Test http server"""
        test_dir, application = self.create_server()

        # Prepare server thread
        server = Server(("localhost", 0), application.rest)
        server.prepare()
        server_port = server.bind_addr[1]
        thread = threading.Thread(target=server.serve)
        thread.start()

        # Run test
        response = urlopen(f"http://localhost:{server_port}/en/cs/unit/Hello/")
        payload = json.loads(response.read().decode("utf-8"))
        assert payload[0]["target"] == "Ahoj"

        # Shutdown the server thread
        server.stop()
        thread.join()
        self.cleanup(test_dir, application)
