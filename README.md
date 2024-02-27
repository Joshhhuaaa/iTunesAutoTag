# iTunes AutoTag
iTunes AutoTag simplifies the process of converting FLAC music to Apple's ALAC format, which can be imported into iTunes. Additionally, it automatically adjusts your song metadata, such as artists and genres, matching iTunes's standards.

# Dependencies
iTunes AutoTag relies on [qaac](https://github.com/nu774/qaac) for converting audio from FLAC to ALAC.

For qaac to function properly, the following files from iTunes are required:
- ASL.dll
- CoreAudioToolbox.dll
- CoreFoundation.dll
- icudt62.dll
- libdispatch.dll
- libicuin.dll
- libicuuc.dll
- objc.dll

These files are necessary to use iTunes AutoTag. However, they are not included in the source. If working with the source, you can obtain these files from the releases or an iTunes installation.

# Usage
- Place the FLAC files you want to convert and tag into the "FLAC" folder located in the root directory alongside the executable.
- Run the executable: `iTunes-AutoTag.exe`


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

