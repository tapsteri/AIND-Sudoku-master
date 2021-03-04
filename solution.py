"""
Udacity Artificial Intelligence Nanodegree Program project

Solve a Diagonal Sudoku with AI using the following strategies:
1. Elimination
2. Only Choice
3. Naked Twins
4. Depth First Search
"""
__author__      = "Tapio Kivirauma"
__version__     =  "1.0"

# For storing assingments for visualization with pygame
assignments = []

# Define rows and columns for 9x9 sudoku board
rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    """
    Helper function to return the list formed by all the possible concatenations of a letter s in string 
    a with a letter t in string b
    """
    return [s+t for s in a for t in b]
    pass


# Define the individual squares of the sudoku board
boxes = cross(rows, cols)

# Define the units for classic sudoku
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Define the  additional two diagonals for diagonal sudoku
diags = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]
# Define units and peers as dictionaries
unitlist = row_units + column_units + square_units + diags
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
        
    Go through all the units, and whenever there are identical pairs
    in two boxes of the same unit eliminate both values of the pair
    from other boxes of the unit. 
    
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
"""

    # Iterate through all units one by one
    for unit in unitlist:
        # Iterate through unit to look for 2-digit values
        for i in unit:
            if len(values[i]) == 2:
                # One 2-digit value found, start looking for a twin
                for j in unit:
                    # Look for second 2-digit value, exclude the one already found
                    if values[i] == values[j]  and j != i:
                        # Twins found, store the value for later use
                        digits = values[j]
                        # Remove values from other boxes in the same unit
                        for h in unit:
                            # Exclude the twins
                            if h != i and h != j:
                                # Store the value of box for possible removal of values of the twins
                                twins_eliminated = values[h]
                                # Replace one digit at a time
                                for digit in digits:
                                    twins_eliminated = twins_eliminated.replace(digit, '')
                                # Check if any replacements were actually done, if not no need to assign anything
                                if twins_eliminated != values[h]:
                                    assign_value(values, h, twins_eliminated)
    return values
    pass


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))
    pass


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return
    pass


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values
    pass


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values
    pass


def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice() and naked_twins().
    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of all functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values
    pass


def search(values):
    """
    If sudoku cannot be solved by other srategies alone, solve the sudoku
    using depth-first search and propagation, try all possible values.
    
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """

    # First, reduce and possibly solve the sudoku using other strategies
    values = reduce_puzzle(values)

    if values is False:
        return False ## Failed earlier
    # Check if sudoku is solved
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!

    # Sudoku could not be solved by other stategies alone, have to take
    # also depth-first search strategy into use.
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus
    for value in values[s]:
        new_sudoku = values.copy()
        # assign one value to one of the unfilled squares
        new_sudoku[s] = value
        # try if the sudoku with assigned value can be solved
        attempt = search(new_sudoku)
        if attempt:
            return attempt
    pass


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Call is to search function, however if sudoku is solved by repeatedly applying the other
    # strategies no search is performed.
    return search(grid_values(grid))
    pass


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
