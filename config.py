"""
Configuration file for dataset creation.
Also reference `generate_dataset.py`.
"""

import os
import re

SAMPLING_RATE = 16000

# Path to git root.
GIT_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
# Where to generate the CSV files, e.g. /home/user/../<project_name>/data/<target>.csv
DATA_DIR = CSV_DIR = os.path.join(GIT_ROOT, 'data')

CACHE_DIR = os.path.join(DATA_DIR, 'cache')
CORPUS_DIR = os.path.join(DATA_DIR, 'corpus')

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
