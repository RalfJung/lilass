# LiLaSS: Linux Laptop Screen Setup

## Introduction

This is the documentation of [LiLaSS]( https://www.ralfj.de/projects/lilass), a 
tool to setup screens on a Linux-powered Laptop.

LiLaSS is targeted for a specific use-case: The laptop is used both with the 
internal screen only, and in combination with a single external screen. 
[xrandr](http://www.x.org/wiki/Projects/XRandR) is used to detect whether an 
external screen is plugged in, and to change the configuration according to the 
user's specification.

## Usage

LiLaSS features an interactive and a batched mode of use.
Either way, if LiLaSS is started while no external screen is connected, it
enables the internal screen.

It is in the case that an external screen is plugged in that the two modes
differ.

Simply run `lilass` to start the interactive mode. A window will pop up, 
allowing you to select which screens are enabled, their resolution, and how they 
are positioned relatively to each other. The option `--frontend` (or `-f`) 
can be used to choose the frontend which opens the window. Currently, the 
frontends `qt` (using Qt5) and `zenity` are available. LiLaSS attempts to
choose an adequate frontend automatically.

The option `--relative-position` (`-r`) suppresses the interactive 
configuration. Instead, the given given option (`left`, `right`, `above`, 
`below` or `mirror`) is applied with the default resolution of the external 
screen.

Finally, the flags `--internal-only` (`-i`) and `--external-only` (`-e`) 
tells LiLaSS to use only one of the two screens.

If the internal screen ends up being the only one that is used, LiLaSS attempts 
to turn on your backlight if it was disabled.

## Automatic Configuration

In combination with [x-on-resize](http://keithp.com/blogs/x-on-resize/) by Keith 
Peckard, LiLaSS can automatically pop-up when a screen is plugged in, and 
automatically re-enable the internal screen the external one is plugged off.

Besides, you may want to apply some configuration without pop-up if an
external screen is plugged in when you log in to your desktop environment.

All this is achieved by running the following shell script on log-in:

    LILASS=/path/to/lilass
    x-on-resize -c $LILASS
    $LILASS --external-only

## Configuration File

You can use `~/.lilass.conf` to tell LiLaSS which are the names of your 
internal and external connectors. These are the names as used by `xrandr`. The 
option `internalConnector` gives the name of the xrandr connector 
corresponding to your internal laptop screen. All the others will be considered 
external screens, unless you use the option `externalConnectors` to provide a 
(space-separated) list of connectors to be considered external by LiLaSS. Any 
connector not mentioned in either option will be completely ignored.

## Source, License

You can find the sources in the [git 
repository](http://www.ralfj.de/git/lilass.git) (also available [on 
GitHub](https://github.com/RalfJung/lilass)). They are provided under the 
[GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html) or (at your 
option) any later version of the GPL. See the file `LICENSE-GPL2` for more 
details.

## Contact

If you found a bug, or want to leave a comment, please
[send me a mail](mailto:post-AT-ralfj-DOT-de). I'm also happy about pull
requests :)
