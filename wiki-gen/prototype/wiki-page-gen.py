#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import argparse
# Import pyyaml, for parsing YML files.
import yaml
# Import requests, for retrieving pages from the web.
import requests
# Import custom functions.
from feature_printer import feature_printer
from summary_printer import summary_printer

# Main script
def main( system, emulator, core, verbose ):
  # Download the latest es_system.yml and load the output via the YAML parser.
  # We need to specify that we want the text object and not the whole HTML
  # object. Commented while testing for now.
  #es_sys = requests.get( "https://raw.githubusercontent.com/batocera-linux/ba" \
  #"tocera.linux/master/package/batocera/emulationstation/batocera-es-system/es_" \
  #"systems.yml", allow_redirects=True )
  #es_sys = yaml.safe_load( es_sys.text )
  # Grab from a local file instead.
  es_sys = yaml.safe_load( open( "es_systems.yml" ) )

  # Check if the user has inputted a valid system.
  if not system in es_sys.keys():
    print( "System not found!" )
    # Grab all the available systems and put them into a list object.
    available_systems_sorted = list(es_sys.keys())
    # Sort that list.
    available_systems_sorted.sort()
    # Print out the error message.
    print( "Available systems: " + str(available_systems_sorted) )
    # Exit the program, indicating that an error occurred.
    sys.exit(2)

  # Do the same as above but for features.
  #es_feat = requests.get( "https://raw.githubusercontent.com/batocera-linux/batoc" \
  #"era.linux/master/package/batocera/emulationstation/batocera-es-system/es_featu" \
  #"res.yml", allow_redirects=True )
  #es_feat = yaml.safe_load( es_feat.text )
  # Grab from a local file instead.
  es_feat = yaml.safe_load( open( "es_features.yml" ) )

  # Initialise an empty output string.
  output = ""

  if not emulator and not core:
    if verbose:
      print("No emulator and no core specified.")
    # When only the system is specified, return the entire page.
    output = output + summary_printer( es_sys[system], system )
    # Loop through all the available emulators for the system.
    for emulator_tmp in es_sys[system]['emulators']:
      # Print the header for the emulator.
      output = output + "==== " + emulator_tmp + " ====\n\n"
      output = output + feature_printer( es_feat[emulator_tmp], system )
    return output
  elif emulator and not core:
    if verbose:
      print("Emulator with no core specified.")
    # When the emulator but not the core is specified, return all the cores
    # for that emulator.
    output = output + feature_printer( es_feat['dolphin'], system )
    return output
  elif emulator and core:
    if verbose:
      print("Both emulator and core specified.")
    # When the emulator and the core are specified, return only that core for
    # that emulator.
    output = output + feature_printer( es_feat['dolphin'], system )
    return output
  elif not emulator and core:
    if verbose:
      print("Core specified without an emulator, assuming all cores in the system.")
    return output
  else:
    print("If you see this message, I have screwed up. Please let me know how you did this at my repository.")
    # Exit the program, indicating an error has occurred.
    sys.exit(1)

  # Stuff below here to erase later.
  # Test
  print("This code should not execute.")

  # Grab a list of all systems:
  es_sys.keys()

  # Grab all the metadata, emulator list and readme info for a system:
  es_sys['wii']

  # List their emulators and their cores:
  es_sys['wii']['emulators']

  # List the cores for a specific emulator:
  es_sys['wii']['emulators']['libretro']

  # Grab a list of all emulators for all systems:
  all_emulators = []
  counter = 0

  for current_system in es_sys.keys():
    # Safeguard to avoid errors in case there are no emulators for the system.
    if 'emulators' in es_sys[current_system].keys():
      for current_emulator in es_sys[current_system]['emulators'].keys():
        if not current_emulator in all_emulators:
          all_emulators = all_emulators + [current_emulator]
        counter = counter + 1
    else:
      print("No emulators found for the system!")

  # Grab all the features and advanced settings for Dolphin standalone:
  es_feat['dolphin']

  # Alternative way to do so:
  es_feat.get("dolphin")

  # Grab a list of all standalone emulators.
  set(es_feat)

  # Grab a list of systems for the emulator:
  es_feat['dolphin']['systems'].keys()
  # Get it as a list:
  set( es_feat['dolphin']['systems'].keys() )

# On the condition that this script is called externally by the OS, parse the
# arguments and present a nice help documentation for the stdout if requested.
if __name__ == "__main__":
  # Set up the parser.
  parser = argparse.ArgumentParser( description = "Returns all" \
  " features/options for the system, optionally filtering down to only a" \
  " specified emulator and/or core.", usage="%(prog)s [-h] [-v] <system>" \
  " [-e EMULATOR] [-c CORE]" )
  # Add available inputs.
  parser.add_argument('-v', '--verbose', help="turn on debug messages", action="store_true" )
  parser.add_argument('system', metavar='<system>', help="the system's shortname")
  parser.add_argument('-e', '--emulator', help="specified emulator, when" \
  " excluded assumes you want all emulators for the system.")
  parser.add_argument('-c', '--core', help="specified core for the emulator," \
  " when excluded assumes you want all cores for the specified system and/or" \
  " emulator.")
  # Arguments are accessed with eg. parser.parse_args().core
  # Pass the arguments through in the order of system, emulator and then core.
  sys.stdout.write( main( parser.parse_args().system, parser.parse_args().emulator, parser.parse_args().core, parser.parse_args().verbose ) )
  sys.stdout.flush()
  # Exit the program when done, indicating nothing went wrong.
  sys.exit(0)

# Grab all the features and advanced settings for Dolphin standalone and print
# them:
#try:
#  print( feature_printer( es_feat['dolphin'] ) )
#except:
#  print( "System has no advanced features." )

# Test if the

# Testing (delete later)
#print( feature_printer( es_feat['dolphin'] ) )

# Grab all the Wii-specific advanced features for Dolphin and print them:
#try:
#  dolphin_wii_options = es_feat['dolphin']['systems']['wii']
#  print( feature_printer( dolphin_wii_options ) )
#except:
#  print( "No system-specific advanced features for this emulator." )

# Testing (delete later)
#print( feature_printer( dolphin_wii_options ) )

# Grab all the features and advanced settings for Dolphin standalone:
#es_feat_dolphin = es_feat.features.select_one( 'emulator[name="dolphin"]' )
# Grab all the features and advanced settings for a specific system using
# Dolphin:
#es_feat_dolphin_wii = es_feat_dolphin.select_one( 'system[name="wii"]' )
# Grab all the features and advanced settings for any core named Dolphin:
#es_feat_dolphin_core = es_feat.features.select( 'core[name="dolphin"]' )

# Filter down to just Libretro cores.
#es_feat_libretro = es_feat.features.select_one( 'emulator[name="libretro"]' )
# Grab all the features and advanced settings for Libretro/Dolphin:
#es_feat_libretro_dolphin = es_feat_libretro.select_one( 'core[name="dolphin"]' )
