"""
Print out a length distribution for used WAV files.

TODO: This module is not updated to the current TXT-to-CSV changes.
"""

import os
import pickle
import sys
from multiprocessing import Pool, Lock, cpu_count

import numpy as np
from scipy.io import wavfile
from tqdm import tqdm

from config import MIN_EXAMPLE_LENGTH, MAX_EXAMPLE_LENGTH, CORPUS_DIR
from util.matplotlib_helper import pyplot_display


def calculate_dataset_stats(txt_path, show_buckets=0):
    """Gather mean and standard deviation values. Averaged for every file in the
    training txt data file.

    Args:
        txt_path (str): Path to the `train.txt`.
        show_buckets (int): Display additional bucketing markers if `show_buckets > 0`.

    Returns:
        Nothing.
    """
    # Check if results are buffered.
    tmp_path = '/tmp/sample_length_dump_{}.p'.format(os.path.split(txt_path)[1])
    if not (os.path.exists(tmp_path) and os.path.isfile(tmp_path)):
        sample_lengths = []  # Output buffer.
        sample_lengths_sec = []  # Output buffer.

        # Read train.txt file.
        with open(txt_path, 'r') as file_handle:
            lines = file_handle.readlines()

            # Setup threadpool.
            lock = Lock()
            with Pool(processes=cpu_count()) as pool:
                for length, length_sec in tqdm(
                        pool.imap_unordered(_stat_calculator, lines, chunksize=4),
                        desc='Reading audio samples', total=len(lines), file=sys.stdout,
                        unit='samples', dynamic_ncols=True):
                    lock.acquire()
                    sample_lengths.append(length)
                    sample_lengths_sec.append(length_sec)
                    lock.release()

            pickle.dump(sample_lengths_sec, open(tmp_path, 'wb'))
            print('Stored data to {}'.format(tmp_path))

            total_len = np.sum(sample_lengths_sec)
            print('Total sample length={:.3f}s (~{}h) of {}.'
                  .format(total_len, int(total_len / 60 / 60), txt_path))
            print('Mean sample length={:.0f} ({:.3f})s.'
                  .format(np.mean(sample_lengths), np.mean(sample_lengths_sec)))

    else:
        print('Loading stored dump from {}'.format(tmp_path))
        sample_lengths_sec = pickle.load(open(tmp_path, 'rb'))

    # Add optional bucket markers.
    buckets = _bucketing(show_buckets, sample_lengths_sec)

    # Plot histogram of WAV length distribution.
    _plot_wav_lengths(sample_lengths_sec, buckets=buckets)

    print('Done.')


def _bucketing(number_buckets, sample_lengths):
    if number_buckets <= 0:
        return None

    number_examples = len(sample_lengths)
    step = number_examples // number_buckets
    sorted_lengths = sorted(sample_lengths)
    buckets = [sorted_lengths[i] for i in range(0, len(sorted_lengths), step)]
    # Make sure the last bucket aligns with the highest value.
    if buckets[-1] != sorted_lengths[-1]:
        buckets[-1] = sorted_lengths[-1]

    return buckets


def _stat_calculator(line):
    # Python multiprocessing helper method.
    wav_path, _ = line.split(' ', 1)
    wav_path = os.path.join(CORPUS_DIR, wav_path)

    if not os.path.isfile(wav_path):
        raise ValueError('"{}" does not exist.'.format(wav_path))

    # Load the audio files sample rate and data.
    (sampling_rate, audio_data) = wavfile.read(wav_path)

    length = len(audio_data)
    length_sec = length / sampling_rate

    if length_sec < MIN_EXAMPLE_LENGTH:
        print('WARN: Too short example found: ', line, length_sec)

    if length_sec > MAX_EXAMPLE_LENGTH:
        print('WARN: Overlong example found: ', line, length_sec)

    return length, length_sec


@pyplot_display
def _plot_wav_lengths(plt, sample_lengths_sec, buckets=None):
    # Create figure.
    fig = plt.figure(figsize=(7.0, 2.60))
    plt.hist(sample_lengths_sec, bins=75, facecolor='green', alpha=0.75, histtype='bar')

    if buckets is not None:
        # plt.hist(buckets, bins=len(buckets), facecolor='red', alpha=0.75, stacked=False,
        #          histtype='bar', edgecolor='black', linewidth=0.6)
        for bucket in buckets:
            plt.axvline(bucket, color='red', linewidth=0.5, linestyle='-')

    # Y axis ticks
    # plt.yticks(range(0, 60000, 20000))
    # plt.yscale('log')
    ax = plt.gca()
    import matplotlib
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), '5'))
    )

    plt.title('Sample Length in Seconds', visible=False)
    plt.ylabel('Count', visible=True)
    plt.xlabel('Length (s)', visible=True)
    display_grid = buckets is None
    plt.grid(b=True, which='major', axis='both', linestyle='dashed', linewidth=0.7, aa=False,
             visible=display_grid)
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)

    # Finish plot by tightening everything up.
    plt.tight_layout()
    # This line messes up the pyCharm preview image.
    fig.savefig('/tmp/length-distribution-dev.pdf', bbox_inches='tight')
    # fig.savefig('/tmp/bucketing-example.pdf', bbox_inches='tight')

    return fig


if __name__ == '__main__':
    # Path to `train.csv` test
    __CSV_PATH = os.path.join('./data', 'train.csv')

    # Display dataset stats.
    calculate_dataset_stats(__CSV_PATH, show_buckets=0)
