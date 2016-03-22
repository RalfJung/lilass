# DSL - easy Display Setup for Laptops
# Copyright (C) 2012      Ralf Jung <post@ralfj.de>
# Copyright (C) 2012-2015 Constantin Berhard<constantin@exxxtremesys.lu>
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

from screen import RelativeScreenPosition, ScreenSetup, processOutputIt

from enum import Enum

class OperationMode(Enum):
    INTERNAL_ONLY = ("Use internal display only")
    EXTERNAL_ONLY = ("Use external display only")
    USE_BOTH      = ("Use both displays")
    def __init__(self, text):
        # auto numbering
        cls = self.__class__
        self._value_ = len(cls.__members__)
        # description
        self.text = text

class QuestionFrontend:
    def userChoose (self, title, choices, returns, fallback):
        raise Exception("The abstract method 'userChoose' has not been implemented by %s"%str(self.__class__))

    def selectResolution(self, displayname, availablemodes):
        modedescs = list(map(str, availablemodes))
        return self.userChoose("Select resolution for %s"%displayname, modedescs, availablemodes, None)

    def setup (self, situation):
        if situation.previousSetup:
            applyPrevious = self.userChoose("This display is known. The last setup for it was like this:\n%s.\nApply the last used configuration?" % str(situation.previousSetup), ("Apply last setup", "Enter different setup"), (True,False), None)
            if applyPrevious is None:
                return None
            if applyPrevious is True:
                return situation.previousSetup
            assert applyPrevious is False
        operationmodes = list(OperationMode)
        operationmodedescs = list(map(lambda x: x.text, operationmodes))
        operationmode = self.userChoose ("Display setup", operationmodedescs, operationmodes, None)
        if operationmode is None:
            return None
        elif operationmode is OperationMode.INTERNAL_ONLY:
            intres = self.selectResolution("the internal screen", situation.internalResolutions())
            if intres is None:
                return None
            else:
                return ScreenSetup(intres, None, None, False)
        elif operationmode is OperationMode.EXTERNAL_ONLY:
            extres = self.selectResolution("the external screen", situation.externalResolutions())
            if extres is None:
                return None
            else:
                return ScreenSetup(None, extres, None, True)
        else:
            assert operationmode is OperationMode.USE_BOTH
            relscrpositions = list(RelativeScreenPosition)
            relscrdescs = list(map(lambda x: x.text+" internal screen", relscrpositions))
            relpos = self.userChoose ("Position of external screen", relscrdescs, relscrpositions, None)
            if relpos == None:
                return None
            elif relpos == RelativeScreenPosition.MIRROR:
                # for mirroring only ask for common resolutions
                commonres = self.selectResolution("both screens", situation.commonResolutions())
                if commonres is None:
                    return None
                return ScreenSetup(commonres,commonres,relpos,False)
            # select resolutions independently
            intres = self.selectResolution("the internal screen", situation.internalResolutions())
            if intres is None:
                return None
            extres = self.selectResolution("the external screen", situation.externalResolutions())
            if extres is None:
                return None
            extprim = self.userChoose("Select primary screen", ["Internal screen is primary","External screen is primary"], [False,True], None)
            if extprim is None:
                return None
            return ScreenSetup(intres,extres,relpos,extprim)
