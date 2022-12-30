from random import shuffle

opnum = 0

class GameManager:
    def __init__(self, sz):
        self.__board = Board(sz)
        self.__solved_board = Board(sz)
        self.__human = Player
        self.__solver = Solver()

    def create_random_solved_board(self):
        self.__solved_board.make_board_empty()
        places = [i for i in range(0, self.__board.get_size() * self.__board.get_size())]
        shuffle(places)
        print(self.__solver.solve_board(self.__solved_board, places))

    def print_board(self):
        self.__board.print()

    def print_solved_baord(self):
        self.__solved_board.print()

    def create_unique_solution_puzzle(self):
        pass


class Board:
    __empty = 0

    def __init__(self, n=3):
        if n % 3:
            print("Sudoku Board must be divisible by 3")
            # exit(1)
        self.__size = n
        self.__board = [[self.__empty] * self.__size for i in range(self.__size)]
        self.make_board_empty()

    def get_size(self):
        return self.__size

    def get_board(self):
        return self.__board

    def get_value(self, i, j):
        return self.__board[i][j]

    def get_empty(self):
        return self.__empty

    def print(self):
        for i in range(self.__size):
            for j in range(self.__size):
                print(self.__board[i][j], end="  ")
            print()

    def is_finished(self):
        for row in self.__board:
            for value in row:
                if value == -1:
                    return False
        return True

    def make_board_empty(self):
        self.__board = [[self.__empty] * self.__size for i in range(self.__size)]

    def is_valid_move(self, row, col, value):
        # Checks if this move is valid -> Check valid rows and column,
        # Check is the value found in the square? or is it found in the current row or column

        if row < 0 | col < 0 | row >= self.__size | col >= self.__size:
            return False

        if self.__board[row][col] != self.__empty:
            return False

        for j in range(self.__size):
            if value == self.__board[row][j] or value == self.__board[j][col]:
                return False

        cur_square_row, cur_square_col = 3*int(row / 3), 3*int(col / 3)
        for i in range(cur_square_row, cur_square_row + 3):
            for j in range(cur_square_col, cur_square_col + 3):
                if value == self.__board[i][j]:
                    return False

        return True

    def make_move(self, row, col, value):
        self.__board[row][col] = value

    def undo_move(self, row, col):
        self.__board[row][col] = self.__empty


class Solver:
    dp = dict()
    def count_solutions(self, board, places):
        # returns 0 if no solution for board, 1 if only one unique solution, 2 if more than 1 solution
        if len(places) == 0:
            return 1

        cur = places[len(places) - 1]
        row, col = int(cur / 3), cur % 3

        places.pop()

        no_of_solution = 0

        # in case a value was already here by Human or AI
        if board.get_value(row, col) != board.get_empty():
            no_of_solution += self.count_solutions(board, places)
            if no_of_solution >= 2:
                return 2
            else:
                return no_of_solution

        moves = [range(1, 10)]
        # shuffle(moves)

        for move in moves:
            if board.is_valid_move(row, col, move):
                board.make_move(row, col, move)
                no_of_solution += self.count_solutions(board, places)
                board.undo_move(row, col)
                if no_of_solution >= 2:
                    return 2

        return no_of_solution

    def solve_board(self, board, places):
        global opnum
        opnum += 1
        # print(opnum)
        if len(places) == 0:
            return True

        if board in self.dp.keys():
            return self.dp[board]

        cur = places[len(places) - 1]
        row, col = int(cur / board.get_size()), cur % board.get_size()

        places.pop()

        # in case a value was already here by Human or AI
        #if board.get_value(row, col) != board.get_empty():
        #   if self.solve_board(board, places):
        #    self.dp[board] = True
        #        return True
        #    else:
        #        self.dp[board] = False
        #        return False

        moves = [i for i in range(1, 10)]
        # shuffle(moves)

        for move in moves:
            if board.is_valid_move(row, col, move):
                board.make_move(row, col, move)
                board.print()
                print()
                if self.solve_board(board, places):
                    self.dp[board] = True
                    return True
                board.undo_move(row, col)

        board.make_move(row, col, board.get_empty())
        places.append(cur)
        self.dp[board] = False
        return False


class Player:
    pass


prog = GameManager(6)
prog.create_random_solved_board()
prog.print_solved_baord()
print(opnum)
