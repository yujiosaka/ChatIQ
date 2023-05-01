import argparse
import sys

from gunicorn.app.wsgiapp import WSGIApplication


def run():
    parser = argparse.ArgumentParser(description="Start the ChatIQ server")
    parser.add_argument("-p", "--port", type=int, default=3000, help="Server port (default: 3000)")
    args = parser.parse_args()

    sys.argv = ["gunicorn", "chatiq.main:app", f"--bind=0.0.0.0:{args.port}"]
    WSGIApplication().run()
