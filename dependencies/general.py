def cellname_to_inds(cellname):
    """
    Takes a place cell name and converts it into pythonic indicies.
    This function was taken from the mass-spec-python-tools XLSX class

    **Parameters**

    cellname: *string*
        The alphanumeric cell name coordinates.


    **Returns**

    column: *integer*
        The column index with 0 being the start of the indicies.

    row: *integer*
        The row index with 0 being the start of the indicies.


    **Examples**

    ::

        >>> cellname_to_inds('R57')
        (56, 18)
        >>> cellname_to_inds('AH58793')
        (58792, 34)
        >>> cellname_to_inds('PYTHON1973')
        (1972, 201883748)
        >>> inds_to_cellname(1972, 201883748)
        'PYTHON1973'

    **Notes**

    Based on http://stackoverflow.com/questions/7261936/convert-an-excel-or-spreadsheet-column-letter-to-its-number-in-pythonic-fashion
    """
    string = __import__('string')
    alpha = ''
    numeric = ''
    for x in cellname:  # split into alpha and numeric segments
        if x.isalpha():
            alpha += x
        elif x.isdigit():
            numeric += x
        else:
            pass  # ignores special characters (e.g. $)
            # raise ValueError('An unexpected character was encountered in the row and column address provided: %s' %str(x))
    num = 0
    for c in alpha:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A'))  # + 1
    return num, int(numeric) - 1


def inds_to_cellname(row, col):
    """
    Takes a pythonic index of row and column and returns the corresponding excel
    cell name.
    This function was taken from the mass-spec-python-tools XLSX class

    **Parameters**

    row: *integer*
        The pythonic index for the row, an index of 0 being the first row.

    col: *integer*
        The pythonic index for the column, an index of 0 being the first column.


    **Returns**

    cell name: *string*
        The excel-style cell name.


    **Examples**

    ::

        >>> inds_to_cellname(55,14)
        'O56'
        >>> inds_to_cellname(12,25)
        'Z13'
        >>> inds_to_cellname(18268,558)
        'UM18269'


    **Notes**

    Based on http://stackoverflow.com/questions/23861680/convert-spreadsheet-number-to-column-letter
    """
    div = row + 1
    string = ""
    while div > 0:
        module = (div - 1) % 26
        string += chr(65 + module)
        div = int((div - module) / 26)
    return string[::-1] + str(col + 1)  # string order must be reversed to be accurate