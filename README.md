# iTunes AutoTag
iTunes AutoTag is a simple command line program that converts FLAC music files to Apple's ALAC format and automatically sets up the metadata to iTunes convention.

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
- Place the FLAC files you want to convert and tag into the "FLAC" folder located in the root directory alongside the executable.
- Run the executable: `iTunesAutoTag.exe`

## Featured Artists

Upon starting, you will be prompted to choose how featured artists should be included in the tags:

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

The converted and tagged files will be outputted into the "ALAC" folder in the same directory.

