#!/usr/bin/python3
def summary_printer( system_dict, system ):
  "Usage: summary_printer( <system_dict> )\nPrints out the system summary info."
  # Requires the dict to contain the system like wii_system = es_sys['wii']

  # Define a local temporary variable:
  system_string_tmp = "<WRAP group>\n<WRAP round box twothirds column>\n{{ https://raw.githubusercontent.com/fabricecaruso/es-theme-carbon/master/art/logos/" + system + ".svg?nolink |}}\n\n====== " + system_dict['name'] + " ======\n\nReleased "
  # Manufacturer?
  if system_dict['manufacturer']:
    system_string_tmp = system_string_tmp + "by " + system_dict['manufacturer']
  if system_dict['release']:
    system_string_tmp = system_string_tmp + "in " + str(system_dict['release'])
  system_string_tmp = system_string_tmp + ".\n</WRAP>\n\n<WRAP third column>{{ https://raw.githubusercontent.com/fabricecaruso/es-theme-carbon/master/art/consoles/" + system + ".png?nolink&260 |}}\n</WRAP>\n</WRAP>\n\n==== Quick reference ====\n\n"

  # The below can be approached completely differently, by just accessing the values in the dictionary more directly instead of recreating it. Tackle this tomorrow.
  # Make a list of all the emulators and one for all cores.
  emulators = list(es_sys[system]['emulators'])
  cores = []
  for current_emulator in emulators:
    for current_core in es_sys[system]['emulators'][current_emulator]:
      # Convert current core to a single element object and append it.
      cores = cores + list([current_core])
  # Create new string just for the table header.
  table_header = ""
  # If there's multiple cores, add them to the dictionary.
  if not len(cores) == 1:
    # Add section to the table header string.
    table_header = table_header + "^ Emulators ^"
    # Loop to grab all the emulators and create their own lists.
    for temp2 in cores:
      
  # If the table wasn't appended at all, don't bother with a table.
  if not table == "":
    # Continue from here.
  # Make the bullet points.
  system_string_tmp = system_string_tmp + "  * **Emulator:** " + cores[0] + "\n"
  # Append elements to the table.

  return system_string_tmp
