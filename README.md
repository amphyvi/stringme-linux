# stringme-linux
Music playback information file output for Linux-based systems

#### You're a live streamer. You want to put credit on screen for the music you're listening to, in the easiest and most flexible way possible - somehow that's reliable, simple, and doesn't restrict your creative freedom. (And... you switched to Linux.)

#### Does that describe you? Well, member of an infinitesimally-small fragment of modern society, I believe I have just the solution for you :)

_________

## Overview
This script just writes the current song's artist & title to a text file (OUTPUT_FILE).

If you're using this with OBS, OBS will automatically update to reflect the new artist & song name whenever
the file itself changes (within a second of the track changing). See Usage for setup.

This for sure works on Ubuntu + KDE, and should work on any system that supports MPRIS (most Linux desktop
environments).

## Usage
1. Make sure you have Python and dbus-python installed (`pip3 install dbus-python` - shouldn't be necessary on most systems).
2. Save this script to a file, e.g., stringme-linux.py.
3. Run the script, typically in your terminal: python3 stringme-linux.py
4. In OBS, add a Text (GDI+) source and check "Read from file". Select the stringme.txt file created by the script. By default, it'll be located in your home directory (~).
5. Customize the text appearance in OBS as desired.
That's it! As long as the script is running, it's updating that file for you. It'll check once per second to see if the track info has changed, and if so, the file - and the text on screen in OBS - will update accordingly.

<img width="1884" height="1129" alt="image" src="https://github.com/user-attachments/assets/ab471014-3800-440a-a814-c35ca69a0d0f" />
