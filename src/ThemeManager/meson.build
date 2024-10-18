python_sources = [
  'about_window.py',
	'common.py',
	'DesktopTheme.py',
	'gui.py',
	'indicator.py',
	'__init__.py',
	'logger.py',
	'LoginTheme.py',
	'main.py',
	'time_chooser.py',
	'tm_daemon.py',
]

version_file = configure_file(
  input: 'VERSION.in',
  output: 'VERSION',
  configuration: {
    'version': meson.project_version(),
  }
)

python.install_sources(
  python_sources, version_file,
  subdir: 'ThemeManager',
  preserve_path: true,
)

# Install assets like ui and icons
ui = files('ui/theme-manager.ui', 'ui/logger.ui')

install_data(
  ui,
  install_dir: join_paths(pysrcinstalldir, 'ThemeManager', 'ui')
)
