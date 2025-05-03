import os
import json
import datetime
from typing import List, Dict, Any, Optional

from nwg_displays.utils import get_profiles_dir, save_json, load_json, notify, eprint


class ProfileManager:
    """Manages the saving, loading, and application of display profiles"""

    @staticmethod
    def list_profiles() -> List[str]:
        """Returns a list of available profile names"""
        profiles_dir = get_profiles_dir()
        profiles = []
        for filename in os.listdir(profiles_dir):
            if filename.endswith(".json"):
                profiles.append(filename[:-5])  # Remove .json extension
        return profiles

    @staticmethod
    def save_profile(
        profile_name: str,
        display_buttons: List,
        outputs_activity: Dict[str, bool],
        use_desc: bool = False,
    ) -> bool:
        """Saves current configuration as a profile"""
        if not profile_name:
            return False

        profile_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "displays": [],
            "outputs_activity": outputs_activity,
            "use_desc": use_desc,
        }

        # Save data from each display button
        for db in display_buttons:
            display_data = {
                "name": db.name,
                "description": db.description,
                "x": db.x,
                "y": db.y,
                "physical_width": db.physical_width,
                "physical_height": db.physical_height,
                "transform": db.transform,
                "scale": db.scale,
                "scale_filter": db.scale_filter,
                "refresh": db.refresh,
                "dpms": db.dpms,
                "adaptive_sync": db.adaptive_sync,
                "custom_mode": db.custom_mode,
                "mirror": db.mirror,
                "ten_bit": db.ten_bit,
            }
            profile_data["displays"].append(display_data)

        # Save profile to file
        profile_path = os.path.join(get_profiles_dir(), f"{profile_name}.json")
        return save_json(profile_data, profile_path)

    @staticmethod
    def load_profile(profile_name: str) -> Optional[Dict[str, Any]]:
        """Loads a saved profile configuration"""
        if not profile_name:
            return None

        profile_path = os.path.join(get_profiles_dir(), f"{profile_name}.json")
        return load_json(profile_path)

    @staticmethod
    def delete_profile(profile_name: str) -> bool:
        """Deletes a profile"""
        try:
            profile_path = os.path.join(get_profiles_dir(), f"{profile_name}.json")
            if os.path.exists(profile_path):
                os.remove(profile_path)
                return True
            return False
        except Exception as e:
            eprint(f"Error deleting profile: {e}")
            return False

    @staticmethod
    def apply_profile(
        profile_data: Dict[str, Any],
        display_buttons: List,
        fixed: Gtk.Fixed,
        config: Dict[str, Any],
        update_form_callback=None,
    ):
        """Applies the settings from a profile"""
        outputs_activity = profile_data.get("outputs_activity", {})

        # Apply display settings directly to current outputs
        profile_displays = profile_data.get("displays", [])
        output_map = {out.name: out for out in display_buttons}

        for display_data in profile_displays:
            name = display_data.get("name")
            if name in output_map:
                db = output_map[name]
                # Update display button with profile settings
                db.x = display_data.get("x", db.x)
                db.y = display_data.get("y", db.y)
                db.physical_width = display_data.get(
                    "physical_width", db.physical_width
                )
                db.physical_height = display_data.get(
                    "physical_height", db.physical_height
                )
                db.transform = display_data.get("transform", db.transform)
                db.scale = display_data.get("scale", db.scale)
                db.scale_filter = display_data.get("scale_filter", db.scale_filter)
                db.refresh = display_data.get("refresh", db.refresh)
                db.dpms = display_data.get("dpms", db.dpms)
                db.adaptive_sync = display_data.get("adaptive_sync", db.adaptive_sync)
                db.custom_mode = display_data.get("custom_mode", db.custom_mode)
                db.mirror = display_data.get("mirror", db.mirror)
                db.ten_bit = display_data.get("ten_bit", db.ten_bit)

                # Update display position and size on the UI
                db.rescale_transform()
                fixed.move(db, db.x * config["view-scale"], db.y * config["view-scale"])

        # Update the form if a callback is provided
        if update_form_callback:
            update_form_callback()

        # Notify user
        notify(
            "Profile Loaded",
            "Configuration loaded successfully",
        )

        return outputs_activity
