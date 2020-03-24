import config_cdash
from socketserver import (TCPServer as TCP, StreamRequestHandler as SRH)
from time import ctime, time, sleep
import sys
import os
import urllib2
import shutil
import _elementtree as ET
import json

import configure_cdash_log
from prioritycache import CacheManager

HOST=config_cdash.HOSTNAME
PORT=config_cdash.TCP_PORT_NUMBER
ADDRESS=(HOST,PORT)
MPD_DICT = {}
cache_manager = None

class MyRequestHandler(SRH):
    def handle(self):
        global MPD_DICT
        request = self.rfile.readline().strip()
        print request
        # check if mpd file requested is in Cache Server (dictionary)
        if request in MPD_DICT:
            print('Found MPD in MPD_DICT')

        elif request in config_cdash.MPD_SOURCE_LIST:
            print("MPD not in cache. TCP Server Retrieving from Content server")
            # if mpd is in content server save it in cache server and put it in MPD_DICT and json file
            local_mpd_path, mpd_headers = cache_manager.fetch_file(request)


            print("Downloaded the MPD")


            i = iter(parse_mpd(local_mpd_path))
            print("Parsing MPD file")
            MPD_DICT[request] = {'http_headers': dict(mpd_headers), 'urls': parse_mpd(local_mpd_path)}
            with open(config_cdash.MPD_DICT_JSON_FILE, 'wb') as outfile:
                json.dump(MPD_DICT, outfile)
            print MPD_DICT[request]
            print("Downloading urls in the MPD file")
            #local_file_path, http_headers = cache_manager.fetch_file(request)

        else:
            print "not found"

        before = dict([(f, None) for f in os.listdir(config_cdash.VIDEO_FOLDER)])
        print before
        while 1:
            sleep(0.1)
            after = dict([(f, None) for f in os.listdir(config_cdash.VIDEO_FOLDER)])
            print after
            added = [f for f in after if not f in before]
            if added:
                data = "\nAdded: " + ''.join(added)
                before = after
                self.wfile.write(data)

def parse_mpd(mpd_file):
    tree = ET.ElementTree(file=mpd_file)
    url = []
    urlbase = config_cdash.CONTENT_SERVER


    for elem in tree.iter():
        if 'SegmentTemplate' in elem.tag:
            content_base = elem.attrib.get('media')
            init = elem.attrib.get('initialization')

    base = init
    tempurl = urlbase + base.replace("$RepresentationID$", "0")
    url.append(tempurl)
    tempurl = urlbase + init.replace("$RepresentationID$", "1")
    url.append(tempurl)

    base = content_base

    for i in range(1, 8):
        temp = base.replace("$Number%05d$", str(i).zfill(5))
        temp2=temp
        temp = temp.replace("$RepresentationID$","0")
        tempurl = urlbase + temp
        url.append(tempurl)
        temp = temp2.replace("$RepresentationID$","1")
        tempurl = urlbase + temp
        url.append(tempurl)

    return url

def main():
    config_cdash.LOG = configure_cdash_log.configure_log(config_cdash.LOG_FILENAME, config_cdash.LOG_NAME,
                                                         config_cdash.LOG_LEVEL)
    global MPD_DICT

    try:
        with open(config_cdash.MPD_DICT_JSON_FILE, 'rb') as infile:
            MPD_DICT = json.load(infile)
    except IOError:
        config_cdash.LOG.warning('Starting Cache for first time. Could not find any MPD_json file. ')

    global cache_manager
    config_cdash.LOG.info('Starting the Cache Manager')
    cache_manager = CacheManager.CacheManager()

    try:
        tcpServer = TCP(ADDRESS, MyRequestHandler)
        tcpServer.serve_forever()

    except KeyboardInterrupt:
        print("Terminating the TCP Server")
        return


if __name__ == "__main__":
    sys.exit(main())