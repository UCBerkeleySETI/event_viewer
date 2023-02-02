# event_viewer

This is a web-based image viewer for quickly categorizing candidate signals into real or RFI. 

It is a tiny [flask](http://flask.pocoo.org/) app, built with [bootstrap](http://getbootstrap.com/),
which will display images and their meta information from a table with pagination. It is based on [ImageViewer](https://github.com/smoh/imageviewer) by @smoh.


```
git clone https://github.com/ucberkeleyseti/event_viewer
cd event_viewer
conda env create    # will create viewer conda environment specified in environment.yml
source activate viewer
python app.py
```

and point your browser to `localhost:8001`.

This will show images and their accompanying metadata

![](screenshot.jpg)

Configure static file paths in `app.py` and modify templates in `templates/`
according to your needs. [Flask](http://flask.pocoo.org/) uses the [jinja](http://jinja.pocoo.org/) template engine.


### Overview

The event viewer is currently setup to read data from HDF5 files, and has separate directories for S-band and L-band data. You can use it to assign a 'HitCategory' to each event with the following key presses: 'H' - Hits in off, 'R' - Requires followup, 'P' - Plotting issue, or 'I' - Interesting but not ET. Once you press a key it will load the next hit.

Databases and images are located in `static`:

```
h = h5py.File('static/lband2019/lband2019_events.h5')
h.keys()
>> <KeysViewHDF5 ['DriftBW', 'DriftRateMax', 'DriftRates', 'FileID', 'FreqMid', 'Freqs', 'HitCategory', 'ID', 'Nevent', 'PngFile', 'SNR', 'Source']>
```

Each dataset within the HDF5 file has the same length and can be considered a column from a table, where each row corresponds to an event (i.e. a group of related hits). The columns are:

* ID - unique integer ID
* Source - Name of source H
* FileID - Filterbank file name
* Nevent - Number of events within the file
* DriftRateMax - Maximum drift rate
* DriftRates - Array of drift rates within the event group
* DriftBW - Don't really remember what this is
* FreqMid - Middle frequency of all hits
* Freqs - Array of frequencies for each hit
* PngFile - Name of PNG image file that corresponds to the event
* SNR - Signal to noise ratio reported by turobseti
* HitCategory - one of 'Hits in off', 'Requires followup', 'Plotting issue', or 'Interesting but not ET'.



