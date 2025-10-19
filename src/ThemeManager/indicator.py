# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  Theme Manager – Desktop Theme Handler
#  Copyright (C) 2021–2025 Himadri Sekhar Basu
#  Licensed under GPLv3 or later
# -----------------------------------------------------------------------------


# import the necessary modules!
import gettext
import locale
import logging
import gi

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from gi.repository import AppIndicator3, Gtk, GLib

from ThemeManager.about_window import AboutWindow
from ThemeManager.logger import LoggerWindow
from ThemeManager.cli_args import APP, LOCALE_DIR
from ThemeManager.common import theme_styles
from ThemeManager.tm_daemon import TMStateMonitor
from ThemeManager.DesktopTheme import DesktopTheme

# ------------------------- i18n Setup -------------------------
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# ------------------------- Logger -----------------------------
logger = logging.getLogger("ThemeManager.Indicator")


class ThemeIndicator:
    """System tray icon and controller for Theme Manager."""

    def __init__(self):
        logger.debug("Initializing AppIndicator for Theme Manager...")
        self.indicator = AppIndicator3.Indicator.new(
            APP, APP, AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_title(_("Theme Manager"))
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Core managers
        self.desktop_manager = DesktopTheme()
        self.daemon = TMStateMonitor()
        self.theme_styles = theme_styles
        self.daemon.start()

        # Attach GTK menu
        self.indicator.set_menu(self._create_menu())

        logger.info(_("Theme Manager Indicator initialized successfully."))
        Gtk.main()

    # ------------------------- Menu Creation -------------------------

    def _create_menu(self):
        """Construct the indicator menu."""
        menu = Gtk.Menu()

        items = [
            (_("Next Theme"), "next", self.next_theme),
            (_("Show Logs"), "text-x-log", self.show_logs),
            (_("About"), "help-about-symbolic", self.open_about),
            (_("Quit"), "application-exit", self._quit),
        ]

        for label, icon, handler in items:
            item = Gtk.ImageMenuItem(label)
            item.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU))
            item.connect("activate", handler)
            menu.append(item)

        menu.show_all()
        return menu

    # ------------------------- Menu Handlers -------------------------
    def next_theme(self, *args, **kwargs):
        """Trigger theme change manually."""
        # Use translation safely
        _translate = _  # Ensure we reference the global translation function

        try:
            logger.info(_translate("User triggered Next Theme from indicator."))
            # state = self.daemon.manager.get_state_info()
            # logger.debug(_translate("State: %s"), state)
            # nxt_theme = self.daemon.manager.prep_theme_variants(state, self.theme_styles)
            # logger.debug(_translate("Next Themes: %s"), state)

            # Run asynchronously to avoid blocking GTK loop
            # GLib.idle_add(self.desktop_manager.set_desktop_theme, state, nxt_theme)
            GLib.idle_add(self.daemon._update_theme)
        except Exception as e:
            # Catch errors safely, with translation
            logger.error(_translate("Error in next_theme: %s"), e)

    def show_logs(self, _action=None, _widget=None):
        """Open Logger window."""
        logger.debug(_("Opening Logger Window..."))
        win = LoggerWindow(Gtk.Window())
        win.show()

    def open_about(self, _action=None, _widget=None):
        """Open About dialog."""
        logger.debug(_("Opening About Window..."))
        win = AboutWindow(Gtk.Window())
        win.show()

    def _quit(self, *args, **kwargs):
        """Exit indicator cleanly."""
        logger.info(_("Exiting Theme Manager Indicator..."))
        self.daemon.stop()
        Gtk.main_quit()


# ------------------------- Entry Point -------------------------
if __name__ == "__main__":
    try:
        ThemeIndicator()
    except KeyboardInterrupt:
        Gtk.main_quit()
        logger.info(_("Theme Manager Indicator exited cleanly."))
