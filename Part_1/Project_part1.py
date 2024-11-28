# Group#: G6
# Student Names: Muntakim Rahman, Tomaz Zlindra

"""
    This program implements a variety of the snake
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self):
        """
            The initializer instantiates the main window and
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour,
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!",
            height = 3, width = 10, font=("Helvetica","14","bold"),
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self):
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()

    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)
class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move"
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        while self.gameNotOver:
            #complete the method implementation below
            time.sleep(SPEED)
            self.move()

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate.
            If based on this new movement, the prey has been
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if
            the game should be over.
            The snake coordinates list (representing its length
            and position) should be correctly updated.
        """
        #TODO -> Determine Prey Capture Logic (If Snake Width > Prey Width, If Prey Width > Snake Width).
        def isCaptured(snakeCoordinates, preyCoordinates) -> bool:
            effectiveSnakeCoordinates: list[tuple] = []
            x_captured, y_captured = False, False
            if self.direction in ("Left", "Right"):
                effectiveSnakeCoordinates = [
                    (snakeCoordinates[0], effectiveYCoordinate) for effectiveYCoordinate in range(snakeCoordinates[1] - SNAKE_ICON_WIDTH // 2, snakeCoordinates[1] + SNAKE_ICON_WIDTH // 2)
                ]
            else:
                effectiveSnakeCoordinates = [
                    (effectiveXCoordinate, snakeCoordinates[1]) for effectiveXCoordinate in range(snakeCoordinates[0] - SNAKE_ICON_WIDTH // 2, snakeCoordinates[0] + SNAKE_ICON_WIDTH // 2)
                ]
            for headCoordinate in effectiveSnakeCoordinates:
                x_captured = (headCoordinate[0] >= preyCoordinates[0]) and (headCoordinate[0] <= preyCoordinates[2])
                y_captured = (headCoordinate[1] >= preyCoordinates[1]) and (headCoordinate[1] <= preyCoordinates[3])
                if (x_captured) and (y_captured):
                    return True
            x_captured: bool = (NewSnakeCoordinates[0] >= preyCoordinates[0]) and (NewSnakeCoordinates[0] <= preyCoordinates[2])
            y_captured: bool = (NewSnakeCoordinates[1] >= preyCoordinates[1]) and (NewSnakeCoordinates[1] <= preyCoordinates[3])
            return x_captured and y_captured

        NewSnakeCoordinates = self.calculateNewCoordinates()
        #complete the method implementation below

        if isCaptured(snakeCoordinates = NewSnakeCoordinates, preyCoordinates = gui.canvas.coords(gui.preyIcon)): # Access from GUI:
            self.score += 1
            self.snakeCoordinates = [*self.snakeCoordinates, NewSnakeCoordinates] # Append New Snake Head

            #TODO -> No Threading in Part 1
            # score_thread = threading.Thread(
            #     target = gameQueue.put_nowait,
            #     args = ({"score" : self.score}, ),
            #     daemon = True # Kill Thread When Spawning Thread Exits
            # )
            # prey_thread = threading.Thread(
            #     target = self.createNewPrey,
            #     daemon = True # Kill Thread When Spawning Thread Exits
            # )
            # score_thread.start()
            # prey_thread.start()

            gameQueue.put_nowait({"score" : self.score})
            self.createNewPrey()
        else:
            self.snakeCoordinates = [*self.snakeCoordinates[1:], NewSnakeCoordinates] # Move Snake
        # lost_thread = threading.Thread(
        #     target = self.isGameOver,
        #     args = (NewSnakeCoordinates, ),
        #     daemon = True # Kill Thread When Spawning Thread Exits
        # )
        # move_thread = threading.Thread(
        #     target = gameQueue.put_nowait,
        #     args = ({"move" :  self.snakeCoordinates}, ),
        #     daemon = True # Kill Thread When Spawning Thread Exits
        # )
        # lost_thread.start()
        # move_thread.start()
        self.isGameOver(NewSnakeCoordinates)
        gameQueue.put_nowait({"move" :  self.snakeCoordinates})

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of
            head of the snake.
            It is used by the move() method.
        """
        lastX, lastY = self.snakeCoordinates[-1]
        #complete the method implementation below
        if self.direction == "Left":
            lastX -= SNAKE_ICON_WIDTH
        elif self.direction == "Right":
            lastX += SNAKE_ICON_WIDTH
        elif self.direction == "Up":
            lastY -= SNAKE_ICON_WIDTH
        else:
            lastY += SNAKE_ICON_WIDTH
        return (lastX, lastY)

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver
            field and also adds a "game_over" task to the queue.
        """
        x, y = snakeCoordinates
        #complete the method implementation below

        x_collision: bool = (x <= 0) or (x >= WINDOW_WIDTH)
        y_collision: bool = (y <= 0) or (y >= WINDOW_HEIGHT)

        if (x_collision) or (y_collision) or ((x, y) in self.snakeCoordinates[:-1]):
            self.gameNotOver = False
            gameQueue.put_nowait({"game_over" : True})
            return

    def createNewPrey(self) -> None:
        """
            This methods picks an x and a y randomly as the coordinate
            of the new prey and uses that to calculate the
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the
            queue handler to represent the new prey.
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls.
        """
        THRESHOLD_X = 5
        THRESHOLD_Y = 10
        #complete the method implementation below

        #TODO -> Generate Prey Outside of Snake Coordinates. Determine if Excluding Radius is Viable
        canvasCoordinates: list[tuple] = [(xCoordinate, yCoordinate) for xCoordinate in range(THRESHOLD_X, WINDOW_WIDTH - THRESHOLD_X, SNAKE_ICON_WIDTH) for yCoordinate in range(THRESHOLD_Y, WINDOW_HEIGHT - THRESHOLD_Y, SNAKE_ICON_WIDTH)]
        for coordinate in self.snakeCoordinates:
           if (coordinate[0], coordinate[1]) in canvasCoordinates:
               canvasCoordinates.remove((coordinate[0], coordinate[1]))
        generatedCoordinates: tuple = (random.choice(canvasCoordinates))
        #generatedCoordinates: tuple = (random.choice(self.snakeCoordinates))

        preyCoordinates: tuple = (
            generatedCoordinates[0] - PREY_ICON_WIDTH // 2, # x0
            generatedCoordinates[1] - PREY_ICON_WIDTH // 2, # y0
            generatedCoordinates[0] + PREY_ICON_WIDTH // 2, # x1
            generatedCoordinates[1] + PREY_ICON_WIDTH // 2 # y1
        )

        gameQueue.put_nowait({"prey" : preyCoordinates})

if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 300
    SNAKE_ICON_WIDTH = 15
    PREY_ICON_WIDTH = 10
    #add the specified constant PREY_ICON_WIDTH here

    BACKGROUND_COLOUR = "black"   #you may change this colour if you wish
    ICON_COLOUR = "blue"        #you may change this colour if you wish

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface

    QueueHandler()  #instantiate the queue handler

    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()