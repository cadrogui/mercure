import json
import os
from pathlib import Path


configuration_timestamp = 0
configuration_filename  = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+'/../configuration/hermes.json')

hermes_defaults = {
    'appliance_name'           : 'Hermes Router',
    'incoming_folder'          : './incoming',
    'outgoing_folder'          : './outgoing',
    'success_folder'           : './success',
    'error_folder'             : './error',
    'discard_folder'           : './discard',
    'router_scan_interval'     :  1,
    'dispatcher_scan_interval' :  1,
    'series_complete_trigger'  : 60,
    'graphite_ip'              : '',
    'graphite_port'            : 2003,
    "destinations"             : {},
    "rules"                    : {}
}

hermes = {}


def read_config():
    global hermes
    global configuration_timestamp    
    configuration_file = Path(configuration_filename)

    # Check for existence of lock file
    lock_file=Path(configuration_file.parent/configuration_file.stem).with_suffix(".lock")

    if lock_file.exists():
        raise ResourceWarning(f"Configuration file locked: {lock_file}")

    if configuration_file.exists():
        # Get the modification date/time of the configuration file
        stat = os.stat(configuration_filename)
        try:
            timestamp=stat.st_mtime
        except AttributeError:
            timestamp=0

        # Check if the configuration file is newer than the version
        # loaded into memory. If not, return
        if timestamp <= configuration_timestamp:
            return hermes               

        print("Reading configuration from: ", configuration_filename)

        with open(configuration_file, "r") as json_file:
            loaded_config=json.load(json_file)
            # Reset configuration to default values (to ensure all needed
            # keys are present in the configuration)
            hermes=hermes_defaults
            # Now merge with values loaded from configuration file
            hermes.update(loaded_config)

            # TODO: Check configuration for errors (esp destinations and rules)

            # Check if directories exist
            if not checkFolders():
                raise FileNotFoundError("Configured folders missing")

            print("")
            print("Active configuration: ")
            print(json.dumps(hermes, indent=4))
            print("")
            configuration_timestamp=timestamp
            return hermes
    else:
        raise FileNotFoundError(f"Configuration file not fould: {configuration_file}")


def checkFolders():
    for entry in ['incoming_folder','outgoing_folder','success_folder','error_folder','discard_folder']:        
        if not Path(hermes[entry]).exists():
            print("ERROR: Folder not found ",hermes[entry])
            return False
    return True

