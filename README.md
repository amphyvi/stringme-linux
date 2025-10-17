# stringme-linux
Music playback information file output for Linux-based systems

<img width="1763" height="1322" alt="image" src="https://github.com/user-attachments/assets/45cc99de-b6e6-4e4b-a1c4-5746318631a4" />


**You're a live streamer. You want to put credit on screen for the music you're listening to, in the easiest and most flexible way possible - somehow that's reliable, simple, and doesn't restrict your creative freedom. (And... you switched to Linux.)**

**Does that describe you? Well, member of a miniscule fragment of modern society, I believe I have just the solution for you!**

_________

## Overview
This script just writes the current song's artist & title to a text file. Pause/stop playback, or exit the script (usually Ctrl + C), to clear the file.

Use arguments to customize your experience:
- `-lower` - output is all lowercase
- `-UPPER` - OUTPUT IS ALL UPPERCASE
- `-art` - Output not just a text file with track info, but grab album art from the audio player to a .jpg file, too (YMMV). **Image is deleted** alongside track info being cleared (pausing playback or exiting script)

If you're using this with OBS, OBS will automatically update changes made to the text file, showing the new artist & song name, whenever the file itself changes (within 1 second). Not sure how to use a script like this? See Usage below for setup.

This for sure works on Kubuntu (Ubuntu + KDE Plasma), and should work on any system that supports MPRIS (which should be most Linux desktop environments).

> **Please note:** I know there's a range of potential features that could be added - such as album name capture, multiple artists capture (if that's even possible?), and OBS automation (so it launches automatically within OBS) just to name a few - and I'm not currently able to make them work out. That last one has been breaking my brain, I'm going to blame my OBS instance being the Flatpak version on this one I think. Anyway, this whole project was created to meet my own personal needs and I lack the understanding to expand on it much more than this. Contributions are not expected of course, but are greatly appreciated <3

## Usage
1. Make sure you have Python and dbus-python installed (`pip3 install dbus-python`). If you're using a conventional Linux distro that came out sometime in the last decade, you should already be set.
2. Save `stringme-linux.py` to a safe spot on your Linux computer.
3. Run the script, typically using your terminal: `python3 /path/to/stringme-linux.py` (add ` -lower` or ` -upper` to the end to change the text case, and/or add ` -art` to grab album art)
5. In OBS, add a Text (GDI+) source and check "Read from file". Select the stringme.txt file created by the script. By default, it'll be located in your home directory (`~`).
6. Using `-art` to capture album art? Add a new Image source, and point it to the stringme-art.jpg file created by the script. By default, it'll *also* be located in your home directory (`~`).
7. Customize text and/or album art image in OBS as desired.

That's it! After you've set it up the first time, just **redo step #3** to get the text (and album art, if using `-art`) to show up in OBS again anytime you want it to be there.

As long as the script is running, it's updating the file(s) for you. It'll check once per second to see if the track info has changed, and if so, the file(s) - and the info on screen in OBS - will update accordingly.

## Known compatible desktop environments (DEs)
- **KDE Plasma 6.x**

I know, that's a really short list. Please feel free to try this on other DEs and let me know how it fares :)

## Tested & working players (using text feature only - no particular order)
- **Spotify** - deb/native
- **Quod Libet** - deb/native
- **Firefox** - Flatpak *(tested YouTube, with* `media.hardwaremediakeys.enabled` *=* `true` *in about:config)*
- **Audacious** - deb/native
- **Rhythmbox** - deb/native
- **Haruna** - deb/native
- **Elisa** - deb/native

**Strawberry Music Player**: Didn't try it (I really *really* don't vibe with the UI, sorry not sorry lmao) but given the list above, it should probably work too.

**DeaDBeeF** - deb/native: I didn't get it to work, but other MPRIS2-compliant solutions (like the spectacular [plasmusic-toolbar](https://github.com/ccatterina/plasmusic-toolbar)) _also_ don't catch DeaDBeeF so that could be a problem with the way mine is configured.

## Known issues
* When playing back audio featuring multiple artists, some (most?) players only seem to provide the first artist in the list. Seems to be an MPRIS limitation?

## Special thanks
- **[noggynoggy](https://github.com/noggynoggy)** - for creating the (now no longer available) "stringme-obs" solution I first used on Windows, which inspired this project
- **[ccatterina](https://github.com/ccatterina)** - for [pointing me in the right direction](https://github.com/ccatterina/plasmusic-toolbar/discussions/223#discussioncomment-14095165) to get this project off the ground!
