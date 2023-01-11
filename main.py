import sys
import time
import timeit
from random import shuffle
from timeit import default_timer
import pygame


class GameManager:
    def __init__(self, sz):
        self._board = Board(sz)
        self._solved_board = Board(sz)
        self._human = Player
        self._solver = Solver()

    def create_random_solved_board(self):
        self._solved_board.make_board_empty()
        places = [i for i in range(0, self._board.get_size() * self._board.get_size())]
        self._solver.solve_board(self._solved_board, places)

    def print_board(self):
        self._board.print()

    def print_solved_baord(self):
        self._solved_board.print()

    def get_board(self):
        return self._board

    def get_sovled_board(self):
        return self._solved_board

    def get_board_size(self):
        return self._board.get_size()

    def create_unique_solution_puzzle(self):
        self._board.set_board(self._solved_board.get_board())
        places = [i for i in range(0, self._board.get_size() * self._board.get_size())]
        shuffle(places)
        ct = 0
        start_time = default_timer()
        for place in places:
            ct += 1
            row, col = int(place / self._board.get_size()), place % self._board.get_size()
            temp_value = self._solved_board.get_value(row, col)

            self._board.undo_move(row, col)

            sz = self._board.get_size()

            moves = [i * sz + j for i in range(sz) for j in range(sz) if
                     self._board.get_value(i, j) == self._board.get_empty()]

            nof_clues = 81 - len(moves)
            if nof_clues <= int(0.33 * sz * sz) or int(default_timer() - start_time) >= 5:
                # print(nof_clues <= int(0.3 * sz * sz))
                break

            # self.__board.print()
            if self._solver.count_solutions(self._board, moves[:]) > 1:
                # print(ct, "YES\n")
                self._board.make_move(row, col, temp_value)
            else:
                # print(ct, "NO\n")
                continue


class Board:
    __empty = 0

    def __init__(self, n=3):
        if n % 3:
            print("Sudoku Board must be divisible by 3")
            exit(1)
        self.__size = n
        self.__board = [[self.__empty] * self.__size for _ in range(self.__size)]
        self.make_board_empty()

    def get_size(self):
        return self.__size

    def get_board(self):
        return self.__board

    def set_board(self, other):
        self.__board = [other[i][:] for i in range(self.get_size())]

    def get_value(self, i, j):
        return self.__board[i][j]

    def get_empty(self):
        return self.__empty

    def get_no_nums(self):
        ans = 0
        for i in range(self.__size):
            for j in range(self.__size):
                if self.__board[i][j] != self.__empty:
                    ans += 1
        return ans

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
        self.__board = [[self.__empty] * self.__size for _ in range(self.__size)]

    def to_string(self):
        s = str()
        for row in self.__board:
            for ele in row:
                s += str(ele)
        return s

    def is_valid_move(self, row, col, value):
        # Checks if this move is valid -> Check valid rows and column,
        # Check is the value found in the square? or is it found in the current row or column

        if row < 0 | col < 0 | row >= self.__size | col >= self.__size:
            return False

        if self.__board[row][col] != self.__empty:
            return False

        for j in range(self.__size):
            if (value == self.__board[row][j]) or (value == self.__board[j][col]):
                return False

        cur_square_row, cur_square_col = 3 * int(row / 3), 3 * int(col / 3)
        for i in range(cur_square_row, cur_square_row + 3):
            for j in range(cur_square_col, cur_square_col + 3):
                if value == self.__board[i][j]:
                    return False

        return True

    def is_valid_move_2(self, row, col, value, vis):
        # Checks if this move is valid -> Check valid rows and column,
        # Check is the value found in the square? or is it found in the current row or column

        if row < 0 | col < 0 | row >= self.__size | col >= self.__size:
            return False


        for j in range(self.__size):
            if (value == self.__board[row][j] and vis[row][j] and j != col) or (value == self.__board[j][col] and vis[j][col] and j != row):
                return False

        cur_square_row, cur_square_col = 3 * int(row / 3), 3 * int(col / 3)
        for i in range(cur_square_row, cur_square_row + 3):
            for j in range(cur_square_col, cur_square_col + 3):
                if value == self.__board[i][j] and (row != i or j != col) and vis[i][j]:
                    return False

        return True

    def make_move(self, row, col, value):
        self.__board[row][col] = value

    def undo_move(self, row, col):
        self.__board[row][col] = self.__empty


class Solver:
    _dp = dict()

    def count_solutions(self, board, places):
        # returns 0 if no solution for board, 1 if only one unique solution, 2 if more than 1 solution
        if len(places) == 0:
            return 1

        board_str = board.to_string()
        if board_str in self._dp.keys():
            return self._dp[board_str]

        cur = places[len(places) - 1]
        row, col = int(cur / board.get_size()), cur % board.get_size()

        places.pop()
        no_of_solution = 0

        moves = [i for i in range(1, 10)]
        shuffle(moves)

        for move in moves:
            if board.is_valid_move(row, col, move):
                board.make_move(row, col, move)
                no_of_solution += self.count_solutions(board, places)
                board.undo_move(row, col)
                if no_of_solution >= 2:
                    self._dp[board_str] = 2
                    return 2

        board.undo_move(row, col)
        places.append(cur)
        self._dp[board_str] = no_of_solution
        return no_of_solution

    def solve_board(self, board, places):
        if len(places) == 0:
            return True

        cur = places[len(places) - 1]
        row, col = int(cur / board.get_size()), cur % board.get_size()

        places.pop()

        # in case a value was already here by Human or AI
        if board.get_value(row, col) != board.get_empty():
            if self.solve_board(board, places):
                return True
            else:
                places.append(cur)
                return False

        moves = [i for i in range(1, 10)]
        shuffle(moves)

        for move in moves:
            if board.is_valid_move(row, col, move):
                board.make_move(row, col, move)
                if self.solve_board(board, places):
                    return True
                board.undo_move(row, col)

        board.undo_move(row, col)
        places.append(cur)
        return False


class Player:
    pass


class GUI_Manager:
    WIDTH, HEIGHT = 1020, 900
    Board_WIDTH, Board_HEIGHT = 800, 800

    def __init__(self, sz):
        self.size = sz
        self.gui_solver = GUI_Solver()

        # Initialize with modules
        pygame.init()
        pygame.display.set_caption("Puzzle Creator")

        # Font to be used
        self.font1 = pygame.font.SysFont("comicsans", 40)
        self.font2 = pygame.font.SysFont("comicsans", 24)
        self.font3 = pygame.font.SysFont("comicsans", 18)

        # create the display window
        self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.WIN.fill((255, 255, 255))

        # create the GUI Board
        self.GUI_Board = GUI_Board(sz, self.Board_WIDTH, self.Board_HEIGHT)
        self.GUI_Solved_Board = GUI_Board(sz, self.Board_WIDTH, self.Board_HEIGHT)

    def draw_loading(self):
        txt = "Creating The Puzzle.."
        loading_txt = self.font1.render(txt, True, (0, 0, 0))
        self.WIN.blit(loading_txt, (0,
                                    self.Board_HEIGHT +
                                    (self.HEIGHT - self.Board_HEIGHT - self.font1.size(txt)[1]) / 2))

    def draw_done(self):
        txt = "Here is your Unique Puzzle.. Press Enter to Solve"
        loading_txt = self.font2.render(txt, True, (255, 0, 100))
        self.WIN.blit(loading_txt, (0,
                                    self.Board_HEIGHT +
                                    (self.HEIGHT - self.Board_HEIGHT - self.font2.size(txt)[1]) / 2))

    def draw_press_space(self):
        txt = "You can press SPACE anytime to stop.."
        loading_txt = self.font1.render(txt, True, (0, 0, 0))
        self.WIN.blit(loading_txt, (0,
                                    self.Board_HEIGHT +
                                    (self.HEIGHT - self.Board_HEIGHT - self.font1.size(txt)[1]) / 2))

    def undo_press_space(self):
        s = "You can press SPACE anytime to stop.."
        sur = pygame.Surface(self.font1.size(s))
        sur.fill((255, 255, 255))
        self.WIN.blit(sur, (0,
                            self.Board_HEIGHT +
                            (self.HEIGHT - self.Board_HEIGHT - self.font1.size(s)[1]) / 2))

    def undo_loading(self):
        s = "Creating The Puzzle.."
        sur = pygame.Surface(self.font1.size(s))
        sur.fill((255, 255, 255))
        self.WIN.blit(sur, (0,
                            self.Board_HEIGHT +
                            (self.HEIGHT - self.Board_HEIGHT - self.font1.size(s)[1]) / 2))

    def draw_loading_dots(self, n, x, y):
        s = '.' * (n % 3 + 1)

        sur = pygame.Surface(self.font1.size(s))
        sur.fill((255, 255, 255))
        self.WIN.blit(sur, (x, y))
        pygame.display.flip()

        dots = self.font1.render(s, True, (0, 0, 0))
        self.WIN.blit(dots, (x, y))
        pygame.display.flip()

    def put_puzzle(self, choice, max_time=None):
        self.create_random_solved_board()
        if choice == 1:
            self.create_unique_solution_puzzle()
        else:
            self.create_unique_solution_puzzle(max_time, True)
        self.GUI_Board.set_rl_board(self.GUI_Board.get_rl_board())

    def draw_full_board(self):
        self.draw_board()
        self.draw_board_lines()

    def draw_board(self):
        # Draw the white board
        self.WIN.blit(self.GUI_Board.get_surf(), (0, 0))
        # pygame.display.flip()

    def draw_board_lines(self):
        VerLine, HorLine = self.GUI_Board.get_lines()
        BoldVerLine, BoldHorLine = self.GUI_Board.get_bold_lines()
        # Draw the Lines
        for i in range(0, self.size + 1):
            if i % 3 == 0:
                self.WIN.blit(BoldHorLine, (0, i * self.Board_HEIGHT / self.size))
                self.WIN.blit(BoldVerLine, (i * self.Board_WIDTH / self.size, 0))
            else:
                self.WIN.blit(HorLine, (0, i * self.Board_HEIGHT / self.size))
                self.WIN.blit(VerLine, (i * self.Board_WIDTH / self.size, 0))
        # self.WIN.blit(BoldHorLine, (0, self.Board_HEIGHT))
        # self.WIN.blit(BoldVerLine, (self.Board_WIDTH, 0))

    def draw_outer_board(self, outer_board):
        temp = self.GUI_Board
        self.GUI_Board = outer_board
        self.draw_full_board()
        self.GUI_Board = temp

    def draw_solved_board(self):
        temp = self.GUI_Board
        self.GUI_Board = self.GUI_Solved_Board
        self.draw_full_board()
        self.GUI_Board = temp

    def draw_values(self):
        # Draw values on board
        values = self.GUI_Board.get_values_render(self.font1)
        for value in values:
            x = value[1] * self.Board_WIDTH / self.size + (self.Board_WIDTH / self.size - value[3][0]) / 2
            y = value[2] * self.Board_HEIGHT / self.size + (self.Board_HEIGHT / self.size - value[3][1]) / 2
            self.WIN.blit(value[0], (x, y))

    def draw_values_2(self, vis):
        for i in range(self.size):
            for j in range(self.size):
                if vis[i][j]:
                    label = self.font1.render(str(self.GUI_Board.rl_board.get_value(i, j)), True, (0, 0, 0))
                    txt_size = self.font1.size(str(self.GUI_Board.rl_board.get_value(i, j)))
                    x = j * self.Board_WIDTH / self.size + (self.Board_WIDTH / self.size - txt_size[0]) / 2
                    y = i * self.Board_HEIGHT / self.size + (self.Board_HEIGHT / self.size - txt_size[1]) / 2
                    cell_width = self.Board_WIDTH / self.size
                    cell_height = self.Board_HEIGHT / self.size

                    square = pygame.Surface((cell_width, cell_height))
                    inside_rect = pygame.Rect(0, 0, cell_width, cell_height)

                    if vis[i][j] == 1:
                        square.fill((255, 255, 0), inside_rect)
                    else:
                        square.fill((255, 0, 0), inside_rect)

                    self.draw_board_lines()
                    self.WIN.blit(square,
                                  (j * self.Board_WIDTH / self.size + 1, i * self.Board_HEIGHT / self.size + 1))
                    if vis[i][j] == 1:
                        self.WIN.blit(label, (x, y))
                elif not vis[i][j] and self.GUI_Board.rl_board.get_value(i, j) != self.GUI_Board.rl_board.get_empty():
                    continue
                    label = self.font3.render(str(self.GUI_Board.rl_board.get_value(i, j)), True, (0, 0, 0))
                    label.set_alpha(20)
                    txt_size = self.font3.size(str(self.GUI_Board.rl_board.get_value(i, j)))
                    x = j * self.Board_WIDTH / self.size + (self.Board_WIDTH / self.size - txt_size[0]) / 2
                    y = i * self.Board_HEIGHT / self.size + (self.Board_HEIGHT / self.size - txt_size[1]) / 2
                    self.WIN.blit(label, (x, y))

    def draw_values_3(self, vis):
        for i in range(self.size):
            for j in range(self.size):
                if vis[i][j] == 1:
                    label = self.font1.render(str(self.GUI_Board.rl_board.get_value(i, j)), True, (0, 0, 0))
                    txt_size = self.font1.size(str(self.GUI_Board.rl_board.get_value(i, j)))
                    x = j * self.Board_WIDTH / self.size + (self.Board_WIDTH / self.size - txt_size[0]) / 2
                    y = i * self.Board_HEIGHT / self.size + (self.Board_HEIGHT / self.size - txt_size[1]) / 2
                    cell_width = self.Board_WIDTH / self.size
                    cell_height = self.Board_HEIGHT / self.size

                    square = pygame.Surface((cell_width, cell_height))
                    inside_rect = pygame.Rect(0, 0, cell_width, cell_height)

                    square.fill((255, 255, 0), inside_rect)
                    # square.fill((255, 0, 0), inside_rect)

                    self.draw_board_lines()
                    self.WIN.blit(square,
                                  (j * self.Board_WIDTH / self.size + 1, i * self.Board_HEIGHT / self.size + 1))
                    self.WIN.blit(label, (x, y))
                elif vis[i][j] == 0 and self.GUI_Board.rl_board.get_value(i, j) != self.GUI_Board.rl_board.get_empty():
                    label = self.font1.render(str(self.GUI_Board.rl_board.get_value(i, j)), True, (0, 0, 0))
                    txt_size = self.font1.size(str(self.GUI_Board.rl_board.get_value(i, j)))
                    x = j * self.Board_WIDTH / self.size + (self.Board_WIDTH / self.size - txt_size[0]) / 2
                    y = i * self.Board_HEIGHT / self.size + (self.Board_HEIGHT / self.size - txt_size[1]) / 2
                    cell_width = self.Board_WIDTH / self.size
                    cell_height = self.Board_HEIGHT / self.size

                    square = pygame.Surface((cell_width, cell_height))
                    inside_rect = pygame.Rect(0, 0, cell_width, cell_height)

                    # square.fill((255, 255, 0), inside_rect)
                    square.fill((255, 0, 0), inside_rect)

                    self.draw_board_lines()
                    self.WIN.blit(square,
                                  (j * self.Board_WIDTH / self.size + 1, i * self.Board_HEIGHT / self.size + 1))
                    self.WIN.blit(label, (x, y))
                elif vis[i][j] == 2:
                    label = self.font1.render(str(self.GUI_Board.rl_board.get_value(i, j)), True, (0, 0, 0))
                    txt_size = self.font1.size(str(self.GUI_Board.rl_board.get_value(i, j)))
                    x = j * self.Board_WIDTH / self.size + (self.Board_WIDTH / self.size - txt_size[0]) / 2
                    y = i * self.Board_HEIGHT / self.size + (self.Board_HEIGHT / self.size - txt_size[1]) / 2
                    self.WIN.blit(label, (x, y))



    def draw_solved_values(self):
        # Draw values on board
        values = self.GUI_Solved_Board.get_values_render(self.font1)
        for value in values:
            x = value[1] * self.Board_WIDTH / self.size + (self.Board_WIDTH / self.size - value[3][0]) / 2
            y = value[2] * self.Board_HEIGHT / self.size + (self.Board_HEIGHT / self.size - value[3][1]) / 2
            self.WIN.blit(value[0], (x, y))

    def draw_timer(self, st, end, mxTime=None, reverse_print=False):
        df = str(end - st)
        if mxTime is not None and reverse_print:
            df = str(max(mxTime - (end - st), 0.0))
        if df[1] == '.':
            df = '0' + df
        if len(df) == 4:
            df += '0'
        df = df[0:df.find('.') + 3]
        txt = self.font2.render(df, True, (255, 0, 0))
        txt_width, txt_height = self.font2.size(df)

        sur = pygame.Surface((txt_width + 5, txt_height + 5))
        sur.fill((255, 255, 255))
        self.WIN.blit(sur, (self.WIDTH - txt_width - 5, self.HEIGHT - txt_height - 5))

        self.WIN.blit(txt, (self.WIDTH - txt_width, self.HEIGHT - txt_height))

    def draw_welcome(self):
        s = "Welcome To The Unique Sudoku Creator!"
        label = self.font2.render(s, True, (0, 0, 0))
        self.WIN.blit(label, ((self.Board_WIDTH - self.font2.size(s)[0]) / 2, self.Board_HEIGHT))

        s1 = "Press '1' For STOP WATCH mod: No Time Limits - Fewest Clues"
        label1 = self.font3.render(s1, True, (240, 0, 0))
        self.WIN.blit(label1, (0, self.Board_HEIGHT + self.font2.size(s)[1]))

        s2 = "Press '2' For TIMER mod: Time Limits - More Clues"
        label2 = self.font3.render(s2, True, (240, 0, 0))
        self.WIN.blit(label2, (0, self.Board_HEIGHT + self.font2.size(s)[1] + self.font3.size(s1)[1]))

    def draw_clues(self, n):
        nof_clues = self.size * self.size - n

        s = "Left Clues: "
        label = self.font2.render(s, True, (255, 0, 0))
        self.WIN.blit(label, (
            self.Board_WIDTH + (self.WIDTH - self.Board_WIDTH - self.font2.size(s)[0]) / 2,
            self.Board_HEIGHT / self.size))

        s = str(nof_clues) + '/' + str(self.size * self.size)
        label = self.font2.render(s, True, (255, 0, 0))
        self.WIN.blit(label, (self.Board_WIDTH + (self.WIDTH - self.Board_WIDTH - self.font2.size(s)[0]) / 2,
                              self.Board_HEIGHT / self.size + self.font2.size(s)[1]))

    def draw_operations(self, n):
        nof_op = self.size * self.size - n
        s = "Left Operations: "
        label = self.font2.render(s, True, (255, 0, 0))
        self.WIN.blit(label, (self.Board_WIDTH + (self.WIDTH - self.Board_WIDTH - self.font2.size(s)[0]) / 2, 0))

        s = str(nof_op) + '/' + str(self.size * self.size)
        label = self.font2.render(s, True, (255, 0, 0))
        self.WIN.blit(label, (
            self.Board_WIDTH + (self.WIDTH - self.Board_WIDTH - self.font2.size(s)[0]) / 2, self.font2.size(s)[1]))

    def take_welcome_choice(self):
        pygame.event.clear()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0
                elif event.key == pygame.K_1:
                    return 1
                elif event.key == pygame.K_2:
                    return 2

    def take_timer_choice(self):
        pygame.event.clear()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0
                elif event.key == pygame.K_1:
                    return 1
                elif event.key == pygame.K_2:
                    return 2
                elif event.key == pygame.K_3:
                    return 3
                elif event.key == pygame.K_4:
                    return 4
                elif event.key == pygame.K_5:
                    return 5
                elif event.key == pygame.K_6:
                    return 6

    def draw_timer_options(self, t=("1. 15sec", "2. 30sec", "3. 60sec", "4. 120sec", "5. 240sec", "6. 480sec")):
        no_in_row = len(t) // 2
        is_odd = len(t) % 2
        for i in range(0, no_in_row + is_odd):
            s = t[i]
            lbl = self.font2.render(s, True, (0, 0, 0))
            self.WIN.blit(lbl, (i * self.Board_WIDTH / no_in_row + 5, self.Board_HEIGHT + 10))

        for i in range(0, no_in_row):
            s = t[no_in_row + i + is_odd]
            lbl = self.font2.render(s, True, (0, 0, 0))
            self.WIN.blit(lbl,
                          (i * self.Board_WIDTH / no_in_row + 5, self.Board_HEIGHT + self.font2.size(t[0])[1] + 20))

    def solve_to_user(self):
        sz = self.size
        places = [i * sz + j for i in range(sz) for j in range(sz) if
                  self.GUI_Board.rl_board.get_value(i, j) == self.GUI_Board.rl_board.get_empty()]
        vis = [[2 for i in range(sz)] for j in range(sz)]
        for p in places:
            vis[p // sz][p % sz] = 0
        places.reverse()
        self.gui_solver.solve_board_show(self.GUI_Board.rl_board, places, self, vis, timeit.default_timer())

    def run_creator(self):
        # draw board with lines
        self.draw_full_board()
        self.draw_welcome()
        pygame.display.flip()
        choice = self.take_welcome_choice()
        if choice == 0:
            pygame.quit()
            sys.exit()

        # Clean Screen After taking Choice
        self.WIN.fill((255, 255, 255))
        self.draw_full_board()
        # self.draw_loading()
        pygame.display.flip()

        if choice == 2:
            self.draw_timer_options()
            pygame.display.flip()
            ch = self.take_timer_choice()
            if ch == 0:
                pygame.quit()
                sys.exit()
            self.put_puzzle(choice, int(15 * pow(2, ch - 1)))
        else:
            # get the puzzle
            self.put_puzzle(choice)

        # clean screen and redraw puzzle
        self.draw_full_board()
        self.draw_values()
        self.undo_loading()
        self.undo_press_space()
        self.draw_done()
        pygame.display.flip()

        Run = True
        while Run:
            for even in pygame.event.get():
                if even.type == pygame.KEYDOWN:
                    if even.key == pygame.K_ESCAPE:
                        Run = False
                    elif even.key == pygame.K_RETURN:
                        self.solve_to_user()
                if even.type == pygame.QUIT:
                    Run = False

    def create_random_solved_board(self):
        self.GUI_Solved_Board.make_board_empty()
        places = [i for i in range(0, self.GUI_Solved_Board.get_size() * self.GUI_Solved_Board.get_size())]
        places.reverse()
        self.gui_solver.solve_board(self.GUI_Solved_Board.rl_board, places, self)

    def shuffle_subsets(self, places, n):
        ans = []
        for i in range(0, len(places), n):
            l = []
            for j in range(i, i + n):
                if j >= len(places): break
                l.append(places[j])
            ans.append(l)
        shuffle(ans)
        ct = 0
        for lst in ans:
            for val in lst:
                places[ct] = val
                ct += 1

    def create_unique_solution_puzzle(self, mxTime=None, print_reverse_timer=False):
        self.GUI_Board.set_rl_board(self.GUI_Solved_Board.get_rl_board())
        board = self.GUI_Board.get_rl_board()
        places = [i for i in range(0, board.get_size() * board.get_size())]
        # self.shuffle_subsets(places, 5)
        shuffle(places)
        ct = 0
        start_time = default_timer()
        for place in places:
            # time.sleep(.3)
            row, col = int(place / board.get_size()), place % board.get_size()
            temp_value = board.get_value(row, col)
            sz = board.get_size()

            vis = [[0 for i in range(sz)] for j in range(sz)]
            for i in range(sz):
                for j in range(sz):
                    if i == row and j == col:
                        vis[i][j] = 2
                    elif board.get_value(i, j) != board.get_empty():
                        vis[i][j] = 1

            board.undo_move(row, col)

            moves = [i * sz + j for i in range(sz) for j in range(sz) if
                     board.get_value(i, j) == board.get_empty()]

            ln = len(moves)

            if mxTime is not None and int(default_timer() - start_time) >= mxTime:
                break

            if self.gui_solver.count_solutions(board, moves[:], self, vis, start_time, mxTime,
                                               print_reverse_timer) > 1:
                # print(ct, "YES\n")
                board.make_move(row, col, temp_value)
                vis[row][col] = 1
                ln -= 1
            else:
                vis[row][col] = 0
                # print(ct, "NO\n")

            if not self.gui_solver.stop:
                ct += 1

            self.WIN.fill((255, 255, 255))
            self.draw_full_board()
            self.draw_values_2(vis)
            if timeit.default_timer() - start_time < 15:
                self.draw_loading()
            else:
                self.draw_press_space()
            self.draw_timer(start_time, timeit.default_timer(), mxTime, print_reverse_timer)
            self.draw_clues(ln)
            self.draw_operations(ct)
            pygame.display.flip()

        self.gui_solver.stop = False


class GUI_Solver:
    dp = dict()
    stop = False

    def solve_board(self, board, places, gui_manager):
        gui_manager.draw_solved_board()
        gui_manager.draw_solved_values()

        if len(places) == 0:
            return True

        cur = places[len(places) - 1]
        row, col = int(cur / board.get_size()), cur % board.get_size()

        places.pop()

        # in case a value was already here by Human or AI
        if board.get_value(row, col) != board.get_empty():
            if self.solve_board(board, places, gui_manager):
                return True
            else:
                places.append(cur)
                return False

        moves = [i for i in range(1, 10)]
        shuffle(moves)

        for move in moves:
            if board.is_valid_move(row, col, move):
                board.make_move(row, col, move)
                if self.solve_board(board, places, gui_manager):
                    return True
                board.undo_move(row, col)

        board.undo_move(row, col)
        places.append(cur)
        return False

    def solve_board_show(self, board, places, gui_manager, vis, st):
        #if self.stop:
        #    return 2

        if len(places) == 0:
            return True

        cur = places[len(places) - 1]
        row, col = int(cur / board.get_size()), cur % board.get_size()


        vis[row][col] = 1

        #time.sleep(5)

        for even in pygame.event.get():
            if even.type == pygame.KEYDOWN:
                if even.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif even.key == pygame.K_SPACE:
                    self.stop = True
                    return 2
            if even.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        places.pop()

        moves = [i for i in range(1, 10)]
        # shuffle(moves)

        lst = 0
        for move in moves:
            time.sleep(.01)
            board.make_move(row, col, move)
            gui_manager.draw_board()
            gui_manager.draw_values_3(vis)
            gui_manager.draw_timer(st, timeit.default_timer())
            pygame.display.flip()
            if board.is_valid_move_2(row, col, move, vis):
                lst = move
                if self.solve_board_show(board, places, gui_manager, vis, st):
                    return True

        if lst != 0:
            board.make_move(row, col, lst)
        vis[row][col] = 0
        places.append(cur)
        return False

    def count_solutions(self, board, places, gui_manager, vis, st, mxTime, reverse_timer):
        if self.stop:
            return 2
        gui_manager.draw_board()
        gui_manager.draw_values_2(vis)
        gui_manager.draw_timer(st, timeit.default_timer(), mxTime, reverse_timer)
        pygame.display.flip()

        # returns 0 if no solution for board, 1 if only one unique solution, 2 if more than 1 solution
        if len(places) == 0:
            return 1

        for even in pygame.event.get():
            if even.type == pygame.KEYDOWN:
                if even.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif even.key == pygame.K_SPACE:
                    self.stop = True
                    return 2
            if even.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if mxTime is not None and timeit.default_timer() - st >= mxTime:
            return 2

        board_str = board.to_string()
        if board_str in self.dp.keys():
            return self.dp[board_str]

        cur = places[len(places) - 1]
        row, col = int(cur / board.get_size()), cur % board.get_size()

        places.pop()
        no_of_solution = 0

        moves = [i for i in range(1, 10)]
        shuffle(moves)

        for move in moves:
            if board.is_valid_move(row, col, move):
                board.make_move(row, col, move)
                no_of_solution += self.count_solutions(board, places, gui_manager, vis, st, mxTime,
                                                       reverse_timer)
                board.undo_move(row, col)
                if no_of_solution >= 2:
                    self.dp[board_str] = 2
                    return 2

        board.undo_move(row, col)
        places.append(cur)
        self.dp[board_str] = no_of_solution
        return no_of_solution


class GUI_Board:

    def __init__(self, sz, width, height):
        self.size = sz
        # save the console board inside variable rl_board
        self.rl_board = Board(sz)
        self.WIDTH, self.HEIGHT = width, height

        # Creating the Board
        self.Board = pygame.Surface((width, height))
        self.Board.fill((255, 255, 255))

        # Create Horizontal-Vertical Lines
        self.HorLine = pygame.Surface((width, 1))
        self.HorLine.fill((0, 0, 0))
        self.VerLine = pygame.Surface((1, height))
        self.VerLine.fill((0, 0, 0))

        # Create Bold Horizontal-Vertical Lines
        self.BoldHorLine = pygame.Surface((width, 3))
        self.BoldHorLine.fill((0, 0, 0))
        self.BoldVerLine = pygame.Surface((3, height + 3))
        self.BoldVerLine.fill((0, 0, 0))

    def get_surf(self):
        return self.Board

    def get_lines(self):
        return self.VerLine, self.HorLine

    def get_bold_lines(self):
        return self.BoldVerLine, self.BoldHorLine

    def set_rl_board(self, rl_board):
        self.rl_board = rl_board

    def get_values_render(self, font):
        ans = []
        for i in range(self.size):
            for j in range(self.size):
                if self.rl_board.get_value(i, j) != self.rl_board.get_empty():
                    # j represents the x axis, i represents y axis
                    # append the Text_Render with x, y axis and the text width
                    val = font.render(str(self.rl_board.get_value(i, j)), True, (0, 0, 0))
                    ans.append((val, j, i, font.size(str(self.rl_board.get_value(i, j)))))

        return ans

    def get_rl_board(self):
        return self.rl_board

    def get_size(self):
        return self.size

    def make_board_empty(self):
        self.rl_board.make_board_empty()


gm = GUI_Manager(9)
gm.run_creator()
