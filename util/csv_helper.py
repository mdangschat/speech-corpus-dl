"""
Helper methods to generate the CSV files.
"""

import csv
import os
import re

from config import CSV_HEADER_LABEL, CSV_HEADER_LENGTH, CSV_FIELDNAMES
from config import LABEL_WHITELIST_PATTERN, CSV_DIR, CSV_DELIMITER, WIN_STEP
from util.storage_helper import delete_file_if_exists
from util.matplotlib_helper import pyplot_display


def generate_csv(dataset_name, target, csv_data):
    """
    Generate CSV files containing the audio path and the corresponding sentence.
    Generated files are being stored at `CSV_TARGET_PATH`.
    Examples with labels consisting of one or two characters are omitted.

    Return additional data set information, see below.

    Args:
        dataset_name (str):
            Name of the dataset, e.g. 'libri_speech'.

        target (str):
            Target name, e.g. 'train', 'test', 'dev'

        csv_data (List[Dict]):
            List containing the csv content for the `<dataset_name>_<target>.csv` file.

    Returns:
        str: Path to the created CSV file.
    """

    target_csv_path = os.path.join(CSV_DIR, '{}_{}.csv'.format(dataset_name, target))
    print('Starting to generate: {}'.format(os.path.basename(target_csv_path)))

    # Remove illegal characters from labels.
    for csv_entry in csv_data:
        # Apply label whitelist filter.
        csv_entry[CSV_HEADER_LABEL] = re.sub(LABEL_WHITELIST_PATTERN,
                                             '',
                                             csv_entry[CSV_HEADER_LABEL].lower())
        # Remove double spaces.
        csv_entry[CSV_HEADER_LABEL] = csv_entry[CSV_HEADER_LABEL].strip().replace('  ', ' ')

    # Filter out labels that are only shorter than 2 characters.
    csv_data = list(filter(lambda x: len(x[CSV_HEADER_LABEL]) >= 2, csv_data))

    # Write list to CSV file.
    print('> Writing {} lines of {} files to {}'.format(len(csv_data), target, target_csv_path))
    # Delete the old file if it exists.
    delete_file_if_exists(target_csv_path)

    # Write data to the file.
    with open(target_csv_path, 'w', encoding='utf-8') as file_handle:
        writer = csv.DictWriter(file_handle, delimiter=CSV_DELIMITER, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()

        writer.writerows(csv_data)

    return target_csv_path


def merge_csv_files(csv_files, target):
    """
    Merge a list of CSV files into a single target CSV file.

    Args:
        csv_files (List[str]): List of paths to dataset CSV files.
        target (str): 'test', 'dev', 'train'

    Returns:
        Tuple[str, int]: Path to the created CSV file and the number of examples in it.
    """
    if target not in ['test', 'dev', 'train']:
        raise ValueError('Invalid target.')

    buffer = []

    # Read and merge files.
    for csv_file in csv_files:
        if not (os.path.exists(csv_file) and os.path.isfile(csv_file)):
            raise ValueError('File does not exist: ', csv_file)

        with open(csv_file, 'r', encoding='utf-8') as file_handle:
            reader = csv.DictReader(file_handle, delimiter=CSV_DELIMITER, fieldnames=CSV_FIELDNAMES)

            # Serialize reader data and remove header.
            lines = list(reader)[1:]

            # Add CSV data to buffer.
            buffer.extend(lines)

    # Write data to target file.
    target_file = os.path.join(CSV_DIR, '{}.csv'.format(target))
    with open(target_file, 'w', encoding='utf-8') as file_handle:
        writer = csv.DictWriter(file_handle, delimiter=CSV_DELIMITER, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()

        writer.writerows(buffer)

        print('Added {:,d} lines to: {}'.format(len(buffer), target_file))

    return target_file


def sort_by_seq_len(csv_path, max_length=17.0):
    """
    Sort a train.csv like file by it's audio files sequence length.
    Additionally outputs longer than `max_length` are being discarded from the given CSV file.
    Also it prints out optimal bucket sizes after computation.

    Args:
        csv_path (str):
            Path to the `train.csv`.

        max_length (float):
            Positive float. Maximum length in seconds for a feature vector to keep.
            Set to `0.` to keep everything.

    Returns:
        Nothing.
    """
    assert os.path.exists(csv_path) and os.path.isfile(csv_path)

    # Read train.csv file.
    with open(csv_path, 'r', encoding='utf-8') as file_handle:
        reader = csv.DictReader(file_handle, delimiter=CSV_DELIMITER, fieldnames=CSV_FIELDNAMES)

        # Read all lines into memory and remove CSV header.
        csv_data = [csv_entry for csv_entry in reader][1:]

    # Sort entries by sequence length.
    csv_data = sorted(csv_data, key=lambda x: float(x[CSV_HEADER_LENGTH]))

    # Remove samples longer than `max_length` points.
    if max_length > 0:
        number_of_entries = len(csv_data)
        csv_data = [d for d in csv_data if float(d[CSV_HEADER_LENGTH]) < max_length]
        print('Removed {:,d} examples because they are too long.'
              .format(number_of_entries - len(csv_data)))

    # Write CSV data back to file.
    delete_file_if_exists(csv_path)
    with open(csv_path, 'w', encoding='utf-8') as file_handle:
        writer = csv.DictWriter(file_handle, delimiter=CSV_DELIMITER, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()

        writer.writerows(csv_data)

    with open(csv_path, 'r', encoding='utf-8') as file_handle:
        print('Successfully sorted {} lines of {}'.format(len(file_handle.readlines()), csv_path))


def get_corpus_length(csv_path):
    """
    Count the number of data entries in CSV file.
    Sum the length fields of every entry from a given CSV file.
    The CSV file is assumed to contain a header.

    Args:
        csv_path (str): Path to CSV file.

    Returns:
        Tuple[int, float]: Number of data entries in CSV file and total length in seconds.
    """
    assert os.path.exists(csv_path) and os.path.isfile(csv_path)

    with open(csv_path, 'r', encoding='utf-8') as file_handle:
        reader = csv.DictReader(file_handle, delimiter=CSV_DELIMITER, fieldnames=CSV_FIELDNAMES)

        # Read all lines into memory and remove CSV header.
        csv_data = [csv_entry for csv_entry in reader][1:]

        total_length_seconds = sum(map(lambda x: float(x[CSV_HEADER_LENGTH]), csv_data))

        return len(csv_data), total_length_seconds


def get_bucket_boundaries(csv_path, num_buckets):
    """
    Generate a list of bucket boundaries, based on the example length in the CSV file.
    The boundaries are chose based on the distribution of example lengths, to allow each bucket
    to fill up at the same rate. This produces at max `num_buckets`.

    Args:
        csv_path (str): Path to the CSV file. E.g. '../data/train.csv'.
        num_buckets (int): The maximum amount of buckets to create.

    Returns:
        List[int]: List containing bucket boundaries.
    """
    assert os.path.exists(csv_path) and os.path.isfile(csv_path)

    with open(csv_path, 'r', encoding='utf-8') as file_handle:
        reader = csv.DictReader(file_handle, delimiter=CSV_DELIMITER, fieldnames=CSV_FIELDNAMES)
        csv_data = [csv_entry for csv_entry in reader][1:]

        # Calculate optimal bucket sizes.
        lengths = [int(float(d[CSV_HEADER_LENGTH]) / WIN_STEP) for d in csv_data]
        step = len(lengths) // num_buckets

        buckets = set()
        for i in range(step, len(lengths), step):
            buckets.add(lengths[i])
        buckets = list(buckets)
        buckets.sort()

        return buckets


@pyplot_display
def __plot_sequence_lengths(plt, lengths):
    # Plot histogram of feature vector length distribution.
    fig = plt.figure()
    plt.hist(lengths, bins=50, facecolor='green', alpha=0.75, edgecolor='black', linewidth=0.9)
    plt.title('Sequence Length\'s Histogram')
    plt.ylabel('Count')
    plt.xlabel('Length')
    plt.grid(True)

    return fig


if __name__ == '__main__':
    # Path to `train.csv` file.
    __CSV_PATH = os.path.join(CSV_DIR, 'train.csv')

    # Display dataset stats.
    sort_by_seq_len(__CSV_PATH)
