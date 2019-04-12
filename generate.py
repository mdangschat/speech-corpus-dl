"""Generate `train.csv`, `dev.csv`, and `test.csv` for the `LibriSpeech`_, `TEDLIUMv2`_, `TIMIT`_,
`TATOEBA`_ and `Common Voice`_ (v1 & v2) corpora.

The selected parts of various corpora are merged into combined files at the end.

Downloading all supported archives requires approximately 80GB of free disk space.
The extracted corpus requires an additional ~125GB of free disk space.

Generated CSV data format:
    CSV Header: `path;label;length in seconds`
    Example: `path/to/sample.wav;transcription of the sample wave file;1.23`

    The transcription is in lower case letters a-z with every word separated
    by a <space>. Punctuation is removed by default.

.. _COMMON_VOICE:
    https://voice.mozilla.org/en

.. _LibriSpeech:
    http://openslr.org/12

.. _TATOEBA:
    https://tatoeba.org/eng/downloads

.. _TEDLIUMv2:
    http://openslr.org/19

.. _TIMIT:
    https://catalog.ldc.upenn.edu/LDC93S1
"""

import json

from config import JSON_PATH
# from downloader.common_voice_v1 import cv_loader
from downloader.common_voice_v2 import cv_loader
from downloader.libri_speech import libri_loader
from downloader.tatoeba import tatoeba_loader
from downloader.tedlium_v2 import tedlium_loader
from downloader.timit import timit_loader
from util.csv_helper import sort_by_seq_len, get_corpus_length, merge_csv_files


def generate_dataset(keep_archives=True, use_timit=False):
    """Download and pre-process the corpus.

    Args:
        keep_archives (bool): Cache downloaded archive files?
        use_timit (bool): Include the TIMIT corpus? If `True` it needs to be placed in the
            `./data/corpus/TIMIT/` directory by hand.

    Returns:
        Nothing.
    """
    # Common Voice v1
    # cv_train, cv_test, cv_dev = cv_loader(keep_archives)

    # Common Voice v2
    cv2_train = cv_loader(keep_archives)

    # Libri Speech ASR
    ls_train, ls_test, ls_dev = libri_loader(keep_archives)

    # Tatoeba
    tatoeba_train = tatoeba_loader(keep_archives)

    # TEDLIUM v2
    ted_train, ted_test, ted_dev = tedlium_loader(keep_archives)

    # TIMIT
    if use_timit:
        timit_train, timit_test = timit_loader()
    else:
        timit_train = None

    # Assemble and merge CSV files:
    # Train
    train_csv = merge_csv_files(
        [cv2_train, ls_train, tatoeba_train, ted_train, timit_train],
        'train'
    )

    # Test
    test_csv = merge_csv_files(
        [ls_test],
        'test'
    )

    # Dev
    dev_csv = merge_csv_files(
        [ls_dev],
        'dev'
    )

    # Sort train.csv file (SortaGrad).
    sort_by_seq_len(train_csv)

    # Determine number of data entries and length in seconds per corpus.
    train_len, train_total_length_seconds = get_corpus_length(train_csv)
    test_len, _ = get_corpus_length(test_csv)
    dev_len, _ = get_corpus_length(dev_csv)

    # Write corpus metadata to JSON.
    store_corpus_json(train_len, test_len, dev_len, train_total_length_seconds)


def store_corpus_json(train_size, test_size, dev_size, train_length):
    """Store corpus metadata in `/python/data/corpus.json`.

    Args:
        train_size (int): Number of training examples.
        test_size (int): Number of test examples.
        dev_size (int): Number of dev/validation examples.
        train_length (float): Total length of the training dataset in seconds.

    Returns:
        Nothing.
    """
    with open(JSON_PATH, 'w', encoding='utf-8') as file_handle:
        data = {
            'train_size': train_size,
            'test_size': test_size,
            'dev_size': dev_size,
            'train_length': train_length
        }
        json.dump(data, file_handle, indent=2)


# Generate data.
if __name__ == '__main__':
    # TODO: This needs a terminal config menu and notes about the corpora's licenses.
    print('Starting to generate corpus.')

    generate_dataset(keep_archives=True, use_timit=False)

    print('Done. Please verify that "data/cache" contains only data that you want to keep.')
