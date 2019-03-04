# [WiP] Speech Corpus Downloader

Download and prepare common free speech corpora.
It converts all files to 16 kHz, mono, WAV files and stores them in CSV files (e.g. `train.csv`, `dev.csv`).

## Supported Corpora
### Common Voice
* Website: https://voice.mozilla.org/en
* License: [CC-0](https://voice.mozilla.org/en/datasets)
* Supported versions:
    * [x] v1
    * [ ] [https://github.com/mozilla/CorporaCreator/blob/master/README.rst](v2)
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
    * [x] [http://www.openslr.org/19/](release2)
    * [ ] [http://www.openslr.org/51/](release3); [https://arxiv.org/abs/1805.04699](paper)


### TIMIT
* Website: https://catalog.ldc.upenn.edu/LDC93S1
* License: [https://catalog.ldc.upenn.edu/license/ldc-non-members-agreement.pdf](LDC User Agreement for Non-Members)
* Note: This is a special case since this is not a free corpus, therefore no download available.
    If you have a license, the corpus can be included:
    * Enable the `use_timit` flag in `generate.py`
    * Place the extracted timit data in the `corpus/timit/TIMIT/` directory of your destination folder.
