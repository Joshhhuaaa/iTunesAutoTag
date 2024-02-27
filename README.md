# <img src="icon.ico" width="32"> iTunes AutoTag
iTunes AutoTag is a simple command line script that converts FLAC music files to Apple's ALAC format and automatically sets up the metadata to iTunes convention.

# Dependencies
iTunes AutoTag uses [qaac](https://github.com/nu774/qaac) for converting audio from FLAC to ALAC.

For qaac to function properly, the following files from iTunes are required:
- ASL.dll
- CoreAudioToolbox.dll
- CoreFoundation.dll
- icudt62.dll
- libdispatch.dll
- libicuin.dll
- libicuuc.dll
- objc.dll

These files are are included in the source and releases.

# Usage
- Place any FLAC files you want to convert and tag into the "FLAC" folder located in the main directory alongside the executable.
  - Optionally, you can set a custom path for your FLAC and ALAC folders using `config.ini`.
- Run the executable: `iTunesAutoTag.exe`

## Configuration File
`config.ini` located in the main directory, allows you to adjust preferences related to paths and metadata tagging.

```
[Paths]
# Override default paths of the included "FLAC" and "ALAC" folders
# Example: C:\Users\Administrator\Desktop\Output
FLAC = FLAC
ALAC = ALAC

[Preferences]
# Determines which tag to include featured artists
# Supported values: Artist, Title
FeaturedArtistsTagPreference = None
```

If `FLAC` and `ALAC` paths are unspecified, the script will default to using the main directory folders.
If `FeaturedArtistsTagPreference` is unspecified, the script will ask for your preference prior to starting.

# Metadata Tags
## Featured Artists

### TITLE (iTunes convention)
```
TITLE = <SongName> (feat. <FeaturedArtist1>, <FeaturedArtist2> & <FeaturedArtist3>)
ARTIST = <MainArtist>
```
### ARTIST
```
TITLE = <SongName>
ARTIST = <MainArtist> (feat. <FeaturedArtist1>, <FeaturedArtist2> & <FeaturedArtist3>)
```

The converted and tagged files will be outputted into the 'ALAC' folder. If you specify a custom path in `config.ini`, they will be outputted there instead.
