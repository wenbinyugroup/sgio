import xml.etree.ElementTree as et

def readNextNonEmptyLine(file):
    line = file.readline().strip()
    while line == '':
        line = file.readline().strip()
    return line


def listToString(flist, delimiter='', fmt=''):
    sfmt = '{0:' + fmt + '}'
    s = ''
    for i, n in enumerate(flist):
        if i > 0:
            s = s + delimiter
        s += sfmt.format(n)
    return s


def matrixToString(matrix, delimiter='', fmt=''):
    srows = []
    for row in matrix:
        s = listToString(row, delimiter, fmt)
        srows.append(s)
    ss = '\n'.join(srows)

    return ss


def parseLayupCode(s_code):
    l_code = []
    ilsb = s_code.find('[')
    irsb = s_code.find(']')
    # print ilsb, irsb
    angles = s_code[ilsb + 1:irsb]
    # print angles
    ns = 0
    if irsb + 1 < len(s_code):
        ns = s_code[irsb + 1:].strip('s')
        if len(ns) == 0:
            ns = '1'
        ns = int(ns)
    # print ns

    # ilrbs = []
    # irrbs = []
    islash_level1 = []  # index
    is_in_brackets = False
    for i, c in enumerate(angles):
        if c == '(':
            is_in_brackets = True
            # ilrbs.append(i)
        if c == ')':
            is_in_brackets = False
            # irrbs.append(i)
        if (c == '/') and (not is_in_brackets):
            islash_level1.append(i)
    # print ilrbs
    # print irrbs
    # print islash_level1

    islash_level1.append(len(angles))
    list_angles = []
    i = 0
    for j in islash_level1:
        list_angles.append(angles[i:j])
        i = j + 1

    # print list_angles

    for i, a in enumerate(list_angles):
        temp = a.split(':')
        temp[0] = temp[0].strip('(').strip(')')
        # print temp[0]
        repeat = 1
        if len(temp) > 1:
            repeat = int(temp[-1])
        for k in range(repeat):
            if '/' in temp[0]:
                temp2 = temp[0].split('/')
                for l in temp2:
                    l_code.append(l)
            else:
                l_code.append(temp[0])

    l_code = list(map(float, l_code))
    # print l_code

    for s in range(ns):
        temp = l_code[:]
        temp.reverse()
        # print l_code
        # print temp
        l_code = l_code + temp

    # for angle in l_code:
    #     print angle

    return l_code




def writeFormatIntegers(file, numbers, fmt='8d', newline=True):
    """Write a list of integers into a file

    Parameters
    ----------
    file : file
        The file object for writing.
    numbers : list of ints
        The list of numbers that is going to be written.
    fmt : str
        The desired format for each number.
    newline : bool
        If append the character ``\\n`` after writting all numbers or not.
    """
    fmt = '{0:' + fmt + '}'
    for i in numbers:
        file.write(fmt.format(i))
    if newline:
        file.write('\n')
    return


def writeFormatFloats(file, numbers, fmt='16.6E', newline=True, indent=0):
    """Write a list of floats into a file

    Parameters
    ----------
    file : file
        The file object for writing.
    numbers : list of floats
        The list of numbers that is going to be written.
    fmt : str
        The desired format for each number.
    newline : bool
        If append the character ``\\n`` after writting all numbers or not.
    """
    fmt = '{0:' + fmt + '}'
    file.write(' '*indent)
    for f in numbers:
        file.write(fmt.format(f))
    if newline:
        file.write('\n')
    return


def writeFormatFloatsMatrix(fobj, matrix, fmt='16.6E', indent=0):
    """Write a 2D list/array of float as a format matrix into file.

    Parameters
    ----------
    fobj : file object
        Output file.
    matrix : list/array
        Matrix of float that is goint to be written into file.
    """
    for row in matrix:
        writeFormatFloats(fobj, row, fmt, indent=indent)
    return


def writeFormatIntegersMatrix(fobj, matrix, fmt='8d'):
    for row in matrix:
        writeFormatIntegers(fobj, row, fmt)
    return


def textToMatrix(textList):
    """Convert the text of a block of numbers into a matrix

    Parameters
    ----------
    textList : list of strings
        The block of text representing a matrix

    Returns
    -------
    list of lists of floats
        A matrix of numbers.

    Examples
    --------

    >>> lines = ['1 2 3', '4 5 6', '7 8 9']
    >>> utilities.textToMatrix(lines)
    [[1., 2., 3.],
     [4., 5., 6.],
     [7., 8., 9.]]
    """
    matrix = []
    for line in textList:
        line = line.strip()
        line = line.split()
        row = list(map(float, line))
        # for j in line:
        #     row.append(float(j))
        matrix.append(row)

    return matrix









# ====================================================================
# XML
# ====================================================================

def parseXML(fn_xml):
    """Parse an XML file and get the root element

    Parameters
    ----------
    fn_xml : str
        File name of the XML file.

    Returns
    -------
    xml.etree.ElementTree.Element
        Root element of the XML tree.
    """
    xt = et.parse(fn_xml)
    root = xt.getroot()

    return root


def updateXMLElement(parent, tag, value):
    """ Update/Create an element with given tag and value.

    :param parent: Parent element
    :type parent: xml.etree.ElementTree.Element

    :param tag: Tag of the element
    :type tag: string

    :param value: Value of the element
    :type value: string
    """
    _se = parent.find(tag)
    if _se is None:
        _se = et.SubElement(parent, tag)
    _se.text = value


