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

# interactive command line interface, question based

from question_frontend import QuestionFrontend

import sys

class CLIFrontend(QuestionFrontend):
    def error(self, message):
        print(message, file=sys.stderr)

    def userChoose (self, title, choices, returns, fallback):
        while True:
            # print question
            print(title)
            for i in range(len(choices)):
                print("%d. %s"%(i,choices[i]))
            print("Enter 'c' to cancel.")
            # handle input
            answer = input("> ")
            if answer == "c":
                return None
            #else
            try:
                answerint = int(answer)
                if answerint >= 0 and answerint < len(choices):
                    return returns[answerint]
            except ValueError:
                pass
            # if we are here something invalid was entered
            print("INVALID ANSWER: '%s'" % answer)

    @staticmethod
    def isAvailable():
        return True
