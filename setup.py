
import glob

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

setup(
data_files=[('share/theme-manager/ui', glob.glob("data/ui/*")),
            ('share/applications', glob.glob("data/applications/*.desktop")),
            ('share/icons/hicolor/scalable/apps', glob.glob("data/icons/*")),
            ]
)
