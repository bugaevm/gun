from random import randrange as rnd, choice
import tkinter as tk
import math
import time

# print (dir(math))

root = tk.Tk()
fr = tk.Frame(root)
root.geometry('800x600')
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)


class ball():
    def __init__(self, x=40, y=450):
        """ Конструктор класса ball
		Args:
		x - начальное положение мяча по горизонтали
		y - начальное положение мяча по вертикали
		"""
        self.x = x
        self.y = y
        self.r = 15
        self.vx = 0
        self.vy = 0

        col = hex(rnd(0, int('FFFFFF', base=16) + 1))
        self.color = '#' + ('0' * 6 + col[2:])[-6:]

        self.id = canv.create_oval(
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r,
            fill=self.color)

    def set_coords(self):
        canv.coords(
            self.id,
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r
        )

    def move(self):
        """Переместить мяч по прошествии единицы времени.
		Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
		self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
		и стен по краям окна (размер окна 800х600).
		"""
        # FIXME
        canv.move(self.id, self.vx, self.vy)
        self.x = canv.coords(self.id)[0] + self.r
        self.y = canv.coords(self.id)[1] + self.r

        if ((canv.coords(self.id)[0] < 0) or (canv.coords(self.id)[2] > 800)):
            self.vx = -self.vx * 0.6
            if (canv.coords(self.id)[0] < 0):
                canv.coords(self.id, 0, self.y - self.r, 2 * self.r, self.y + self.r)
            if (canv.coords(self.id)[2] > 800):
                canv.coords(self.id, 800 - 2 * self.r, self.y - self.r, 800, self.y + self.r)

        if ((canv.coords(self.id)[1] < 0) or (canv.coords(self.id)[3] > 600)):
            self.vy = -self.vy * 0.8
            if (canv.coords(self.id)[1] < 0):
                canv.coords(self.id, self.x - self.r, 0, self.x + self.r, 2 * self.r)
            if (canv.coords(self.id)[3] > 600):
                canv.coords(self.id, self.x - self.r, 600 - 2 * self.r, self.x + self.r, 600)
        self.vy += 1


    def hittest(self, obj):
        if (((canv.coords(obj.id)[0] + obj.r - (canv.coords(self.id)[0] + self.r)) ** 2 + (
                canv.coords(obj.id)[1] + obj.r - canv.coords(self.id)[1] - self.r) ** 2) <= (self.r + obj.r) ** 2):
            return True
        else:
            return False



class gun():
    def __init__(self):
        self.f2_power = 10
        self.f2_on = False
        self.angle = 1
        self.id = canv.create_line(20, 450, 50, 420, width=7)

    def fire2_start(self, event):
        self.f2_on = True

    def fire2_end(self, event):
        """Выстрел мячом.
        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = ball()
        if (event.x - new_ball.x) != 0:
            self.angle = math.atan((event.y - new_ball.y) / (event.x - new_ball.x))
        elif (event.y - new_ball.y) > 0:
            self.angle = math.pi / 2
        else:
            self.angle = - math.pi / 2
        new_ball.vx = self.f2_power * math.cos(self.angle)
        new_ball.vy = self.f2_power * math.sin(self.angle)
        if len(balls) > 10:
            canv.delete(balls[0].id)
            for i in range(len(balls) - 1):
                balls[i] = balls[i + 1]
            balls[len(balls) - 1] = new_ball
        else:
            balls += [new_ball]
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event=0):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if (event.x - 20) != 0:
                self.angle = math.atan((event.y - 450) / (event.x - 20))
            elif (event.y - 450) > 0:
                self.angle = math.pi / 2
            else:
                self.angle = - math.pi / 2

        if self.f2_on:
            canv.itemconfig(self.id, fill='orange')
        else:
            canv.itemconfig(self.id, fill='black')
        canv.coords(self.id, 20, 450,
                    20 + max(self.f2_power, 20) * math.cos(self.angle),
                    450 + max(self.f2_power, 20) * math.sin(self.angle)
                    )

    def power_up(self):
        if self.f2_on is True:
            if self.f2_power < 100:
                self.f2_power += 1
            canv.itemconfig(self.id, fill='orange')
        else:
            canv.itemconfig(self.id, fill='black')


class target():
    def __init__(self, color='red'):
        self.points = 0
        self.id = canv.create_oval(0, 0, 0, 0)
        self.color = color
        self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """
        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)
        r = self.r = rnd(2, 50)
        self.dir = 3
        color = self.color
        canv.coords(self.id, x - r, y - r, x + r, y + r)
        canv.itemconfig(self.id, fill=color)
        self.live = True

    def hit(self):
        """Попадание шарика в цель."""
        global points

        canv.coords(self.id, -10, -10, -10, -10)
        points += 1
        #self.points += points
        show_points()

    def move(self):
        self.dir += rnd(-100, 100) / (100 * math.pi)
        v = bullet + 0.5

        r = self.r
        x = self.x = max(r, min(800 - r, self.x + v * math.cos(self.dir)))
        y = self.y = max(r, min(600 - r, self.y + v * math.sin(self.dir)))

        if self.live:
            canv.coords(self.id, x - r, y - r, x + r, y + r)


targets = list()
#t1 = target()
for c in ('red', 'yellow', 'cyan'):
    targets.append(target(c))

screen1 = canv.create_text(400, 300, text='', font='28')
g1 = gun()
bullet = 0
balls = []


def new_game(event=''):
    global gun, points, screen1, balls, bullet
    for t in targets:
        t.new_target()
    bullet = 0
    balls = []
    canv.bind('<Button-1>', g1.fire2_start)
    canv.bind('<ButtonRelease-1>', g1.fire2_end)
    canv.bind('<Motion>', g1.targetting)

    z = 0.03

    while any([t.live for t in targets]) or balls:
        for t in targets:
            t.move()

        del_balls()
        for b in balls:
            b.move()
            for t in targets:
                if b.hittest(t) and t.live:
                    t.live = False
                    t.hit()
                    #canv.bind('<Button-1>', '')
                    #canv.bind('<ButtonRelease-1>', '')
                    canv.itemconfig(screen1, text=f'Вы уничтожили цель за {bullet} выстрел{ending(bullet)}')

        canv.update()
        time.sleep(z)
        g1.targetting()
        g1.power_up()

    canv.itemconfig(screen1, text='')
    canv.delete(gun)

    root.after(750, new_game)


def del_balls():
    global balls
    counter = 0
    for i in range(len(balls)):
        if (-1 < balls[i].vy < 1) and (balls[i].y > 550):
            canv.delete(balls[i].id)
            balls[i] = None
            counter += 1

    for i in range(counter):
        balls[balls.index(None)] = balls[len(balls) - 1]
        balls.pop()

points = 0
t_points = canv.create_text(30, 30, text='', font='28')
def show_points():
    canv.itemconfig(t_points, text=str(points))

def ending(num):
    if 11 <= num <= 14:
        return 'ов'

    if num % 10 == 1:
        return ''

    if 2 <= num % 10 <= 4:
        return 'а'

    return 'ов'

new_game()

root.mainloop()
