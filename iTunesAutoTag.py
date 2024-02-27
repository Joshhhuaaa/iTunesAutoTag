import os
import subprocess
import glob
import re
import sys
import chardet
import configparser

print("--- iTunes AutoTag: Convert FLAC to ALAC and automate tags for iTunes ---\n")

# Path to script (py/exe)
# script_path = os.path.dirname(os.path.realpath(__file__))
script_path = os.path.dirname(sys.executable)

# Path to FLAC music
flac_path = os.path.join(script_path, "FLAC")

# Path to ALAC music
alac_path = os.path.join(script_path, "ALAC")

# Path to QAAC
qaac_path = os.path.join(script_path, "qaac64.exe")

# Path to MetaFlac
metaflac_path = os.path.join(script_path, "metaflac.exe")

# Path to AtomicParsley
atomicparsley_path = os.path.join(script_path, "AtomicParsley.exe")

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

def convert_flac_to_alac_with_tagging(flac_path, alac_path, qaac_path, metaflac_path, atomicparsley_path, tag_preference):
    flac_files = glob.glob(os.path.join(flac_path, "*.flac"))
    converted_count = 0

    for flac_file in flac_files:
        if os.path.exists(flac_file):
            song_file_name = os.path.splitext(os.path.basename(flac_file))[0]
            alac_file_path = os.path.join(alac_path, f"{song_file_name}.m4a")

            # Convert FLAC to ALAC
            subprocess.run([qaac_path, "--alac", "--threading", "--copy-artwork", "-i", flac_file, "-o", alac_file_path], stderr=subprocess.DEVNULL)

            print(f"====================\nConverted: {os.path.basename(flac_file)} to ALAC.")

            # Get artists from FLAC
            artists = get_artists_from_flac(flac_file, metaflac_path)

            # Get title from ALAC
            title = get_title_from_alac(alac_file_path, atomicparsley_path)
            
            # Get genre from ALAC
            genre = get_genre_from_alac(alac_file_path, atomicparsley_path)

            # Check and correct genre
            if genre and re.match(r"Rap|Hip Hop|Hip-Hop|Rap/Hip Hop|Rap/Hip-Hop|Hip Hop/Rap", genre):
                corrected_genre = "Hip-Hop/Rap"
                command = f'{atomicparsley_path} "{alac_file_path}" --genre "{corrected_genre}" --overWrite'
                subprocess.run(command, shell=True, stderr=subprocess.DEVNULL)
                print(f"Updated GENRE tag for {os.path.basename(alac_file_path)}.")


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
                        command = f'{atomicparsley_path} "{alac_file_path}" --title "{new_title_tag}" --overWrite'
                        subprocess.run(command, shell=True, stderr=subprocess.DEVNULL)
                        print(f"Updated TITLE tag for {os.path.basename(alac_file_path)}.")
                        # Set artist tag with main artist only
                        subprocess.run([atomicparsley_path, alac_file_path, "--artist", main_artist.encode('utf-8'), "--overWrite"], stderr=subprocess.DEVNULL)
                        print(f"Updated ARTIST tag for {os.path.basename(alac_file_path)}.")
                    else:
                        # Set artist tag with main artist and featured artists
                        new_artist_tag = f"{main_artist} (feat. {featured_artists})"
                        command = f'{atomicparsley_path} "{alac_file_path}" --artist "{new_artist_tag}" --overWrite'
                        subprocess.run(command, shell=True, stderr=subprocess.DEVNULL)
                        print(f"Updated ARTIST tag for {os.path.basename(alac_file_path)}.")
                else:
                    # Set artist tag with main artist only
                    subprocess.run([atomicparsley_path, alac_file_path, "--artist", main_artist.encode('utf-8'), "--overWrite"], stderr=subprocess.DEVNULL)
                    print(f"Updated ARTIST tag for {os.path.basename(alac_file_path)}.")
            else:
                print(f"No artists found for {os.path.basename(flac_file)}.")

            converted_count += 1
        else:
            print(f"Failed: {os.path.basename(flac_file)} not found.")

    print(f"====================\nSuccessfully converted and tagged {converted_count} audio file(s).")

# Cleans missed temporary files from AtomicParsley     
def cleanup_temp_files(directory):
    files = glob.glob(os.path.join(directory, "*-data-*.m4a"))
    
    for file_path in files:
        try:
            os.remove(file_path)
            print(f"\nRemoved temp file: {file_path}")
        except Exception as e:
            print(f"\nFailed to remove temp file: {file_path}. Error: {e}")

# Config
config = configparser.ConfigParser()
config.read('config.ini')

try:
    # If config is found, use user values
    flac_path = os.path.join(script_path, config.get('Paths', 'FLAC'))
    alac_path = os.path.join(script_path, config.get('Paths', 'ALAC'))
    tag_preference = config.get('Preferences', 'FeaturedArtistsTagPreference').lower()
except configparser.NoSectionError:
    # If the config is not found, use default values
    flac_path = os.path.join(script_path, "FLAC")
    alac_path = os.path.join(script_path, "ALAC")
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
