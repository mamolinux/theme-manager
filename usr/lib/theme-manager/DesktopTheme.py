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
import os
import subprocess

class desktop_theme():
	
	def __init__(self):
			pass
	
	def set_desktop_theme(self, state, nexttheme):
		thisDE = str(state['DE']).lower()
		if thisDE == "x-cinnamon":
			# When the DE is cinnamon set
			# Desktop theme
			os.system("gsettings set org.cinnamon.theme name %s" % nexttheme[3])
			# Gtk theme
			os.system("gsettings set org.cinnamon.desktop.interface gtk-theme %s" % nexttheme[4])
			# Window border/Metacity
			os.system("gsettings set org.cinnamon.desktop.wm.preferences theme %s" % nexttheme[3])
			# Icon theme
			os.system("gsettings set org.cinnamon.desktop.interface icon-theme %s" % nexttheme[5])
			# Cursor theme
			os.system("gsettings set org.cinnamon.desktop.interface cursor-theme %s" % nexttheme[6])
	
	def get_desktop_theme(self, state):
		thisDE = state['DE'].lower()
		currenttheme = ['Unknown', 'Unknown']
		if thisDE == "x-cinnamon":
			# When the DE is cinnamon get
			# Desktop theme
			currenttheme.append(self.run_command("gsettings get org.cinnamon.theme name"))
			# Gtk theme
			currenttheme.append(self.run_command("gsettings get org.cinnamon.desktop.interface gtk-theme"))
			# Window border/Metacity
			currenttheme.append(self.run_command("gsettings get org.cinnamon.desktop.wm.preferences theme"))
			# Icon theme
			currenttheme.append(self.run_command("gsettings get org.cinnamon.desktop.interface icon-theme"))
			# Cursor theme
			currenttheme.append(self.run_command("gsettings get org.cinnamon.desktop.interface cursor-theme"))
		
		return currenttheme
	
	def run_command(self, command):
		output = subprocess.check_output(command, stderr = subprocess.PIPE, shell = True)
		return output.decode('utf-8', "strict").strip('\n').strip('\'')
