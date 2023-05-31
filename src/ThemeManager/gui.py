# Copyright (C) 2021-2023 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
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
import gi
import locale
import logging
import setproctitle
import warnings

# Suppress GTK deprecation warnings
warnings.filterwarnings("ignore")

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

# imports from current package
from ThemeManager.about_window import AboutWindow
from ThemeManager.logger import LoggerWindow
from ThemeManager.common import APP, CONFIG_FILE, LOCALE_DIR, UI_PATH, __version__, theme_styles, _async, TMBackend
from ThemeManager.indicator import TMIndicator
from ThemeManager.DesktopTheme import desktop_theme
from ThemeManager.time_chooser import TimeChooserButton
# from ThemeManager.LoginTheme import login_theme

setproctitle.setproctitle(APP)

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('ThemeManager.gui')


class theme_manager(Gtk.Application):
	# Main initialization routine
	def __init__(self, application_id, flags):
		Gtk.Application.__init__(self, application_id=application_id, flags=flags)
		self.connect("activate", self.activate)
	
	def activate(self, application):
		windows = self.get_windows()
		if (len(windows) > 0):
			window = windows[0]
			window.present()
			window.show()
		else:
			window = ThemeManagerWindow(self)
			self.add_window(window.window)
			window.window.show()

class ThemeManagerWindow():
	
	def __init__(self, application):
		
		self.application = application
		self.settings = Gio.Settings(schema_id="org.mamolinux.theme-manager")
		self.manager = TMBackend()
		self.destop_manager = desktop_theme()
		self.icon_theme = Gtk.IconTheme.get_default()
		
		# Set the Glade file
		gladefile = UI_PATH+"theme-manager.ui"
		self.builder = Gtk.Builder()
		self.builder.add_from_file(gladefile)
		self.window = self.builder.get_object("MainWindow")
		self.window.set_title(_("Theme Manager"))
		
		# Create variables to quickly access dynamic widgets
		self.statusbar = self.builder.get_object("status_bar")
		# input values
		self.color_variants = self.builder.get_object("colour_variants")
		self.systemtheme_variants = self.builder.get_object("system_theme_name")
		self.darkmode_name = self.builder.get_object("dark_mode_name")
		self.darkermode_switch = self.builder.get_object("darker_switch")
		self.darkermode_label = self.builder.get_object("darker_mode_label")
		self.darkermode_name = self.builder.get_object("darker_mode_name")
		
		self.icon_settings = self.builder.get_object("icon_settings")
		self.icon_theme_name = self.builder.get_object("icon_theme_name")
		self.icon_colour_variants = self.builder.get_object("icon_colour_variants")
		self.icon_darkmode_name = self.builder.get_object("icon_dark_mode_name")
		
		self.plank_settings = self.builder.get_object("plank_settings")
		self.plank_theme_name = self.builder.get_object("plank_theme_name")
		self.plank_colour_variants = self.builder.get_object("plank_colour_variants")
		self.plank_darkmode_name = self.builder.get_object("plank_dark_mode_name")
		
		self.cursor_settings = self.builder.get_object("cursor_settings")
		self.cursor_theme_name = self.builder.get_object("cursor_theme_name")
		self.cursor_colour_variants = self.builder.get_object("cursor_colour_variants")
		
		self.systime_grid = self.builder.get_object("system_time_grid")
		self.systime_transition_grid = self.builder.get_object("system_time_transition_grid")
		
		self.day_start_time = TimeChooserButton()
		self.night_start_time = TimeChooserButton()
		self.d2n_start_time = TimeChooserButton()
		self.n2d_start_time = TimeChooserButton()
		
		self.systime_grid.attach(self.day_start_time, 1, 0, 1, 1)
		self.systime_grid.attach(self.night_start_time, 1, 1, 1, 1)
		self.systime_transition_grid.attach(self.d2n_start_time, 1, 0, 1, 1)
		self.systime_transition_grid.attach(self.n2d_start_time, 1, 1, 1, 1)
		
		self.user_interval_box = self.builder.get_object("user_interval_box")
		self.user_interval = TimeChooserButton()
		self.user_interval_box.pack_start(self.user_interval, False, False, 0)
		
		self.user_interval_HH = self.builder.get_object("hour")
		self.user_interval_MM = self.builder.get_object("minute")
		self.user_interval_SS = self.builder.get_object("second")
		
		# Buttons
		self.icon_switch = self.builder.get_object("icon_switch")
		self.cursor_switch = self.builder.get_object("cursor_switch")
		self.plank_switch = self.builder.get_object("plank_switch")
		self.darkermode_switch = self.builder.get_object("darker_switch")
		self.systime_switch = self.builder.get_object("system_time_switch")
		self.randomize_button = self.builder.get_object("randomize_theme_button")
		self.save_button = self.builder.get_object("save_button")
		
		# Combo box
		theme_style_store = Gtk.ListStore(str)
		self.theme_styles = theme_styles
		for style in self.theme_styles:
			theme_style_store.append([style])
		self.theme_name_style_combo = self.builder.get_object("theme_name_style_combo")
		renderer = Gtk.CellRendererText()
		self.theme_name_style_combo.pack_start(renderer, True)
		self.theme_name_style_combo.add_attribute(renderer, "text", 0)
		self.theme_name_style_combo.set_model(theme_style_store)
		
		self.icon_theme_name_style_combo = self.builder.get_object("icon_theme_name_style_combo")
		renderer = Gtk.CellRendererText()
		self.icon_theme_name_style_combo.pack_start(renderer, True)
		self.icon_theme_name_style_combo.add_attribute(renderer, "text", 0)
		self.icon_theme_name_style_combo.set_model(theme_style_store)
		
		self.plank_theme_name_style_combo = self.builder.get_object("plank_theme_name_style_combo")
		renderer = Gtk.CellRendererText()
		self.plank_theme_name_style_combo.pack_start(renderer, True)
		self.plank_theme_name_style_combo.add_attribute(renderer, "text", 0)
		self.plank_theme_name_style_combo.set_model(theme_style_store)
		
		# Widget signals
		self.randomize_button.connect("clicked", self.on_random_button)
		self.save_button.connect("clicked", self.on_save_button)
		# self.quit_button.connect("clicked", self.on_quit)
		
		#TODO: Show entries when icon, cursor and darker switch is clicked
		# self.icon_switch.connect("notify::active", self.load_conf)
		# self.cursor_switch.connect("notify::active", self.load_conf)
		# self.darkermode_switch.connect("notify::active", self.load_conf)
		
		# Menubar
		accel_group = Gtk.AccelGroup()
		self.window.add_accel_group(accel_group)
		menu = self.builder.get_object("main_menu")
		# Add "Start Indicator" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("theme-manager", Gtk.IconSize.MENU))
		item.set_label(_("Start Indicator"))
		item.connect("activate", self.start_indicator)
		key, mod = Gtk.accelerator_parse("<Control>I")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "Show Logs" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("text-x-log", Gtk.IconSize.MENU))
		item.set_label(_("Show Logs"))
		item.connect("activate", self.show_logs, self.window)
		key, mod = Gtk.accelerator_parse("<Control>L")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "About" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU))
		item.set_label(_("About"))
		item.connect("activate", self.open_about, self.window)
		key, mod = Gtk.accelerator_parse("F1")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "Quit" option in drop-down menu
		item = Gtk.ImageMenuItem(label=_("Quit"))
		image = Gtk.Image.new_from_icon_name("application-exit-symbolic", Gtk.IconSize.MENU)
		item.set_image(image)
		item.connect('activate', self.on_quit)
		key, mod = Gtk.accelerator_parse("<Control>Q")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		key, mod = Gtk.accelerator_parse("<Control>W")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Show all drop-down menu options
		menu.show_all()
		
		self.load_conf()
		self.state = self.manager.get_state_info()
		self.currenttheme = self.destop_manager.get_desktop_theme(self.state, self.manager.systemthemename, self.manager.colvariants)
		self.current_status()
	
	def load_conf(self):
		
		self.manager.load_config()
		self.color_variants.set_text(str(self.manager.colorvariants))
		self.systemtheme_variants.set_text(str(self.manager.systemthemename))
		self.darkmode_name.set_text(str(self.manager.darkmode_suffix))
		self.darkermode_switch.set_active(self.manager.darkermode)
		self.darkermode_name.set_text(str(self.manager.darkermode_suffix))
		self.theme_name_style_combo.set_active(self.manager.theme_name_style) # Select 1st category
		if self.manager.darkermode:
			self.darkermode_label.set_visible(True)
			self.darkermode_name.set_visible(True)
		else:
			self.darkermode_label.set_visible(False)
			self.darkermode_name.set_visible(False)
		
		self.icon_switch.set_active(self.manager.icon_theme)
		self.icon_theme_name.set_text(str(self.manager.iconthemename))
		self.icon_colour_variants.set_text(str(self.manager.icon_colorvariants))
		if self.manager.icon_theme:
			self.icon_settings.set_visible(True)
		else:
			self.icon_settings.set_visible(False)
		self.icon_darkmode_name.set_text(str(self.manager.icon_darkmode_suffix))
		self.icon_theme_name_style_combo.set_active(self.manager.icon_theme_name_style) # Select 1st category
		
		self.cursor_switch.set_active(self.manager.cursor_theme)
		self.cursor_theme_name.set_text(str(self.manager.cursorthemename))
		self.cursor_colour_variants.set_text(str(self.manager.cursor_colorvariants))
		if self.manager.cursor_theme:
			self.cursor_settings.set_visible(True)
		else:
			self.cursor_settings.set_visible(False)
		
		self.plank_switch.set_active(self.manager.plank_theme)
		self.plank_theme_name.set_text(str(self.manager.plankthemename))
		self.plank_colour_variants.set_text(str(self.manager.plank_colorvariants))
		if self.manager.plank_theme:
			self.plank_settings.set_visible(True)
		else:
			self.plank_settings.set_visible(False)
		self.plank_darkmode_name.set_text(str(self.manager.plank_darkmode_suffix))
		self.plank_theme_name_style_combo.set_active(self.manager.plank_theme_name_style) # Select 1st category
		
		self.systime_switch.set_active(self.manager.use_systemtime)
		if self.manager.use_systemtime:
			self.systime_grid.set_visible(True)
			if self.manager.darkermode:
				self.systime_transition_grid.set_visible(True)
			else:
				self.systime_transition_grid.set_visible(False)
		else:
			self.systime_grid.set_visible(False)
			self.systime_transition_grid.set_visible(False)
		
		self.day_start_time.set_time(self.manager.day_start_time)
		self.night_start_time.set_time(self.manager.night_start_time)
		self.d2n_start_time.set_time(self.manager.d2n_start_time)
		self.n2d_start_time.set_time(self.manager.n2d_start_time)
		
		self.user_interval_HH.set_value(self.manager.theme_interval_HH)
		self.user_interval_MM.set_value(self.manager.theme_interval_MM)
		self.user_interval_SS.set_value(self.manager.theme_interval_SS)
	
	def open_about(self, signal, widget):
		about_window = AboutWindow(widget)
		about_window.show()
	
	def show_logs(self, signal, widget):
		loggerwindow = LoggerWindow(widget)
		loggerwindow.show()
	
	def on_quit(self, widget):
		self.application.quit()
	
	def on_random_button(self, widget):
		module_logger.info("User requested change using Randomize button.")
		self.state = self.manager.get_state_info()
		self.nexttheme = self.manager.prep_theme_variants(self.state, self.theme_styles)
		self.destop_manager.set_desktop_theme(self.state, self.nexttheme)
		self.currenttheme = self.destop_manager.get_desktop_theme(self.state, self.manager.systemthemename, self.manager.colvariants)
		self.current_status()
	
	def on_save_button(self, widget):
		"""Saves user configurations to config file.
		
		Saves user-defined configurations to config file.
		If the config file does not exist, it creates a new
		config file (~/.config/theme-manager/config.cfg)
		in user's home directory.
		"""
		Hr = str(self.user_interval_HH.get_value_as_int())
		Min = str(self.user_interval_MM.get_value_as_int())
		Sec = str(self.user_interval_SS.get_value_as_int())
		user_interval = Hr+':'+Min+':'+Sec
		self.manager.config['system-theme'] = {
			'color-variants': self.color_variants.get_text(),
			'system-theme-name': self.systemtheme_variants.get_text(),
			'dark-mode-suffix': self.darkmode_name.get_text(),
			'darker-mode': self.darkermode_switch.get_active(),
			'darker-mode-suffix': self.darkermode_name.get_text(),
			'theme-style-name': self.theme_name_style_combo.get_active(),
			'icon-theme': self.icon_switch.get_active(),
			'icon-theme-name': self.icon_theme_name.get_text(),
			'icon-color-variants': self.icon_colour_variants.get_text(),
			'icon-dark-mode-suffix': self.icon_darkmode_name.get_text(),
			'icon-theme-style-name': self.icon_theme_name_style_combo.get_active(),
			'cursor-theme': self.cursor_switch.get_active(),
			'cursor-theme-name': self.cursor_theme_name.get_text(),
			'cursor-color-variants': self.cursor_colour_variants.get_text(),
			'plank-theme': self.plank_switch.get_active(),
			'plank-theme-name': self.plank_theme_name.get_text(),
			'plank-color-variants': self.plank_colour_variants.get_text(),
			'plank-dark-mode-suffix': self.plank_darkmode_name.get_text(),
			'plank-theme-style-name': self.plank_theme_name_style_combo.get_active()
		}
		self.manager.config['time-settings'] = {
			'use-system-time': self.systime_switch.get_active(),
			'day-start-time': self.day_start_time.get_time(),
			'night-start-time': self.night_start_time.get_time(),
			'd2n-start-time': self.d2n_start_time.get_time(),
			'n2d-start-time': self.n2d_start_time.get_time(),
			'theme-interval': user_interval
		}
		with open(CONFIG_FILE, 'w') as f:
				self.manager.config.write(f)
		
		self.load_conf()
	
	def current_status(self):
		'''
		Show current theme info in status bar.
		'''
		status = "DE: %s, \tState: %s, \tVariant: %s, \tLast Updated: %s, \tThemes: %s" % (self.state['DE'], self.state['State'], self.currenttheme["Variant"], self.currenttheme["Last Updated"], self.currenttheme["Themes"])
		
		context_id = self.statusbar.get_context_id("status")
		self.statusbar.push(context_id, status)
	
	def start_indicator(self, widget):
		module_logger.info("Initiaing Theme Manager Indicator from main window.")
		_async(TMIndicator())
		

def run_TMwindow():
	application = theme_manager("org.mamolinux.theme-manager", Gio.ApplicationFlags.FLAGS_NONE)
	application.run()
