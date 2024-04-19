#!/usr/bin/env python3

"""
#########################################################################
# Title:         Declutarr - Hard Drive Space Declutter Script          #
# Author(s):     Dosk3n                                                 #
# URL:           https://github.com/Dosk3n/decluttarr                   #
# Description:   Declutter low space by removing unused media.          #
# --                                                                    #
#########################################################################
#                   GNU General Public License v3.0                     #
#########################################################################
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import configparser
from datetime import datetime, timedelta
import json


# Set working directory to the script's directory
script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_directory)

# Setup logger
log_filename = os.path.join(script_directory, 'decluttarr.log')
handler = RotatingFileHandler(log_filename, maxBytes=20*1024*1024, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger("decluttarr")
log.addHandler(handler)
log.setLevel(logging.INFO)

# Import custom API libraries after logging in case of issue with libraries
try:
    from TautulliApiHandler import TautulliApiHandler
    from SonarrApiCaller import SonarrApiCaller
except Exception as e:
    log.exception("An error occurred: %s", str(e))
    sys.exit(1)


##### DEFINE FUNCTIONS #####

def sonarr(SONARR_CONFIG, TAUTULLI_CONFIG):
    sonarr = SonarrApiCaller(SONARR_CONFIG['host'], SONARR_CONFIG['api_key'])
    tautulli = TautulliApiHandler(TAUTULLI_CONFIG['host'], TAUTULLI_CONFIG['api_key'])
    paths_to_process = triggered_paths(sonarr, SONARR_CONFIG)
    for path_to_process in paths_to_process:
        log.info(f"Decluttarring path {path_to_process['path']}.")
        recent_history = get_recent_history(tautulli, SONARR_CONFIG, path_to_process)


def triggered_paths(arr, conf):
    root_folders = arr.get_root_folders()
    log.info(f"Root folders loaded from API: {root_folders}")
    log.info(f"Checking for Low Space Triggers.")

    paths_to_process = []
    for folder in root_folders:
        folder_path = folder["path"]
        folder_free_space = int(folder["freeSpace"] / (1024 ** 3))
        log.info(f"Processing Root Folder {folder_path}.")

        log.info(f"Determining if path exists in config.")
        for path_info in conf['paths']:
            if folder_path == path_info.get('path'):

                if folder_path in conf['exemptions']:
                    log.info(f"Path {folder_path} found in exemption list. Skipping.")
                    break

                low_space_trigger = path_info.get('low_space_trigger')
                log.info(f"Path {folder_path} found in config paths - Free Space: {folder_free_space} GB - Trigger: {low_space_trigger} GB")

                if int(folder_free_space) < int(low_space_trigger):
                    log.info(f"Low space determined for path {folder_path}. Adding to process list.")
                    folder['days_older_than'] = path_info.get('days_older_than')
                    paths_to_process.append(folder)

                break
        else:
            log.info(f"Path {folder_path} not found in config paths.")
    
    log.info(f"Processing Paths Complete. Paths to Process: {paths_to_process}")
    return paths_to_process

def get_recent_history(tautulli, conf, path_to_process):
    days_to_subtract = int(path_to_process['days_older_than'])
    today = datetime.today()
    target_date = today - timedelta(days=days_to_subtract)
    date_x_days_prior_to_today = target_date.strftime('%Y-%m-%d')
    arr_type = conf.get('name', {})
    
    if arr_type == "sonarr":
        media_type = "episode"
    if arr_type == "radarr":
        media_type = "movie" # Confirm this

    log.info(f"Getting {media_type} history for the last {path_to_process['days_older_than']} days.")
    history = tautulli.get_history(length=500000, media_type="episode", after=date_x_days_prior_to_today)
    log.info(f"History Events: {len(history['response']['data']['data'])}")



    # Sonarr History - Find out whats recently been added so we dont return them in our data set

    # Sonarr get all series
    # series = s.get_series()
    # log.info(f"Number of Series: {len(series)}")
    # for s in series:
    #     log.info(f"id: {s['id']} - title: {s['title']} - sortTitle: {s['sortTitle']} - path: {s['path']} - rootFolderPath: {s['rootFolderPath']} - imdbId: {s['imdbId']} - tvdbId: {s['tvdbId']}")
        



    # t = TautulliApiHandler(TAUTULLI_CONFIG['host'], TAUTULLI_CONFIG['api_key'])
    
    # for event in history['response']['data']['data']:
    #     metadata = t.get_metadata(event['rating_key'])
    #     log.info(metadata['response']['data']['guids'])
    #     if not metadata:
    #         sys.exit(1) # Handle this better!
    #     log.info(f"Epoch: {event['date']} - Date: {datetime.fromtimestamp(event['date']).strftime('%Y-%m-%d')} - User: {event['user']} - Original Title: {event['original_title']} - parent_guids: {metadata['response']['data']['guids']} - Grandparent Title: {event['grandparent_title']} - grandparent_guids: {metadata['response']['data']['grandparent_guids']}")


try:
    log.info(f"Starting Decluttarr Script.")
    # Check if the config.ini file exists
    log.info(f"Loading Configs.")
    config_file_path = 'config.json'
    if os.path.isfile(config_file_path):
        # Load Configurations
        with open(config_file_path, 'r') as jsonfile:
            config = json.load(jsonfile)
        SONARR_CONFIG = config.get('Sonarr', {})
        TAUTULLI_CONFIG = config.get('Tautulli', {})
    else:
        log.error("Unable to load config.json. Make sure its correct, it exists or create it.")
        sys.exit(1)

    
    if os.environ.get('sonarr_eventtype') == "Test":
        log.info(f"Sonarr Triggered.")
        if SONARR_CONFIG['enabled']:
            sonarr(SONARR_CONFIG, TAUTULLI_CONFIG)
        else:
            log.info(f"Sonarr is not enabled in config.")
        sys.exit(0)
        
    elif os.environ.get('radarr_eventtype') == "Test":
        sys.exit(0)
    elif 'sonarr_eventtype' in os.environ:
        log.info("sonarr_eventtype was triggered.")
        sys.exit(0)
        # sourceFile = os.environ.get('sonarr_episodefile_sourcepath')
        # sourceFolder = os.environ.get('sonarr_episodefile_sourcefolder')
    else:
        log.error("Unable to determine requester. This must be either 'sonarr' or 'radarr'.")
        sys.exit(0)

except Exception as e:
    log.exception("An error occurred: %s", str(e))
    sys.exit(1)
