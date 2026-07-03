from tkinter import *
from tkinter.font import Font

from components import BoardInfo, LilMinesweeper

""" GAME INFO """
BOARD = BoardInfo()
AI = LilMinesweeper(BOARD)
CELLS = []
GAMEOVER = False
AIRUNNING = False

""" FUNCTIONS """
def draw_board(v_boardFrame, v_controlFrame):
    global BOARD
    # Set Window and Board size
    buttonSize = s_buttonSize
    boardWidth = buttonSize * BOARD.cols + 2
    boardHeight = buttonSize * BOARD.rows + 2
    windowWidth = boardWidth + s_padding * 5 + 35
    windowHeight = boardHeight + s_padding * 2
    if (windowWidth > game.winfo_screenwidth()):
        boardWidth = game.winfo_screenwidth() - 100
        buttonSize = int((boardWidth - 2) / BOARD.cols)
        boardHeight = int(buttonSize * BOARD.rows + 2)
        windowWidth = int(boardWidth + s_padding * 5 + 35)
        windowHeight = boardHeight + s_padding * 2
    if (windowHeight > game.winfo_screenheight()):
        boardHeight = game.winfo_screenheight() - 100
        buttonSize = (boardHeight - 2) / BOARD.rows
        boardWidth = int(buttonSize * BOARD.cols + 2)
        windowWidth = int(boardWidth + s_padding * 5 + 35)
        windowHeight = boardHeight + s_padding * 2
    game.minsize(windowWidth, windowHeight)
    game.maxsize(windowWidth, windowHeight)
    v_boardFrame.config(width=boardWidth, height=boardHeight)
    v_controlFrame.config(height=boardHeight)
    infoFrame.place_configure(y=boardHeight / 2 - 25)
    aiButton.place_configure(y=boardHeight - s_padding * 2 - 30)
    # Add Board Cells
    for i in range(0, BOARD.rows):
        CELLS.append([])
        for j in range(0, BOARD.cols):
            cell = Button(v_boardFrame, borderwidth=4, relief="raised", font=s_numberFont, bg=s_buttonColorDefault)
            cell.place(x=buttonSize*j, y=buttonSize*i, width=buttonSize, height=buttonSize)
            cell.bind("<Button-1>", lambda event, i=i, j=j: open_cell(event, i, j))
            cell.bind("<Button-2>", lambda event, i=i, j=j: flag_cell(event, i, j))
            cell.bind("<Button-3>", lambda event, i=i, j=j: flag_cell(event, i, j))
            CELLS[-1].append(cell)

def open_cell(event, i, j):
    global GAMEOVER
    if GAMEOVER or AIRUNNING: return
    elif event.widget.cget("state") == 'disabled' and BOARD.numbers[i][j] > 0:
        neighbours = BOARD.cells_near_number(i, j)
        for k, l in neighbours:
            actionResult = BOARD.mark_cell(k, l, False)
            process_result(actionResult, k, l)
    else:
        actionResult = BOARD.mark_cell(i, j, False)
        process_result(actionResult, i, j)
    

def flag_cell(event, i, j):
    if GAMEOVER or AIRUNNING or event.widget.cget("state") == 'disabled': return
    actionResult = BOARD.mark_cell(i, j, True)
    process_result(actionResult, i, j)

def call_ai():
    global AIRUNNING
    if GAMEOVER or AIRUNNING: return
    AIRUNNING = True
    position, toFlag = AI.move()
    actionResult = BOARD.mark_cell(position[0], position[1], toFlag)
    process_result(actionResult, position[0], position[1])
    AIRUNNING = False
  
def process_result(v_actionResult, i, j):
    # Process click result
    global GAMEOVER
    if v_actionResult == "unflagged":
        CELLS[i][j].config(image="")
        infoLabel.config(text=f"{int(infoLabel['text']) + 1}")
    elif v_actionResult == "flagged":
        CELLS[i][j].config(image=flagImage)
        infoLabel.config(text=f"{int(infoLabel['text']) - 1}")
    elif v_actionResult == "loss":
        GAMEOVER = True
        resetButton.config(image=resetLoseImage)
        for x, y in BOARD.bombs: CELLS[x][y].configure(image=bombImage)
        return
    elif v_actionResult == "clicked":
        revealedNumber = BOARD.numbers[i][j]
        CELLS[i][j].configure(text=revealedNumber, image="", disabledforeground=s_numberColors[revealedNumber], bg=s_buttonColorPressed, relief="sunken", state="disabled")
        if revealedNumber == 0:
            neighbours = BOARD.cells_near_zero(i, j)
            for k, l in neighbours:
                revealedNumber = BOARD.numbers[k][l]
                CELLS[k][l].configure(text=revealedNumber, image="", disabledforeground=s_numberColors[revealedNumber], bg=s_buttonColorPressed, relief="sunken", state="disabled")
    if len(BOARD.flagged) == BOARD.bombCount and len(BOARD.clicked) == BOARD.rows * BOARD.cols - BOARD.bombCount:
        GAMEOVER = True
        resetButton.config(image=resetWinImage)

def set_game(event):
    global GAMEOVER, AIRUNNING
    for row in CELLS:
        for cell in row: cell.destroy()
    CELLS.clear()
    BOARD.mode = selectedMode.get()
    BOARD.set_board_data()
    draw_board(boardFrame, controlFrame)
    resetButton.config(image=resetImage)
    infoLabel.config(text=f"{BOARD.bombCount}")
    GAMEOVER = False
    AIRUNNING = False

def reset_game():
    global BOARD, GAMEOVER, AIRUNNING
    BOARD.reset_game_data()
    # Reset Cells
    for i in range(BOARD.rows):
        for j in range(BOARD.cols):
            CELLS[i][j].config(text="", image="", bg=s_buttonColorDefault, relief="raised", state="normal")
    resetButton.config(image=resetImage)
    infoLabel.config(text=f"{BOARD.bombCount}")
    GAMEOVER = False
    AIRUNNING = False

""" WINDOW """
game = Tk()
game.title("Minesweeper")
game.config(bg="gray25")

""" STYLES """
s_padding = 15
s_buttonSize = 40
s_numberFont = Font(family="Arial", size=20, weight="bold")
s_bombNumFont = Font(family="Arial", size=20, weight="bold")
s_buttonColorDefault = "gray82"
s_buttonColorPressed = "gray45"
s_numberColors = {0: "ghost white", 1: "dodger blue", 2: "lawn green", 3: "chocolate1", 4: "MediumOrchid2", 5: "hot pink", 6: "sky blue", 7: "VioletRed4", 8: "black"}
aiImage = PhotoImage(file='images/ai.png')
bombImage = PhotoImage(file='images/bomb.png')
flagImage = PhotoImage(file='images/flag.png')
resetImage = PhotoImage(file='images/reset.png')
resetLoseImage = PhotoImage(file='images/reset-lose.png')
resetWinImage = PhotoImage(file='images/reset-win.png')

game.iconphoto(False, bombImage)

boardFrame = Frame(game, highlightthickness = 2, highlightbackground = "black")
boardFrame.grid(row=0, column=0, padx=s_padding, pady=s_padding) 

controlFrame = Frame(game, width=35 + s_padding * 2, highlightthickness = 2, highlightbackground = "black", bg = s_buttonColorDefault)

# Menu that allows to choose between easy, medium, and hard modes
modes = ["1", "2", "3"]
selectedMode = StringVar()
selectedMode.set(modes[0])
modeMenu = OptionMenu(controlFrame, selectedMode, *modes, command=set_game)
modeMenu.place(x=5, y=5)
modeMenu.config(font=["Arial", 12], bg="white")

resetButton = Button(controlFrame, command=reset_game, borderwidth=4, image=resetImage)
resetButton.place(x=5, y=50)

# Frame that shows how much unflagged bombs left
infoFrame = Frame(controlFrame, width=51, height=51, highlightbackground = s_buttonColorPressed, highlightthickness = 2)
infoLabel = Label(infoFrame, text=f"{BOARD.bombCount}", bg="black", fg="red2", font=s_bombNumFont)
infoLabel.pack(fill="both", expand=True)
infoFrame.pack_propagate(False)
infoFrame.place(x=5, y=5)

aiButton = Button(controlFrame, command=call_ai, borderwidth=4, image=aiImage)
aiButton.place(x=5, y=5)

controlFrame.grid(row=0, column=1)

# Set up the board
BOARD.set_board_data()
draw_board(boardFrame, controlFrame)

game.mainloop()
