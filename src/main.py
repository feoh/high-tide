# main.py
#
# Copyright 2023 Nokse
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from gettext import gettext as _
from typing import Any, Callable, List, cast

from gi.repository import Adw, Gio, Gtk  # pyright: ignore[reportAttributeAccessIssue]

from .lib import utils
from .lib.player_object import AudioSink
from .window import HighTideWindow


DEFAULT_FONT_DPI = 96 * 1024
TEXT_SIZE_SCALES = (1.0, 1.25, 1.5, 2.0)


class HighTideApplication(Adw.Application):
    """The main application singleton class.

    This class handles the main application lifecycle, manages global actions,
    preferences, and provides the entry point for the High Tide TIDAL music player.
    """

    def __init__(self) -> None:
        super().__init__(
            application_id="io.github.nokse22.high-tide",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        self.create_action("quit", lambda *_: self.quit(), ["<primary>q", "<primary>w"])
        self.create_action("about", self.on_about_action)
        self.create_action(
            "preferences", self.on_preferences_action, ["<primary>comma"]
        )
        self.create_action("log-in", self.on_login_action)
        self.create_action("log-out", self.on_logout_action)

        utils.init()
        utils.setup_logging()

        self.settings: Gio.Settings = Gio.Settings.new("io.github.nokse22.high-tide")
        self.gtk_settings: Gtk.Settings | None = Gtk.Settings.get_default()
        self.base_font_dpi = DEFAULT_FONT_DPI
        if self.gtk_settings:
            configured_dpi = self.gtk_settings.get_property("gtk-xft-dpi")
            if configured_dpi > 0:
                self.base_font_dpi = configured_dpi

        self.settings.connect("changed::text-size", self.on_text_size_setting_changed)
        self.apply_text_size()

        self.preferences: Gtk.Window | None = None
        self.win: HighTideWindow

        self.alsa_devices = utils.get_alsa_devices()

    def do_open(self, files: List[Gio.File], n_files: int, hint: str) -> None:
        win = cast(HighTideWindow | None, self.props.active_window)
        if win is None:
            self.do_activate()
            win = self.win
        else:
            self.win = win

        uri: str = files[0].get_uri()
        if uri:
            if win.is_logged_in:
                utils.open_tidal_uri(uri)
            else:
                win.queued_uri = cast(Any, uri)

    def on_login_action(self, *args) -> None:
        """Handle the login action by initiating a new login process."""
        self.win.new_login()

    def on_logout_action(self, *args) -> None:
        """Handle the logout action by logging out the current user."""
        self.win.logout()

    def do_activate(self) -> None:
        """Activate the application by creating and presenting the main window."""
        win = cast(HighTideWindow | None, self.props.active_window)
        if win is None:
            win = HighTideWindow(application=self)

        self.win = win
        win.present()

    def on_about_action(self, widget: Any, *args) -> None:
        """Display the about dialog with application information"""
        about = Adw.AboutDialog(
            application_name="High Tide",
            application_icon="io.github.nokse22.high-tide",
            developer_name="The High Tide Contributors",
            version="1.4.0",
            developers=[
                "Nokse https://github.com/Nokse22",
                "Nila The Dragon https://github.com/nilathedragon",
                "Dråfølin https://github.com/drafolin",
                "Plamper https://github.com/Plamper",
            ],
            copyright="© 2023-2025 Nokse",
            license_type="GTK_LICENSE_GPL_3_0",
            issue_url="https://github.com/Nokse22/high-tide/issues",
            website="https://github.com/Nokse22/high-tide",
        )

        about.add_link(_("Donate with Ko-Fi"), "https://ko-fi.com/nokse22")
        about.add_link(_("Donate with Github"), "https://github.com/sponsors/Nokse22")

        about.set_support_url("https://matrix.to/#/%23high-tide:matrix.org")

        about.present(self.props.active_window)

    def on_preferences_action(self, *args) -> None:
        """Display the preferences window and bind settings to UI controls"""

        if not self.preferences:
            builder: Gtk.Builder = Gtk.Builder.new_from_resource(
                "/io/github/nokse22/high-tide/ui/preferences.ui"
            )

            builder.get_object("_text_size_row").set_selected(
                self.settings.get_int("text-size")
            )
            builder.get_object("_text_size_row").connect(
                "notify::selected", self.on_text_size_changed
            )

            builder.get_object("_quality_row").set_selected(
                self.settings.get_int("quality")
            )
            builder.get_object("_quality_row").connect(
                "notify::selected", self.on_quality_changed
            )

            builder.get_object("_sink_row").set_selected(
                self.settings.get_int("preferred-sink")
            )
            builder.get_object("_sink_row").connect(
                "notify::selected", self.on_sink_changed
            )

            bg_row: Gtk.Widget = builder.get_object("_background_row")
            bg_row.set_active(self.settings.get_boolean("run-background"))
            self.settings.bind(
                "run-background", bg_row, "active", Gio.SettingsBindFlags.DEFAULT
            )

            builder.get_object("_normalize_row").set_active(
                self.settings.get_boolean("normalize")
            )
            builder.get_object("_normalize_row").connect(
                "notify::active", self.on_normalize_changed
            )

            builder.get_object("_quadratic_volume_row").set_active(
                self.settings.get_boolean("quadratic-volume")
            )
            builder.get_object("_quadratic_volume_row").connect(
                "notify::active", self.on_quadratic_volume_changed
            )

            builder.get_object("_video_cover_row").set_active(
                self.settings.get_boolean("video-covers")
            )
            builder.get_object("_video_cover_row").connect(
                "notify::active", self.on_video_covers_changed
            )

            builder.get_object("_discord_rpc_row").set_active(
                self.settings.get_boolean("discord-rpc")
            )
            builder.get_object("_discord_rpc_row").connect(
                "notify::active", self.on_discord_rpc_changed
            )

            self.alsa_row = builder.get_object("_alsa_device_row")

            # Create a new label factory to just set max_width
            # Idk how to add the tickmark back
            factory = Gtk.SignalListItemFactory()

            def setup(factory, list_item):
                label = Gtk.Label(xalign=0)
                label.set_width_chars(1)
                list_item.set_child(label)

            def bind(factory, list_item):
                label = list_item.get_child()
                string_obj = list_item.get_item()
                label.set_text(string_obj.get_string())

            factory.connect("setup", setup)
            factory.connect("bind", bind)

            self.alsa_row.set_factory(factory)

            names = Gtk.StringList.new([d["name"] for d in self.alsa_devices])
            self.alsa_row.set_model(names)

            last_used_device = self.settings.get_string("alsa-device")

            selected_index = next(
                (
                    i
                    for i, d in enumerate(self.alsa_devices)
                    if d["hw_device"] == last_used_device
                ),
                0,
            )
            self.alsa_row.set_selected(selected_index)
            builder.get_object("_alsa_device_row").set_selected(selected_index)
            self.alsa_row.connect("notify::selected", self.on_alsa_device_changed)

            alsa_used = AudioSink.ALSA == self.settings.get_int("preferred-sink")
            self.alsa_row.set_sensitive(alsa_used)
            if not alsa_used:
                self.alsa_row.set_selected(0)

            builder.get_object("_sink_row").connect(
                "notify::selected-item", self.deactive_alsa_device_row
            )

            self.preferences = builder.get_object("_preference_window")

        preferences = self.preferences
        if preferences:
            preferences.present(self.win)

    def apply_text_size(self) -> None:
        """Apply the selected text scale to this GTK process."""
        if not self.gtk_settings:
            return

        selected = self.settings.get_int("text-size")
        scaled_dpi = round(self.base_font_dpi * TEXT_SIZE_SCALES[selected])
        self.gtk_settings.set_property("gtk-xft-dpi", scaled_dpi)

    def on_text_size_setting_changed(self, *args) -> None:
        """Apply text size changes made through GSettings."""
        self.apply_text_size()

    def on_text_size_changed(self, widget: Any, *args) -> None:
        """Persist the text size selected in preferences."""
        selected = widget.get_selected()
        if selected != self.settings.get_int("text-size"):
            self.settings.set_int("text-size", selected)

    def on_quality_changed(self, widget: Any, *args) -> None:
        self.win.select_quality(widget.get_selected())

    def on_sink_changed(self, widget: Any, *args) -> None:
        self.win.change_audio_sink(widget.get_selected())

    def on_alsa_device_changed(self, widget: Any, *args) -> None:
        index = widget.get_selected()
        device_string = self.alsa_devices[index]["hw_device"]
        self.win.change_alsa_device(device_string)

    def on_normalize_changed(self, widget: Any, *args) -> None:
        self.win.change_normalization(widget.get_active())

    def on_quadratic_volume_changed(self, widget: Any, *args) -> None:
        self.win.change_quadratic_volume(widget.get_active())

    def on_video_covers_changed(self, widget: Any, *args) -> None:
        self.win.change_video_covers_enabled(widget.get_active())

    def on_discord_rpc_changed(self, widget: Any, *args) -> None:
        self.win.change_discord_rpc_enabled(widget.get_active())

    def deactive_alsa_device_row(self, widget: Any, *args) -> None:
        alsa_used = widget.get_selected() == AudioSink.ALSA
        self.alsa_row.set_sensitive(alsa_used)
        if not alsa_used:
            self.alsa_row.set_selected(0)

    def create_action(
        self,
        name: str,
        callback: Callable[..., Any],
        shortcuts: List[str] | None = None,
    ) -> None:
        """Create a new application action with optional keyboard shortcuts.

        Args:
            name: The action name
            callback: The callback function to execute when action is triggered
            shortcuts: Optional list of keyboard shortcut strings
        """
        action: Gio.SimpleAction = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version: str) -> int:
    """The application's entry point."""
    app: HighTideApplication = HighTideApplication()
    return app.run(sys.argv)
