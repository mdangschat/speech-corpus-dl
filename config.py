"""
Configuration file for dataset creation.
Also reference `generate_dataset.py`.
"""

import os
import re

from util.storage_helper import makedirs

# Audio config.
SAMPLING_RATE = 16000
# Minimum and maximum audio file length (in seconds).
MIN_EXAMPLE_LENGTH = 0.7
MAX_EXAMPLE_LENGTH = 17.0
# The step between successive windows in seconds.
WIN_STEP = 0.010

# Path to data directory, this must be an existing folder.
DATA_DIR = os.path.join(os.path.expanduser('~'), 'workspace/speech-corpus')
assert os.path.exists(DATA_DIR) and os.path.isdir(DATA_DIR) and os.access(DATA_DIR, os.W_OK), \
    'The target folder provided in `config.py` does not exist.'

CACHE_DIR = os.path.join(DATA_DIR, 'cache')
CORPUS_DIR = os.path.join(DATA_DIR, 'corpus')
makedirs([CACHE_DIR, CORPUS_DIR])

CSV_DELIMITER = ';'

# CSV field names. The field order is always the same as this list from top to bottom.
CSV_HEADER_PATH = 'path'
CSV_HEADER_LABEL = 'label'
CSV_HEADER_LENGTH = 'length'
CSV_FIELDNAMES = [CSV_HEADER_PATH, CSV_HEADER_LABEL, CSV_HEADER_LENGTH]

# (Whitelist) RegEX filter pattern for valid characters.
LABEL_WHITELIST_PATTERN = re.compile(r'[^a-z ]+')

# Path to `corpus.json` file, that contains information about the dataset.
JSON_PATH = os.path.join(DATA_DIR, 'corpus.json')


def sox_commandline(input_path, target_path):
    """
    Create the parametrized list of commands to convert some audio file into another format, using
    sox.
    See `man sox`.

    Args:
        input_path (str):
            Path to the audio file that should be converted. With file extension.

        target_path (str):
            Path to where the converted file should be stored. With file extension.
    Returns:
        List[str]: List containing the call parameters for `subprocess.call`.
    """

    return [
        'sox',
        '-V1',  # Verbosity set to only errors (default is 2).
        '--volume', '0.95',
        input_path,
        '--rate', str(SAMPLING_RATE),
        target_path,
        'remix', '1'  # Channels: Mono
    ]
