import BaseHTTPServer
import sys
import os
import urllib2
import shutil
import errno
import hashlib
import json
from itertools import izip

import config_cdash
import timeit
import datetime
from os import stat
from prioritycache import CacheManager
import configure_cdash_log
import _elementtree as ET
MPD_DICT = {}




cache_manager = None
# HTTP CODES
HTTP_OK = 200
HTTP_NOT_FOUND = 404

class MyHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """HTTPHandler to serve the video"""
    # check if MPD_DICT file in cache exists
    def do_GET(self):
        """Function to handle the get message"""

        global MPD_DICT
        request = self.path.strip("/").split('?')[0]
        config_cdash.LOG.info("Received request {}".format(request))

        if 'mpd' in request:
            request_path = request.replace('/', os.path.sep)
            make_sure_path_exists(config_cdash.MPD_FOLDER)
            local_mpd_path = os.path.join(config_cdash.MPD_FOLDER, request_path)
            for header in self.headers:
                config_cdash.LOG.info(header)
            self.send_response(HTTP_OK)
            for header, header_value in MPD_DICT[request]['http_headers'].items():
                self.send_header(header, header_value)
            self.end_headers()

            with open(local_mpd_path, 'rb') as request_file:
                self.wfile.write(request_file.read())
                config_cdash.LOG.info('Served the MPD file from the cache server')


        elif 'm4s' in request:
            # Check if it is a valid request
            config_cdash.LOG.info('Request for m4s {}'.format(request))

            local_file_path, http_headers = cache_manager.fetch_file(request)
            config_cdash.LOG.debug('M4S request: local {}, http_headers: {}'.format(local_file_path, http_headers))
            self.send_response(HTTP_OK)
            for header, header_value in http_headers.items():
                self.send_header(header, header_value)
            self.end_headers()
            with open(local_file_path, 'rb') as request_file:
                self.wfile.write(request_file.read())

def make_sure_path_exists(path):
    """ Module to make sure the path exists if not create it
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def main():
    """ Main program wrapper """

    config_cdash.LOG = configure_cdash_log.configure_log(config_cdash.LOG_FILENAME, config_cdash.LOG_NAME,
                                                         config_cdash.LOG_LEVEL)
    global MPD_DICT


    config_cdash.LOG.info('Starting the cache in {} mode'.format(config_cdash.PREFETCH_SCHEME))

    try:
        with open(config_cdash.MPD_DICT_JSON_FILE, 'rb') as infile:
            MPD_DICT = json.load(infile)
    except IOError:
        config_cdash.LOG.warning('Starting Cache for first time. Could not find any MPD_json file. ')
    # Starting the Cache Manager
    global cache_manager
    config_cdash.LOG.info('Starting the Cache Manager')
    cache_manager = CacheManager.CacheManager()
    # Function to start server
    http_server = BaseHTTPServer.HTTPServer((config_cdash.HOSTNAME, config_cdash.PORT_NUMBER),
                                            MyHTTPRequestHandler)
    config_cdash.LOG.info("Cache-Server listening on {}, port:{} - press ctrl-c to stop".format(config_cdash.HOSTNAME,
                                                                                            config_cdash.PORT_NUMBER))
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        config_cdash.LOG.info('Terminating the Cache Manager')
        cache_manager.terminate()
        return

if __name__ == "__main__":
    sys.exit(main())
