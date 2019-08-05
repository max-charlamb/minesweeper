import sys
import colorama
import keyboard
from termcolor import colored
from random import randrange
from time import sleep
from threading import Timer

class Game():
    """Handles the clock and user input"""
    def __init__(self):
        self._timer = None
        self.interval = 1 / 250
        self.is_running = False
        self.timinginterval = 25
        self.setup()

        self.flaggedlastframe = 0
        self.movedlastframe = 0

    def setup(self):
        """Asks the user to enter size and number of bombs and creates the field"""
        self.clear()
        print('Standard Sizes: \nEasy: Size = 10 and Bombs = 10\nMedium: Size = 18 and Bombs = 40\nHard: Size = 24 and Bombs = 99')
        size = ''
        while type(size) != int or (size < 4 or size > 99):
            size = input('Size: ')
            try:
                size = int(size)
                if size < 4:
                    print('Minimum size is 4.')
                if size > 99:
                    print('Maximum size is 99.')
            except (ValueError, TypeError):
                print('Not Valid Entry. Try Again.')
        bombs = ''
        while type(bombs) != int or bombs >= (size * size) or bombs <= 0:
            bombs = input('Bombs: ')
            try:
                bombs = int(bombs)
                if bombs >= size * size:
                    print('Too many bombs for a {} size grid. {} bombs is the maximum.'.format(size, size * size - 9))
                if bombs <= 0:
                    print('Bombs must be greater than 0.')
            except (ValueError, TypeError):
                print('Not Valid Entry. Try Again.')
        self.b = Board(size, bombs)
        self.showBoard(self.b.getState())
        self.start()

    def run(self):
        """Called every clock cycle and handles the main game loop."""
        changed = False
        moved = False
        if keyboard.is_pressed('w') and self.movedlastframe == 0:
            changed = True
            moved = True
            self.b.moveMouseUp()
        if keyboard.is_pressed('a') and self.movedlastframe == 0:
            changed = True
            moved = True
            self.b.moveMouseLeft()
        if keyboard.is_pressed('s') and self.movedlastframe == 0:
            changed = True
            moved = True
            self.b.moveMouseDown()
        if keyboard.is_pressed('d') and self.movedlastframe == 0:
            changed = True
            moved = True
            self.b.moveMouseRight()
        if keyboard.is_pressed('f') and self.flaggedlastframe == 0:
            changed = True
            self.flaggedlastframe = self.timinginterval
            self.b.flagTile()
        else:
            if self.flaggedlastframe > 0:
                self.flaggedlastframe -= 1
        if keyboard.is_pressed(' '):
            changed = True
            self.b.revealTile()
        if keyboard.is_pressed('e'):
            changed = True
            self.b.specialRevealTile()
        if moved:
            self.movedlastframe = self.timinginterval
        else:
            if self.movedlastframe > 0:
                self.movedlastframe -= 1
        if changed:
            gameState = self.b.getState()
            if gameState[0] == 2:
                self.defeat(gameState)
            if gameState[0] == 3:
                self.victory(gameState)
            self.showBoard(gameState)

    def clear(self):
        """Clears the terminal"""
        print('\n' * 30)

    def showBoard(self, gameState):
        """
        Prints the board state and some instructions to the console.
        It is important to do the bulk of the printing in one command to
        reduce blur.
        """
        accum = '\n' * 30
        accum += 'Controls \nFlag: "F"\nReveal: "Space"\nSpecial Reveal: "E"\nMove: "WASD"'
        accum += '\n' * 2
        accum += 'Bombs Left: {}'.format(gameState[2] - gameState[3])
        accum += '\n' * 2
        accum += str(self.b)
        print(accum)

    def defeat(self, gameState):
        """Sets up the defeat state and restarts the game"""
        self.stop()
        self.clear()
        self.b.revealAll()
        accum = ' F: Flagged Correctly\n B: Unflagged bomb\n X: Flagged Incorrectly\n\n'
        accum += str(self.b) + '\n'
        print (accum)
        temp = input('You lost on a {} size board with {} bombs. Press enter to try again. \n\n'.format(gameState[1], gameState[2]))
        self.setup()

    def victory(self, gameState):
        """Sets up the victory state and restarts the game"""
        self.stop()
        self.clear()
        self.b.revealAll()
        accum = ' F: Flagged Correctly\n B: Unflagged bomb\n X: Flagged Incorrectly\n\n'
        accum += str(self.b) + '\n'
        print (accum)
        temp = input('You won on a {} size board with {} bombs. Press enter to try again. \n\n'.format(gameState[1], gameState[2]))
        self.setup()

    def start(self):
        """Called to start the clock cycle"""
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        """Stops the clock from running"""
        self._timer.cancel()
        self.is_running = False

    def _run(self):
        """
        Used internally with self.start to create a constant clock.
        Calls self.run every clock cycle.
        """
        self.is_running = False
        self.start()
        self.run()


class Board():
    """Data structure to hold information about the board"""
    def __init__(self, size, bombs):
        self.size = size
        self.tiles = [] # y,x
        self.bombs = bombs
        self.init()
        self.initTiles()
        self.initMouse()

    def __str__(self):
        accum = ''
        for y, row in enumerate(self.tiles):
            accum += '{}:    '.format(str(y).zfill(2)) + '  '.join(map(str,row))
            accum += '\n'
        accum += '\n'
        accum += ' ' * 6
        for x in range(self.size):
            accum += str(x).zfill(2) + ' '
        return accum

    def initTiles(self):
        """Initializes the 2-dimensional array of tiles."""
        self.tiles = []
        for y in range(self.size):
            self.tiles.append([])
            for x in range(self.size):
                self.tiles[y].append(Tile('({}, {})'.format(x, y)))

        radius = 1
        for y in range(self.size):
            for x in range(self.size):
                outs = []
                for i in range(y - radius, y + radius + 1):
                    for j in range(x - radius, x + radius + 1):
                        if (0 <= i < self.size and 0 <= j < self.size) and (i != y or j != x):
                            outs.append(self.tiles[i][j])
                self.tiles[y][x].addNeighboring(outs)

    def init(self):
        """Initializes the board variables"""
        self.flagged = 0
        self.hasScatteredBombs = False
        self.state = 0
#        state 0 is before bombs placed
#        state 1 is game playing
#        state 2 is game over
#        state 3 is victory

    def initMouse(self):
        """Initializes the cursor to the top-left"""
        self.mouse = (0, 0) # x, y
        self.tiles[0][0].setMouse()


    def scatterBombs(self, start=None):
        """
        Scatters bombs along the field. Optionally takes a tile which will
        prevent bombs from spawning around it.
        """
        self.state = 1
        left = self.bombs
        while(left > 0):
            tile = self.tiles[randrange(0, self.size)][randrange(0, self.size)]
            if (not (start == tile or start in tile.getNeighboring()) and not tile.getBomb()):
                tile.setBomb()
                left -= 1
        for i in self.tiles:
            for j in i:
                j.updateNeighboring()

    def flagTile(self):
        """Attemps to flags the tile at the cursor."""
        tile = self.tiles[self.mouse[1]][self.mouse[0]]
        if tile.getHidden():
            if tile.getFlagged():
                tile.setFlagged(False)
                self.flagged -= 1
            elif (self.bombs - self.flagged) > 0:
                tile.setFlagged(True)
                self.flagged += 1
                self.checkVictory()

    def moveMouseUp(self):
        """Moves the cursor up."""
        self.tiles[self.mouse[1]][self.mouse[0]].removeMouse()
        self.mouse = (self.mouse[0], (self.mouse[1] - 1) % self.size)
        self.tiles[self.mouse[1]][self.mouse[0]].setMouse()

    def moveMouseDown(self):
        """Moves the cursor down."""
        self.tiles[self.mouse[1]][self.mouse[0]].removeMouse()
        self.mouse = (self.mouse[0], (self.mouse[1] + 1) % self.size)
        self.tiles[self.mouse[1]][self.mouse[0]].setMouse()

    def moveMouseLeft(self):
        """Moves the cursor left."""
        self.tiles[self.mouse[1]][self.mouse[0]].removeMouse()
        self.mouse = ((self.mouse[0] - 1) % self.size, self.mouse[1])
        self.tiles[self.mouse[1]][self.mouse[0]].setMouse()

    def moveMouseRight(self):
        """Moves the cursor right."""
        self.tiles[self.mouse[1]][self.mouse[0]].removeMouse()
        self.mouse = ((self.mouse[0] + 1) % self.size, self.mouse[1])
        self.tiles[self.mouse[1]][self.mouse[0]].setMouse()

    def revealTile(self, tile=None):
        """Attemps to reveal the tile at the cursor."""
        if not tile:
            tile = self.tiles[self.mouse[1]][self.mouse[0]]
        if not self.hasScatteredBombs:
            self.scatterBombs(tile)
            self.hasScatteredBombs = True
        if tile.hidden == False: return
        bomb = tile.show() == 1
        self.checkVictory()
        if bomb:
            self.state = 2

    def checkVictory(self):
        """Checks victory condition and updates self.state to correct value."""
        victory = True
        for row in self.tiles:
            for tile in row:
                if tile.getHidden():
                    if tile.getFlagged() and tile.getBomb():
                        pass
                    else:
                        victory = False
        if victory:
            self.state = 3

    def specialRevealTile(self):
        """Attempts to special reveal at cursor."""
        tile = self.tiles[self.mouse[1]][self.mouse[0]]
        flaggedneighbors = 0
        for neighbor in tile.getNeighboring():
            if neighbor.getFlagged():
                flaggedneighbors += 1
        if not tile.getHidden() and flaggedneighbors == tile.getNumNeighboringBombs():
            for neighbor in tile.getNeighboring():
                if not neighbor.getFlagged():
                    self.revealTile(neighbor)

    def getState(self):
        """Returns important variables about the current state of the board."""
            return [self.state, self.size, self.bombs, self.flagged]

    def revealAll(self):
        """Reveals all tiles."""
        for row in self.tiles:
            for tile in row:
                tile.revealAll()



class Tile():
    """One tile in the minesweeper board."""
    def __init__(self, id):
        self.isBomb = False
        self.neighboring = []
        self.id = id
        self.mouse = False
        self.flagged = False
        self.hidden = True

    def __repr__(self):
        return 'Tile: {}'.format(self.id)

    def __str__(self):
        if self.mouse: return colored('X', 'yellow')
        elif self.flagged: return colored('F', 'red')
        elif not self.hidden:
            if self.isBomb:
                return colored('B', 'magenta')
            else:
                return colored('{}'.format(' ' if self.getNumNeighboringBombs() == 0 else str(self.getNumNeighboringBombs())), 'cyan')
        else: return '#'

    def addNeighboring(self, neighbor):
        """
        Adds other tiles to the list of neighboring tiles.
        Neighbor can either be a Tile or a list of Tiles.
        """
        if isinstance(neighbor, Tile): self.neighboring.append(neighbor)
        else: self.neighboring += neighbor

    def getNeighboring(self):
        return self.neighboring

    def setBomb(self):
        self.isBomb = True

    def getBomb(self):
        return self.isBomb

    def getNumNeighboringBombs(self):
        return self.numNeighboringBombs

    def setMouse(self):
        self.mouse = True

    def removeMouse(self):
        self.mouse = False

    def setFlagged(self, bool):
        self.flagged = bool

    def getFlagged(self):
        return self.flagged

    def getHidden(self):
        return self.hidden

    def show(self):
        """Shows self and updates neighbors if needed."""
        self.hidden = False
        if self.getNumNeighboringBombs() == 0:
            for neighbor in self.neighboring:
                if neighbor.getHidden():
                    neighbor.show()
        if self.isBomb: return 1
        return 0

    def updateNeighboring(self):
        """Updates the number of neighboring bombs."""
        accum = 0
        for neighbor in self.neighboring:
            if neighbor.getBomb(): accum += 1
        self.numNeighboringBombs = accum

    def revealAll(self):
        """Reveals all about the tile."""
        self.mouse = False
        if self.flagged:
            if not self.isBomb:
                self.mouse = True
        else:
            self.hidden = False

if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    if sys.platform == 'win32':
        colorama.init()
    g = Game()
    g.run()
