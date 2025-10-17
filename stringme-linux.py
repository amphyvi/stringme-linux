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
This script just writes the current song's artist & title to a text file. Pause/stop playback, or exit the
script (usually Ctrl + C), to clear the file.

Use arguments to customize your experience:

    '-lower' - output is all lowercase
    '-UPPER' - OUTPUT IS ALL UPPERCASE
    '-art' - Output not just a text file with track info, but grab album art from the audio player to a .jpg
     file, too (YMMV). Image is deleted alongside track info being cleared (pausing playback or exiting
     script)

If you're using this with OBS, OBS will automatically update changes made to the text file, showing the new
artist & song name, whenever the file itself changes (within 1 second). Not sure how to use a script like
this? See Usage below for setup.

This for sure works on Kubuntu (Ubuntu + KDE Plasma), and should work on any system that supports MPRIS
(which should be most Linux desktop environments).

Usage:

1. Make sure you have Python and dbus-python installed (pip3 install dbus-python). If you're using a
   conventional Linux distro that came out sometime in the last decade, you should already be set.
2. Save this stringme-linux.py - you're reading it right now! - to a safe spot on your Linux computer.
3. Run the script, typically using your terminal:
   python3 /path/to/stringme-linux.py
   (add ' -lower' or ' -upper', without the '', to the end to change the text case)
   (and/or add ' -art' to grab album art!)
4. In OBS, add a Text (GDI+) source and check "Read from file". Select the stringme.txt file created by the
   script. By default, it'll be located in your home directory (~).
5. Using -art to capture album art? Add a new Image source, and point it to the stringme-art.jpg file created
   by the script. By default, it'll also be located in your home directory (~).
6. Customize text and/or album art image in OBS as desired.


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
import argparse
import fcntl
import base64

# Clear terminal
from os import system
system("clear||cls")

sys.stdout.write("\x1b]2;stringme-linux\x07")

OUTPUT_FILE = os.path.expanduser("~/stringme.txt")   # <-- Song info text location
ART_FILE = os.path.expanduser("~/stringme-art.jpg")  # <-- Song album art location
MPRIS_PATTERN = re.compile(r"^org\.mpris\.MediaPlayer2\..+")

def get_mpris_players(session_bus):
    names = session_bus.list_names()
    players = [name for name in names if MPRIS_PATTERN.match(name)]
    return players

def get_media_properties():
    session_bus = dbus.SessionBus()
    players = get_mpris_players(session_bus)
    if not players:
        return "", "", None, None

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
                # Get title and artist as before
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
                    
                # Get album art - first try mpris:artUrl
                art_data = None
                art_url = metadata.get("mpris:artUrl", "")
                if art_url:  # Changed to handle both file:// and http(s):// URLs
                    if art_url.startswith("file://"):
                        art_path = art_url[7:]  # Remove 'file://' prefix
                        if os.path.exists(art_path):
                            with open(art_path, 'rb') as f:
                                art_data = f.read()
                    elif art_url.startswith(("http://", "https://")):
                        # For Spotify and other remote art URLs
                        import urllib.request
                        try:
                            with urllib.request.urlopen(art_url) as response:
                                art_data = response.read()
                        except Exception:
                            pass
                
                return title, artist_str, playback_status, art_data
                
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
            return title, artist_str, playback_status, None  # Added None for art_data
        except dbus.exceptions.DBusException:
            continue

    return "", "", None, None

def main():
    # Add argument parser
    parser = argparse.ArgumentParser(description='Display current playing song in a text file.')
    parser.add_argument('-lower', action='store_true', help='Convert output text to lowercase')
    parser.add_argument('-upper', action='store_true', help='Convert output text to uppercase')
    parser.add_argument('-art', action='store_true', help='Also save album art to a separate file')
    args = parser.parse_args()

    # Remove the conflicting arguments check since we now handle both flags
    
    # Try to open and lock the file
    try:
        file_handle = open(OUTPUT_FILE, "w", encoding="utf-8")
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        try:
            while True:
                print("\033[1;31mx Error: The output file is already being used by another process!\033[0m")
                print("\033[1;31m  Make sure you're not running multiple instances of this script.\033[0m")
                print("\033[1;31m  If you're not sure why this error is happening, try rebooting your computer.\033[0m")
                print("\033[1;31m  (Press Ctrl+C to exit)\033[0m")
                time.sleep(1)  # Wait 1 second between message repeats
                # Clear the last 4 lines
                sys.stdout.write('\033[F\033[K' * 4)
        except KeyboardInterrupt:
            print("\n")
            sys.exit(1)
    
    # Clear the file contents
    file_handle.write("")
    file_handle.flush()
    
    # Prep first message - highlight case conversion arg, if any
    CYAN = "\033[0;36m"
    RESET = "\033[0m"
    lower_disp = f"{CYAN}-lower{RESET}" if args.lower else "-lower"
    upper_disp = f"{CYAN}-upper{RESET}" if args.upper else "-upper"
    art_disp = f"{CYAN}-art{RESET}" if args.art else "-art"

    # Print first block of text to terminal
    firstmessage = (
        f"\u2713 Running successfully (or at least it should be! <3)\n\n"
        f"\033[1m> Output file: \t{OUTPUT_FILE}\033[0m\n"
        f"  Want it somewhere else? Edit the OUTPUT_FILE variable (line 107).\n\n"
        "\033[1;33m! To properly exit & clear the output file, do one of these:\033[0m\n" # orange color: \033[38;5;172m
        "\033[1;33m  \u25e6 Use the keyboard shortcut to quit (usually Ctrl+C), or\033[0m\n"
        "\033[1;33m  \u25e6 Pause/stop/quit the source before exiting\033[0m\n\n"
        "  Tips:\n"
        "\u2022 Play audio from one player at a time to ensure accurate output.\n"
        f"\u2022 Run with {lower_disp} or {upper_disp} to change the text case accordingly.\n"
        f"\u2022 Run with {art_disp} to pull album art (Spotify works, YMMV with others).\n"
        "\u2022 Playback is going, but the player isn't being detected? Your player may not be supported, or something else is amiss.\n"
        f"\u2022 Want to monitor the output file directly? Use in a separate terminal instance:\n  \033[90mwatch --interval 1 --equexit 3600 cat {OUTPUT_FILE}\033[0m\n"
    )
    print(firstmessage)

    # Animation frames for playing state
    PLAY_FRAMES = ["⣦⣇", "⣷⣼", "⣴⣆", "⣾⣄", "⣴⣠", "⣸⣰", "⣄⣼", "⣰⣷", "⣆⣦"]

    # Braille characters:
    # ⣇ ⣆ ⣄ ⣀ ⣠ ⣰ ⣸
    # ⠀ ⣧ ⣦ ⣤ ⣴ ⣼
    # ⠀ ⠀ ⣷ ⣶ ⣾
    # ⠀ ⠀ ⠀ ⣿

    # Animation frame for paused/stopped state
    PAUSE_FRAME = "⣀⣀"
    current_frame = 0
    ANIMATION_INTERVAL = 0.1  # animation playback speed in seconds
    last_animation_time = time.time()

    last_title = None
    last_artist = None
    last_art = None
    last_line = ""
    line = ""
    animation = PAUSE_FRAME
    
    try:
        while True:
            current_time = time.time()
            
            # Check media properties every second
            if current_time - last_animation_time >= 1.0 or last_line == "":
                title, artist, playback_status, art_data = get_media_properties()
                
                # Handle both files together in synchronized blocks
                if playback_status == "Paused":
                    # Clear both files at once
                    try:
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            f.write("")
                        if args.art and os.path.exists(ART_FILE):
                            os.remove(ART_FILE)
                    except Exception as e:
                        print(f"\nError clearing files: {e}")
                    last_title, last_artist, last_art = None, None, None
                    line = ""
                    animation = PAUSE_FRAME
                else:
                    line = f"{artist} \u2022 {title}".strip(" -")
                    # Handle text case conversion
                    if args.lower and args.upper:
                        line = ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(line))
                    elif args.lower:
                        line = line.lower()
                    elif args.upper:
                        line = line.upper()
                    
                    # Update both files together if content changed
                    if title != last_title or artist != last_artist or art_data != last_art:
                        try:
                            # Update text file
                            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                                f.write(line)
                            
                            # Update art file in the same block
                            if args.art:
                                if art_data:
                                    # Ensure directory exists
                                    art_dir = os.path.dirname(ART_FILE)
                                    os.makedirs(art_dir, exist_ok=True)
                                    with open(ART_FILE, 'wb') as f:
                                        f.write(art_data)
                                elif os.path.exists(ART_FILE):
                                    os.remove(ART_FILE)
                        except Exception as e:
                            print(f"\nError updating files: {e}")
                            
                        last_title, last_artist, last_art = title, artist, art_data

            # Update animation frame every 400ms if media is playing
            if current_time - last_animation_time >= ANIMATION_INTERVAL:
                if line:  # If there's media playing
                    animation = PLAY_FRAMES[current_frame]
                    current_frame = (current_frame + 1) % len(PLAY_FRAMES)
                else:  # If no media or paused
                    animation = PAUSE_FRAME
                
                # Update terminal display
                sys.stdout.write("\r" + " " * 80 + "\r")  # Clear the line
                sys.stdout.write(f"\r\033[1;36m{animation} {line} \033[0m") # music note unicode was: \u266B
                sys.stdout.flush()
                last_animation_time = current_time
            
            time.sleep(0.2)  # Small sleep to prevent CPU hogging
            
    except KeyboardInterrupt:
        # Clear both files on exit
        file_handle.seek(0)
        file_handle.truncate()
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        file_handle.close()
        if args.art and os.path.exists(ART_FILE):
            os.remove(ART_FILE)
        finalmessage = f"\n\n\u25A0 Exiting. \033[1m{os.path.basename(OUTPUT_FILE)}\033[0m should be empty & ready for next time. Bye!\n"
        print(finalmessage)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
