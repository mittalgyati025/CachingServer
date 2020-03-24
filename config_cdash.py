import os
import time
import logging
from time import strftime

# CACHE Server Parameters
HOSTNAME = 'localhost'
PORT_NUMBER = 8006
TCP_PORT_NUMBER = 8011
MPD_SOURCE_LIST = ['VIDEO_0065.mpd']
CWD = os.getcwd()
MAX_THREADS = 4
MPD_DICT_JSON_FILE = os.path.join(CWD, 'MPD_DICT.json')
MPD_FOLDER = os.path.join(CWD, 'MPD_FILES')
if not os.path.exists(MPD_FOLDER):
    os.makedirs(MPD_FOLDER)
# Parameters for the priority cache
FETCH_CODE = 'FETCH'
PREFETCH_CODE = 'PRE-FETCH'
CONTENT_SERVER = 'https://storage.googleapis.com/vr-paradrop/fusion-test/dash-test/'
VIDEO_FOLDER = os.path.join(CWD, 'Videos')
VIDEO_FILE_EXTENTION = 'm4s'
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
else:
    print "Clearing the Cache"
    import glob
    video_match = os.path.join(VIDEO_FOLDER, "*")
    video_list = glob.glob(video_match)
    for video_file in video_list:
        os.remove(video_file)

CACHE_LIMIT = 100
PREFETCH_LIMIT = 100
PREFETCH_SCHEME = 'BASIC'
CURRENT_THREAD = True
PREFETCH_THREAD = True


# Cache Logging
LOG_NAME = 'cache_LOG'
# LOG level to be set by the configure_log file
LOG_LEVEL = logging.INFO

# Initialize the Log Folders
LOG_FOLDER = os.path.join(CWD, "Cache_LOGS")
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
LOG_FILENAME = os.path.join(LOG_FOLDER, strftime('cache_n_dash_LOG_{}_%Y-%m-%d.%H_%M_%S.log'.format(PREFETCH_SCHEME)))
LOG_FILE_HANDLE = None
# To be set by configure_log_file.py
LOG = None

# TODO: Maybe put the following in a JSON?
VIDEO_CACHE_CONTENT = { 'init-stream1.m4s', 'init-stream0.m4s', 'chunk-stream0-00001.m4s', 'chunk-stream0-00002.m4s', 'chunk-stream0-00003.m4s', 'chunk-stream0-00004.m4s','chunk-stream0-00005.m4s', 'chunk-stream0-00006.m4s', 'chunk-stream0-00007.m4s', 'chunk-stream1-00001.m4s', 'chunk-stream1-00002.m4s' ,'chunk-stream1-00003.m4s', 'chunk-stream1-00004.m4s', 'chunk-stream1-00005.m4s', 'chunk-stream1-00006.m4s', 'chunk-stream1-00007.m4s'

}

# Number of segments for moving average
BASIC_DELTA_COUNT = 5
MAX_BUFFER_SIZE = 60
INITIAL_BUFFERING_COUNT = 2
