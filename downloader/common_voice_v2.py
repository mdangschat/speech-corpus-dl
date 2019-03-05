"""
Load the Mozilla `Common Voice`_ (v2) dataset.

This only provides a train set at the moment, since the official train.tsv, etc. files do not
contain enough examples.

Corpus information: https://github.com/mozilla/CorporaCreator/blob/master/README.rst

.. Common Voice:
    https://voice.mozilla.org/en
"""

import csv
import os
import subprocess
import sys
from functools import partial
from multiprocessing import Pool, Lock, cpu_count

from scipy.io import wavfile
from tqdm import tqdm

from config import CACHE_DIR, CORPUS_DIR, sox_commandline
from config import CSV_HEADER_PATH, CSV_HEADER_LABEL, CSV_HEADER_LENGTH
from config import MIN_EXAMPLE_LENGTH, MAX_EXAMPLE_LENGTH
from util import download
from util.csv_helper import generate_csv
from util.storage_helper import delete_file_if_exists

# Path to the Mozilla Common Voice dataset.
__URL = 'https://voice-prod-bundler-ee1969a6ce8178826482b88e843c335139bd3fb4.s3.amazonaws.com/' \
        'cv-corpus-1/en.tar.gz'
__MD5 = 'a639b0e22b969d76abe1c40beb0d3439'
__NAME = 'commonvoicev2'
__FOLDER_NAME = 'cvv2'
__SOURCE_PATH = os.path.join(CACHE_DIR, __FOLDER_NAME)
__TARGET_PATH = os.path.realpath(os.path.join(CORPUS_DIR, __FOLDER_NAME))

# Define valid accents.
__VALID_ACCENTS = ['us',
                   'england',
                   'canada',
                   'australia',
                   'wales',
                   'newzealand',
                   'ireland',
                   'scotland',
                   'wales',
                   '']


def cv_loader(keep_archive):
    """
    Download, extract and convert the Common Voice archive.
    Then build all possible CSV files (e.g. `<dataset_name>_train.csv`, `<dataset_name>_test.csv`).

    Uses only the valid dataset, additional constraints are:
    * Downvotes must be at maximum 1/4 of upvotes.
    * Valid accents are: 'us', 'england', 'canada', 'australia'.
    * Accepting samples with only 1 upvote at the moment.

    Args:
        keep_archive (bool): Keep or delete the downloaded archive afterwards.

    Returns:
        str: String containing the created CSV file path.
    """

    # Download and extract the dataset if necessary.
    download.maybe_download(__URL, md5=__MD5, cache_archive=keep_archive, target_subdir='cvv2')
    if not os.path.isdir(__SOURCE_PATH):
        raise ValueError('"{}" is not a directory.'.format(__SOURCE_PATH))

    tsv_path = os.path.join(CACHE_DIR, 'cvv2', 'validated.tsv')
    assert os.path.exists(tsv_path), '.TSV file not found: {}'.format(tsv_path)

    # Generate the path and label for the `<target>.csv` file.
    output = __common_voice_loader(tsv_path)
    # Generate the `<target>.csv` file.
    csv_path = generate_csv(__NAME, 'train', output)

    # Cleanup extracted folder.
    download.cleanup_cache(__FOLDER_NAME)

    return csv_path


def __common_voice_loader(tsv_path):
    """
    Build the data that can be written to the desired CSV file.

    Uses only the valid datasets, additional constraints are:
    * Downvotes must be at maximum 1/4 of upvotes.
    * Valid accents are: 'us', 'england', 'canada', 'australia'.
    * Accepting samples with only 1 upvote at the moment.

    Args:
        tsv_path (str): A string containing a TSV file path, e.g. `'.../cache/cvv2/train.tsv'`.

    Returns:
        List[Dict]: List containing the CSV dictionaries that can be written to the CSV file.
    """

    output = []

    # Open .csv file.
    with open(tsv_path, 'r', encoding='utf-8') as tsv_file:
        csv_reader = csv.reader(tsv_file, delimiter='\t')
        csv_lines = list(csv_reader)
        # print('csv_header:', csv_lines[0], '<EOL>')
        # client_id: str, path: str, sentence: str, up_votes: int, down_votes: int,
        # age: <str>, gender: <str>, accent: <str>

        # First line contains header.
        csv_lines = csv_lines[1:]

        lock = Lock()
        with Pool(processes=cpu_count()) as pool:
            target_directory = os.path.join(__TARGET_PATH,
                                            os.path.splitext(os.path.basename(tsv_path))[0])

            # Create target directory if necessary.
            if not os.path.exists(target_directory):
                os.makedirs(target_directory)

            for result in tqdm(pool.imap_unordered(partial(__common_voice_loader_helper,
                                                           target_dir=target_directory), csv_lines,
                                                   chunksize=1),
                               desc='Converting Common Voice MP3 to WAV', total=len(csv_lines),
                               file=sys.stdout, unit='files', dynamic_ncols=True):
                if result is not None:
                    lock.acquire()
                    output.append(result)
                    lock.release()

    return output


def __common_voice_loader_helper(csv_line, target_dir):
    # Helper method for thread pool.
    audio_file_hash = csv_line[1]
    label = csv_line[2].strip().replace('  ', ' ').replace('"', '')
    upvotes = int(csv_line[3])
    downvotes = int(csv_line[4])
    # age = line[5]
    # gender = line[6]
    accent = csv_line[7]

    # Source and target paths.
    mp3_path = os.path.join(__SOURCE_PATH, 'clips', '{}.mp3'.format(audio_file_hash))
    wav_path = os.path.join(target_dir, '{}.wav'.format(audio_file_hash))

    # Enforce min label length.
    if len(label) < 3:
        # print('WARN: Label "{}" to short: {}'.format(label, mp3_path))
        return None

    # Check upvotes vs. downvotes relation.
    if downvotes >= 1 and upvotes / downvotes > 1 / 4:
        # print('WARN: Too many down votes ({}/{}): {}'.format(upvotes, downvotes, mp3_path))
        return None

    # Check if speaker accent is valid.
    if accent not in __VALID_ACCENTS:
        # print('WARN: Invalid accent "{}": {}'.format(accent, mp3_path))
        return None

    # Make sure the file exists and is not empty.
    if not os.path.exists(mp3_path):
        print('WARN: MP3 file not found: {}'.format(mp3_path))
        return None
    if os.path.getsize(mp3_path) < 1024:
        print('WARN: MP3 file appears to be empty: {}'.format(mp3_path))
        return None

    delete_file_if_exists(wav_path)
    # Convert MP3 to WAV, reduce volume to 0.95, downsample to 16kHz and mono sound.
    subprocess.call(sox_commandline(mp3_path, wav_path))
    assert os.path.isfile(wav_path), 'Created WAV file not found: {}'.format(wav_path)

    # Validate that the example length is within boundaries.
    (sampling_rate, audio_data) = wavfile.read(wav_path)
    length_sec = len(audio_data) / sampling_rate
    if not MIN_EXAMPLE_LENGTH <= length_sec <= MAX_EXAMPLE_LENGTH:
        return None

    # Add dataset relative to dataset path, label to CSV file buffer.
    wav_path = os.path.relpath(wav_path, CORPUS_DIR)

    return {
        CSV_HEADER_PATH: wav_path,
        CSV_HEADER_LABEL: label,
        CSV_HEADER_LENGTH: length_sec
    }


# Test download script.
if __name__ == '__main__':
    print('Common Voice csv_paths: ', cv_loader(True))
    print('\nDone.')
