# Speech Corpus Downloader

Download and prepare common free speech corpora.

## Default Configuration
It converts all files to 16 kHz, mono, WAV files and stores them in CSV files (e.g. `train.csv`, `dev.csv`).
Examples shorter than 0.7 or longer than 17.0 seconds are removed.
TED-LIUM examples with labels with fewer than 5 words are removed, due to a subjective higher transcription 
error rate.

The generated corpus contains about 1275 hours of speech for training and takes up 144GiB of disk space.
Example of the generated output folder structure:
```terminal
speech-corpus
├── cache
├── commonvoicev2_train.csv
├── corpus
│   ├── cvv2
│   ├── LibriSpeech
│   ├── tatoeba_audio_eng
│   └── TEDLIUM_release2
├── corpus.json
├── dev.csv
├── librispeech_dev.csv
├── librispeech_test.csv
├── librispeech_train.csv
├── tatoeba_train.csv
├── tedlium_dev.csv
├── tedlium_test.csv
├── tedlium_train.csv
├── test.csv
└── train.csv
```

### Composition
* **train.csv**:
  * Common Voice v2, all validated files.
  * Libri Speech train set
  * Tatoeba
  * Tedlium v2 train set
* **dev.csv**:
  * Libri Speech dev set
* **test.csv**:
  * Libri Speech test set


## Supported Corpora
### Common Voice
* Website: https://voice.mozilla.org/en
* License: [CC-0](https://voice.mozilla.org/en/datasets)
* Supported versions:
    * [x] v1
    * [x] [v2](https://github.com/mozilla/CorporaCreator/blob/master/README.rst)
* **NOTE**: Please confirm Mozilla's terms and conditions before downloading Common Voice v2.


### Libri Speech
* Website: http://www.openslr.org/12/
* Paper: http://www.danielpovey.com/files/2015_icassp_librispeech.pdf
* License: CC BY 4.0
* By: Vassil Panayotov, Guoguo Chen, Daniel Povey and Sanjeev Khudanpur


### Tatoeba
* Website: https://tatoeba.org/eng/downloads
* License: Mixed


### TED-LIUM
TODO: Document
* Website: https://lium.univ-lemans.fr/ted-lium2/
* License: CC BY-NC-ND 3.0
* Supported versions:
    * [x] [release2](http://www.openslr.org/19/)
    * [ ] [release3](http://www.openslr.org/51/); [paper](https://arxiv.org/abs/1805.04699)


### TIMIT
* Website: https://catalog.ldc.upenn.edu/LDC93S1
* License: [LDC User Agreement for Non-Members](https://catalog.ldc.upenn.edu/license/ldc-non-members-agreement.pdf)
* Note: This is a special case since this is not a free corpus, therefore no download available.
    If you have a license, the corpus can be included:
    * Enable the `use_timit` flag in `generate.py`
    * Place the extracted timit data in the `corpus/timit/TIMIT/` directory of your destination folder.


## Statistics
```terminal
TODO
```

* **TODO**: Add word length distribution plots.

