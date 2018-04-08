#!/usr/bin/env bash

set -o errexit

# From http://opus.nlpl.eu/OpenSubtitles2018.php
# Contains actual subtitles
wget -N http://opus.nlpl.eu/download.php?f=OpenSubtitles2018/en.tar.gz -P ./corpus/

# Untar corpus if not already there
if [ ! -d "./corpus/OpenSubtitles2018" ]; then
  tar --extract --verbose --keep-old-files --file ./corpus/*OpenSubtitles2018*.tar.gz --directory ./corpus/
fi

# From https://www.opensubtitles.org/en/downloads#exports
#      http://dl.opensubtitles.org/addons/export/
# Contains movie names linked to IDs which are missing in the corpus above.
wget -N http://dl.opensubtitles.org/addons/export/subtitles_all.txt.gz -P ./corpus/