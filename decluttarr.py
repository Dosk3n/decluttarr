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
import os
import sys
import configparser
from datetime import datetime, timedelta

# Set working directory to the script's directory
script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_directory)

# Setup logger
log_filename = os.path.join(script_directory, 'decluttarr.log')
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
log = logging.getLogger("decluttarr")

# Import custom API libraries after logging in case of issue with libraries
try:
    from TautulliApiHandler import TautulliApiHandler
    from SonarrApiCaller import SonarrApiCaller
except Exception as e:
    log.exception("An error occurred: %s", str(e))
    sys.exit(1)

def sonarr():
    s = SonarrApiCaller(SONARR_HOST, SONARR_API_KEY)
    root_folders = s.get_root_folders()
    log.info(f"Root folders loaded from API: {root_folders}")
    for folder in root_folders:
        log.info(f'Path: {folder["path"]} - Free Space: {int(folder["freeSpace"] / (1024 ** 3))} GB')

    # Sonarr History - Find out whats recently been added so we dont return them in our data set

    # Sonarr get all series
    series = s.get_series()
    log.info(f"Number of Series: {len(series)}")
    # for s in series:
    #     log.info(f"id: {s['id']} - title: {s['title']} - sortTitle: {s['sortTitle']} - path: {s['path']} - rootFolderPath: {s['rootFolderPath']}")



    # # Tautull History
    days_to_subtract = int(SONARR_DAYS_OLDER_THAN)
    today = datetime.today()
    target_date = today - timedelta(days=days_to_subtract)
    x_days_prior_to_today = target_date.strftime('%Y-%m-%d')


    t = TautulliApiHandler(TAUTULLI_HOST, TAUTULLI_API_KEY)
    history = t.get_history(length=50000, media_type="episode", after=x_days_prior_to_today)
    log.info(f"History Events: {len(history['response']['data']['data'])}")
    # for event in history['response']['data']['data']:
    #     log.info(f"Epoch: {event['date']} - Date: {datetime.fromtimestamp(event['date']).strftime('%Y-%m-%d')} - User: {event['user']} - Original Title: {event['original_title']} - Grandparent Title: {event['grandparent_title']}")

try:
    # Check if the config.ini file exists
    config_file_path = 'config.ini'
    if os.path.isfile(config_file_path):
        # Load configuration from the file
        config = configparser.ConfigParser()
        config.read(config_file_path)

        SONARR_HOST = config.get('Sonarr', 'host')
        SONARR_API_KEY = config.get('Sonarr', 'api_key')
        SONARR_LOW_SPACE_TRIGGER = config.get('Sonarr', 'low_space_trigger')
        SONARR_DAYS_OLDER_THAN = config.get('Sonarr', 'days_older_than')
        log.info(f"Config loaded. SONARR_HOST: {SONARR_HOST}")

        TAUTULLI_HOST = config.get('Tautulli', 'host')
        TAUTULLI_API_KEY = config.get('Tautulli', 'api_key')
        log.info(f"Config loaded. TAUTULLI_HOST: {TAUTULLI_HOST}")
    else:
        # Use hardcoded default values if the config.ini file doesn't exist
        SONARR_HOST = 'host_here'
        SONARR_API_KEY = 'api_here'
        TAUTULLI_HOST = 'host_here'
        TAUTULLI_API_KEY = 'api_here'
        log.warning(f"Config file not found. Using default values. SONARR_HOST: {SONARR_HOST} - TAUTULLI_HOST: {TAUTULLI_HOST}")

    
    if os.environ.get('sonarr_eventtype') == "Test":
        sonarr()
        sys.exit(0)
    elif os.environ.get('radarr_eventtype') == "Test":
        sys.exit(0)
    else:
        log.error("Unable to determine requester. This must be either 'sonarr' or 'radarr'.")
        sys.exit(0)

except Exception as e:
    log.exception("An error occurred: %s", str(e))
    sys.exit(1)
