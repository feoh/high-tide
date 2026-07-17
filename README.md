<div align="center">
  <img height="128" src="data/icons/hicolor/scalable/apps/io.github.nokse22.high-tide.svg" alt="High Tide Logo"/>
  
  # High Tide
  
  <p align="center">
    <strong>Linux client for TIDAL streaming service</strong>
  </p>
  
  <p align="center">
    <a href="https://www.gnu.org/licenses/gpl-3.0">
      <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3"/>
    </a>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Made%20with-Python-ff7b3f.svg" alt="Made with Python"/>
    </a>
  </p>
</div>

> [!IMPORTANT] 
> Not affiliated in any way with TIDAL, this is a third-party unofficial client

<table>
  <tr>
    <th><img src="data/resources/screenshot 1.png"/></th>
    <th><img src="data/resources/screenshot 2.png"/></th>
  </tr>
</table>

## 🚀 Installation
### 🛒 Flathub

<a href='https://flathub.org/apps/io.github.nokse22.high-tide'><img height='80' alt='Download on Flathub' src='https://dl.flathub.org/assets/badges/flathub-badge-en.png'/></a>
</details>

### 📦 From latest build

Go to the [Actions page](https://github.com/Nokse22/high-tide/actions), click on the latest working build and download the Artifact for your architecture.
Extract the .flatpak file from the downloaded .zip file and install it clicking on it or with:

`flatpak install high-tide.flatpak`

Beware: Locales are not available when installing from a `.flatpak` file, since flatpak locales are stored in another runtime for optimisations, and `.flatpak` files only export the app without runtimes.

If you want/need locales, please build from source.

### ⚡ From source (binary)

You just need to clone the repository and build with Meson.

For a safe user-local install into `~/.local`, use the helper script:

```sh
git clone https://github.com/Nokse22/high-tide.git
cd high-tide
bin/high-tide-local install
```

This configures `build-local` with `--prefix ~/.local`, builds the app,
installs it, and leaves Meson's install log in
`build-local/meson-logs/install-log.txt` for a matching uninstall.

If your shell has already cached the `high-tide` command path, refresh it after
installing:

```sh
# zsh
rehash

# bash
hash -r
```

Or open the project in GNOME Builder and click "Run Project".

## ❌ Uninstallation

First, terminate all High Tide processes. Keep in mind that "Run in
background" is an option, usually pressing ^Q should be enough to terminate it.

### Local source install

If you installed from this checkout with `bin/high-tide-local install`, preview
the uninstall first:

```sh
cd high-tide
bin/high-tide-local uninstall --dry-run
```

Then remove the installed files:

```sh
bin/high-tide-local uninstall --yes
```

The helper only removes High Tide files listed in Meson's install log and
matching High Tide's expected install paths. It does not delete user preferences,
login state, caches, or history.

Refresh your shell's command cache afterwards if needed:

```sh
# zsh
rehash

# bash
hash -r
```

### Flatpak install

If you installed the Flatpak package, remove it with Flatpak:

```sh
# When installed system-wide (default)
flatpak uninstall --delete-data io.github.nokse22.high-tide

# When installed for the current user (-u flag at installation)
flatpak uninstall --delete-data -u io.github.nokse22.high-tide
```

The `--delete-data` flag should get rid of Flatpak's app data directories.

## 🤝 Contributing

Read [CONTRIBUTING](CONTRIBUTING.md) for all information about how to contribute to High Tide, you can also contact us on Matrix [#high-tide:matrix.org](https://matrix.to/#/%23high-tide:matrix.org).

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](COPYING) file for details.

## 🌟 Support the Project

If you find High Tide useful, please consider:

- ⭐ Starring this repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 🔄 Sharing with others who might find it useful

---

<div align="center">
  <p>Made with ❤️ by the High Tide community</p>
  <p>
    <a href="https://github.com/Nokse22/high-tide">View on GitHub</a> • 
    <a href="https://github.com/Nokse22/high-tide/issues">Report Bug</a> • 
    <a href="https://github.com/Nokse22/high-tide/issues">Request Feature</a>
  </p>
</div>
