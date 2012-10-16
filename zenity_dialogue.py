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
# along with this program (gpl.txt); if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import subprocess
from dsl import RelativeScreenPosition, ScreenSetup, res2user

def userChoose (title, choices, returns):
	assert len(choices) == len(returns)
	p = subprocess.Popen(["zenity", "--list", "--text="+title, "--column="]+choices, stdout=subprocess.PIPE)
	switch = dict (zip (choices,returns))
	for line in p.stdout:
		return switch.get(line.strip(), None)

def run (internalResolutions, externalResolutions):
	relpos = userChoose ("Position of external screen", ["Left of internal screen", "Right of internal screen", "Use external screen only"], [RelativeScreenPosition.LEFT, RelativeScreenPosition.RIGHT, RelativeScreenPosition.EXTERNAL_ONLY])
	if relpos == None:
		return None
	intres = internalResolutions[0]
	if relpos != RelativeScreenPosition.EXTERNAL_ONLY:
		intres = userChoose ("internal display resolution", map(res2user,internalResolutions), internalResolutions)
	if intres == None:
		return None
	extres = userChoose ("external display resolution", map(res2user,externalResolutions), externalResolutions)
	if extres == None:
		return None
	extprim = userChoose ("Which display should be the primary display?", ["internal display", "external display"], [False, True])
	if extprim == None:
		return None
	return ScreenSetup(relpos,intres,extres,extprim)
