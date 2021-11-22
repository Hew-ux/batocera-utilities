# wiki-gen
 Used to automatically generate a template for a system page on the wiki.

## About

 Originally, I had wrote this code from scratch, using logical deductions as to what would be required. After getting a working prototype, I discovered that there was a lot of information missing, and that the way Batocera itself interprets the information is very complicated and naunced. Instead of reinventing the wheel, I restarted the project based on the original scripts Batocera uses available at https://github.com/batocera-linux/batocera.linux/blob/master/package/batocera/emulationstation/batocera-es-system/batocera-es-system.py and made the necessary modifications to it for my purposes.

 The original prototype can be viewed in the `prototype` folder.

## Usage

 Python 3.7 or higher is required to run this script. Requires `yaml` module to be accessible, which can be installed with:

```
pip3 install pyyaml
```

Just run `python3 wiki-gen.py <system shortname>` to generate a page for that system. For example:

```python3 wiki-gen.py psx```

By default, the latest `es_systems.yml` and `es_features.yml`, so please don't spam it or automate it frequently. If you'd like to use a local copy of those files, you can utilise the optional `-s` and `-f` flags. I've included a sample es_features and es_systems file to test with, based on the equivalent files at https://github.com/batocera-linux/batocera.linux/tree/master/package/batocera/emulationstation/batocera-es-system

For further syntax help, the program's usage documentation can be summoned with the `-h` flag. Here's a static copy of that output:

```
usage: wiki-page-gen.py [-h] [-v] <system> [-s SYSTEMS_YML] [-f FEATURES_YML]

Returns all features/options for the system, optionally filtering down to only
a specified emulator and/or core.

positional arguments:
  <system>              The system's shortname, required. If you insert an
                        invalid name you will be shown a list of valid names.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         turn on debug messages
  -s SYSTEMS_YML, --systems_yml SYSTEMS_YML
                        es_systems.yml definition file
  -f FEATURES_YML, --features_yml FEATURES_YML
                        es_features.yml definition file
```

## Licensing
 This program uses the LGPL v3 license for being a derivative of "code specifically written by the Batocera Linux team". More info in the `LICENSE` file.
