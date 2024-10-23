python_sources = [
  'about_window.py',
  'cli_args.py',
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

args_file = configure_file(
  input: 'cli_args.py',
  output: 'cli_args.py',
  configuration: {
    'appname': application_id,
    'localedir': join_paths(prefix, get_option('localedir')),
  }
)

python.install_sources(
  python_sources, version_file, args_file,
  subdir: 'ThemeManager',
  preserve_path: true,
)

# Install assets like ui and icons
ui = files('ui/theme-manager.ui', 'ui/logger.ui')

install_data(
  ui,
  install_dir: join_paths(pysrcinstalldir, 'ThemeManager', 'ui')
)
