## Demerio

This is the main repository for Demerio app.

The app depends on Qt5 please see [install pyQt](./install_pyqt.md) file to know how to install pyQt5 as it is not avaiable in `Pypi`.

To install other dependencies use :

```
pip install -r requirements.txt [--upgrade|-U]
```

It depends on several others modules, you need to add the path to the project into your PYTHONPATH variable.

To launch the app use :
```
python demerio_gui/main.py
```

To do so you need to have the secret file that contains the secret keys to the app. Please ask Victor if you are in this case.

## Daemon module for Demerio

This module contains the daemon for demerio.
Is is responsible of detecting change on file system and treating them.

The main logic of datalords is in the DatalordsHandler class.

## Mapping module for Demerio

This module contains the map to track informations between local storage and clouds.

## Split module for Demerio

This module contains the split and rebuild functions.

## Sync module for Demerio

This module contains the sync part ( transfer to the clouds ) of demerio app.

## Utils module for Demerio

I put here everything that is in common between all demerio modules.
