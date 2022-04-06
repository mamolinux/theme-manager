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
import configparser
import datetime
import gettext
import locale
import logging
import os
import random
import subprocess
import threading

from gi.repository import GObject


# Used as a decorator to run things in the background
def _async(func):
	def wrapper(*args, **kwargs):
		thread = threading.Thread(target=func, args=args, kwargs=kwargs)
		thread.daemon = True
		thread.start()
		return thread
	return wrapper

# Used as a decorator to run things in the main loop, from another thread
def idle(func):
	def wrapper(*args):
		GObject.idle_add(func, *args)
	return wrapper

# i18n
APP = 'theme-manager'
LOCALE_DIR = "/usr/share/locale"
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('Theme Manager.common')

# Constants
CONFIG_DIR = os.path.expanduser('~/.config/theme-manager/')
CONFIG_FILE = os.path.join(CONFIG_DIR+'config.cfg')


# This is the backend.
# It contains utility functions to manage
# themes
class ThemeManager():
	
	def __init__(self):
		if os.path.exists(CONFIG_DIR):
			pass
		else:
			os.makedirs(CONFIG_DIR)
		
		self.config = configparser.ConfigParser()
		self.save_config()
		self.load_config()
		
	def load_config(self):
		"""Loads configurations from config file.
		
		Tries to read and parse from config file.
		If the config file is missing or not readable,
		then it triggers default configurations.
		"""
		
		self.config.read(CONFIG_FILE)
		try:
			colvars = self.config["system-theme"]['color-variants'].split(',')
			self.systemthemename = self.config["system-theme"]['system-theme-name']
			self.iconthemename = self.config["system-theme"]['icon-theme-name']
			self.cursorthemename = self.config["system-theme"]['cursor-theme-name']
			
			self.colorvariants = ""		# This string will be saved in config file
			self.colvariants = []		# This list will be used to randomize variants
			for var in colvars:
				self.colorvariants += str(var+",")
				self.colvariants.append(var.strip().strip('"').strip("'"))
			self.colorvariants = self.colorvariants.strip(",")	# removes the last comma, it looks ugly with the comma
			self.user_interval = self.config["system-theme"]['cursor-theme-name']
			
			theme_interval = self.config["system-theme"]['theme-interval']
			self.theme_interval_HH = int(theme_interval.split(':')[0])
			self.theme_interval_MM = int(theme_interval.split(':')[1])
			self.theme_interval_SS = int(theme_interval.split(':')[2])
			self.theme_interval_in_sec = self.theme_interval_HH*3600 + self.theme_interval_MM*60 + self.theme_interval_SS
		except:
			self.colvariants = []
			self.colorvariants = ""
			self.systemthemename = ""
			self.iconthemename = ""
			self.cursorthemename = ""
			self.theme_interval_HH = 1
			self.theme_interval_MM = 0
			self.theme_interval_SS = 0
			
	
	def save_config(self):
		if os.path.exists(CONFIG_FILE):
			pass
		else:
			self.config['system-theme'] = {
				'color-variants': "",
				'system-theme-name': "",
				'icon-theme-name': "",
				'cursor-theme-name': ""
			}
			with open(CONFIG_FILE, 'w') as f:
				self.config.write(f)
	
	def get_state_info(self):
		session = os.environ.get('XDG_CURRENT_DESKTOP')
		module_logger.info("Desktop session: %s", session)
		
		command = 'redshift -p | grep "Period" | cut -d " " -f 2'
		rawstate = subprocess.check_output(command, stderr = subprocess.PIPE, shell = True)
		currentstate = rawstate.decode('utf-8', "strict").strip('\n')
		module_logger.info("Current State: %s", currentstate)
		
		return {'DE': session, 'State': currentstate}
	
	def prep_theme_variants(self, state):
		now = datetime.datetime.now()
		timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
		
		currentcolor = random.choice(self.colvariants)
		cursrcolor = currentcolor
		currentstate = state['State'].lower()
		
		shelltheme = wmtheme = gtktheme = icontheme = cursrtheme = ""
		stateflag = 1
		module_logger.debug("Current State: %s", currentstate)
		if currentstate == "daytime":
			stateflag = 1
			wmtheme = self.systemthemename
			if len(currentcolor) != 0:
				shelltheme = self.systemthemename+"-"+currentcolor
				icontheme = self.iconthemename+"-"+currentcolor
				cursrtheme = self.cursorthemename+"-"+currentcolor
			else:
				shelltheme = self.systemthemename
				icontheme = self.iconthemename
				
				while len(cursrcolor) == 0:
					try:
						cursrcolor = random.choice(self.colvariants)
						cursrtheme = self.cursorthemename+"-"+cursrcolor
					except:
						cursrcolor = ""
			
			gtktheme = shelltheme
		
		elif currentstate == "night":
			stateflag = 1
			wmtheme = self.systemthemename+"-Dark"
			if len(currentcolor) != 0:
				shelltheme = self.systemthemename+"-Dark-"+currentcolor
				icontheme = self.iconthemename+"-Dark-"+currentcolor
				cursrtheme = self.cursorthemename+"-"+currentcolor
			else:
				shelltheme = self.systemthemename+"-Dark"
				icontheme = self.iconthemename+"-Dark"
				
				while len(cursrcolor) == 0:
					cursrcolor = random.choice(self.colvariants)
					cursrtheme = self.cursorthemename+"-"+cursrcolor
			
			gtktheme = shelltheme
		
		else:
			stateflag = 0
			wmtheme = self.systemthemename+"-Dark"
			if len(currentcolor) != 0:
				shelltheme = self.systemthemename+"-Dark-"+currentcolor
				gtktheme = self.systemthemename+"-Darker-"+currentcolor
				icontheme = self.iconthemename+"-"+currentcolor
				cursrtheme = self.cursorthemename+"-"+currentcolor
			else:
				shelltheme = self.systemthemename+"-Dark"
				gtktheme = self.systemthemename+"-Darker"
				icontheme = self.iconthemename
				
				while len(cursrcolor) == 0:
					cursrcolor = random.choice(self.colvariants)
					cursrtheme = self.cursorthemename+"-"+cursrcolor
		
		nxt_theme = [timestamp, currentcolor, stateflag, shelltheme, gtktheme, wmtheme, icontheme, cursrtheme]
		themes = {}
		themes["System"] = gtktheme
		themes["DE Theme"] = shelltheme
		themes["Decoration"] = wmtheme
		themes["Icon"] = icontheme
		themes["Cursor"] = cursrtheme
		module_logger.debug("Next Colour Variant: %s, Next Themes: %s" % (nxt_theme[1], themes))
		
		return nxt_theme

if __name__ == "__main__":
	pass
	