# DSL - easy Display Setup for Laptops
# Copyright (C) 2012-2015 Ralf Jung <post@ralfj.de>
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

# interactive zenity interface, question based

from question_frontend import QuestionFrontend
from screen import processOutputIt

import subprocess

class ZenityFrontend(QuestionFrontend):
    def error(self, message):
        '''Displays a fatal error to the user'''
        subprocess.check_call(["zenity", "--error", "--text="+message])

    def userChoose (self, title, choices, returns, fallback):
        assert len(choices) == len(returns)
        args = ["zenity", "--list", "--text="+title, "--column="]+list(choices)
        switch = dict (list(zip (choices,returns)))
        try:
            for line in processOutputIt(*args):
                return switch.get(line.strip(), fallback)
        except Exception:
            # on user cancel, the return code of zenity is nonzero
            return fallback
        # if the output was empty
        return fallback

    def isAvailable():
        try:
            processOutputIt("zenity", "--version")
            return True
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
