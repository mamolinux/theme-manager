# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  Theme Manager Daemon
#  Copyright (C) 2021–2025 Himadri Sekhar Basu
#  Licensed under GPLv3 or later
# -----------------------------------------------------------------------------

import gettext
import locale
import logging
import threading
from time import sleep

from ThemeManager.cli_args import APP, LOCALE_DIR
from ThemeManager.common import theme_styles, _async, TMBackend
from ThemeManager.DesktopTheme import DesktopTheme

# ------------------------- i18n Setup -------------------------
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# ------------------------- Logger -----------------------------
logger = logging.getLogger("ThemeManager.tm_daemon")


class TMStateMonitor:
    """Background daemon to monitor and apply desktop theme changes."""

    def __init__(self):
        logger.debug(_("Initializing Theme Manager Daemon."))
        self.manager = TMBackend()
        self.theme_styles = theme_styles
        self.desktop_manager = DesktopTheme()
        self.last_state = None
        self._stop_event = threading.Event()

    # ------------------------- Public API -------------------------

    def start(self):
        """Start daemon threads for state and interval monitoring."""
        logger.info(_("Starting Theme Manager Daemon threads..."))

        self._run_async(self._monitor_state_change, delay=0)
        self._run_async(self._auto_change_interval, delay=10)

    def stop(self):
        """Gracefully stop daemon threads."""
        logger.info(_("Stopping Theme Manager Daemon..."))
        self._stop_event.set()

    # ------------------------- Internal Helpers -------------------------

    def _run_async(self, target, delay=0):
        """Helper to start async daemon thread with optional delay."""
        @_async
        def runner():
            if delay:
                sleep(delay)
            target()
        runner()

    def _update_theme(self):
        """Prepare and apply next theme based on current system state."""
        self.state = self.manager.get_state_info()
        next_theme = self.manager.prep_theme_variants(self.state, self.theme_styles)
        self.desktop_manager.set_desktop_theme(self.state, next_theme)

    # ------------------------- Daemon Threads -------------------------

    def _monitor_state_change(self):
        """Continuously monitor system state and react to theme changes."""
        logger.info(_("State-change daemon started."))
        while not self._stop_event.is_set():
            try:
                state = self.manager.get_state_info()
                current_state = state.get("State", "unknown").lower()
                logger.debug(_("Current state: %s, Last: %s"), current_state, self.last_state)

                if current_state != self.last_state:
                    logger.info(_("State changed: %s → %s"), self.last_state, current_state)
                    self.last_state = current_state
                    self._update_theme()

            except Exception as e:
                logger.error(_("Error in state monitor: %s"), e)

            sleep(60)  # Check every minute

    def _auto_change_interval(self):
        """Periodically trigger theme changes at user-defined intervals."""
        logger.info(_("Auto-change daemon started."))
        while not self._stop_event.is_set():
            try:
                self._update_theme()
            except Exception as e:
                logger.error(_("Error in auto-change daemon: %s"), e)

            sleep(self.manager.theme_interval_in_sec)


# ------------------------- Entry Point -------------------------
if __name__ == "__main__":
    daemon = TMStateMonitor()
    daemon.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        daemon.stop()
        logger.info(_("Theme Manager Daemon exited cleanly."))
