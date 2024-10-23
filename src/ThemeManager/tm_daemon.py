# Copyright (C) 2021-2024 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
#
# This file is part of theme-manager.
#
# theme-manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# theme-manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with theme-manager. If not, see <http://www.gnu.org/licenses/>
# or write to the Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA..
#
# Author: Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
#

# import the necessary modules!
import gettext
import locale
import logging

from time import sleep

# imports from current package
from ThemeManager.cli_args import APP, LOCALE_DIR
from ThemeManager.common import theme_styles, _async, TMBackend
from ThemeManager.DesktopTheme import desktop_theme


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('ThemeManager.tm_daemon')

class TMState_monitor():
	def __init__(self):
		module_logger.debug("Initiaing Theme Manager daemon.")
		self.manager = TMBackend()
		self.theme_styles = theme_styles
		self.destop_manager = desktop_theme()
		self.last_state = 'Unknown'
	
	def startdaemons(self):
		module_logger.debug("Initiaing state change daemon.")
		statechange_daemon = _async(self.on_statechange)
		statechange_daemon()
		sleep(10)
		
		module_logger.debug("Initiaing auto-change at regular interval daemon.")
		autouser_request_daemon = _async(self.on_autouser_request)
		autouser_request_daemon()
	
	def on_statechange(self):
		module_logger.info("Starting to monitor state change.")
		while True:
			self.state = self.manager.get_state_info()
			currentstate = self.state['State'].lower()
			module_logger.debug("Now state: "+currentstate)
			module_logger.debug("Old state: "+self.last_state)
			if self.last_state != currentstate:
				self.last_state = currentstate
				self.nexttheme = self.manager.prep_theme_variants(self.state, self.theme_styles)
				self.destop_manager.set_desktop_theme(self.state, self.nexttheme)
			sleep(60)	# check once in a minute whether the state is changed
	
	def on_autouser_request(self):
		module_logger.info("Starting auto-change at regular interval.")
		while True:
			self.state = self.manager.get_state_info()
			self.nexttheme = self.manager.prep_theme_variants(self.state, self.theme_styles)
			self.destop_manager.set_desktop_theme(self.state, self.nexttheme)
			sleep(self.manager.theme_interval_in_sec)
