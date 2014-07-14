DSL - easy Display Setup for Laptops
====================================

Introduction
------------

This is the documentation of DSL_, a tool to setup screens on a Linux-powered
Laptop.

DSL is targeted for a specific use-case: The laptop is used both with the
internal screen only, and in combination with a single external screen.
xrandr_ is used to detect whether an external screen is plugged in, and
to change the configuration according to the user's specification.

.. _DSL: https://www.ralfj.de/projects/dsl
.. _xrandr: http://www.x.org/wiki/Projects/XRandR

Usage
-----

DSL features an interactive and a batched mode of use.
Either way, of DSL is started while no external screen is connected, it
enables the internal screen. It also resets the backlight to 100%, as some
laptops keep the backlight off if it was turned off by power-saving features.

It is in the case that an external screen is plugged in that the two modes
differ.

Simply run ``dsl.py`` to start the interactive mode. A window will pop up,
allowing you to select the resolution of the external screen and where it
will appear relative to the laptop. The option ``--frontend`` (or ``-f``) can
be used to choose the frontend which opens the window. Currently, the
frontends ``qt`` and ``zenity`` are available. DSL attempts to choose an
adequate frontend automatically.

The option ``--relative-position`` (``-f``) suppresses the interactive
configuration. Instead, the given given option (``left``, ``right`` or
``external-only``) is applied with the default resolution of the external
screen.

Finally, the flag ``--internal-only`` (``-i``) tells DSL to ignore the
external screen and enable the internal one.

Automatic Configuration
-----------------------

In combination with x-on-resize_ by Keith Peckard, DSL can automatically
pop-up when a screen is plugged in, and automatically re-enable the internal
screen the external one is plugged off.

Besides, you may want to apply some configuration without pop-up if an
external screen is plugged in when you log in to your desktop environment.

All this is achieved by running the following shell script on log-in::

  DSL=/path/to/dsl.py
  x-on-resize -c $DSL
  $DSL -r external-only

.. _x-on-resize: http://keithp.com/blogs/x-on-resize/

Configuration File
------------------

You can use ``~/.dsl.conf`` to tell DSL which are the names of your internal
and external connectors. These are the names as used by ``xrandr``.
The option ``internalConnector`` gives the name of the xrandr connector
corresponding to your internal laptop screen. All the others will be
considered external screens, unless you use the option ``externalConnectors``
to prove a (space-separated) list of connectors to be considered external by
DSL. Any connector not mentioned in either option will be completely ignored.

Source, License
---------------

You can find the sources in the `git repository`_. They are provided under
the GPLv2_ or (at your option) any later version of the GPL.

.. _git repository: http://www.ralfj.de/git/dsl.git
.. _GPLv2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

Contact
-------

If you found a bug, or want to leave a comment, please
`send me a mail <mailto:post-AT-ralfj-DOT-de>`_.
