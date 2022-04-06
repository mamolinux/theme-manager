#!/usr/bin/python3

# Copyright (C) 2021-2022 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
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
import os
from threading import Thread
from time import sleep

# third-party library
import gi
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from common import ThemeManager
from DesktopTheme import desktop_theme


# i18n
APP = 'theme-manager'
LOCALE_DIR = "/usr/share/locale"
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('Theme Manager.tm_daemon')

# indicator icons
ICONS = {"app": "tray-icon.svg"}
_path = os.path.dirname(os.path.abspath(__file__))
_icon_path = _path + '/icons/'

for key in ICONS:
	ICONS[key] = _icon_path + ICONS[key]

class TMdaemon():
	def __init__(self):
		module_logger.debug("Initiaing Theme Manager daemon.")
		self.manager = ThemeManager()
		self.destop_manager = desktop_theme()
		self.last_state = 'Unknown'
	
	def startdaemons(self):
		module_logger.debug("Initiaing state change daemon.")
		self.statechange_daemon = Thread(target=self.on_statechange)
		self.statechange_daemon.setDaemon(True)
		self.statechange_daemon.start()
		
		module_logger.debug("Initiaing auto-change at regular interval daemon.")
		self.autouser_request_daemon = Thread(target=self.on_autouser_request)
		self.autouser_request_daemon.setDaemon(True)
		self.autouser_request_daemon.start()
	
	def on_statechange(self):
		module_logger.info("Initiaing state change daemon.")
		while True:
			self.state = self.manager.get_state_info()
			currentstate = self.state['State'].lower()
			module_logger.debug("Now state: "+currentstate)
			module_logger.debug("Old state: "+self.last_state)
			if self.last_state != currentstate:
				self.last_state = currentstate
				self.nexttheme = self.manager.prep_theme_variants(self.state)
				self.destop_manager.set_desktop_theme(self.state, self.nexttheme)
			sleep(60)	# check once in a minute whether the state is changed
	
	def on_autouser_request(self):
		module_logger.info("Initiaing auto-change at regular interval daemon.")
		while True:
			self.state = self.manager.get_state_info()
			self.nexttheme = self.manager.prep_theme_variants(self.state)
			self.destop_manager.set_desktop_theme(self.state, self.nexttheme)
			sleep(self.manager.theme_interval_in_sec)
	
class AppIndicator():
	"""Class for system tray icon.
	
	This class will show Theme Manager icon in system tray.
	"""
	def __init__(self):
		module_logger.debug("Initiaing Appindicator.")
		self.indicator = AppIndicator3.Indicator.new(APP, ICONS['app'], AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
		self.indicator.set_title(_('Theme Manager'))
		self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		
		TMdaemon().startdaemons()
		
		# create menu
		self.indicator.set_menu(self.__create_menu())
		Gtk.main()
	
	def __create_menu(self):
		menu = Gtk.Menu()
		
		item_quit = Gtk.MenuItem(_('Quit'))
		item_quit.connect("activate", self.__quit)
		menu.append(item_quit)
		menu.show_all()
		
		return menu
	
	def __quit(self, *args):
		Gtk.main_quit()
		