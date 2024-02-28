import configparser
import glob
import os
import re
import subprocess
import sys
from pathlib import Path

import chardet

print("--- iTunes AutoTag: Convert FLAC to ALAC and automate tags for iTunes ---\n")

# Path to script
if getattr(sys, 'frozen', False):
    script_path = Path(sys.executable).parent
else:
    script_path = Path(__file__).parent

# Path to FLAC music
flac_path = script_path / "FLAC"

# Path to ALAC music
alac_path = script_path / "ALAC"

# Path to QAAC
qaac_path = script_path / "qaac64.exe"

# Path to MetaFlac
metaflac_path = script_path / "metaflac.exe"

# Path to AtomicParsley
atomicparsley_path = script_path / "AtomicParsley.exe"

def get_artists_from_flac(flac_file_path, metaflac_path):
    artists = []
    try:
        # Getting artists from FLAC file using MetaFlac
        output = subprocess.check_output([metaflac_path, "--show-tag=ARTIST", flac_file_path], stderr=subprocess.DEVNULL)
        encoding = chardet.detect(output)['encoding']
        output = output.decode(encoding).strip()

        # Extract artist name(s)
        artist_tags = re.findall(r'ARTIST=(.*)', output)
        for artist in artist_tags:
            artists.append(artist)
    except subprocess.CalledProcessError:
        print(f"\nFailed to retrieve artists from {flac_file_path}.")
    return artists

def get_title_from_alac(alac_file_path, atomicparsley_path):
    try:
        # Getting title from ALAC file using AtomicParsley
        output = subprocess.check_output([atomicparsley_path, alac_file_path, "-t"], stderr=subprocess.DEVNULL)
        encoding = chardet.detect(output)['encoding']
        output = output.decode(encoding).strip()

        # Extract title
        title = re.search(r'Atom "\u00A9nam" contains: (.*)', output)
        if title:
            return title.group(1)
    except subprocess.CalledProcessError:
        print(f"\nFailed to retrieve title from {alac_file_path}.")
    return None

def get_genre_from_alac(alac_file_path, atomicparsley_path):
    try:
        # Getting genre from ALAC file using AtomicParsley
        output = subprocess.check_output([atomicparsley_path, alac_file_path, "-t"], stderr=subprocess.DEVNULL)
        encoding = chardet.detect(output)['encoding']
        output = output.decode(encoding).strip()

        # Extract genre
        genre = re.search(r'Atom "\u00A9gen" contains: (.*)', output)
        if genre:
            return genre.group(1)
    except subprocess.CalledProcessError:
        print(f"\nFailed to retrieve genre from {alac_file_path}.")
    return None

def convert_flac_to_alac_with_tagging(flac_path: Path, alac_path: Path, qaac_path: Path, metaflac_path: Path, atomicparsley_path: Path, tag_preference: str):
    flac_files = list(flac_path.glob("*.flac"))
    converted_count = 0
    
    if not flac_files:
        print("\nNo FLAC files found in the specified path.")
        return

    for flac_file in flac_files:
        if flac_file.exists():
            song_file_name = flac_file.stem
            alac_file_path = alac_path / f"{song_file_name}.m4a"

            # Convert FLAC to ALAC
            subprocess.run([str(qaac_path), "--alac", "--threading", "--copy-artwork", "-i", str(flac_file), "-o", str(alac_file_path)], stderr=subprocess.DEVNULL)

            print(f"====================\nConverted: {flac_file.name} to ALAC.")

            # Get artists from FLAC
            artists = get_artists_from_flac(str(flac_file), str(metaflac_path))
            
            # Get title from ALAC
            title = get_title_from_alac(str(alac_file_path), str(atomicparsley_path))
            
            # Get genre from ALAC
            genre = get_genre_from_alac(str(alac_file_path), str(atomicparsley_path))

            # Check and correct genre
            if genre and re.match(r"Rap|Hip Hop|Hip-Hop|Rap/Hip Hop|Rap/Hip-Hop|Hip Hop/Rap", genre):
                corrected_genre = "Hip-Hop/Rap"
                command = [str(atomicparsley_path), str(alac_file_path), "--genre", corrected_genre, "--overWrite"]
                subprocess.run(command, stderr=subprocess.DEVNULL)
                print(f"Updated GENRE tag for {alac_file_path.name}.")

            # Tags based on user preference
            if artists and title:
                main_artist = artists[0]
                if len(artists) > 1:
                    if len(artists) == 2:  # Only one featured artist
                        featured_artists = artists[1]
                    else:  # More than one featured artist
                        featured_artists = ", ".join(artists[1:-1])  # Join featured artists, including a comma, except the last one
                        featured_artists += f" & {artists[-1]}"  # Add "&" before the last artist

                    if tag_preference == "title":
                        # Set title tag with featured artists
                        new_title_tag = f"{title} (feat. {featured_artists})"
                        command = [str(atomicparsley_path), str(alac_file_path), "--title", new_title_tag, "--overWrite"]
                        subprocess.run(command, stderr=subprocess.DEVNULL)
                        print(f"Updated TITLE tag for {alac_file_path.name}.")
                        # Set artist tag with main artist only
                        subprocess.run([str(atomicparsley_path), str(alac_file_path), "--artist", main_artist.encode('utf-8'), "--overWrite"], stderr=subprocess.DEVNULL)
                        print(f"Updated ARTIST tag for {alac_file_path.name}.")
                    else:
                        # Set artist tag with main artist and featured artists
                        new_artist_tag = f"{main_artist} (feat. {featured_artists})"
                        command = [str(atomicparsley_path), str(alac_file_path), "--artist", new_artist_tag, "--overWrite"]
                        subprocess.run(command, stderr=subprocess.DEVNULL)
                        print(f"Updated ARTIST tag for {alac_file_path.name}.")
                else:
                    # Set artist tag with main artist only
                    subprocess.run([str(atomicparsley_path), str(alac_file_path), "--artist", main_artist.encode('utf-8'), "--overWrite"], stderr=subprocess.DEVNULL)
                    print(f"Updated ARTIST tag for {alac_file_path.name}.")
            else:
                print(f"No artists found for {flac_file.name}.")

            converted_count += 1
        else:
            print(f"Failed: {flac_file.name} not found.")

    print(f"====================\nSuccessfully converted and tagged {converted_count} audio file(s).")

# Cleans missed temp files from AtomicParsley     
def cleanup_temp_files(directory: Path):
    print(f"====================")
    temp_files = list(directory.glob("*-data-*.m4a"))
    
    for file_path in temp_files:
        try:
            file_path.unlink()
            print(f"Removed temp file: {file_path}\n")
        except Exception as e:
            print(f"\nFailed to remove temp file: {file_path}. Error: {e}\n")


# Config
config_path = os.path.join(script_path, 'config.ini')            
config = configparser.RawConfigParser()
config.read('config.ini')

try:
    # If config is found, use user values
    flac_path = Path(os.path.join(script_path, config.get('Paths', 'FLAC')))
    alac_path = Path(os.path.join(script_path, config.get('Paths', 'ALAC')))
    tag_preference = config.get('Preferences', 'FeaturedArtistsTagPreference').lower()
except configparser.NoSectionError:
    # If the config is not found, use default values
    flac_path = Path(os.path.join(script_path, "FLAC"))
    alac_path = Path(os.path.join(script_path, "ALAC"))
    tag_preference = None
    
if tag_preference not in ["artist", "title"]:
    while True:
        tag_preference = input("Include featured artists in the 'TITLE' tag like iTunes or use 'ARTIST' tag instead?\nEnter your preferred tag (artist/title): ").lower()
        if tag_preference in ["artist", "title"]:
            break
        else:
            print("\nInvalid tag. Enter 'artist' or 'title'.")
            
convert_flac_to_alac_with_tagging(flac_path, alac_path, qaac_path, metaflac_path, atomicparsley_path, tag_preference)

cleanup_temp_files(alac_path)

input("\nPress Enter to exit.")
