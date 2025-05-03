import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from nwg_displays.profile.manager import ProfileManager
from nwg_displays.utils import notify


class ProfileDialogs:
    def __init__(
        self,
        parent_window,
        config,
        voc,
        display_buttons,
        outputs_activity,
        handle_keyboard,
        close_dialog,
        fixed,
        update_form_callback,
    ):
        self.parent_window = parent_window
        self.config = config
        self.voc = voc
        self.display_buttons = display_buttons
        self.outputs_activity = outputs_activity
        self.handle_keyboard = handle_keyboard
        self.close_dialog = close_dialog
        self.fixed = fixed
        self.update_form_callback = update_form_callback
        self.dialog_win = None

    def create_save_profile_dialog(self, btn=None):
        """Creates a dialog to save the current configuration as a profile"""
        if self.dialog_win:
            self.dialog_win.destroy()

        self.dialog_win = Gtk.Window()
        self.dialog_win.set_title(self.voc.get("save-profile", "Save Profile"))
        self.dialog_win.set_resizable(False)
        self.dialog_win.set_modal(True)
        self.dialog_win.connect("key-release-event", self.handle_keyboard)

        grid = Gtk.Grid()
        for prop in ["margin_start", "margin_end", "margin_top", "margin_bottom"]:
            grid.set_property(prop, 10)
        grid.set_column_spacing(12)
        grid.set_row_spacing(12)
        self.dialog_win.add(grid)

        # Name label and entry
        lbl = Gtk.Label()
        lbl.set_text(self.voc.get("profile-name", "Profile Name:"))
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 0, 1, 1)

        entry = Gtk.Entry()
        grid.attach(entry, 1, 0, 1, 1)

        # Existing profiles label
        profiles = ProfileManager.list_profiles()
        if profiles:
            lbl_existing = Gtk.Label()
            lbl_existing.set_markup(
                "<small>"
                + self.voc.get("existing-profiles", "Existing profiles:")
                + " "
                + ", ".join(profiles)
                + "</small>"
            )
            lbl_existing.set_line_wrap(True)
            lbl_existing.set_max_width_chars(40)
            grid.attach(lbl_existing, 0, 1, 2, 1)

        # Buttons
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(box, 0, 2, 2, 1)

        btn_save = Gtk.Button()
        btn_save.set_label(self.voc.get("save", "Save"))
        btn_save.connect("clicked", self.on_save_profile_btn, self.dialog_win, entry)
        box.pack_end(btn_save, False, False, 0)

        btn_cancel = Gtk.Button()
        btn_cancel.set_label(self.voc.get("cancel", "Cancel"))
        btn_cancel.connect("clicked", self.close_dialog, self.dialog_win)
        box.pack_end(btn_cancel, False, False, 6)

        self.dialog_win.show_all()

    def on_save_profile_btn(self, w, win, entry):
        """Handles saving a profile when the save button is clicked"""
        profile_name = entry.get_text().strip()
        if not profile_name:
            # Show error - empty name not allowed
            self.show_error_dialog(
                win, self.voc.get("error-empty-name", "Profile name cannot be empty")
            )
            return

        # Check if profile already exists
        if profile_name in ProfileManager.list_profiles():
            # Confirm overwrite
            self.confirm_overwrite_dialog(win, profile_name)
            return

        # Save profile
        if ProfileManager.save_profile(
            profile_name,
            self.display_buttons,
            self.outputs_activity,
            use_desc=self.config["use-desc"],
        ):
            notify(
                self.voc.get("profile-saved", "Profile Saved"),
                self.voc.get(
                    "profile-saved-message", "Configuration saved as '{}'"
                ).format(profile_name),
            )
            self.close_dialog(w, win)
        else:
            self.show_error_dialog(
                win, self.voc.get("error-saving-profile", "Error saving profile")
            )

    def confirm_overwrite_dialog(self, parent_win, profile_name):
        """Shows a dialog to confirm overwriting an existing profile"""
        confirm_dialog = Gtk.MessageDialog(
            transient_for=parent_win,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=self.voc.get("confirm-overwrite", "Overwrite existing profile?"),
        )
        confirm_dialog.format_secondary_text(
            self.voc.get(
                "confirm-overwrite-message",
                "Profile '{}' already exists. Do you want to overwrite it?",
            ).format(profile_name)
        )
        response = confirm_dialog.run()
        confirm_dialog.destroy()

        if response == Gtk.ResponseType.YES:
            ProfileManager.save_profile(
                profile_name,
                self.display_buttons,
                self.outputs_activity,
                use_desc=self.config["use-desc"],
            )
            notify(
                self.voc.get("profile-saved", "Profile Saved"),
                self.voc.get(
                    "profile-saved-message", "Configuration saved as '{}'"
                ).format(profile_name),
            )
            self.close_dialog(None, parent_win)

    def show_error_dialog(self, parent_win, message):
        """Shows an error dialog with the given message"""
        error_dialog = Gtk.MessageDialog(
            transient_for=parent_win,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=self.voc.get("error", "Error"),
        )
        error_dialog.format_secondary_text(message)
        error_dialog.run()
        error_dialog.destroy()

    def create_load_profile_dialog(self, btn=None):
        """Creates a dialog to load a saved profile"""
        profiles = ProfileManager.list_profiles()
        if not profiles:
            notify(
                self.voc.get("no-profiles", "No Profiles"),
                self.voc.get("no-profiles-message", "No saved profiles found"),
            )
            return

        if self.dialog_win:
            self.dialog_win.destroy()

        self.dialog_win = Gtk.Window()
        self.dialog_win.set_title(self.voc.get("load-profile", "Load Profile"))
        self.dialog_win.set_resizable(False)
        self.dialog_win.set_modal(True)
        self.dialog_win.connect("key-release-event", self.handle_keyboard)

        grid = Gtk.Grid()
        for prop in ["margin_start", "margin_end", "margin_top", "margin_bottom"]:
            grid.set_property(prop, 10)
        grid.set_column_spacing(12)
        grid.set_row_spacing(12)
        self.dialog_win.add(grid)

        # Profile selection label and combo box
        lbl = Gtk.Label()
        lbl.set_text(self.voc.get("select-profile", "Select Profile:"))
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 0, 1, 1)

        combo = Gtk.ComboBoxText()
        for profile in profiles:
            combo.append(profile, profile)
        combo.set_active(0)
        grid.attach(combo, 1, 0, 1, 1)

        # Buttons
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(box, 0, 1, 2, 1)

        btn_delete = Gtk.Button()
        btn_delete.set_label(self.voc.get("delete", "Delete"))
        btn_delete.connect(
            "clicked", self.on_delete_profile_btn, self.dialog_win, combo
        )
        box.pack_start(btn_delete, False, False, 0)

        btn_load = Gtk.Button()
        btn_load.set_label(self.voc.get("load", "Load"))
        btn_load.connect("clicked", self.on_load_profile_btn, self.dialog_win, combo)
        box.pack_end(btn_load, False, False, 0)

        btn_cancel = Gtk.Button()
        btn_cancel.set_label(self.voc.get("cancel", "Cancel"))
        btn_cancel.connect("clicked", self.close_dialog, self.dialog_win)
        box.pack_end(btn_cancel, False, False, 6)

        self.dialog_win.show_all()

    def on_load_profile_btn(self, w, win, combo):
        """Handles loading a profile when the load button is clicked"""
        profile_name = combo.get_active_id()
        if not profile_name:
            return

        profile_data = ProfileManager.load_profile(profile_name)
        if not profile_data:
            self.show_error_dialog(
                win, self.voc.get("error-loading-profile", "Error loading profile")
            )
            return

        # Apply profile settings using the ProfileManager
        self.outputs_activity = ProfileManager.apply_profile(
            profile_data,
            self.display_buttons,
            self.fixed,
            self.config,
            self.update_form_callback,
        )

        self.close_dialog(w, win)

    def on_delete_profile_btn(self, w, win, combo):
        """Handles deleting a profile when the delete button is clicked"""
        profile_name = combo.get_active_id()
        if not profile_name:
            return

        confirm_dialog = Gtk.MessageDialog(
            transient_for=win,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=self.voc.get("confirm-delete", "Delete Profile?"),
        )
        confirm_dialog.format_secondary_text(
            self.voc.get(
                "confirm-delete-message",
                "Are you sure you want to delete profile '{}'?",
            ).format(profile_name)
        )
        response = confirm_dialog.run()
        confirm_dialog.destroy()

        if response == Gtk.ResponseType.YES:
            if ProfileManager.delete_profile(profile_name):
                # Update combobox
                combo.remove_all()
                profiles = ProfileManager.list_profiles()
                for profile in profiles:
                    combo.append(profile, profile)
                if profiles:
                    combo.set_active(0)
                else:
                    # No profiles left, close dialog
                    self.close_dialog(w, win)
                    notify(
                        self.voc.get("no-profiles", "No Profiles"),
                        self.voc.get("no-profiles-message", "No saved profiles found"),
                    )
            else:
                self.show_error_dialog(win, "Failed to delete profile")
