#!/usr/bin/python3
def feature_printer( emulator_feature_dict, system, emulator = None ):
  "Usage: feature_printer( <emulator_feature_dict> )\nPrints out all the" \
  + " standard and advanced settings. Requires the dict to just contain the" \
  + " list of features like es_feat['dolphin']."

  # Define a local temporary variable:
  feature_string_tmp = ""

  # If an emulator was specified:
  if emulator == None:
    emulator_feature_dict = emulator_feature_dict[emulator]

  # Test if a system emulator even has any features at all:
  try:
    emulator_feature_dict['features']
  except:
    feature_string_tmp = feature_string_tmp + "No detected standard options " \
    + "for this system emulator."
  else:
    feature_string_tmp = feature_string_tmp + "Standardized features available:"
    # Start a for loop for all the elements in the standard feature list.
    for feature_tmp in set(emulator_feature_dict['features']):
      feature_string_tmp = feature_string_tmp + " ''" + system + "." \
      + feature_tmp + "''"

  # New lines to separate from the rest.
  feature_string_tmp = feature_string_tmp + "\n\n"

  # Test if a system has advanced features to begin with:
  try:
    emulator_feature_dict['cfeatures']
  except:
    feature_string_tmp = feature_string_tmp + "There are no advanced system" \
    + " options for this system emulator."
    return feature_string_tmp
  else:
    feature_string_tmp = feature_string_tmp + "^ ES setting name" \
    " ''batocera.conf key'' ^ Description >> ES option ''key value'' ^\n"

  # Create a for loop that repeats for every advanced setting.
  # "feature_tmp" is the particular advanced setting currently in the loop.
  for feature_tmp in emulator_feature_dict['cfeatures']:
    # Grab the option prompt, batocera.conf line and description and append it.
    feature_string_tmp = feature_string_tmp + "| **" \
    + emulator_feature_dict['cfeatures'][feature_tmp]['prompt'] + " \'\'" \
    + system + "." + feature_tmp + "\'\'** | " \
    + emulator_feature_dict['cfeatures'][feature_tmp]['description'] \
    + "\\\\ >> "
    # In order to get all the choices, we need to define some things.
    choice_list_tmp = emulator_feature_dict['cfeatures'][feature_tmp]['choices']
    # Max value of choices to help with detecting when we are at the last
    # choice.
    total_choices = len(choice_list_tmp)
    # Counter.
    current_choice_no = 1
    # Loop to print all the choices that can be chosen:
    for choice in choice_list_tmp:
      # Print the ES value, followed by the batocera.conf value:
      feature_string_tmp = feature_string_tmp + choice + " \'\'" \
      + str(choice_list_tmp[choice]) + "\'\'"
      # Add a comma if not the last value, otherwise end with a period.
      if current_choice_no != total_choices:
        feature_string_tmp = feature_string_tmp + ", "
        current_choice_no = current_choice_no + 1
      else:
        feature_string_tmp = feature_string_tmp + ". |\n"

  feature_string_tmp = feature_string_tmp + "\n"
  return feature_string_tmp
