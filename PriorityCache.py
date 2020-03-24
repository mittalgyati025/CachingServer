from download_file import download_file
import collections
import glob
import os
import config_cdash


def download_segment(segment_path):
    """ Function to download the segment"""
    segment_url = config_cdash.CONTENT_SERVER + segment_path

    if "mpd" in segment_path:
        local_filepath = os.path.join(config_cdash.MPD_FOLDER, segment_path)
    else:
        local_filepath = os.path.join(config_cdash.VIDEO_FOLDER, segment_path)
    print "Inside download function " + segment_url + "  " + local_filepath
    return download_file(segment_url, local_filepath)

class PriorityCache():

    def __init__(self, maxsize):
        config_cdash.LOG.info('Initialed the priority cache')
        self.cache = {}


    def get_file(self, key, code=config_cdash.FETCH_CODE):
        """ Get the file from the cache.
        If not get it from the content server
        """
        config_cdash.LOG.info("code = {}".format(code))
        try:
            local_filepath, http_headers = self.cache[key]
        except KeyError:
            local_filepath, http_headers = download_segment(key)
            self.cache[key] = (local_filepath, http_headers)
            config_cdash.LOG.info('Adding key {} to cache'.format(key))

        return local_filepath, http_headers