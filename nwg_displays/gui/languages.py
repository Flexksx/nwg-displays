import os
import sys
from nwg_displays.tools import eprint, load_json, load_shell_data


def load_vocabulary(vocabulary_dir_name: str) -> None:
    global voc
    # basic vocabulary (for en_US)
    voc = load_json(os.path.join(vocabulary_dir_name, "langs", "en_US.json"))
    if not voc:
        eprint("Failed loading vocabulary, terminating")
        sys.exit(1)

    shell_data = load_shell_data()

    lang = os.getenv("LANG")
    if lang is None:
        lang = "en_US"
    else:
        lang = (
            lang.split(".")[0]
            if not shell_data["interface-locale"]
            else shell_data["interface-locale"]
        )

    # translate if translation available
    if lang != "en_US":
        loc_file = os.path.join(vocabulary_dir_name, "langs", "{}.json".format(lang))
        if os.path.isfile(loc_file):
            # localized vocabulary
            loc = load_json(loc_file)
            if not loc:
                eprint("Failed loading translation into '{}'".format(lang))
            else:
                for key in loc:
                    voc[key] = loc[key]
