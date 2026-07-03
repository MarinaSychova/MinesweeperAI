from random import randint, choice
from copy import deepcopy
from itertools import combinations
from math import comb

class BoardInfo():
    def __init__(self):
        self.mode = "1"     # defines the size of the board and the number of bombs
        self.rows = 9       # number of rows
        self.cols = 9       # number of columns
        self.bombCount = 10 # number of bombs
        self.bombs = []     # bombs' coordinates
        self.numbers = []   # numbers in free cells
        self.clicked = []   # revealed cells
        self.flagged = []   # flagged cells

    def generate_bombs(self):
        if self.bombs: return # Return if bomb list is not empty
        while len(self.bombs) < self.bombCount:
            bomb = (randint(0, self.rows - 1), randint(0, self.cols - 1))
            if bomb not in self.bombs: self.bombs.append(bomb)
        return

    def generate_numbers(self):
        if not self.bombs or self.numbers: return
        for i in range(self.rows):
            self.numbers.append([])
            for j in range(self.cols):
                # If a square hides a bomb, mark it as None
                if (i, j) in self.bombs: self.numbers[-1].append(None)
                # If a square does not hide a bomb, count bombs around them
                else:
                    number = 0
                    for k in range(i-1, i+2):
                        for l in range(j-1, j+2):
                            if k == i and l == j: continue
                            if (k, l) in self.bombs: number += 1
                    self.numbers[-1].append(number)
        return
    
    def reset_game_data(self):
        self.bombs.clear()
        self.numbers.clear()
        self.clicked.clear()
        self.flagged.clear()
        self.generate_bombs()
        self.generate_numbers()
        return

    def set_board_data(self):
        if self.mode == "1":
            self.rows = 9
            self.cols = 9
            self.bombCount = 10
        elif self.mode == "2":
            self.rows = 16
            self.cols = 16
            self.bombCount = 40
        elif self.mode == "3":
            self.rows = 16
            self.cols = 32
            self.bombCount = 99
        self.reset_game_data()
        return

    def mark_cell(self, i, j, isFlagged):
        # No matter what mouse button was clicked
        # Flagged Cells get unflagged
        if (i, j) in self.flagged:
            self.flagged.remove((i, j))
            return "unflagged"
        elif isFlagged:
            self.flagged.append((i, j))
            return "flagged"
        else:
            # If a bomb was clicked -> game over
            if (i, j) in self.bombs:
                return "loss"
            else:
                if (i, j) not in self.clicked:
                    self.clicked.append((i, j))
                    return "clicked"
        return None

    def cells_near_zero(self, i, j):
        '''
            Return a list of cells with zeros around the cell (i, j)
        '''
        neighbours = []

        def get_neighbours(a, b):
            if (self.numbers[a][b] == 0):
                for k in range(a - 1, a + 2):
                    if k < 0 or k >= self.rows: continue
                    for l in range(b - 1, b + 2):
                        if l < 0 or l >= self.cols or (k == a and l == b): continue
                        if (k, l) not in self.clicked and (k, l) not in neighbours:
                            self.clicked.append((k, l))
                            neighbours.append((k, l))
                            get_neighbours(k, l)

        get_neighbours(i, j)
        return neighbours

    def cells_near_number(self, i, j):
        '''
            Return a list of adjacent cells around the cell (i, j)
        '''
        neighbours = []
        
        def get_neighbours(a, b, numberOfBombs):
            for k in range(a - 1, a + 2):
                if k < 0 or k >= self.rows: continue
                for l in range(b - 1, b + 2):
                    if l < 0 or l >= self.cols or (k == a and l == b): continue
                    if (k, l) in self.flagged:
                        numberOfBombs -= 1
                    elif (k, l) not in self.clicked and (k, l) not in neighbours:
                        neighbours.append((k, l))
            return numberOfBombs

        numberOfBombs = get_neighbours(i, j, self.numbers[i][j])
        if numberOfBombs == 0:
            return neighbours
        else:
            return []

class LilMinesweeper():
    def __init__(self, board: BoardInfo):
        self.board = board
        self.clickable = [] # cells that are safe to click
        self.flaggable = [] # cells that are safe to flag
        self.xRows = []     # left part of equation system used for prediction (see derive_obvious_moves function)
        self.yCol = []      # right part of equation system used for prediction (see derive_obvious_moves function)

    def safe_move(self):
        '''
            Return a safe move
            Find more safe moves if none left in stock
        '''
        def give_safe_move():
            while self.clickable:
                move = self.clickable[0]
                self.clickable.pop(0)
                if move not in self.board.clicked:
                    return move, False
            while self.flaggable:
                move = self.flaggable[0]
                self.flaggable.pop(0)
                if move not in self.board.flagged:
                    return move, True
            return None, None

        position, toFlag = give_safe_move()
        if position is None:
            if not self.find_obvious_moves(): self.derive_obvious_moves()
            return give_safe_move()
        else:
            return position, toFlag

    def find_obvious_moves(self):
        '''
            Return safe moves purely based on the numbers in the cells
        '''
        for i, j in self.board.clicked:
            unmarked = [] # cells that are adjacent to Cell (i, j) and are untouched
            number = self.board.numbers[i][j]
            # Find all unmarked Cells and a number of bombs to find
            for k in range(i - 1, i + 2):
                if k < 0 or k >= self.board.rows: continue
                for l in range(j - 1, j + 2):
                    if l < 0 or l >= self.board.cols or (k == i and l == j): continue
                    if (k, l) in self.board.flagged: number -= 1
                    elif (k, l) not in self.board.clicked: unmarked.append((k, l))
            # Find cells to flag
            if len(unmarked) == number and number != 0:
                for k, l in unmarked:
                    if (k, l) not in self.flaggable: self.flaggable.append((k, l))
            # Find cells to click
            elif number == 0 and unmarked:
                for k, l in unmarked:
                    if (k, l) not in self.clickable: self.clickable.append((k, l))
            if self.clickable or self.flaggable:
                return True
        return False

    def derive_obvious_moves(self):
        '''
            Derive moves from equations like:
            cell0 + cell1 = 1
                                        => cell2 + 1 = 2 => cell2 = 1 => cell2 contains a bomb
            cell0 + cell1 + cell2 = 2

            or:
            cell0 + cell1 + cell2 = 0   => cell0, cell1, cell2 contain no bombs
        '''
        xRows = [] # left part of equation system
        yCol = [] # right part of equation system
        # Collect Equations for Equation System
        for i, j in self.board.clicked:
            xRow = []
            y = self.board.numbers[i][j]
            for k in range(i - 1, i + 2):
                if k < 0 or k >= self.board.rows: continue
                for l in range(j - 1, j + 2):
                    if l < 0 or l >= self.board.cols or (k == i and l == j): continue
                    if (k, l) in self.board.flagged: y -= 1
                    elif (k, l) not in self.board.clicked: xRow.append((k, l))
            xRows.append(xRow)
            yCol.append(y)
        # Remove duplicates
        for i in range(len(xRows) - 1, 0, -1):
            if xRows.count(xRows[i]) > 1:
                xRows.pop(i)
                yCol.pop(i)
        # Simplify equations
        for i in range(len(xRows)):
            for j in range(len(xRows)):
                if i == j: continue
                if set(xRows[i]).issubset(xRows[j]):
                    xRows[j] = [x for x in xRows[j] if x not in xRows[i]]
                    yCol[j] -= yCol[i]
                elif set(xRows[j]).issubset(xRows[i]):
                    xRows[i] = [x for x in xRows[i] if x not in xRows[j]]
                    yCol[i] -= yCol[j]
        # Remove empty Equations
        for i in range(len(xRows) - 1, -1, -1):
            if not xRows[i]:
                xRows.pop(i)
                yCol.pop(i)
        # Derive clicks and flags
        for i in range(len(xRows)):
            if yCol[i] == 0:
                for x in xRows[i]: self.clickable.append(x)
            elif yCol[i] == len(xRows[i]):
                for x in xRows[i]: self.flaggable.append(x)
        self.xRows = xRows
        self.yCol = yCol
            
    def compute_probabilities(self):
        '''
            If no obvious moves are visible, compute weighted probabilities of cells (adjacent to numbers) containing bombs
            Return the cell with the smallest probability
        '''
        if not self.xRows: return None, None
        bombsLeftCount = self.board.bombCount - len(self.board.flagged) # how much unflagged bombs left
        unmarked = [] # unknown cells adjacent to numbers
        for xRow in self.xRows:
            for x in xRow:
                if x not in unmarked: unmarked.append(x)
        possibleArrangements = [] # all possible arrangements of bombs
        
        def get_arrangements(arrangement, iteration):
            '''
                Create all possible bomb arrangements for the given equation
            '''
            def isSatisfiable(arrangement):
                '''
                    Check if the bomb arrangement satisfies the equations
                    Return True if it is OK and if it is completed
                '''
                # If Arrangement contains too many bombs -> it is not OK
                if sum([x for x in arrangement.values() if x is not None]) > bombsLeftCount:
                    return False, False
                isComplete = True # True if Arrangement is complete (has no 'None's)
                for i in range(len(self.xRows)):
                    number = self.yCol[i]
                    for x in self.xRows[i]:
                        if arrangement[x] is None: isComplete = False
                        else: number -= arrangement[x]
                    # If Arrangement does not fit Equation -> Arrangement is not OK
                    if number < 0:
                        return False, False
                return True, isComplete

            # Copy current equation and leave only unmarked cells
            number = self.yCol[iteration]
            xRow = deepcopy(self.xRows[iteration])
            for i in range(len(xRow) - 1, -1, -1):
                if arrangement[xRow[i]] is not None:
                    number -= arrangement[xRow[i]]
                    xRow.pop(i)
            if number < 0: return False
            # Get all possible bomb arrangements for the current equation
            possibleBombs = list(combinations(xRow, number))
            for pb in possibleBombs:
                # Update Arrangement
                newArrangement = deepcopy(arrangement)                
                for b in pb:
                    newArrangement[b] = 1
                for x in xRow:
                    if newArrangement[x] is None: newArrangement[x] = 0
                # Check if Arrangement is satisfying
                isOk, isComplete = isSatisfiable(newArrangement)
                if isOk:
                    # If Arrangement is OK -> keep it
                    if isComplete:
                        possibleArrangements.append(newArrangement)
                    # If Arrangement has unmarked cells -> pass it with the next equation
                    elif iteration < len(self.xRows) - 1:
                        get_arrangements(newArrangement, iteration + 1)
            return True

        # Create all possible arrangements of bombs
        cellVallues = {x: None for x in unmarked}
        successfulChecks = get_arrangements(cellVallues, 0)
        if not successfulChecks or not possibleArrangements: return None, None
        # Get the number of non adjacent to numbers cells
        unknownCellsCount = self.board.rows * self.board.cols - len(self.board.clicked) - len(self.board.flagged) - len(unmarked)
        # Get the total possible numbers of bombs in the arrangements and how many arrangements with these numbers of bombs are there 
        bombArrangementsCount = {}
        for pa in possibleArrangements:
            bombSum = sum(pa.values())
            if bombSum not in bombArrangementsCount: bombArrangementsCount[bombSum] = 1
            else: bombArrangementsCount[bombSum] += 1
        # Get the number of all possible arrangements (including in non adjacent cells)
        totalArrangementsCount = 0
        for bombCount in bombArrangementsCount:
            totalArrangementsCount += bombArrangementsCount[bombCount] * comb(unknownCellsCount, bombsLeftCount - bombCount)
        # Compute weighted probabilities of unmarked cells containing a bomb
        probabilities = {}
        for cell in unmarked:
            probability = 0
            totalBombCounts = {}
            for pa in possibleArrangements:
                if pa[cell] == 1:
                    bombCount = sum(pa.values())
                    if bombCount in totalBombCounts: totalBombCounts[bombCount] += 1
                    else: totalBombCounts[bombCount] = 1
            for bombCount in totalBombCounts:
                probability += totalBombCounts[bombCount] * comb(unknownCellsCount, bombsLeftCount - bombCount)
            probability /= totalArrangementsCount
            probabilities[cell] = probability
        # Flag the cell that is flagged in all arrangements
        maxProbability = max(probabilities.values())
        if maxProbability == 1:
            bestCells = [cell for cell, probability in probabilities.items() if probability == maxProbability]
            if bestCells:
                return choice(bestCells), True
        # Get cells with the smallest probabilities and choose one of them
        minProbability = min(probabilities.values())
        bestCells = [cell for cell, probability in probabilities.items() if probability == minProbability]
        return choice(bestCells), False

    def random_move(self):
        while(True):
            move = (randint(0, self.board.rows - 1), randint(0, self.board.cols - 1))
            if move not in self.board.clicked and move not in self.board.flagged:
                return move, False
    
    def move(self):
        # Either make a safe move, a calculated-but-risky move or a random move
        move, toFlag = self.safe_move()
        if move is not None:
            return move, toFlag
        move, toFlag = self.compute_probabilities()
        if move is not None:
            return move, toFlag
        return self.random_move()
