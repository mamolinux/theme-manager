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
import setproctitle
import sys

# imports from current package
from ThemeManager.common import APP, LOCALE_DIR, LOGFILE, __version__
from ThemeManager.cli_args import command_line_args
from ThemeManager.indicator import ThemeIndicator
from ThemeManager.gui import run_TMwindow


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

setproctitle.setproctitle(APP)

# Parse arguments
parser = command_line_args()
args = parser.parse_args()

args.start_window = True

if args.show_version:
    print("%s: version %s" % (APP, __version__))
    sys.exit(0)

# Create logger
logger = logging.getLogger('ThemeManager')
# Set logging level
logger.setLevel(logging.DEBUG)
# create log formatter
log_format = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')

# create file handler which logs only info messages
fHandler = logging.FileHandler(LOGFILE)
# Set level for FileHandler
fHandler.setLevel(logging.INFO)

# add formatter to the fHandler
fHandler.setFormatter(log_format)

# add the handler to the logger
logger.addHandler(fHandler)

if args.show_debug:
	# be verbose only when "-v[erbose]" is supplied
	# Create StreamHandler which logs even debug messages
	cHandler = logging.StreamHandler()
	# Set level for StreamHandler
	cHandler.setLevel(logging.DEBUG)
	
	# add formatter to the handler
	cHandler.setFormatter(log_format)

	# add the handler to the logger
	logger.addHandler(cHandler)

# module logger
module_logger = logging.getLogger('ThemeManager.main')

def start_TM ():
	if args.start_indicator:
		args.start_window = False
		# initiaing app indicator
		module_logger.debug("Initiaing Theme Manager Indicator.")
		try:
			ThemeIndicator()
		except KeyboardInterrupt:
			logger.info(_("Theme Manager Indicator exited cleanly."))
	
	if args.start_window:
		# initiaing app window
		module_logger.debug("Initiaing Theme Manager Window.")
		run_TMwindow()
