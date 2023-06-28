import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, length, ships_prow_point, route, strength):
        self.length = length
        self.ships_prow_point = ships_prow_point
        self.route = route
        self.strength = strength

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.ships_prow_point.x
            cur_y = self.ships_prow_point.y
            if self.route == 0:
                cur_x += i
            elif self.route == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.shootencount = 0
        self.field = [['0'] * size for _ in range(size)]
        self.busypoints = []
        self.ships = []

    def __str__(self):
        pr = ''
        pr += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, j in enumerate(self.field):
            pr += f'\n{i + 1} | ' + ' | '.join(j) + ' |'
        if self.hid:
            pr = pr.replace("■", "0")
        return pr

    def out(self, dot):
        return not (0 <= dot.x < self.size) or not (0 <= dot.y < self.size)

    def contour(self, ship, verb=False):
        environment = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        for p in ship.dots:
            for px, py in environment:
                cur = Dot(p.x + px, p.y + py)
                if not self.out(cur) and cur not in self.busypoints:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busypoints.append(cur)

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busypoints:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
            self.busypoints.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        if dot in self.busypoints:
            raise BoardUsedException()
        self.busypoints.append(dot)
        for ship in self.ships:
            if dot in ship.dots:
                ship.strength -= 1
                self.field[dot.x][dot.y] = 'X'
                if ship.strength == 0:
                    print('Корабль потоплен')
                    self.shootencount += 1
                    self.contour(ship, verb=True)
                    return False
                else:
                    print('Вы попали')
                    return True
        self.field[dot.x][dot.y] = '.'
        print('Мимо')
        return False

    def begin(self):
        self.busypoints = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        p = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f'Ход от ИИ: {p.x + 1}{p.y + 1}')
        return p


class User(Player):
    def ask(self):
        while True:
            move = input("Ваш ход: ").split()
            if len(move) != 2:
                print("Введите 2 координаты")
                continue
            x, y = move
            if not x.isdigit() or not y.isdigit():
                print("Введите координаты в формате чисел")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:
    def greet(self):
        print("Добро пожаловать в игру Морской Бой! Вводите координаты своего хода в формате x y")

    def try_gen_board(self):
        arr = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for i in arr:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(i, Dot(random.randint(0, self.size), random.randint(0, self.size)),
                            random.randint(0, 1), i)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_gen_board()
        return board

    def __init__(self, size=6):
        self.size = 6
        playerboard = self.random_board()
        aiboard = self.random_board()
        aiboard.hid = True
        self.ai = AI(aiboard, playerboard)
        self.player = User(playerboard, aiboard)

    def loop(self):
        num = 0
        while True:
            print("Доска Игрока")
            print(self.player.board)
            print("Доска ИИ")
            print(self.ai.board)
            if num % 2 == 0:
                print("Ваш ход")
                repeat = self.player.move()
                num += 1
            else:
                print("Ход компьютера")
                repeat = self.ai.move()
                num += 1
            if repeat:
                num -= 1
            if self.ai.board.shootencount == 7:
                print("Игрок победил!")
                break
            if self.player.board.shootencount == 7:
                print("Компьютер победил!")
                break

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()