#!/usr/bin/python3

# Copyright (C) 2021 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
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
import os
import random
import subprocess
import threading

from gi.repository import GObject


# Used as a decorator to run things in the background
def _async(func):
	def wrapper(*args, **kwargs):
		thread = threading.Thread(target=ThemeManager.__run_daemon, args=args, kwargs=kwargs)
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

# Constants
LOG_FILE = "/tmp/theme-manager.log"
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
		except:
			self.colvariants = []
			self.colorvariants = ""
			self.systemthemename = ""
			self.iconthemename = ""
			self.cursorthemename = ""
			
	
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
		command = 'redshift -p | grep "Period" | cut -d " " -f 2'
		rawstate = subprocess.check_output(command, stderr = subprocess.PIPE, shell = True)
		currentstate = rawstate.decode('utf-8', "strict").strip('\n')
		
		return {'DE': session, 'State': currentstate}
	
	def prep_theme_variants(self, state):
		now = datetime.datetime.now()
		timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
		
		currentcolor = random.choice(self.colvariants)
		cursrcolor = currentcolor
		currentstate = state['State'].lower()
		
		systheme = wmtheme = gtktheme = icontheme = cursrtheme = ""
		stateflag = 1
		if currentstate == "daytime":
			# print("It's Daytime")
			stateflag = 1
			wmtheme = self.systemthemename
			if len(currentcolor) != 0:
				systheme = self.systemthemename+"-"+currentcolor
				icontheme = self.iconthemename+"-"+currentcolor
				cursrtheme = self.cursorthemename+"-"+currentcolor
			else:
				systheme = self.systemthemename
				icontheme = self.iconthemename
				
				while len(cursrcolor) == 0:
					try:
						cursrcolor = random.choice(self.colvariants)
						cursrtheme = self.cursorthemename+"-"+cursrcolor
					except:
						cursrcolor = ""
			
			gtktheme = systheme
		
		elif currentstate == "night":
			# print("It's Nighttime")
			stateflag = 1
			wmtheme = self.systemthemename+"-Dark"
			if len(currentcolor) != 0:
				systheme = self.systemthemename+"-Dark-"+currentcolor
				icontheme = self.iconthemename+"-Dark-"+currentcolor
				cursrtheme = self.cursorthemename+"-"+currentcolor
			else:
				systheme = self.systemthemename+"-Dark"
				icontheme = self.iconthemename+"-Dark"
				
				while len(cursrcolor) == 0:
					cursrcolor = random.choice(self.colvariants)
					cursrtheme = self.cursorthemename+"-"+cursrcolor
			
			gtktheme = systheme
		
		else:
			# print("It's Transition")
			stateflag = 0
			wmtheme = self.systemthemename+"-Dark"
			if len(currentcolor) != 0:
				systheme = self.systemthemename+"-Dark-"+currentcolor
				gtktheme = self.systemthemename+"-Darker-"+currentcolor
				icontheme = self.iconthemename+"-"+currentcolor
				cursrtheme = self.cursorthemename+"-"+currentcolor
			else:
				systheme = self.systemthemename+"-Dark"
				gtktheme = self.systemthemename+"-Darker"
				icontheme = self.iconthemename
				
				while len(cursrcolor) == 0:
					cursrcolor = random.choice(self.colvariants)
					cursrtheme = self.cursorthemename+"-"+cursrcolor
		
		nxt_theme = [timestamp, currentcolor, stateflag, systheme, gtktheme, wmtheme, icontheme, cursrtheme]
		print("Next Theme: "+str(nxt_theme))
		
		return nxt_theme

if __name__ == "__main__":
	pass
	