# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  Theme Manager – Desktop Theme Handler
#  Copyright (C) 2021–2025 Himadri Sekhar Basu
#  Licensed under GPLv3 or later
# -----------------------------------------------------------------------------

import gettext
import locale
import logging
import subprocess
from pathlib import Path
from typing import Dict
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio

from ThemeManager.cli_args import APP, LOCALE_DIR
from ThemeManager.common import TMBackend, _async

# ------------------------- i18n Setup -------------------------
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# ------------------------- Logger -----------------------------
logger = logging.getLogger("ThemeManager.DesktopTheme")


class DesktopTheme:
    """Handles reading and setting of desktop environment themes."""

    def __init__(self):
        self.manager = TMBackend()

    # ------------------------- Utility Helpers -------------------------

    def run_command(self, command: str) -> str:
        """Run a shell command and return stripped output."""
        try:
            result = subprocess.check_output(command, stderr=subprocess.PIPE, shell=True)
            return result.decode('utf-8', "strict").strip().strip("'")
        except subprocess.CalledProcessError as e:
            logger.error(_("Command failed: %s"), command)
            logger.debug(_("Error details: %s"), e)
            return ""

    def set_gsetting(self, schema: str, key: str, value: str):
        """Safe wrapper for gsettings set."""
        cmd = f"gsettings set {schema} {key} {value}"
        logger.debug(_("Applying setting: %s"), cmd)
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            logger.warning(_("Failed to set gsetting: {schema} {key}").format(schema=schema, key=key))

    def write_schema_to_xml(self, schema_id: str, output_file: Path):
        """Generate missing schema XML if user-theme is absent."""
        content = f"""<schemalist gettext-domain="gnome-shell-extensions">
<schema id="{schema_id}" path="/org/gnome/shell/extensions/user-theme/">
    <key name="name" type="s">
        <default>''</default>
        <summary>Theme name</summary>
        <description>The name of the theme, to be loaded from ~/.themes/name/gnome-shell</description>
    </key>
</schema>
</schemalist>"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")
        logger.info(_("Wrote schema file: %s"), output_file)

    # ----------------------- Core Functionality -----------------------

    @_async
    def set_desktop_theme(self, state: Dict, nexttheme: list):
        """Apply the selected theme asynchronously across DEs."""
        de = state['DE'].lower()
        logger.info(_("Applying desktop theme for DE: %s"), de)

        try:
            if de == "x-cinnamon":
                mapping = {
                    "org.cinnamon.theme": ("name", nexttheme[3]),
                    "org.cinnamon.desktop.interface": [
                        ("gtk-theme", nexttheme[4]),
                        ("icon-theme", nexttheme[7]),
                        ("cursor-theme", nexttheme[8]),
                    ],
                    "org.cinnamon.desktop.wm.preferences": ("theme", nexttheme[5]),
                    "org.x.apps.portal": ("color-scheme", nexttheme[6]),
                }
                self.apply_theme_map(mapping)

            elif de in ["budgie", "budgie:gnome"]:
                mapping = {
                    "com.solus-project.gsettings-daemon.plugins.polkit": ("theme", nexttheme[4]),
                    "org.gnome.desktop.interface": [
                        ("gtk-theme", nexttheme[4]),
                        ("icon-theme", nexttheme[7]),
                        ("cursor-theme", nexttheme[8]),
                        ("color-scheme", nexttheme[6]),
                    ],
                    "org.gnome.desktop.wm.preferences": ("theme", nexttheme[5])
                }
                # Optional: Budgie-specific 'Desktop' theme (the panel look)
                try:
                    self.set_gsetting("com.solus-project.budgie-panel", "theme", nexttheme[3])
                except Exception:
                    pass 
                
                self.apply_theme_map(mapping)

            elif de in ["gnome", "ubuntu:gnome", "unity"]:
                self.apply_gnome_theme(nexttheme)

            elif de == "mate":
                mapping = {
                    "org.mate.interface": [
                        ("gtk-theme", nexttheme[4]),
                        ("icon-theme", nexttheme[7])
                    ],
                    "org.mate.Marco.general": ("theme", nexttheme[5]),
                    "org.gnome.desktop.interface": ("color-scheme", nexttheme[6]),
                    "org.mate.peripherals-mouse": ("cursor-theme", nexttheme[8]),
                }
                self.apply_theme_map(mapping)

            # Plank theme (dock)
            if self.manager.plank_theme:
                try:
                    self.set_gsetting("net.launchpad.plank.dock.settings", "theme", nexttheme[9])
                except subprocess.CalledProcessError:
                    self.set_gsetting(
                        "net.launchpad.plank.dock.settings:/net/launchpad/plank/docks/dock1/",
                        "theme", nexttheme[9]
                    )

            logger.info(_("Theme applied successfully. Variant: %s"), nexttheme[1])
            logger.debug(_("Themes used: %s"), {
                "System": nexttheme[4],
                "DE Theme": nexttheme[3],
                "Decoration": nexttheme[5],
                "Icon": nexttheme[7],
                "Cursor": nexttheme[8],
                "Plank": nexttheme[9],
                "Color scheme": nexttheme[6],
            })

        except Exception as e:
            logger.error(_("Error applying theme: %s"), e)

    def apply_gnome_theme(self, nexttheme: list):
        """Handle GNOME/Unity-specific theme schema setup."""
        schema_id = 'org.gnome.shell.extensions.user-theme'
        schema_source = Gio.SettingsSchemaSource.get_default()
        schema_exists = schema_source.lookup(schema_id, True)

        if not schema_exists:
            schema_dir = Path.home() / ".local/share/glib-2.0/schemas"
            output_file = schema_dir / f"{schema_id}.gschema.xml"
            self.write_schema_to_xml(schema_id, output_file)
            subprocess.run(f"glib-compile-schemas {schema_dir}", shell=True, check=False)
            logger.info(_("Compiled new GSettings schema at %s"), schema_dir)

        mapping = {
            schema_id: ("name", nexttheme[3]),
            "org.gnome.desktop.interface": [
                ("gtk-theme", nexttheme[4]),
                ("icon-theme", nexttheme[7]),
                ("cursor-theme", nexttheme[8]),
                ("color-scheme", nexttheme[6]),
                ("accent-color", nexttheme[1]),
            ],
            "org.gnome.desktop.wm.preferences": ("theme", nexttheme[5])
        }
        self.apply_theme_map(mapping)

    def apply_theme_map(self, mapping: Dict[str, list]):
        """Iterate through mapping and apply all theme settings."""
        for schema, entries in mapping.items():
            if isinstance(entries, tuple):
                self.set_gsetting(schema, entries[0], entries[1])
            elif isinstance(entries, list):
                for key, value in entries:
                    self.set_gsetting(schema, key, value)

    def get_desktop_theme(self, state: Dict, systheme: str, colvariants: list) -> Dict:
        """Retrieve current theme configuration from the system."""
        de = state['DE'].lower()
        logger.info(_("Reading desktop theme for DE: %s"), de)
        themes = {}

        schema_map = {
            "budgie": {
                "Applications": "org.gnome.desktop.interface gtk-theme",
                "Decoration": "org.gnome.desktop.wm.preferences theme",
                "Icon": "org.gnome.desktop.interface icon-theme",
                "Cursor": "org.gnome.desktop.interface cursor-theme",
            },
            "x-cinnamon": {
                "Applications": "org.cinnamon.desktop.interface gtk-theme",
                "Decoration": "org.cinnamon.desktop.wm.preferences theme",
                "DE Theme": "org.cinnamon.theme name",
                "Icon": "org.cinnamon.desktop.interface icon-theme",
                "Cursor": "org.cinnamon.desktop.interface cursor-theme",
            },
            "gnome": {
                "Applications": "org.gnome.desktop.interface gtk-theme",
                "Decoration": "org.gnome.desktop.wm.preferences theme",
                "DE Theme": "org.gnome.shell.extensions.user-theme name",
                "Icon": "org.gnome.desktop.interface icon-theme",
                "Cursor": "org.gnome.desktop.interface cursor-theme",
            },
            "mate": {
                "Applications": "org.mate.interface gtk-theme",
                "Decoration": "org.mate.Marco.general theme",
                "Icon": "org.mate.interface icon-theme",
                "Cursor": "org.mate.peripherals-mouse cursor-theme",
            },
        }

        try:
            if de in schema_map:
                for k, cmd in schema_map[de].items():
                    themes[k] = self.run_command(f"gsettings get {cmd}")

            if self.manager.plank_theme:
                try:
                    themes["Plank"] = self.run_command("gsettings get net.launchpad.plank.dock.settings theme")
                except subprocess.CalledProcessError:
                    themes["Plank"] = self.run_command(
                        "gsettings get net.launchpad.plank.dock.settings:/net/launchpad/plank/docks/dock1/ theme"
                    )

            # Detect variant
            variant = "Default"
            for v in colvariants:
                if v and v.lower() in themes.get("Applications", "").lower():
                    variant = v
                    break

            logger.info(_("Detected theme variant: %s"), variant)
            return {"Variant": variant, "Themes": themes}

        except Exception as e:
            logger.error(_("Error retrieving desktop theme: %s"), e)
            return {"Variant": "Unknown", "Themes": {}}
