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

z = 0.03

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
        self.age = 0
        self.growing = rnd(300, 500) / 5000

        col = hex(rnd(0, int('FFFFFF', base=16) + 1))
        self.color = '#' + ('0' * 6 + col[2:])[-6:]

        self.id = canv.create_oval(
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r,
            fill=self.color)

        self.age_id = canv.create_oval(
            self.x - self.age,
            self.y - self.age,
            self.x + self.age,
            self.y + self.age,
            fill='black')

    def set_coords(self):
        canv.coords(
            self.id,
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r
        )

        canv.coords(
            self.age_id,
            self.x - self.age,
            self.y - self.age,
            self.x + self.age,
            self.y + self.age
        )

    def move(self):
        """Переместить мяч по прошествии единицы времени.
		Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
		self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
		и стен по краям окна (размер окна 800х600).
		"""
        # FIXME
        canv.move(self.id, self.vx, self.vy)
        canv.move(self.age_id, self.vx, self.vy)
        self.x = canv.coords(self.id)[0] + self.r
        self.y = canv.coords(self.id)[1] + self.r
        canv.coords(self.age_id,
            self.x - self.age,
            self.y - self.age,
            self.x + self.age,
            self.y + self.age)

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
        self.age += self.growing

        if self.age >= self.r:
            self.delete()


    def hittest(self, obj):
        if not canv.coords(self.id):
            return False
        if (((canv.coords(obj.id)[0] + obj.r - (canv.coords(self.id)[0] + self.r)) ** 2 + (
                canv.coords(obj.id)[1] + obj.r - canv.coords(self.id)[1] - self.r) ** 2) <= (self.r + obj.r) ** 2):
            return True
        return False

    def delete(self):
        global balls
        canv.delete(self.id)
        canv.delete(self.age_id)
        balls -= {self}

        explosion(self.x, self.y, self.color)



class gun():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.f2_power = 10
        self.f2_on = False
        self.angle = 1
        self.id = canv.create_line(self.x, self.y, self.x + 30, self.y - 30, width=7)

    def fire2_start(self, event):
        self.f2_on = True

    def fire2_end(self, event):
        """Выстрел мячом.
        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = ball(self.x, self.y)
        if (event.x - new_ball.x) != 0:
            self.angle = math.atan((event.y - new_ball.y) / (event.x - new_ball.x))
        elif (event.y - new_ball.y) > 0:
            self.angle = math.pi / 2
        else:
            self.angle = - math.pi / 2
        new_ball.vx = self.f2_power * math.cos(self.angle)
        new_ball.vy = self.f2_power * math.sin(self.angle)
        if len(balls) > 900:
            deleting_ball = balls.pop()
            deleting_ball.delete()

        balls.add(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event=0):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if (event.x - self.x) != 0:
                self.angle = math.atan((event.y - self.y) / (event.x - self.x))
            elif (event.y - self.y) > 0:
                self.angle = math.pi / 2
            else:
                self.angle = - math.pi / 2

        if self.f2_on:
            canv.itemconfig(self.id, fill='orange')
        else:
            canv.itemconfig(self.id, fill='black')
        canv.coords(self.id, self.x, self.y,
                    self.x + max(self.f2_power, 20) * math.cos(self.angle),
                    self.y + max(self.f2_power, 20) * math.sin(self.angle))

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
        self.a = 1
        self.h = 0
    def new_target(self):
        """ Инициализация новой цели. """
        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)
        r = self.r = rnd(2, 50)
        self.dir = 3
        self.a = 1
        self.h = 0
        color = self.color
        canv.coords(self.id, x - r, y - r, x + r, y + r)
        canv.itemconfig(self.id, fill=color)
        self.live = True

    def hit(self):
        """Попадание шарика в цель."""
        global points
        if (self.h == 1):
            canv.coords(self.id, -10, -10, -10, -10)
            points += 1
            #self.points += points
            show_points()
            self.h = 0

    def move(self):
        self.dir += rnd(-100, 100) / (100 * math.pi)
        v = bullet + 1

        r = self.r
        x = self.x = max(r, min(800 - r, self.x + v * math.cos(self.dir)))
        y = self.y = max(r, min(600 - r, self.y + v * math.sin(self.dir)))

        if self.live:
            canv.coords(self.id, x - r, y - r, x + r, y + r)

        if (self.live == 0 and self.a < 50):
             canv.coords(self.id, x - r*self.a, y - r*self.a, x + r*self.a, y + r*self.a)
             self.a += 5
        if (self.a > 50):
            self.h = 1
            self.a = 50





targets = list()
guns = list()
#t1 = target()
for c in ('red', 'yellow', 'cyan'):
    targets.append(target(c))

for i in range (15):
	guns.append(gun(20, 420 - i*10))

screen1 = canv.create_text(400, 300, text='', font='28')
bullet = 0
balls = set()


def new_game(event=''):
    global gun, points, screen1, balls, bullet
    for t in targets:
        t.new_target()
    bullet = 0
    balls = set()
    canv.bind('<Button-1>', fire_start)
    canv.bind('<ButtonRelease-1>', fire_end)
    canv.bind('<Motion>', targeting)


    while any([t.live for t in targets]) or balls:
        for t in targets:
            t.move()
            t.hit()

        #del_balls()
        cur_balls = set(balls)
        for b in cur_balls:
            b.move()
            for t in targets:
                if b.hittest(t) and t.live:
                    t.live = False
                    t.hit()
                    #canv.bind('<Button-1>', '')
                    #canv.bind('<ButtonRelease-1>', '')
                    canv.itemconfig(screen1, text='Вы уничтожили цель за {} выстрел{}'.format(bullet, ending(bullet)))

        canv.update()
        time.sleep(z)
        for g in guns:
            g.targetting()
            g.power_up()


    canv.itemconfig(screen1, text='')
    canv.delete(gun)

    root.after(750, new_game)


# def del_balls():
#     global balls
#     counter = 0
#     for i in range(len(balls)):
#         if (-1 < balls[i].vy < 1) and (balls[i].y > 550):
#             canv.delete(balls[i].id)
#             balls[i] = None
#             counter += 1
#
#     for i in range(counter):
#         balls[balls.index(None)] = balls[len(balls) - 1]
#         balls.pop()

points = 0
t_points = canv.create_text(30, 30, text='', font='28')
def show_points():
    canv.itemconfig(t_points, text=str(points))

def explosion(x, y, col):
    v = 30
    r_max = 400

    shards = list()

    for i in range(15):
        dir = rnd(0, 360) / 180 * math.pi
        obj = canv.create_oval(x - 4, y - 4, x + 4, y + 4, fill=col, outline=col)
        shards.append((obj, dir))

    def move():
        for shard in shards:
            obj, dir = shard
            canv.move(obj, v * math.cos(dir), v * math.sin(dir))

        x1, y1, x2, y2 = canv.coords(obj)
        xc, yc = (x1 + x2) / 2, (y1 + y2) / 2

        if (xc - x) ** 2 + (yc - y) ** 2 < r_max ** 2:
            root.after(int(z * 1000), move)
        else:
            delete()

    def delete():
        for shard in shards:
            canv.delete(shard[0])

    move()


def ending(num):
    if 11 <= num <= 14:
        return 'ов'

    if num % 10 == 1:
        return ''

    if 2 <= num % 10 <= 4:
        return 'а'

    return 'ов'

def fire_start(event):
    global guns
    for g in guns:
        g.fire2_start(event)


def fire_end(event):
    global guns
    for g in guns:
        g.fire2_end(event)

def targeting(event):
    global guns
    for g in guns:
        g.targetting(event)

new_game()

root.mainloop()
