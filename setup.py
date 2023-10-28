import glob, os
import distutils.command.install_data

from distutils.log import info
from setuptools import setup
from subprocess import check_output

for line in check_output('dpkg-parsechangelog --format rfc822'.split(),
                         universal_newlines=True).splitlines():
    header, colon, value = line.lower().partition(':')
    if header == 'version':
        version = value.strip()
        break
else:
    raise RuntimeError('No version found in debian/changelog')

with open("src/ThemeManager/VERSION", "w") as f:
    if '~' in version:
        version = version.split('~')[0]
    f.write("%s" % version)

gschema_dir_suffix = 'share/glib-2.0/schemas'

class install_data(distutils.command.install_data.install_data):
    def run(self):
        # Python 3 'super' call.
        super().run()
        
        # Compile '*.gschema.xml' to update or create 'gschemas.compiled'.
        info("compiling gsettings schemas")
        # Use 'self.install_dir' to build the path, so that it works
        # for both global and local '--user' installs.
        gschema_dir = os.path.join(self.install_dir, gschema_dir_suffix)
        self.spawn(["glib-compile-schemas", gschema_dir])

setup(data_files=[('share/applications', glob.glob("data/applications/*.desktop")),
        ('share/icons/hicolor/scalable/apps', glob.glob("data/icons/*")),
        (gschema_dir_suffix, glob.glob("data/*.xml"))
        ],
        cmdclass = {'install_data': install_data}
)
