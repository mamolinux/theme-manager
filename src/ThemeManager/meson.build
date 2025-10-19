python_sources = files(
  run_command(
    'find', '.', '-name', '*.py', '-not', '-name', 'cli_args*', check: true
  ).stdout().strip().split('\n')
)

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
ui = files(
  run_command(
    'find', 'ui', '-name', '*.ui', check: true
  ).stdout().strip().split('\n')
)

install_data(
  ui,
  install_dir: join_paths(pysrcinstalldir, 'ThemeManager', 'ui')
)
