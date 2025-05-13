#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains compiled regular expressions which will be used throughout :mod:`inpRW`.
In addition, it sets several groupings of keyword names and other similar items that are 
constant and need to be referenced throughout :mod:`~inpRW`.
See `How do I share global variables across modules? <https://docs.python.org/3/faq/programming.html#how-do-i-share-global-variables-across-modules>`_
for more information."""

# cspell:includeRegExp comments

import re

re1  = re.compile('\S') #: Matches a non-whitespace character
re2  = re.compile('".*?"') #: Matches everything between quotes, non-greedy
re3  = re.compile('(?<=\<)\w*(?=\>)') #: Matches Abaqus PARAMETER reference (i.e. <variable1>)
re4  = re.compile("(?<=\S)\s+(?=\S)") #: Matches all whitespace between non-whitespace
re5  = re.compile('\S+') #: Matches 1 or more non-whitespace character
#re6  = re.compile('(?<=[\d.])([dDeE][+\-]?)(?=\d+)') #: Matches scientific notation numbers, currently unused
re7  = re.compile('[de]', re.IGNORECASE) #: Matches scientific notation symbol d or e, case-insensitive
re8  = re.compile("[dDeE]") #: Matches scientific notation symbol d or e, case-insensitive
re9  = re.compile("\d") #: Matches one numeric digit
re10 = re.compile('[dD]') #: Matches d or D
re11 = re.compile('(?<=-) +') #: Matches 1 or more spaces if they are preceded by "-"
re12 = re.compile("(?<![a-zA-Z])\-?[1-9]+[0-9]*(?![a-zA-Z])") #: Matches a valid Python integer, which must not have any letter characters, and must start with a non-zero digit
re13 = re.compile("(?<=\d)[dD](?=[-\+]\d+)") #: Matches a scientific notation number with d or D as the exponent symbol. Not currently used
re14 = re.compile('\\r*\\n') #: Matches 0 or more carriage returns and then a new line
#re15 = re.compile('\\r*\\n([ \t]*)(?=\*[a-zA-Z])') # DOESN'T WORK WITH WHITESPACE PRIOR TO *
re15 = re.compile('\\r*\\n(?=[ \t]*\*[a-zA-Z])') #: Matches the whitespace immediately prior to the start of an Abaqus keyword (one "*" and a letter)
re16 = re.compile('[ \t]*\*[aA-zZ]') #: Matches the whitespace prior to an Abaqus Keyword, and the start of the Abaqus keyword "*" and one letter. Single line only.
re17 = re.compile('\\r*\\n(?!=\*\*)') #: Matches any number of carriage returns and a new line, as long as they are not followed by an Abaqus comment "**"
re18 = re.compile('([ \t]+)(?=\*[a-zA-Z])') #: Matches any whitespace prior to the * in a keyword line
re19 = re.compile("(?<=[de])[-+]?\d*\s*", re.IGNORECASE) #: Matches the exponent value of a number and trailing whitespace, not including the exponent symbol. For example, if we perform ``re19.search('1.25 e-2')``, the result will be `-2`.
#re20 = re.compile(r'([+\-*^/**]+)')
re21 = re.compile('(?<=.keywords\[)-?\d+(?=\])') #: Matches the indices of the keywords portion of an :attr:`~inpKeyword.inpKeyword.path`.
re22 = re.compile('(?<=.suboptions\[)-?\d+(?=\])') #: Matches the indices of the suboptions portion of an :attr:`~inpKeyword.inpKeyword.path`.
re23 = re.compile('(?<=.data\[)-?\d+(?=\])') #: Matches the indices of the data portion of an :attr:`~inpKeyword.inpKeyword.path`.
re24 = re.compile('(?<=\[)-?\d+(?=\])') #: Matches indices between brackets (i.e. ["100"])
re25 = re.compile('.*(?=\*[aA-zZ])') #: Matches whatever is on the line before the start of a keyword (\*A). Used only to find leading comments before first keyword.
re26 = re.compile(',\s*(?!\S)\Z') #: Searches for trailing comma and optionally whitespace at the end of a string. Used to check if an element definition has been completed.
#re27 = re.compile()
#re28 = re.compile()
#re29 = re.compile()
#re30 = re.compile()
#re31 = re.compile()


