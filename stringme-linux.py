"""

stringme-linux
by amphyvi

As a streamer, I wanted a simple way to display my currently playing song in OBS. The best solution I found
when I was still on Windows was a Python script called "stringme-OBS" by noggynoggy, which I modified (as
best as I knew at the time) to work with my media player of choice. I'd link to "stringme-OBS" but it
seems to have been taken down. Thanks anyway, noggynoggy!

That ended up being a high-overhead solution just to get a text file with the current artist & track name, 
and it even proved to be unreliable... though that's very likely my fault lol. This new script has proven to
be a lot more reliable. Common Linux W I guess

/!\ I AM NOT A PROGRAMMER. I just managed to cobble this together. I will most likely NOT be able to help
    if you have any issues. Contributions are warmly accepted but not expected of course - thanks in advance
    if you choose to contribute!

-------------------------------------------------------------------------------------------------------------

Overview:
This script just writes the current song's artist & title to a text file (OUTPUT_FILE).
If you're using this with OBS, OBS will automatically update to reflect the new artist & song name whenever
the file itself changes (within a second of the track changing). See Usage for setup.

This for sure works on Ubuntu + KDE, and should work on any system that supports MPRIS (most Linux desktop
environments).

Usage:
1. Make sure you have Python and dbus-python installed (`pip3 install dbus-python` - shouldn't be necessary
   on most systems).
2. Save this script to a file, e.g., stringme-linux.py.
3. Run the script, typically in your terminal: python3 stringme-linux.py
4. In OBS, add a Text (GDI+) source and check "Read from file". Select the stringme.txt file created by the
   script. By default, it'll be located in your home directory (~).
5. Customize the text appearance in OBS as desired.

-------------------------------------------------------------------------------------------------------------

There's lots of ways to run the script. My personal preferred method: Create a menu entry in KDE*! To do that:
1. Open the KDE Menu Editor (right-click the application launcher icon and select "Edit Applications").
2. Choose a category where you want to add the new entry (e.g., "Utilities").
3. Click "New Item" to create a new menu entry.
4. Fill in the details:
    - Name: stringme-linux
    - Description: Playback Output for OBS
    - Comment: Display current song in OBS
    - Environment variables: (leave blank)
    - Program: konsole
    - Command-line arguments: -e bash -c 'python3 <!! Path To This Script Here !!>'
5. Press the empty square near the top-right corner to set an icon (optional). I like using "audio-x-scpls",
   or you can download the one I designed (from the Github repo) if you want.
6. Click "Save" to save the new menu entry.

Some other suggestions for running the script:
- Run it in a terminal window (Usage step 3 above) and keep that window open/minimized while streaming.
- Set it up to run automatically when you start streaming, OBS supports LUA scripting I believe.
- Running KDE? My preferred method is to add a menu item (see bottom of this comment block).
- Create a systemd service for it, or add it to your KDE autostart applications... but that's probably
  overkill for a lot of people

* Not on KDE, or prefer to create a .desktop file instead? Here's an example you can use:
    [Desktop Entry]
    Type=Application
    Name=stringme-linux
    GenericName=Playback Output for OBS
    Exec=python3 <!! Path To This Script Here !!>
    Icon=audio-x-scpls
    Comment=Display current song in OBS
    Categories=Audio;Player;Recorder;

"""

import time
import dbus
import re
import os
import sys

# Clear terminal
from os import system
system("clear||cls")

sys.stdout.write("\x1b]2;stringme-linux\x07")

OUTPUT_FILE = os.path.expanduser("~/stringme.txt")
MPRIS_PATTERN = re.compile(r"^org\.mpris\.MediaPlayer2\..+")

def get_mpris_players(session_bus):
    names = session_bus.list_names()
    players = [name for name in names if MPRIS_PATTERN.match(name)]
    return players

def get_media_properties():
    session_bus = dbus.SessionBus()
    players = get_mpris_players(session_bus)
    if not players:
        return "", "", None

    # First, try to find a player that is actively playing
    for player_name in players:
        try:
            player = session_bus.get_object(
                player_name,
                "/org/mpris/MediaPlayer2"
            )
            iface = dbus.Interface(player, "org.freedesktop.DBus.Properties")
            props = iface.GetAll("org.mpris.MediaPlayer2.Player")
            playback_status = props.get("PlaybackStatus", "")
            if playback_status == "Playing":
                metadata = props.get("Metadata", {})
                title = metadata.get("xesam:title", "")
                if hasattr(title, '__iter__') and not isinstance(title, str):
                    title = " ".join(str(t) for t in title)
                else:
                    title = str(title)
                artist = metadata.get("xesam:artist", "")
                if hasattr(artist, '__iter__') and not isinstance(artist, str):
                    artist_str = ", ".join(str(a) for a in artist)
                elif isinstance(artist, str):
                    artist_str = artist
                else:
                    artist_str = str(artist) if artist else ""
                return title, artist_str, playback_status
        except dbus.exceptions.DBusException:
            continue

    # If none are playing, fall back to the first available player
    for player_name in players:
        try:
            player = session_bus.get_object(
                player_name,
                "/org/mpris/MediaPlayer2"
            )
            iface = dbus.Interface(player, "org.freedesktop.DBus.Properties")
            props = iface.GetAll("org.mpris.MediaPlayer2.Player")
            metadata = props.get("Metadata", {})
            playback_status = props.get("PlaybackStatus", "")
            title = metadata.get("xesam:title", "")
            if hasattr(title, '__iter__') and not isinstance(title, str):
                title = " ".join(str(t) for t in title)
            else:
                title = str(title)
            artist = metadata.get("xesam:artist", "")
            if hasattr(artist, '__iter__') and not isinstance(artist, str):
                artist_str = ", ".join(str(a) for a in artist)
            elif isinstance(artist, str):
                artist_str = artist
            else:
                artist_str = str(artist) if artist else ""
            return title, artist_str, playback_status
        except dbus.exceptions.DBusException:
            continue

    return "", "", None

def main():
    # Ensure the output file exists and is empty at start
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")
    
    # Print first block of text to terminal
    firstmessage = f"\u2713 Running successfully (or at least it should be!) <3\n\n> \033[1mOutput file: \t{OUTPUT_FILE}\033[0m\n> Want it somewhere else? Edit the OUTPUT_FILE variable (line 86).\n\n  Tips:\n\u2022 Play audio from one source at a time to ensure accurate output.\n\u2022 To exit, use the standard keyboard shortcut (usually: Ctrl + C)\n\u2022 Want to keep an eye on the file in your terminal? Open a new window & use:\twhile true; do cat {OUTPUT_FILE}; echo; sleep 1; done\n\u2022 Playing audio, but there's nothing next to the \u266B symbol? Your player may not be supported, or something else is amiss.\n"
    print(firstmessage)
    last_title = None
    last_artist = None
    last_line = ""
    try:
        while True:
            title, artist, playback_status = get_media_properties()
            if playback_status == "Paused":
                # If paused for a second, clear the file
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    f.write("")
                last_title, last_artist = None, None
                line = ""
            else:
                line = f"{artist} - {title}".strip(" -")  # <<< Text to display in 
                if title != last_title or artist != last_artist:
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        f.write(line)
                    last_title, last_artist = title, artist
            # Only update the terminal if the line has changed
            if line != last_line:
                sys.stdout.write("\r" + " " * 80 + "\r")  # Clear the line
                sys.stdout.write(f"\r\033[1;36m\u266B {line} \033[0m")  # Write line to terminal for monitoring
                sys.stdout.flush()
                last_line = line
            time.sleep(1)
    except KeyboardInterrupt:
        # Clear the contents of OUTPUT_FILE on exit
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("")
        finalmessage = f"\n\n\u238B Exiting. '{os.path.basename(OUTPUT_FILE)}' should be empty & ready for next time. Bye!\n"
        print(finalmessage)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
