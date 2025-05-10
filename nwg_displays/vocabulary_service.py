import os
import sys
from typing import Dict, Any, Optional
from nwg_displays.tools import eprint, load_json, load_shell_data


class VocabularyService:
    def __init__(self) -> None:
        self._vocabulary: Dict[str, str] = {}
        self._is_loaded = False

    def load(self, vocabulary_dir_name: str) -> None:
        """
        Load vocabulary from files, starting with English and then applying
        translations from the user's locale if available.
        """
        # Basic vocabulary (for en_US)
        base_voc = load_json(os.path.join(vocabulary_dir_name, "langs", "en_US.json"))
        if not base_voc:
            eprint("Failed loading vocabulary, terminating")
            sys.exit(1)

        self._vocabulary = base_voc

        # Determine language from environment or shell data
        shell_data = load_shell_data()
        lang = os.getenv("LANG")
        if lang is None:
            lang = "en_US"
        else:
            lang = (
                lang.split(".")[0]
                if not shell_data.get("interface-locale")
                else shell_data["interface-locale"]
            )

        # Translate if translation available
        if lang != "en_US":
            loc_file = os.path.join(
                vocabulary_dir_name, "langs", "{}.json".format(lang)
            )
            if os.path.isfile(loc_file):
                # Localized vocabulary
                loc = load_json(loc_file)
                if not loc:
                    eprint("Failed loading translation into '{}'".format(lang))
                else:
                    for key in loc:
                        self._vocabulary[key] = loc[key]

        self._is_loaded = True

    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a vocabulary item by key, with an optional default value.

        Args:
            key: The vocabulary key to look up
            default: The default value to return if key not found. If None and the key
                     is not found, returns the key with first letter capitalized.

        Returns:
            The vocabulary string or default value
        """
        if not self._is_loaded:
            eprint("Warning: Vocabulary not loaded before use")

        if default is None:
            # If no default provided, use the key with first letter capitalized
            default = key.capitalize()

        return self._vocabulary.get(key, default)

    def is_loaded(self) -> bool:
        """Check if vocabulary has been loaded"""
        return self._is_loaded

    def get_all(self) -> Dict[str, str]:
        """Get all vocabulary items"""
        return self._vocabulary.copy()
