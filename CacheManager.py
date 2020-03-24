import threading
import time
import os
from PriorityCache import PriorityCache
import config_cdash
import Queue
import json

class CheckableQueue(Queue.Queue):
    """ Extending Queue to be able to check for existing values
    """
    def __contains__(self, item):
        with self.mutex:
            return item in self.queue


class CacheManager():
    def __init__(self, cache_size=config_cdash.CACHE_LIMIT):

        config_cdash.LOG.info('Initializing the Cache Manager')
        self.cache = PriorityCache(cache_size)
        config_cdash.LOG.info('Initialed the Cache Manager')
        self.prefetch_queue = CheckableQueue()
        self.current_queue = CheckableQueue()
        self.stop = threading.Event()
        self.current_thread = threading.Thread(target=self.current_function, args=())
        self.current_thread.daemon = True
        self.current_thread.start()
        config_cdash.LOG.info('Started the Current fetch thread')
        self.prefetch_thread = threading.Thread(target=self.prefetch_function, args=())
        self.prefetch_thread.daemon = True
        self.prefetch_thread.start()
        config_cdash.LOG.info('Started the Preftech thread')

    def terminate(self):
        self.stop.set()
        self.prefetch_thread.join()
        self.current_thread.join()

    def fetch_file(self, file_path):
        config_cdash.LOG.info('Fetching the file {}'.format(file_path))
        # Add the current request to the current_thread
        local_filepath, http_headers = self.cache.get_file(file_path)
        config_cdash.LOG.info('Added {} to current queue'.format(file_path))
        if "mpd" in file_path:
            print "fetching mpd file"
            self.current_queue.put(file_path)
        print "fetching m4s file"
        return local_filepath, http_headers

    def current_function(self):
        config_cdash.LOG.info('Current Thread: Started thread. Stop value = {}'.format(self.stop.is_set()))
        while not self.stop.is_set():
            try:
                current_request = self.current_queue.get(timeout=None)
                config_cdash.LOG.info('Retrieved the file: {}'.format(current_request))
            except Queue.Empty:
                config_cdash.LOG.error('Current Thread: Thread GET returned Empty value')
                current_request = None
                continue
            # Determining the next bitrates and adding to the prefetch list
            print "MPD_DICT before sleep"

            time.sleep(5)


            with open(config_cdash.MPD_DICT_JSON_FILE, 'rb') as infile:
                MPD_DICT = json.load(infile)

            print "MPD_DICT after sleep and loading"
            print MPD_DICT

            for url in MPD_DICT[current_request]['urls']:
                prefetch_request = url.split('/')[-1]
                config_cdash.LOG.info('Current Thread: {}, Prefetch Thread: {}'.format(current_request,prefetch_request))
                self.prefetch_queue.put(prefetch_request)
            else:
                config_cdash.LOG.info('No current request')


    def prefetch_function(self):

        while not self.stop.is_set():
            try:
                # Pre-fetching the files
                prefetch_request = self.prefetch_queue.get(timeout=None)
            except Queue.Empty:
                config_cdash.LOG.error('Could not read from the Pre-fetch queue')
                time.sleep(config_cdash.WAIT_TIME)
                continue
            config_cdash.LOG.info('Pre-fetching the segment: {}'.format(prefetch_request))
            #for i in range(0, config_cdash.MAX_THREADS + 1):
            t = threading.Thread(target=self.cache.get_file,args=(prefetch_request,))
            t.start()


        else:
            config_cdash.LOG.warning('Pre-fetch thread terminated')

    """
    def test():
        print check_content_server(" .m4s")

    if __name__ == "__main__":
        sys.exit(test())
    """