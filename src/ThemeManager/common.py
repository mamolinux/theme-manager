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
import getpass
import gettext
import glob
import locale
import logging
import os
import random
import string
import subprocess

from gi.repository import GObject
from random import choice
from threading import Thread

# i18n
APP = 'theme-manager'
LOCALE_DIR = "/usr/share/locale"
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext


## Setup logfile
def create_logfile():
	logpath = '/tmp/'
	dlimitter = '_'
	username = getpass.getuser()
	random_code =  ''.join(choice(string.digits) for _ in range(4))
	if len(glob.glob(logpath+APP+dlimitter+username+'*')) ==0:
		logfile = logpath + APP + dlimitter + username + dlimitter + random_code + '.log'
	else:
		logfile = glob.glob(logpath+APP+dlimitter+username+'*')[0]
	
	return logfile
# Set the log filename
LOGFILE = create_logfile()

# logger
module_logger = logging.getLogger('ThemeManager.common')

# get version
_path = os.path.dirname(os.path.abspath(__file__))
version_file = _path+'/VERSION'
__version__ = open(version_file, 'r').readlines()[0]

# Constants
CONFIG_DIR = os.path.expanduser('~/.config/theme-manager/')
CONFIG_FILE = os.path.join(CONFIG_DIR+'config.cfg')
UI_PATH = _path+"/ui/"
theme_styles = ["name-mode-color", "name-color-mode"]

# Used as a decorator to run things in the background
def _async(func):
	def wrapper(*args, **kwargs):
		thread = Thread(target=func, args=args, kwargs=kwargs)
		thread.daemon = True
		thread.start()
		return thread
	return wrapper

# Used as a decorator to run things in the main loop, from another thread
def idle(func):
	def wrapper(*args):
		GObject.idle_add(func, *args)
	return wrapper


# This is the backend.
# It contains utility functions to manage
# themes
class TMBackend():
	
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
			self.darkmode_suffix = self.config["system-theme"]['dark-mode-suffix']
			self.darkermode = self.config["system-theme"].getboolean('darker-mode')
			self.darkermode_suffix = self.config["system-theme"]['darker-mode-suffix']
			self.theme_name_style = int(self.config["system-theme"]['theme-style-name'])
			
			self.colorvariants = ""		# This string will be saved in config file
			self.colvariants = []		# This list will be used to randomize variants
			for var in colvars:
				self.colorvariants += str(var+",")
				self.colvariants.append(var.strip().strip('"').strip("'"))
			self.colorvariants = self.colorvariants.strip(",")	# removes the last comma, it looks ugly with the comma
			
			# Icon Theme
			self.icon_theme = self.config["system-theme"].getboolean('icon-theme')
			self.iconthemename = self.config["system-theme"]['icon-theme-name']
			self.icon_darkmode_suffix = self.config["system-theme"]['icon-dark-mode-suffix']
			self.icon_theme_name_style = int(self.config["system-theme"]['icon-theme-style-name'])
			
			colvars = self.config["system-theme"]['icon-color-variants'].split(',')
			self.icon_colorvariants = ""		# This string will be saved in config file
			self.icon_colvariants = []		# This list will be used to randomize variants
			for var in colvars:
				self.icon_colorvariants += str(var+",")
				self.icon_colvariants.append(var.strip().strip('"').strip("'"))
			self.icon_colorvariants = self.icon_colorvariants.strip(",")	# removes the last comma, it looks ugly with the comma
			
			# Cursor Theme
			self.cursor_theme = self.config["system-theme"].getboolean('cursor-theme')
			self.cursorthemename = self.config["system-theme"]['cursor-theme-name']
			
			colvars = self.config["system-theme"]['cursor-color-variants'].split(',')
			self.cursor_colorvariants = ""		# This string will be saved in config file
			self.cursor_colvariants = []		# This list will be used to randomize variants
			for var in colvars:
				self.cursor_colorvariants += str(var+",")
				self.cursor_colvariants.append(var.strip().strip('"').strip("'"))
			self.cursor_colorvariants = self.cursor_colorvariants.strip(",")	# removes the last comma, it looks ugly with the comma
			
			# Plank Theme
			self.plank_theme = self.config["system-theme"].getboolean('plank-theme')
			self.plankthemename = self.config["system-theme"]['plank-theme-name']
			self.plank_darkmode_suffix = self.config["system-theme"]['plank-dark-mode-suffix']
			self.plank_theme_name_style = int(self.config["system-theme"]['plank-theme-style-name'])
			
			colvars = self.config["system-theme"]['plank-color-variants'].split(',')
			self.plank_colorvariants = ""		# This string will be saved in config file
			self.plank_colvariants = []		# This list will be used to randomize variants
			for var in colvars:
				self.plank_colorvariants += str(var+",")
				self.plank_colvariants.append(var.strip().strip('"').strip("'"))
			self.plank_colorvariants = self.plank_colorvariants.strip(",")	# removes the last comma, it looks ugly with the comma
			
			theme_interval = self.config["system-theme"]['theme-interval']
			self.theme_interval_HH = int(theme_interval.split(':')[0])
			self.theme_interval_MM = int(theme_interval.split(':')[1])
			self.theme_interval_SS = int(theme_interval.split(':')[2])
			self.theme_interval_in_sec = self.theme_interval_HH*3600 + self.theme_interval_MM*60 + self.theme_interval_SS
		except:
			self.colvariants = []
			self.colorvariants = ""
			self.systemthemename = ""
			self.darkmode_suffix = "Dark"
			self.darkermode = False
			self.darkermode_suffix = "Darker"
			self.theme_name_style = 0
			
			self.icon_theme = True
			self.iconthemename = ""
			self.icon_darkmode_suffix = "Dark"
			self.icon_colvariants = []
			self.icon_colorvariants = ""
			self.icon_theme_name_style = 0
			
			self.cursor_theme = False
			self.cursorthemename = ""
			self.cursor_colvariants = []
			self.cursor_colorvariants = ""
			
			self.plank_theme = False
			self.plankthemename = ""
			self.plank_darkmode_suffix = "Dark"
			self.plank_colvariants = []
			self.plank_colorvariants = ""
			self.plank_theme_name_style = 0
			
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
				'dark-mode-suffix': "Dark",
				'darker-mode': False,
				'darker-mode-suffix': "Darker",
				'theme-style-name': 0,
				'icon-theme': True,
				'icon-theme-name': "",
				'icon-color-variants': "",
				'icon-dark-mode-suffix': "Dark",
				'icon-theme-style-name': 0,
				'cursor-theme': False,
				'cursor-theme-name': "",
				'cursor-color-variants': "",
				'plank-theme': False,
				'plank-theme-name': "",
				'plank-color-variants': "",
				'plank-dark-mode-suffix': "Dark",
				'plank-theme-style-name': 0,
				'theme-interval': '1:0:0'
			}
			with open(CONFIG_FILE, 'w') as f:
				self.config.write(f)
	
	def get_state_info(self):
		session = os.environ.get('XDG_CURRENT_DESKTOP')
		module_logger.debug("Desktop session: %s", session)
		
		command = 'redshift -p | grep "Period" | cut -d " " -f 2'
		rawstate = subprocess.check_output(command, stderr = subprocess.PIPE, shell = True)
		currentstate = rawstate.decode('utf-8', "strict").strip('\n')
		module_logger.debug("Current State: %s", currentstate)
		
		return {'DE': session, 'State': currentstate}
	
	def prep_theme_variants(self, state, theme_styles):
		now = datetime.datetime.now()
		timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
		
		currentcolor = random.choice(self.colvariants)
		currentstate = state['State'].lower()
		
		shelltheme = wmtheme = gtktheme = icontheme = cursrtheme = ""
		stateflag = 1
		module_logger.info("Current State: %s", currentstate)
		
		if self.icon_theme:
			icontheme = self.prep_icon_theme(currentstate, currentcolor)
		
		if self.cursor_theme:
			cursrtheme = self.prep_cursor_theme(currentcolor)
		
		if self.plank_theme:
			planktheme = self.prep_plank_theme(currentstate, currentcolor)
		
		if currentstate == "daytime":
			wmtheme = self.systemthemename
			if len(currentcolor) != 0:
				shelltheme = self.systemthemename+"-"+currentcolor
			else:
				shelltheme = self.systemthemename
			gtktheme = shelltheme
			color_pref = "prefer-light"
		
		elif currentstate == "night":
			wmtheme = self.systemthemename+"-"+self.darkmode_suffix
			if len(currentcolor) != 0:
				if theme_styles[self.theme_name_style] == theme_styles[0]:
					shelltheme = self.systemthemename+"-"+self.darkmode_suffix+"-"+currentcolor
				else:
					shelltheme = self.systemthemename+"-"+currentcolor+"-"+self.darkmode_suffix
			else:
				shelltheme = self.systemthemename+"-"+self.darkmode_suffix
			gtktheme = shelltheme
			color_pref = "prefer-dark"
		
		else:
			wmtheme = self.systemthemename+"-"+self.darkmode_suffix
			if len(currentcolor) != 0:
				if theme_styles[self.theme_name_style] == theme_styles[0]:
					shelltheme = self.systemthemename+"-"+self.darkmode_suffix+"-"+currentcolor
					if self.darkermode:
						gtktheme = self.systemthemename+"-"+self.darkermode_suffix+"-"+currentcolor
					else:
						gtktheme = self.systemthemename+"-"+self.darkmode_suffix+"-"+currentcolor
				else:
					shelltheme = self.systemthemename+"-"+currentcolor+"-"+self.darkmode_suffix
					if self.darkermode:
						gtktheme = self.systemthemename+"-"+currentcolor+"-"+self.darkermode_suffix
					else:
						gtktheme = self.systemthemename+"-"+currentcolor+"-"+self.darkmode_suffix
			else:
				shelltheme = self.systemthemename+"-"+self.darkmode_suffix
				if self.darkermode:
					gtktheme = self.systemthemename+"-"+self.darkermode_suffix
				else:
					gtktheme = self.systemthemename+"-"+self.darkmode_suffix
			
			color_pref = "prefer-dark"
		
		nxt_theme = [timestamp, currentcolor, stateflag, shelltheme, gtktheme, wmtheme, color_pref, icontheme, cursrtheme, planktheme]
		themes = {}
		themes["System"] = gtktheme
		themes["DE Theme"] = shelltheme
		themes["Decoration"] = wmtheme
		themes["Icon"] = icontheme
		themes["Cursor"] = cursrtheme
		themes["Plank"] = planktheme
		module_logger.debug("Next Colour Variant: %s, Next Themes: %s" % (nxt_theme[1], themes))
		
		return nxt_theme
		
	def prep_icon_theme(self, currentstate, currentcolor):
		for color in self.icon_colvariants:
			if currentcolor.lower() in color.lower():
				iconcolor = color
				break
		else:
			iconcolor = random.choice(self.icon_colvariants)
		module_logger.debug("Icon Colour Variant: %s", iconcolor)
		if currentstate == "night":
			if len(iconcolor) != 0:
				if theme_styles[self.icon_theme_name_style] == theme_styles[0]:
					icontheme = self.iconthemename+"-"+self.icon_darkmode_suffix+"-"+iconcolor
				else:
					icontheme = self.iconthemename+"-"+iconcolor+"-"+self.icon_darkmode_suffix
			else:
				icontheme = self.iconthemename+"-"+self.icon_darkmode_suffix
		else:
			# for daytime and transition
			if len(iconcolor) != 0:
				icontheme = self.iconthemename+"-"+iconcolor
			else:
				icontheme = self.iconthemename
		
		module_logger.debug("Icon Theme: %s, Colour Variant: %s" % (icontheme, iconcolor))
		return icontheme
	
	def prep_cursor_theme(self, currentcolor):
		for color in self.cursor_colvariants:
			if currentcolor.lower() in color.lower():
				cursrcolor = color
				break
		else:
			cursrcolor = random.choice(self.cursor_colvariants)
		module_logger.debug("Cursor Colour Variant: %s", cursrcolor)
		if len(cursrcolor) != 0:
			cursrtheme = self.cursorthemename+"-"+cursrcolor
		else:
			count = 0
			while len(cursrcolor) == 0:
				cursrcolor = random.choice(self.cursor_colvariants)
				cursrtheme = self.cursorthemename+"-"+cursrcolor
				count = count + 1
				if count > 10:
					break
				
			cursrtheme = self.cursorthemename
		
		module_logger.debug("Cursor Theme: %s, Colour Variant: %s" % (cursrtheme, cursrcolor))
		return cursrtheme
		
	def prep_plank_theme(self, currentstate, currentcolor):
		for color in self.plank_colvariants:
			if currentcolor.lower() in color.lower():
				plankcolor = color
				break
		else:
			plankcolor = random.choice(self.plank_colvariants)
		module_logger.debug("Plank Colour Variant: %s", plankcolor)
		if currentstate == "night":
			if len(plankcolor) != 0:
				if theme_styles[self.plank_theme_name_style] == theme_styles[0]:
					planktheme = self.plankthemename+"-"+self.plank_darkmode_suffix+"-"+plankcolor
				else:
					planktheme = self.plankthemename+"-"+plankcolor+"-"+self.plank_darkmode_suffix
			else:
				planktheme = self.plankthemename+"-"+self.plank_darkmode_suffix
		else:
			# for daytime and transition
			if len(plankcolor) != 0:
				planktheme = self.plankthemename+"-"+plankcolor
			else:
				planktheme = self.plankthemename
		
		module_logger.debug("Plank Theme: %s, Colour Variant: %s" % (planktheme, plankcolor))
		return planktheme

if __name__ == "__main__":
	pass
	