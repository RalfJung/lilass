# LiLaSS: Linux Laptop Screen Setup

## Introduction

This is the documentation of [LiLaSS](https://www.ralfj.de/projects/lilass), a
tool to setup screens on a Linux-powered Laptop.

LiLaSS is targeted for a specific use-case: The laptop is used both with the
internal screen only, and in combination with a single external screen.
[xrandr](http://www.x.org/wiki/Projects/XRandR) is used to detect whether an
external screen is plugged in, and to change the configuration according to the
user's specification.  Furthermore, LiLaSS remembers the configuration used for
any particular screen, so that it can offer the same configuration next time.
You can even make it apply that configuration automatically.

## Usage

LiLaSS features an interactive and a batched mode of use.  Either way, if LiLaSS
is started while no external screen is connected, it enables the internal
screen.

It is in the case that an external screen is plugged in that the two modes
differ.

Simply run `lilass` to start the interactive mode.  A window will pop up,
allowing you to select which screens are enabled, their resolution, and how they
are positioned relatively to each other.  The option `--frontend` (or `-f`) can
be used to choose the frontend which opens the window. Currently, the frontends
`qt` (using Qt5), `zenity` and `cli` are available.  LiLaSS attempts to choose
an adequate frontend automatically.

If a screen is connected that was already configured with LiLaSS before, the
previously selected configuration will be offered per default.  You can pass
`--silent` (`-s`) to instead suppress the UI altogether, and just apply the
previous configuration.  You can disable the use of the stored screen
configurations by passing `--no-db`.

Furthermore, you can also suppress the UI in case LiLaSS sees a new screen by
telling LiLaSS directly what to do with that screen: With the flags
`--internal-only` (`-i`) and `--external-only` (`-e`), one of the two screens is
picked and the other one disabled.  With `--relative-position` (`-r`), the
relative position of the two screens can be set (`left`, `right`, `above`,
`below` or `mirror`). In either case, the preferred possible resolution(s) of
the screen(s) will be picked if applicable. (In `mirror` mode, LiLaSS instead
picks the largest resolution that both screens have in common.)

If the internal screen ends up being the only one that is used, LiLaSS attempts 
to turn on your backlight if it was disabled.

## Automatic Configuration

In combination with [x-on-resize](http://keithp.com/blogs/x-on-resize/) by Keith
Peckard, LiLaSS can be run automatically when a screen is plugged in, and
automatically re-enable the internal screen the external one is plugged off.  As
LiLaSS remembers the screen configuration that was used last time, this
automatic mode will use the previous configuration if the same screen is
connected again.

All this is achieved by running the following on log-in:

    x-on-resize --config "lilass -s -r mirror" --start

Of course, instead of `-r mirror`, you can pick a different default
configuration applied to screens that have not been seen previously. By dropping
this option altogether, LiLaSS will instead pop up and ask what to do when a new
screen is connected.

## Configuration File

You can use `~/.config/lilass.conf` to tell LiLaSS which are the names of your
internal and external connectors.  These are the names as used by `xrandr`.  The
option `internalConnector` gives the name of the xrandr connector corresponding
to your internal laptop screen.  All the others will be considered external
screens, unless you use the option `externalConnectors` to provide a
(space-separated) list of connectors to be considered external by LiLaSS.  Any
connector not mentioned in either option will be completely ignored.

## Source, License

You can find the sources in the
[git repository](https://git.ralfj.de/lilass.git) (also available
[on GitHub](https://github.com/RalfJung/lilass)). They are provided under the
[GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html) or (at your
option) any later version of the GPL.  See the file `LICENSE-GPL2` for more
details.

## Contact

If you found a bug, or want to leave a comment, please
[send me a mail](mailto:post-AT-ralfj-DOT-de).  I'm also happy about pull
requests :)
