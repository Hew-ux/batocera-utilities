#!/usr/bin/python3
import yaml
import re
import argparse
#import os
#import shutil
import sys
import requests
from collections import OrderedDict
from operator import itemgetter

# This is used to organise the loader. Not sure if want.
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

class EsSystemConf:

    default_parentpath = "/userdata/roms"
    default_command    = "python /usr/lib/python3.9/site-packages/configgen/emulatorlauncher.py %CONTROLLERSCONFIG% -system %SYSTEM% -rom %ROM%"

    # Generate the es_systems.cfg file by searching the information in the es_system.yml file
    @staticmethod
    def generate(system, es_sys, featuresYaml, verbose):
        # If default, download the latest es_sys from the Github.
        if not es_sys:
            es_sys_rules = yaml.safe_load( requests.get( "https://raw.githubusercontent.com/batocera-linux/batocera.linux/master/package/batocera/emulationstation/batocera-es-system/es_systems.yml", allow_redirects=True ).text )
        else:
            es_sys_rules = yaml.safe_load(open(es_sys, "r"))
        es_system = ""

        # sort to be determinist
        #sortedRules = sorted(es_sys_rules)

        if verbose:
            print("Generating the system summary...")
        # What if the user inputted an invalid system? Let's give them a helpful message.
        if not system in es_sys_rules.keys():
            print( "System not found!" )
            # Grab all the available systems and put them into a list object.
            available_systems_sorted = list(es_sys_rules.keys())
            # Sort that list.
            available_systems_sorted.sort()
            # Print out the error message.
            print( "Available systems: " + str(available_systems_sorted) )
            # Exit the program, indicating that an error occurred.
            sys.exit(2)
        # Append the information.
        es_system += EsSystemConf.generateSystem(system, es_sys_rules[system], verbose)

        if verbose:
            print("Generating the feature lists...")
        # Generate all the feature text.
        es_feature = EsSystemConf.createEsFeatures(system, featuresYaml, es_sys_rules[system]['emulators'])

        # Generate the controls.
        controls = EsSystemConf.createControls(system, es_sys_rules[system]['emulators'])

        return { 'es_systems': es_system , 'es_features': es_feature, 'controls': controls }

    # Generate emulator system
    @staticmethod
    def generateSystem(system, rules, verbose):
        listEmulatorsTxt = EsSystemConf.listEmulators(system, rules)

        #pathValue      = EsSystemConf.systemPath(system, rules)
        platformValue  = EsSystemConf.systemPlatform(system, rules)
        #listExtensions = EsSystemConf.listExtension(rules, False)
        groupValue     = EsSystemConf.systemGroup(system, rules)
        # This can be per-core, but needs to be deterministically coded later.
        #command        = EsSystemConf.commandName(rules)

        # Opening WRAPs.
        systemTxt = "<WRAP group>\n<WRAP round box twothirds column>\n"
        # Embed logo from es-carbon. Concatenation is easier to understand here.
        systemTxt += "{{ https://raw.githubusercontent.com/fabricecaruso/es-theme-carbon/master/art/logos/" + system + ".svg?nolink&h=300 }}\n\n"
        # Main header.
        systemTxt += f"====== {rules['name']} ======\n\n"
        # Summary intro, full name.
        systemTxt += f"The {rules['name']} is"
        systemTxt += f" a {rules['hardware']}"
        systemTxt += f" developed by {rules['manufacturer']}."
        systemTxt += f" It was released in {rules['release']}.\n\n"
        # Platform (metadata scraper group), theme (theme to load from current theme-set) and whether it's grouped or not.
        if platformValue != "":
            systemTxt += f"This system scrapes metadata for the ''{platformValue}'' group(s)"
        systemTxt += f" and loads the ''{EsSystemConf.themeName(system, rules)}'' set from the currently selected theme, if available.\n\n"
        if groupValue != "":
            systemTxt += "Grouped with the %s group of systems.\n\n" % (groupValue)  

        # Close WRAP round box twothirds column, begin WRAP third column.
        systemTxt += "</WRAP>\n\n<WRAP third column>\n"
        # Embed console art from es-carbon.
        systemTxt += "{{ https://raw.githubusercontent.com/fabricecaruso/es-theme-carbon/master/art/consoles/" + system + ".png?nolink&350 |}}\n"
        # Close both WRAPs.
        systemTxt += "</WRAP>\n</WRAP>\n\n"

        # Quick reference section.
        systemTxt += "==== Quick reference ====\n\n"
        systemTxt += listEmulatorsTxt
        systemTxt += "\n"
        return systemTxt

    # Returns the path to the rom folder for the emulator
    @staticmethod
    def systemPath(system, rules):
        if "path" in rules:
            if rules["path"] is None:
                return ""
            else:
                if rules["path"][0] == "/": # absolute path
                    return rules["path"]
                else:
                    return EsSystemConf.default_parentpath + "/" + rules["path"]
        return EsSystemConf.default_parentpath + "/" + system

    # Determines where the subfolder path is if it exists.
    # Not necessary for wiki-gen but could come in handy, keeping for now.
    @staticmethod
    def systemSubRomsDir(system, data):
        if "path" in data:
            if data["path"] is None:
                return None # no path to create
            else:
                if data["path"][0] == "/": # absolute path
                    return None # don't create absolute paths
                else:
                    return data["path"]
        return system
        
    # Returns the platform (for metadata scraping) for the emulator.
    @staticmethod
    def systemPlatform(system, rules):
        # Only execute if the is a platform specified in the rules.
        if "platform" in rules:
            if rules['platform'] is None:
                return ""
            # Return the string as-is.
            return rules['platform']
        # If there is no platform specified, assume it is the system shortname itself.
        return system

    # Some emulators have different names between roms and themes
    @staticmethod
    def themeName(system, data):
        if "theme" in data:
          return data["theme"]
        return system

    # In case you need to specify a different command line 
    @staticmethod
    def commandName(data):
        if "command" in data:
          return data["command"]
        return EsSystemConf.default_command

    # Creates an _info.txt file inside the emulators folders in roms with the information of the supported extensions.
    # This is unneccessary for wiki-gen, but will keep (for now).
    @staticmethod
    def infoSystem(system, data, romsdir):
        subdir = EsSystemConf.systemSubRomsDir(system, data)

        # nothing to create
        if subdir is None:
            return

        infoTxt = "## SYSTEM %s ##\n" % (data["name"].upper())
        infoTxt += "-------------------------------------------------------------------------------\n"
        infoTxt += "ROM files extensions accepted: \"%s\"\n" % (EsSystemConf.listExtension(data, False))
        if "comment_en" in data:
            infoTxt += "\n" + data["comment_en"]
        infoTxt += "-------------------------------------------------------------------------------\n"
        infoTxt += "Extensions des fichiers ROMs permises: \"%s\"\n" % (EsSystemConf.listExtension(data, False))
        if "comment_fr" in data:
            infoTxt += "\n" + data["comment_fr"]

        arqtxt = romsdir + "/" + subdir + "/" + "_info.txt"

        systemsInfo = open(arqtxt, 'w')
        systemsInfo.write(infoTxt)
        systemsInfo.close()

    # Write the information in the es_features.cfg file
    @staticmethod
    def createEsFeatures(system, featuresYaml, SystemSpecificEmulators):
        # If no featuresyaml specified, download the latest from the github.
        if not featuresYaml:
            features = yaml.safe_load(requests.get( "https://raw.githubusercontent.com/batocera-linux/batocera.linux/master/package/batocera/emulationstation/batocera-es-system/es_features.yml", allow_redirects=True ).text)
        else:
            features = yaml.safe_load(open(featuresYaml, "r"))
        #features = ordered_load(open(featuresYaml, "r"))
        # Header
        featuresTxt = "===== Emulators =====\n\n"

        for emulator in SystemSpecificEmulators:
            # Initialize the emulator_featuresTxt string. Since videomode is available to all systems, we can initialize with that.
            emulator_featuresTxt = f"''{system}.videomode''"
            if "features" in features[emulator]:
                for feature in features[emulator]["features"]:
                    if emulator_featuresTxt != "":
                        emulator_featuresTxt += ", "
                    emulator_featuresTxt += f"''{system}.{feature}''"
            # Since RetroArch is so prevalent, it's worth having a stock description of it.
            if emulator == "libretro":
                featuresTxt += "==== RetroArch ====\n\n[[https://docs.libretro.com/|RetroArch]] (formerly SSNES), is a ubiquitous frontend that can run multiple \"cores\", which are essentially the emulators themselves. The most common cores use the [[https://www.libretro.com/|libretro]] API, so that's why cores run in RetroArch in Batocera are referred to as \"libretro/(core name)\".\n\n"
            else:
                featuresTxt += f"==== {emulator} ====\n\n"

            # Special exceptions for special emulators.
            if emulator == "libretro":
                featuresTxt += "=== RetroArch configuration ===\n\n"
                featuresTxt += "RetroArch offers a **Quick Menu** accessed by pressing ''[HOTKEY]'' + {{:wiki:south.png?nolink&20|South button (B SNES)}} which can be used to alter various things like [[:advanced_retroarch_settings|RetroArch and core options]], and [[:remapping_controls_per_emulator|controller mapping]].\n\n"
                featuresTxt += f"Standardized features available to all libretro cores: {emulator_featuresTxt}\n\n"
            else:
                featuresTxt += f"=== {emulator} configuration ===\n\nStandardized features available to all cores of this emulator: {emulator_featuresTxt}\n\n"
            
            # Table header.
            tableheader = "^ ES setting name ''batocera.conf key'' ^ Description => ES option ''key value'' ^\n"
            # Optimization to only execute the following if there is at least one of these subdictionaries in the emulator dictionary.
            if "cores" in features[emulator] or "systems" in features[emulator] or "cfeatures" in features[emulator]:
                if "cfeatures" in features[emulator]:
                    # Insert text for the settings that apply to all systems for that emulator.
                    featuresTxt += tableheader
                    featuresTxt += "^ Settings that apply to all cores of this emulator |\n"
                    for cfeature in features[emulator]["cfeatures"]:
                        featuresTxt += EsSystemConf.featureprinter(system, features[emulator], cfeature)
                    featuresTxt += "\n"
                # In the case that the emulator contains a cores subdictionary:
                if "cores" in features[emulator]:
                    # Loop through just the emulators that system supports.
                    for core in SystemSpecificEmulators[emulator]:
                        # Header for the unique core.
                        featuresTxt += f"=== {emulator}/{core} ===\n\n"
                        # Initialize temporary string.
                        core_featuresTxt = ""
                        # Safeguard for if the core doesn't have any features at all.
                        if core in features[emulator]["cores"]:
                            # Subheader for the specific emulator/core.
                            featuresTxt += f"== {emulator}/{core} configuration ==\n\n"
                            # Grab all standardized features.
                            if "features" in features[emulator]["cores"][core]:
                                for feature in features[emulator]["cores"][core]["features"]:
                                    if core_featuresTxt != "":
                                        core_featuresTxt += ", "
                                    core_featuresTxt += feature
                                if not features[emulator]["cores"][core]:
                                    featuresTxt += f"Standardized features for this core: {core_featuresTxt}\n\n"
                            # Optimization to only execute the following if the core has custom features.
                            if "cfeatures" in features[emulator]["cores"][core] or "systems" in features[emulator]["cores"][core]:
                                # Create the feature table.
                                featuresTxt += tableheader
                                # Print out the custom features if applicable.
                                if "cfeatures" in features[emulator]["cores"][core]:
                                   featuresTxt += "^ Settings that apply to all systems this core supports |\n"
                                   for cfeature in features[emulator]["cores"][core]["cfeatures"]:
                                       featuresTxt += EsSystemConf.featureprinter(system, features[emulator]["cores"][core], cfeature)
                                # Print out the custom features that only apply to particular systems.
                                if "systems" in features[emulator]["cores"][core]:
                                   for system in features[emulator]["cores"][core]["systems"]:
                                       system_featuresTxt = ""
                                       featuresTxt += f"^ Settings specific to {system} |"
                                       if "features" in features[emulator]["cores"][core]["systems"][system]:
                                           for feature in features[emulator]["cores"][core]["systems"][system]["features"]:
                                               if system_featuresTxt != "":
                                                   system_featuresTxt += ", "
                                               system_featuresTxt += f"{feature}."
                                           featuresTxt += f" Standardized features: {system_featuresTxt} |"
                                       featuresTxt += f"\n"
                                       if "cfeatures" in features[emulator]["cores"][core]["systems"][system]:
                                           for cfeature in features[emulator]["cores"][core]["systems"][system]["cfeatures"]:
                                               featuresTxt += EsSystemConf.featureprinter(system, features[emulator]["cores"][core]["systems"][system], cfeature)
                                # Insert text after the table for system-specific to core options.
                                featuresTxt += "\n"
                            #else:
                                # Text before the table only when there's no custom or system subdictionaries for the core. Currently unused.
                                #featuresTxt += "uniquetext {} somemoreuniquetext {} whatami\n".format(core, core_featuresTxt)
                # For system subdictionaries in the feature list:
                if "systems" in features[emulator]:
                    # Insert text before the table. Currently unused.
                    #featuresTxt += ""
                    # Grab the features only for all systems. We don't want this as we only want one system.
                    #for system in features[emulator]["systems"]:
                    system_featuresTxt = ""
                    if system in features[emulator]["systems"]:
                        if "features" in features[emulator]["systems"][system]:
                            for feature in features[emulator]["systems"][system]["features"]:
                                if system_featuresTxt != "":
                                    system_featuresTxt += ", "
                                system_featuresTxt += f"{feature}."
                        featuresTxt += "^ Settings specific to ''{}'' |".format(system)
                        # What if there are no additional standardized features?
                        if not system_featuresTxt:
                            featuresTxt += "\n"
                        else:
                            featuresTxt += " Standardized features for this system only: {} |\n".format(system_featuresTxt)
                        # Safeguard to only attempt the loop if there are custom features present.
                        if "cfeatures" in features[emulator]["systems"][system]:
                            # Iterate through all the custom features on this emulator for this system only.
                            for cfeature in features[emulator]["systems"][system]["cfeatures"]:
                                # Call special function to list the feature and all its choices.
                                featuresTxt += EsSystemConf.featureprinter(system, features[emulator]["systems"][system], cfeature)
                        # Insert text after the table for system-specific settings. Currently unused.
                        #featuresTxt += ""
                #featuresTxt += "\n"
            #else:
                #featuresTxt += "\n"
        #featuresTxt += "\n"
        return featuresTxt

    # Feature printer. Return a string of the feature intended to be used in the table.
    @staticmethod
    def featureprinter(system, data, custfeatname):
        description = ""
        rettext = ""
        if 'description' in data['cfeatures'][custfeatname]:
            description = data['cfeatures'][custfeatname]['description']
        rettext += f"| **{data['cfeatures'][custfeatname]['prompt']} ''{system}.{custfeatname}''** | {description}\\\\ => "
        choicetext = ""
        for choice in data['cfeatures'][custfeatname]['choices']:
            if choicetext != "":
                choicetext += ", "
            choicetext += f"{choice} ''{data['cfeatures'][custfeatname]['choices'][choice]}''"
        rettext += f"{choicetext}. |\n"
        return rettext

    # Returns the extensions supported by the emulator
    @staticmethod
    def listExtension(data, uppercase):
        extension = ""
        if "extensions" in data:
            extensions = data["extensions"]
            firstExt = True
            for item in extensions:
                if not firstExt:
                    extension += " "
                firstExt = False
                extension += "." + str(item).lower()
                if uppercase == True:
                    extension += " ." + str(item).upper()
        return extension

    # Returns group to emulator rom folder
    @staticmethod
    def systemGroup(system, data):
        if "group" in data:
            if data["group"] is None:
                return ""
            return data["group"]
        return ""

    # Returns the enabled cores in a string
    @staticmethod
    def listEmulators(system, rules):
        # Set up some known values.
        pathValue      = EsSystemConf.systemPath(system, rules)
        listExtensions = EsSystemConf.listExtension(rules, False)

        # What we will be returning later.
        listEmulatorsTxt = ""
        # Initialize variable to add to later!
        emulators = {}
        # Safeguard in case an system doesn't have emulator (like ports?)
        if "emulators" in rules:
            emulators = rules["emulators"]

        # What if there's only one emulator?
        if len(emulators) == 1:
            # What's the emulator name?
            listEmulatorsTxt += f"  * **Emulator:** {list(rules['emulators'].keys())[0]}"
            # Make a list of all the cores.
            corelist = EsSystemConf.listcores(system, rules)
            # What if this one emulator has multiple cores?
            if len(corelist) >= 2:
                listEmulatorsTxt += "\n    * **Cores available:** "
                # We need a temp string with a unique name to help with counting.
                whackycore = ""
                for core in rules['emulators'][list(rules['emulators'].keys())[0]]:
                    if whackycore != "":
                        whackycore += ", "
                    whackycore += f"{core}"
                listEmulatorsTxt += whackycore
            else:
                # Otherwise, we'll just append the only core.
                listEmulatorsTxt += f"/{list(rules['emulators'][list(rules['emulators'].keys())[0]])[0]}"
            listEmulatorsTxt += "\n"
            if listExtensions != "":
                # Folder path?
                if pathValue != "":
                    listEmulatorsTxt += f"  * **Folder:** ''{pathValue}''\n"
            # Accepted ROMs?
            listEmulatorsTxt += "  * **Accepted ROM formats:**"
            # Loop to add all the successive formats.
            for extension in rules['extensions']:
                listEmulatorsTxt += f" ''.{extension}''"
            listEmulatorsTxt += "\n"
            # BIOS files (WIP)
            # BIOS required? (WIP)
            # Configuration via? (WIP, not sure if this can be automated at all)
            # Launch command (WIP, needs to be system-specific)
            # command        = EsSystemConf.commandName(rules)
            #listEmulatorsTxt += f"  * **Launch command:** {command}"
        else:
            # New variable as we don't want to write directly into listEmulatorsTxt yet.
            emulatorsTxt = ""
            # To keep track of if emulators/cores use different extensions.
            uniqueroms = False
            for emulator in emulators:
                emulatorData = rules["emulators"][emulator]
                # Opening part.
                emulatorTxt = f"| [[#{emulator}"

                # CORES
                corelist = EsSystemConf.listcores(system, rules)
                coresTxt = ""
                # If there's only one core:
                if len(corelist) == 1:
                    coresTxt += f"/{corelist[0]}|{emulator}/{corelist[0]}]] |"
                    # Wipe the string for this core in case the last core for the last emulator had any.
                    incompatible_extensionsTxt = ""
                    if "incompatible_extensions" in emulatorData[core]:
                        for ext in emulatorData[core]["incompatible_extensions"]:
                            if incompatible_extensionsTxt != "":
                                incompatible_extensionsTxt += " "
                            incompatible_extensionsTxt += "." + ext.lower()
                        incompatible_extensionsTxt = " incompatible_extensions=\"" + incompatible_extensionsTxt + "\""
                    coresTxt += "\n"
                else:
                    for core in emulatorData:
                        # Only for cores not the first.
                        if not core == list(emulatorData.keys())[0]:
                            # Insert the emulator/core name.
                            coresTxt += f"| [[#{emulator}/{core}|└───/{core}]] |"
                        else:
                            # Insert the full emulator/core name.
                            coresTxt += f"/{core}|{emulator}/{core}]] |"
                        incompatible_extensionsTxt = ""
                        if "incompatible_extensions" in emulatorData[core]:
                            for ext in emulatorData[core]["incompatible_extensions"]:
                                if incompatible_extensionsTxt != "":
                                    incompatible_extensionsTxt += " "
                                incompatible_extensionsTxt += "." + ext.lower()
                            coresTxt += f" Incompatible extensions: {incompatible_extensionsTxt} |"
                            # Set flag to create table header later.
                            uniqueroms = True
                        # Append the launch command. WIP
                        #coresTxt += EsSystemConf.commandName(rules)
                        coresTxt += "\n"

                # What if there were no cores lmao?
                if coresTxt == "":
                    # Append NOTHING!
                    emulatorTxt = ""
                else:
                    # Append the core information.
                    emulatorTxt  += coresTxt
                    emulatorsTxt += emulatorTxt
            # Start the table.
            listEmulatorsTxt += "^ Emulators ^"
            # What if multiple folders?
            #if:
            # What if multiple accepted ROM formats
            if uniqueroms:
                listEmulatorsTxt += " Accepted ROM formats ^"
            # What if multiple BIOS files (is there a way to check for that?)
            #if:
            # Configuration via? (WIP, not sure if this can be automated at all)
            # Launch command (hm... should this be in the detailed section?)
            #listEmulatorsTxt += " Launch command ^"
            #command        = EsSystemConf.commandName(rules)
            # End the header.
            listEmulatorsTxt += "\n"
            # Append the table elements from earlier.
            listEmulatorsTxt += emulatorsTxt

        return listEmulatorsTxt

    @staticmethod
    def listcores(system, systemsYaml):
        listEmulatorsTxt = ""
        emulators = {}
        if "emulators" in systemsYaml:
            emulators = systemsYaml["emulators"]
        corelist = []
        for emulator in emulators:
            emulatorData = systemsYaml["emulators"][emulator]
            #corelist = []
            for core in emulatorData:
                corelist += [core]
        return corelist

    @staticmethod
    def createControls(system, rules):
        # Header.
        controlTxt = "===== Controls =====\n\n"
        controlTxt += "{{ https://raw.githubusercontent.com/batocera-linux/batocera-controller-overlays/master/solid-4k/" + system + ".png }}\n"
        
        return controlTxt        

if __name__ == "__main__":
  # Set up the parser.
  parser = argparse.ArgumentParser( description = "Returns all" \
  " features/options for the system, optionally filtering down to only a" \
  " specified emulator and/or core.", usage="%(prog)s [-h] [-v] <system>" \
  " [-s SYSTEMS_YML] [-f FEATURES_YML]" )
  # Add available inputs.
  parser.add_argument('-v', '--verbose', help="turn on debug messages", action="store_true" )
  parser.add_argument('system', metavar='<system>', help="The system's shortname, required. If you insert an invalid name you will be shown a list of valid names.")
  # If you'd like to see how these flags would have worked, check the prototype
  # script iteration. It would be too complicated to implement these options here. Maybe in the future.
  #parser.add_argument('-e', '--emulator', help="specified emulator, when" \
  #" excluded assumes you want all emulators for the system.")
  #parser.add_argument('-c', '--core', help="specified core for the emulator," \
  #" when excluded assumes you want all cores for the specified system and/or" \
  #" emulator.")
  parser.add_argument('-s', '--systems_yml', help="(Optional) Specify a es_systems.yml definition file. If unspecified, will download the latest from the batocera.linux repository.")
  parser.add_argument('-f', '--features_yml', help="(Optional) Specify a es_features.yml definition file. If unspecified, will download the latest from the batocera.linux repository.")
  args = parser.parse_args()

  # Save the output of the generator to a dictionary to be accessed later.
  output = EsSystemConf.generate(args.system, args.systems_yml, args.features_yml, args.verbose)
  # Send the two string results to stdout. Encode to 'utf-8' then write directly to the buffer to avoid 'latin-1' encoding errors (probably not a good idea but makes this script more robust).
  sys.stdout.buffer.write( output['es_systems'].encode('utf-8') )
  sys.stdout.write( output['es_features'] )
  sys.stdout.write( output['controls'] )
  sys.stdout.flush()
  sys.exit(0)
