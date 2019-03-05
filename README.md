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
$ ipython tools/wav_lengths.py 
Reading audio samples: 100%|██████████████████████████████████████████████████████████████| 897948/897948 [35:38<00:00, 419.93samples/s]
Total sample length=4592557.368s (~1275h) of workspace/speech-corpus/train.csv.
Mean sample length=81832 (5.115)s.
Plot saved to: /tmp/_plot_wav_lengths.png
```
![Example length distribution plot](images/train_plot_wav_lengths.png)

```terminal
$ ipython tools/word_counts.py 
Calculating statistics for workspace/speech-corpus/train.csv
Word based statistics:
	total_words = 11,716,026
	number_unique_words = 82,352
	mean_sentence_length = 13.05 words
	min_sentence_length = 1 words
	max_sentence_length = 84 words
	Most common words:  [('the', 649751), ('to', 347617), ('and', 296845), ('a', 279516), ('of', 271555), ('i', 220023), ('you', 181157), ('in', 174778), ('that', 162348), ('it', 139181)]
	27344 words occurred only 1 time; 37,415 words occurred only 2 times; 49,962 words occurred only 5 times; 57,979 words occurred only 10 times.

Character based statistics:
	total_characters = 60,402,553
	mean_label_length = 67.27 characters
	min_label_length = 2 characters
	max_label_length = 422 characters
	Most common characters: [(' ', 10818079), ('e', 6112206), ('t', 4864057), ('o', 4006837), ('a', 3917617), ('i', 3437314), ('n', 3319309), ('s', 3051207), ('h', 3000228), ('r', 2703305), ('d', 2059374), ('l', 1976372), ('u', 1444798), ('m', 1347476), ('w', 1231782), ('c', 1175514), ('y', 1145448), ('g', 1045719), ('f', 979325), ('p', 838584), ('b', 756279), ('v', 486572), ('k', 465861), ('j', 73971), ('x', 73567), ('q', 39701), ('z', 32051)]
	Most common characters: [' ', 'e', 't', 'o', 'a', 'i', 'n', 's', 'h', 'r', 'd', 'l', 'u', 'm', 'w', 'c', 'y', 'g', 'f', 'p', 'b', 'v', 'k', 'j', 'x', 'q', 'z']
```

