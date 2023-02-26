# [Theme Manager](https://hsbasu.github.io/theme-manager)

<p align="center">
  	<img src="https://raw.githubusercontent.com/mamolinux/theme-manager/master/data/icons/theme-manager.svg?sanitize=true" height="128" alt="Logo">
</p>

<p align="center">
	<a href="#">
		<img src="https://img.shields.io/github/actions/workflow/status/mamolinux/theme-manager/ci.yml?branch=master&label=CI%20Build" alt="CI build">
	</a>
	<a href="#">
		<img src="https://img.shields.io/github/actions/workflow/status/mamolinux/theme-manager/codeql-analysis.yml?branch=master&label=CodeQL%20Build" alt="CodeQL build">
	</a>
	<a href="https://github.com/mamolinux/theme-manager/blob/master/LICENSE">
		<img src="https://img.shields.io/github/license/mamolinux/theme-manager?label=License" alt="License">
	</a>
  	<a href="#">
		<img src="https://img.shields.io/github/repo-size/mamolinux/theme-manager?label=Repo%20size" alt="GitHub repo size">
  	</a>
	<a href="https://github.com/mamolinux/theme-manager/issues" target="_blank">
		<img src="https://img.shields.io/github/issues/mamolinux/theme-manager?label=Issues" alt="Open Issues">
	</a>
	<a href="https://github.com/mamolinux/theme-manager/pulls" target="_blank">
		<img src="https://img.shields.io/github/issues-pr/mamolinux/theme-manager?label=PR" alt="Open PRs">
	</a>
  	<a href="https://github.com/mamolinux/theme-manager/releases/latest">
    	<img src="https://img.shields.io/github/v/release/mamolinux/theme-manager?label=Latest%20Stable%20Release" alt="GitHub release (latest by date)">
  	</a>
	<a href="#download-latest-version">
		<img src="https://img.shields.io/github/downloads/mamolinux/theme-manager/total?label=Downloads" alt="Downloads">
	</a>
	<a href="https://github.com/mamolinux/theme-manager/releases/download/1.1.3/theme-manager_1.1.3_all.deb">
		<img src="https://img.shields.io/github/downloads/mamolinux/theme-manager/1.1.3/theme-manager_1.1.3_all.deb?color=blue&label=Downloads%40Latest%20Binary" alt="GitHub release (latest by date and asset)">
	</a>
</p>

Very simple Python3-based GUI application to set different theme colour and mode (dark/light) variants on linux.

## Download Latest Version
<p align="center">
	<a href="https://github.com/mamolinux/theme-manager/zipball/master">Download Source (.zip)</a></br>
	<a href="https://github.com/mamolinux/theme-manager/tarball/master">Download Source (.tar.gz)</a></br>
	<a href="https://github.com/mamolinux/theme-manager/releases/download/1.1.3/theme-manager_1.1.3_all.deb">Download Binary (.deb)</a>
</p>

## Features and Screenshots

The main purpose of this application is to randomly choose and set a desktop theme based on time.

<p align="center">
	<img src="https://github.com/mamolinux/theme-manager/raw/gh-pages/screenshots/main-window-light.png" alt="Main Window (Light)">
	<img src="https://github.com/mamolinux/theme-manager/raw/gh-pages/screenshots/main-window-dark.png" alt="Main Window (Dark)">
</p>


## Contents
- [Download Latest Version](#download-latest-version)
- [Features and Screenshots](#features-and-screenshots)
- [Dependencies](#dependencies)
	- [Debian/Ubuntu based systems](#debianubuntu-based-distro)
	- [Other Linux-based systems](#other-linux-based-distro)
- [Installation](#build-and-install-the-latest-version)
	- [Debian/Ubuntu based systems](#debianubuntu-based-systems)
	- [Other Linux-based systems](#other-linux-based-systems)
	- [For Developers](#for-developers)
- [User Manual](#user-manual)
- [Issue Tracking and Contributing](#issue-tracking-and-contributing)
- [Contributors](#contributors)
	- [Authors](#author)

## Dependencies
```
gir1.2-appindicator3-0.1
python3
python3-configobj
python3-gi
python3-setproctitle
python3-tldextract
redshift
```
To use or test Theme Manager, you need these dependencies to be installed.

### Debian/Ubuntu based distro
To install dependencies on Debian/Ubuntu based systems, run:
```
sudo apt install gir1.2-appindicator3-0.1 python3 python3-configobj python3-gi \
python3-setproctitle python3-tldextract redshift
```
**Note**: If you are using `gdebi` to install **Theme Manager** from a `.deb` file, it will automatically install the dependencies and you can skip this step.

### Other Linux-based distro
Replace `apt install` in the command given in [Debian/Ubuntu based distros](#debianubuntu-based-distro) and use the command for the package manager of the target system(eg. `yum install`, `dnf install`, `pacman -S` etc.)

**Note**: There might be cases where one or more dependencies might not be available for your system. But that is highly unlikely. In such situations, please [create an issue](#issue-tracking-and-contributing).

## Build and Install the Latest Version
### Debian/Ubuntu based systems
There are two methods, this app can be installed/used on a Debian/Ubuntu based system. First, download and unzip the source package using:
```
wget https://github.com/mamolinux/theme-manager/archive/refs/heads/master.zip
unzip master.zip
cd theme-manager-master
```

1. **Option 1:** Manually copying necessary files to root (`/`). For that, follow the steps below:
	1. [**Optional**] [**In Progress**] To make translations/locales in languages other than **English**, run:
		```
		make
		```
		from the `theme-manager-master` in a terminal. It will create the translations/locales in `usr/share/locale`.
	
	2. Install python package using `pip3`:
		```
		sudo pip3 install .
		```
		It will install all files under `/usr/local/`
	3. Compile `schemas` using:
		```
		sudo glib-compile-schemas /usr/local/share/glib-2.0/schemas
		```

2. **Option 2:** Build a debian package and install it. To build a debian package on your own:
	1. from the `theme-manager-master` run:
		```
		dpkg-buildpackage --no-sign
		```
		This will create a `theme-manager_*.deb` package at `../theme-manager-master`.
	
	2. Install the debian package using
		```
		sudo dpkg -i ../theme-manager_*.deb
		sudo apt install -f
		```
After it is installed, run `theme-manager` from terminal or use the `theme-manager.desktop`.

### Other Linux-based systems
1. Install the [dependencies](#other-linux-based-distro).
2. From instructions for [Debian/Ubuntu based systems](#debianubuntu-based-systems), follow **Option 1**.


### For Developers
Instructions for devs are coming soon or create a [PR](https://github.com/mamolinux/theme-manager/compare).

**I have no knowledge on how to use `meson` or `npm` for testing. If you can offer any help regarding this, please start a discussion [here](https://github.com/mamolinux/theme-manager/discussions) or create a [PR](https://github.com/mamolinux/theme-manager/compare). It will be more than welcome.**

## User Manual
Coming Soon or create a PR.

## Issue Tracking and Contributing
If you are interested to contribute and enrich the code, you are most welcome. You can do it by:
1. If you find a bug, to open a new issue with details: [Click Here](https://github.com/mamolinux/theme-manager/issues)

2. If you know how to fix a bug or want to add new feature/documentation to the existing package, please create a [Pull Request](https://github.com/mamolinux/theme-manager/compare).

## Contributors

### Author
[Himadri Sekhar Basu](https://github.com/hsbasu) is the author and current maintainer.

## Donations
I am a freelance programmer. So, If you like this app and would like to offer me a coffee ( &#9749; ) to motivate me further, you can do so via:

[![](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/hsbasu/donate)
[![](https://www.paypalobjects.com/webstatic/i/logo/rebrand/ppcom.svg)](https://paypal.me/hsbasu)
[![](https://hsbasu.github.io/styles/icons/logo/svg/upi-logo.svg)](https://hsbasu.github.io/images/upi-qr.jpg)
