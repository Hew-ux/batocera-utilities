#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
# Import pyyaml, for parsing YML files.
import yaml
# Import requests, for retrieving pages from the web.
import requests
# Import custom functions.
#from feature_printer import feature_printer
# Static variables

# Main script
# Download the latest es_system.yml and load the output via the YAML parser.
# We need to specify that we want the text object and not the whole HTML
# object.
#es_sys = requests.get( "https://raw.githubusercontent.com/batocera-linux/ba" \
#"tocera.linux/master/package/batocera/emulationstation/batocera-es-system/es_" \
#"systems.yml", allow_redirects=True )
#es_sys = yaml.safe_load( es_sys.text )
# Local file load.
es_sys = yaml.safe_load( open( "es_systems.yml" ) )

# Do the same as above but for features.
#es_feat = requests.get( "https://raw.githubusercontent.com/batocera-linux/batoc" \
#"era.linux/master/package/batocera/emulationstation/batocera-es-system/es_featu" \
#"res.yml", allow_redirects=True )
#es_feat = yaml.safe_load( es_feat.text )
# Local file load.
es_feat = yaml.safe_load( open( "es_features.yml" ) )

# Test
#output = feature_printer( es_feat['dolphin'], "wii" )
