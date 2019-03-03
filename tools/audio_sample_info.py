"""Provides display options for audio files and their preprocessed features.

Note that the network does not use `librosa`_ anymore, because it has problems
with concurrent sample loading. This module has not been updated yet.

.. _librosa:
    https://librosa.github.io/librosa/index.html
"""

import os
# noinspection PyUnresolvedReferences
import random

import librosa
import numpy as np
import python_speech_features as psf
from librosa import display
from matplotlib import pyplot as plt
from matplotlib import rc
from scipy.io import wavfile

from config import DATA_DIR, WIN_STEP

WIN_LENGTH = 0.025

rc('font', **{'family': 'serif',
              'serif': ['DejaVu Sans'],
              'size': 12
              })
rc('text', usetex=True)

CORPUS_DIR = os.path.join(DATA_DIR, 'corpus')


def display_sample_info(file_path, label=''):
    """Generate various representations a given audio file.
    E.g. Mel, MFCC and power spectrogram's.

    Args:
        file_path (str): Path to the audio file.
        label (str): Optional label to display for the given audio file.

    Returns:
        Nothing.
    """

    if not os.path.isfile(file_path):
        raise ValueError('{} does not exist.'.format(file_path))

    # By default, all audio is mixed to mono and resampled to 22050 Hz at load time.
    y, sr = librosa.load(file_path, sr=None, mono=True)

    # At 16000 Hz, 512 samples ~= 32ms. At 16000 Hz, 200 samples = 12ms. 16 samples = 1ms @ 16kHz.
    hop_length = 200  # Number of samples between successive frames e.g. columns if a spectrogram.
    f_max = sr / 2.  # Maximum frequency (Nyquist rate).
    f_min = 64.  # Minimum frequency.
    n_fft = 1024  # Number of samples in a frame.
    n_mels = 80  # Number of Mel bins to generate.
    n_mfcc = 13  # Number of Mel cepstral coefficients to extract.
    win_length = 333  # Window length.

    # Create info string.
    num_samples = y.shape[0]
    duration = librosa.get_duration(y=y, sr=sr)
    info_str_format = 'Label: {}\nPath: {}\nDuration={:.3f}s with {:,d} Samples\n' \
                      'Sampling Rate={:,d} Hz\nMin, Max=[{:.2f}, {:.2f}]'
    info_str = info_str_format.format(label, file_path, duration, num_samples, sr,
                                      np.min(y), np.max(y))
    print(info_str)
    # Escape some LaTeX special characters
    info_str_tex = info_str.replace('_', '\\_')

    plt.figure(figsize=(10, 7))
    plt.subplot(3, 1, 1)
    display.waveplot(y, sr=sr)
    plt.title('Monophonic')

    # Plot waveforms.
    y_harm, y_perc = librosa.effects.hpss(y)
    plt.subplot(3, 1, 2)
    display.waveplot(y_harm, sr=sr, alpha=0.33)
    display.waveplot(y_perc, sr=sr, color='r', alpha=0.40)
    plt.title('Harmonic and Percussive')

    # Add file information.
    plt.subplot(3, 1, 3)
    plt.axis('off')
    plt.text(0.0, 1.0, info_str_tex, color='black', verticalalignment='top')
    plt.tight_layout()

    # Calculating MEL spectrogram and MFCC.
    db_pow = np.abs(
        librosa.stft(y=y, n_fft=n_fft, hop_length=hop_length, win_length=win_length)) ** 2

    s_mel = librosa.feature.melspectrogram(S=db_pow, sr=sr, hop_length=hop_length,
                                           fmax=f_max, fmin=f_min, n_mels=n_mels)

    s_mel = librosa.power_to_db(s_mel, ref=np.max)
    s_mfcc = librosa.feature.mfcc(S=s_mel, sr=sr, n_mfcc=n_mfcc)

    # STFT (Short-time Fourier Transform)
    # https://librosa.github.io/librosa/generated/librosa.core.stft.html
    plt.figure(figsize=(12, 10))
    db = librosa.amplitude_to_db(librosa.magphase(librosa.stft(y))[0], ref=np.max)
    plt.subplot(3, 2, 1)
    display.specshow(db, sr=sr, x_axis='time', y_axis='linear', hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Linear-frequency power spectrogram')

    plt.subplot(3, 2, 2)
    display.specshow(db, sr=sr, x_axis='time', y_axis='log', hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Log-frequency power spectrogram')

    plt.subplot(3, 2, 3)
    display.specshow(s_mfcc, sr=sr, x_axis='time', y_axis='linear', hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('MFCC spectrogram')

    # # CQT (Constant-T Transform)
    # # https://librosa.github.io/librosa/generated/librosa.core.cqt.html
    cqt = librosa.amplitude_to_db(librosa.magphase(librosa.cqt(y, sr=sr))[0], ref=np.max)
    # plt.subplot(3, 2, 3)
    # display.specshow(cqt, sr=sr, x_axis='time', y_axis='cqt_note', hop_length=hop_length)
    # plt.colorbar(format='%+2.0f dB')
    # plt.title('Constant-Q power spectrogram (note)')

    plt.subplot(3, 2, 4)
    display.specshow(cqt, sr=sr, x_axis='time', y_axis='cqt_hz', hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Constant-Q power spectrogram (Hz)')

    plt.subplot(3, 2, 5)
    display.specshow(db, sr=sr, x_axis='time', y_axis='log', hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Log power spectrogram')

    plt.subplot(3, 2, 6)
    display.specshow(s_mel, x_axis='time', y_axis='mel', hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel spectrogram')

    # TODO Import project used features (python_speech_features).
    # norm_features = 'none'
    # mfcc = load_sample(file_path, feature_type='mfcc', feature_normalization=norm_features)[0]
    # mfcc = np.swapaxes(mfcc, 0, 1)
    #
    # mel = load_sample(file_path, feature_type='mel', feature_normalization=norm_features)[0]
    # mel = np.swapaxes(mel, 0, 1)

    (__sr, __y) = wavfile.read(file_path)

    num_features = 26
    win_len = WIN_LENGTH
    win_step = WIN_STEP
    __mel = psf.logfbank(signal=__y, samplerate=__sr, winlen=win_len,
                         winstep=win_step, nfilt=num_features, nfft=n_fft,
                         lowfreq=f_min, highfreq=f_max, preemph=0.97)

    __mfcc = psf.mfcc(signal=__y, samplerate=__sr, winlen=win_len, winstep=win_step,
                      numcep=num_features // 2, nfilt=num_features, nfft=n_fft,
                      lowfreq=f_min, highfreq=f_max,
                      preemph=0.97, ceplifter=22, appendEnergy=False)

    __mfcc = __mfcc.astype(np.float32)
    __mel = __mel.astype(np.float32)
    __mfcc = np.swapaxes(__mfcc, 0, 1)
    __mel = np.swapaxes(__mel, 0, 1)

    plt.figure(figsize=(5.2, 1.6))
    display.waveplot(y, sr=sr)

    fig = plt.figure(figsize=(10, 4))
    plt.subplot(2, 1, 2)
    display.specshow(__mfcc, sr=__sr, x_axis='time', y_axis='mel', hop_length=win_step * __sr)
    # plt.set_cmap('magma')
    # plt.xticks(rotation=295)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.xlim(left=0)
    plt.ylim(0, 8000)
    plt.colorbar(format='%+2.0f')
    plt.title('MFCC', visible=False)

    plt.subplot(2, 1, 1)
    display.specshow(__mel, sr=__sr, x_axis='time', y_axis='mel', hop_length=win_step * __sr)
    # plt.set_cmap('magma')
    # plt.xticks(rotation=295)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.xlim(left=0)
    plt.ylim(0, 8000)
    plt.colorbar(format='%+2.0f', label='Power (dB)')
    plt.title('Mel Spectrogram', visible=False)

    plt.tight_layout()
    fig.savefig('/tmp/mel-mfcc-plot-we-did-it.pdf', bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    _test_txt_path = os.path.join(DATA_DIR, 'train.csv')

    # Display specific sample info's.
    with open(_test_txt_path, 'r') as f:
        _lines = f.readlines()
        # _line = random.sample(_lines, 1)[0]
        # _line = _lines[37748]       # "The cat is on the roof"
        _line = _lines[375]
        _wav_path, txt = _line.split(' ', 1)
        _wav_path = os.path.join(CORPUS_DIR, _wav_path)
        _txt = txt.strip()
        # display_sample_info(_wav_path, label=_txt)

    # I don't understand a word you just said
    i_dont_understand_path = '/home/marc/Downloads/idontunderstandawordyoujustsaid.wav'
    i_dont_understand_label = "I don't understand a word you just said."
    display_sample_info(i_dont_understand_path, label=i_dont_understand_label)
