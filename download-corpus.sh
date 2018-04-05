#!/usr/bin/env bash

# From http://opus.nlpl.eu/OpenSubtitles2018.php
# Contains actual subtitles
wget -N http://opus.nlpl.eu/download.php?f=OpenSubtitles2018/en.tar.gz -P ./corpus/

# From https://www.opensubtitles.org/en/downloads#exports
#      http://dl.opensubtitles.org/addons/export/
# Contains movie names linked to IDs which are missing in the corpus above.
wget -N http://dl.opensubtitles.org/addons/export/subtitles_all.txt.gz -P ./corpus/