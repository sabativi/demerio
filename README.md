# Demerio

This is the main repository for Demerio app. To know what Demerio is about, visit [landing page](http://www.demerio.com).

This was a startup project that I had been doing with Luc Millet and Frederic Martin for two years.

This code is our last MVP, around two months development project. We wanted to go fast, so it is not a concentration of best practices. However, there are tests, some docs, and a basic architecture that splits logic.

You can find here, the alpha version that we achieved to build.

For more informations on what's remaining to be done, look at [TODO.md](./TODO.md) file.

Basically, the app listen to a local directory for changes on its files, when a change is detected, it will split the files into three pieces such that any 2 of which can reconstruct the original file.

Then pieces are sent to different clouds providers, currently three are supported : Dropbox, Box and Google Drive.

## Dependencies

The app depends on Qt5 please see [install pyQt](./install_pyqt.md) file to know how to install pyQt5 as it is not avaiable in `Pypi`.

I have used python 2.7 since all libraries are not yet python 3 ready.

To install other dependencies use :

```
pip install -r requirements.txt [--upgrade|-U]
```

It depends on several others modules, you need to add the path to the project into your PYTHONPATH variable.


## Launch

To launch the app use :
```
python main.py
```

To do so you need to have the secret file that contains the secret keys to the app.

```
export DROPBOX_SECRET=""
export GOOGLE_DRIVE_SECRET=""
export BOX_SECRET=""
## For tests only
export DRIVE_PASSWD=""
export DROPBOX_PASSWD=""
export BOX_PASSWD=""
```

## Basic architecture.

### Conductor module

The main logic of datalords is in the DemerioHandler class. It acts as a conductor for all others modules.

### Daemon module for Demerio

This module contains the daemon for demerio.

Is is responsible for detecting changes on files.

This module mainly used [watchdog](https://github.com/gorakhargosh/watchdog) library.


### Mapping module for Demerio

This module contains the map to track informations between local storage and clouds.

The map was a simple python ConfigFile.

### Split module for Demerio

This module contains the split and rebuild functions base on [zfec](https://pypi.python.org/pypi/zfec) library.

### Sync module for Demerio

This module contains the sync part ( transfer to the clouds ) of demerio app. It is basically a wrapper of clouds APIs.

### Utils module for Demerio

I put here everything that is in common between all demerio modules.
