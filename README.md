# stringme-linux
Music playback information file output for Linux-based systems

<img width="1884" height="1129" alt="image" src="https://github.com/user-attachments/assets/c73def00-0416-451b-8df1-381e90b65e38" />

#### You're a live streamer. You want to put credit on screen for the music you're listening to, in the easiest and most flexible way possible - somehow that's reliable, simple, and doesn't restrict your creative freedom. (And... you switched to Linux.)

#### Does that describe you? Well, member of an infinitesimally-small fragment of modern society, I believe I have just the solution for you!

_________

## Overview
This script just writes the current song's artist & title to a text file. Pause/stop playback, or exit the script, to clear the file.

If you're using this with OBS, OBS will automatically update to reflect the new artist & song name whenever the file itself changes (within a second of the track changing). See Usage for setup.

This for sure works on Ubuntu + KDE, and should work on any system that supports MPRIS (most Linux desktop environments).

> **Please note:** I know there's a large swath of potential features that could be added - album art capture, multiple artists capture (if that's even possible?), and album capture just to name a few. This was created to meet my own personal needs and I lack the understanding to expand on it much more than this. Contributions are not expected of course but are greatly appreciated <3

## Usage
1. Make sure you have Python and dbus-python installed (`pip3 install dbus-python` - shouldn't be necessary on most systems).
2. Save `stringme-linux.py` to a safe spot on your Linux computer.
3. Run the script, typically in your terminal: `python3 stringme-linux.py`
4. In OBS, add a Text (GDI+) source and check "Read from file". Select the stringme.txt file created by the script. By default, it'll be located in your home directory (`~`).
5. Customize the text appearance in OBS as desired.
That's it! As long as the script is running, it's updating that file for you. It'll check once per second to see if the track info has changed, and if so, the file - and the text on screen in OBS - will update accordingly.

## Known compatible desktop environemnts (DEs)
- KDE

I know, that's a really short list. Please feel free to try this on other DEs and let me know how it fares :)

## Known compatible players (no particular order)
- Spotify
- Quod Libet
- Firefox (with YouTube & `media.hardwaremediakeys.enabled` = `true` in about:config)
- Audacious
- Rhythmbox
- Haruna
- Elisa

Strawberry Music Player: Didn't try it (I really don't vibe with the UI, sorry not sorry lmao) but given the list above, it should probably work too.

Deadbeef: I didn't get it to work, but other MPRIS2-compliant solutions (like ccatterina's spectacular [plasmusic-toolbar](https://github.com/ccatterina/plasmusic-toolbar)) _also_ don't catch DeaDBeeF so that could be a problem with the way mine is configured.

## Known issues
* Some (most?) players only provide the first artist in multi-artist tracks when separated by commas. Seems the first one will show up no matter what.

## Special thanks
- [noggynoggy](https://github.com/noggynoggy) - for creating the (now no longer available) "stringme-obs" solution I first used on Windows, which inspired this project
- [ccatterina](https://github.com/ccatterina) - for [pointing me in the right direction](https://github.com/ccatterina/plasmusic-toolbar/discussions/223#discussioncomment-14095165) to get this project off the ground!
