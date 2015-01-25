# DSL - easy Display Setup for Laptops
# Copyright (C) 2012 Ralf Jung <post@ralfj.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from dsl import RelativeScreenPosition, ScreenSetup, res2user, processOutputIt

def userChoose (title, choices, returns, fallback):
    assert len(choices) == len(returns)
    args = ["zenity", "--list", "--text="+title, "--column="]+choices
    switch = dict (list(zip (choices,returns)))
    for line in processOutputIt(*args):
        return switch.get(line.strip(), fallback)
    return fallback

def run (internalResolutions, externalResolutions):
    relpos = userChoose ("Position of external screen", ["Left of internal screen", "Right of internal screen", "Use external screen only"], [RelativeScreenPosition.LEFT, RelativeScreenPosition.RIGHT, RelativeScreenPosition.EXTERNAL_ONLY], None)
    if relpos == None:
        return None
    intres = internalResolutions[0]
    if relpos != RelativeScreenPosition.EXTERNAL_ONLY:
        intres = userChoose ("internal display resolution", list(map(res2user,internalResolutions)), internalResolutions, internalResolutions[0])
    extres = userChoose ("external display resolution", list(map(res2user,externalResolutions)), externalResolutions, externalResolutions[0])
    extprim = userChoose ("Which display should be the primary display?", ["internal display", "external display"], [False, True], None)
    if extprim == None:
        return None
    return ScreenSetup(relpos,intres,extres,extprim)
