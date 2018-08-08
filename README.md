# romfilter
A utility for filtering one's MAME ROM collection

# Getting Started
This project is extremely early in its development.  Nonetheless, if you'd like to try it out, you'll need:
* Python 3.6
* An extracted copy of the "full driver information in XML format" file from http://mamedev.org/release.html
** Be sure that the version you've downloaded matches the version of your ROM set!
* Optionally, an extracted copy of catver.ini from http://www.progettosnaps.net/catver/
* A ROM set that you want to filter
* Enough spare disk space to have the copy of all of your ROMs
** This is because this utility is non-destructive.  We wouldn't want to accidentally nuke your collection!

# Known issues
* If a ROM relies on another ROM to run (e.g. all NeoGeo games rely on having `neogeo.zip` in the roms path), this
relationship is not currently picked up, so you'll need to manually copy them over for now.
* While parsing out the XML and category files, the UI will hang.  Be patient, and it'll come back eventually.

# Development
## Building the standalone Windows executable
In a Python 3.6 virtual environment where requirements.txt has already been installed:

```
cd romfilter
scripts\build.bat
```

Once complete, `romfilter.exe` will be avilable in the `dist` directory.
