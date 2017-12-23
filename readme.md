# Google Drive File Downloader
## By Simon Pugnet, 2017-12-23

## Introduction

Google Drive File Downloader is a simple Python module (gdrive\_dl.py) which allows a file to be downloaded directly from Google Drive given only a shareable link to that file.

For small files, the file is scanned for viruses by Google Drive and then downloaded.  For larger files, this virus scanning does not take place but a warning is given and the file is still downloaded.  It is important to make sure that all downloaded files are scanned for viruses in this case.


## Usage

The module can be used directly from the command line or as a Python module

### CLI usage

```
python gdrive_dl.py <url>
```

Replace <url> with the shareable link.

For full usage instructions, run:

```
python gdrive_dl.py -h
```

### Python module usage

    import gdrive_dl
    gdrive_dl.download_file('<url>', file_name='file.dat')

Replace <url> with the shareable link.  The `file\_name` argument is optional; if not set then the name of the file on Google Drive will be used.


## Requirements
This module was developed and tested using Python 3.6

A list of requirements is included in requirements.txt. To install all requirements, run:

```
pip install -r requirements.txt
```
