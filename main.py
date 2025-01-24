import random as rn
import numpy as np
import math

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from numpy.random import choice as np_choice

# Импорт pygame
import pygame

import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

IMAGE_DIR = 'source/images'
DURATION = 60

def write_text(pos, text, screen, color=(0, 0, 0), centered=False):
    font = pygame.font.SysFont('comic.ttf', 48)
    render = font.render(text, True, color)
    if centered:
        screen.blit(render, (pos[0] - render.get_width() // 2, pos[1]))
    else:
        screen.blit(render, pos)

def load_image(name, colorkey=None):
    fullname = os.path.join('source/images', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    if colorkey == 0:
        image = pygame.image.load(fullname)
    else:
        image = pygame.image.load(fullname).convert()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

class Ui_interface(QtWidgets.QMainWindow):
    def __init__(self, game):
        super(Ui_interface, self).__init__()
        self.setUi()
        self.setWindowIcon(QtGui.QIcon('ant.ico'))
        self.init_pygame(game)
        self.is_pause = False
        self.cur_iter = 0
        self.setup_buttons()
        self.play_icon = QtGui.QIcon()
        self.play_icon.addPixmap(QtGui.QPixmap(os.path.join(IMAGE_DIR, "play.png")),
                                 QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
        self.pause_icon = QtGui.QIcon()
        self.pause_icon.addPixmap(QtGui.QPixmap(os.path.join(IMAGE_DIR, "pause.png")),
                                  QtGui.QIcon.Normal,
                                  QtGui.QIcon.Off)

    def setUi(self):
        uic.loadUi('source/ui/form.ui', self)

    def init_pygame(self, game):
        self.game = game
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.pygame_loop)
        self.timer.start(0)

    def pygame_loop(self):
        if self.game.is_ready:
            if self.game.loop(self):
                self.close()
            self.cadre_box.setValue(self.game.timer)

    def retranslateUi(self, interface):
        _translate = QtCore.QCoreApplication.translate
        interface.setWindowTitle(_translate("Ant interface", "Ant interface"))
        self.cadre_label.setText(_translate("interface", "Текущий кадр:"))
        self.duration_label.setText(_translate("interface", "Продолжительность анимации:"))
        self.alpha_label.setText(_translate("interface", "alpha"))
        self.beta_label.setText(_translate("interface", "beta"))
        self.decay_label.setText(_translate("interface", "decay"))
        self.best_label.setText(_translate("interface", "best"))
        self.start.setText(_translate("interface", "Начать анимацию"))

    def setup_buttons(self):
        self.start.clicked.connect(self.start_animation)
        self.play.clicked.connect(self.switch_pause)
        self.next.clicked.connect(self.next_iter)
        self.prev.clicked.connect(self.prev_iter)
        self.cadre_box.valueChanged.connect(self.change_cadre)
        self.duration_box.valueChanged.connect(self.change_duration)

    def switch_pause(self):
        self.is_pause = not self.is_pause
        if self.is_pause:
            self.play.setIcon(self.play_icon)
        else:
            self.play.setIcon(self.pause_icon)

    def next_iter(self):
        if self.game.cur_iter + 1 <= self.game.n_iterations:
            self.game.cur_iter += 1
            self.game.timer = 0

    def prev_iter(self):
        if self.game.cur_iter - 1 >= 0:
            self.game.cur_iter -= 1
            self.game.timer = 0

    def change_cadre(self):
        cadre = int(self.cadre_box.value())
        self.game.timer = cadre

    def change_duration(self):
        global DURATION
        duration = int(self.duration_box.value())
        DURATION = duration
        self.cadre_box.setMaximum(self.game.n_inds * DURATION)
        self.game.timer = min(self.game.timer, self.game.n_inds * DURATION)

    def start_animation(self):
        try:
            vals_dicty = dict()

            vals_dicty['alpha'] = float(self.alpha_box.value())
            vals_dicty['beta'] = float(self.beta_box.value())
            vals_dicty['decay'] = float(self.decay_box.value())
            vals_dicty['n_best'] = int(self.best_box.value())

            distance = []

            for row in range(self.tableWidget.rowCount()):
                distance.append(list())
                for column in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(row, column)
                    if item is None:
                        break
                    item_val = int(item.text())
                    if row == column:
                        if item_val != 0:
                            raise Exception(
                                'Расстояние города между собой должно быть равно нулю')
                    distance[row].append(item_val)
            distance = [i for i in distance if i]
            vals_dicty['distances'] = np.array(distance, float)
            if len(vals_dicty['distances']) == 1:
                raise Exception('Матрица должна состоять как минимум из двух городов')
            vals_dicty['n_ants'] = len(distance) * 2
            vals_dicty['n_iterations'] = len(distance) * 4

            self.game.game_init(vals_dicty)
            self.animation_manager.setEnabled(True)
            self.cadre_box.setMaximum(self.game.n_inds * DURATION)
            self.duration_box.setValue(DURATION)
        except ValueError as e:
            self.warning_label.setText('Неправильный формат ячеек')
        except Exception as e:
            self.warning_label.setText(e.__str__())

class Ant(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('ant.png', 0)
        self.rect = self.image.get_rect()
        self.text_pos = 46, 25

    def draw(self, pos, num_of_ants, screen):
        font = pygame.font.SysFont('comic.ttf', 60)
        render = font.render(str(num_of_ants), True, (0, 0, 0))
        pos = (pos[0] - self.image.get_width() // 2, pos[1] - self.image.get_height())
        render_pos = [pos[i] + self.text_pos[i] for i in range(2)]

        screen.blit(self.image, pos)
        screen.blit(render, render_pos)

class CitiesNet:
    def __init__(self):
        self.is_ready = False
        pygame.init()
        pygame.display.set_caption('Ant algorithm')
        ant_icon = pygame.image.load('ant_icon.png')
        pygame.display.set_icon(ant_icon)
        self.WIDTH, self.HEIGHT = self.SIZE = 800, 600
        self.screen = pygame.display.set_mode(self.SIZE)
        self.fps = 30
        self.clock = pygame.time.Clock()

    def draw_net(self):
        # окрашивание тропинок между городами и основных дорог
        for y in range(len(self.distances)):
            for x in range(len(self.distances[0])):
                if self.distances[y][x] != np.inf:
                    pherm_intencity1 = self.conditions_of_ant_colony[self.cur_iter]['pheromone'][y][x]
                    pherm_intencity2 = self.conditions_of_ant_colony[self.cur_iter]['pheromone'][x][y]
                    color = max(((min(255, pherm_intencity1 * 50), 0, 0),
                                 (min(255, pherm_intencity2 * 50), 0, 0)))
                    pygame.draw.line(self.screen, color, self.coords[y], self.coords[x], 10)

                    # рисование длины между тропинок
                    distance = self.distances[y][x]

                    distance_pos = (((self.coords[y][0] + self.coords[x][0]) // 2),
                                    (self.coords[y][1] + self.coords[x][1]) // 2)

                    if self.n_inds == 4 and x in (0, 2) and y in (2, 0):
                        distance_pos = (distance_pos[0], distance_pos[1] + 50)

                    write_text(distance_pos, str(distance), self.screen, centered=True,
                               color=(0, 0, 255))

        # нумерация города
        list_of_coords = [self.coords[i] for i in range(len(self.coords))]
        for i in range(len(list_of_coords)):
            write_text(list_of_coords[i], str(i + 1), color=(0, 255, 0), screen=self.screen)

    def draw_ant(self, timer):
        ant = Ant()

        current_path_index = timer // DURATION
        coef = (timer % DURATION) / DURATION

        if self.conditions_of_ant_colony[self.cur_iter]['all_paths']:
            sorted_all_paths = sorted(self.conditions_of_ant_colony[self.cur_iter]['all_paths'],
                                      key=lambda x: x[1])

            current_inds = [sorted_all_paths[i][0][current_path_index] for i in
                            range(len(sorted_all_paths))]

            for ind in current_inds:
                first_ind, second_ind = self.coords[ind[0]], self.coords[ind[1]]
                if second_ind[0] > first_ind[0]:
                    x = first_ind[0] + round(((second_ind[0] - first_ind[0]) * coef))
                else:
                    x = first_ind[0] - round(((first_ind[0] - second_ind[0]) * coef))
                if second_ind[1] > first_ind[1]:
                    y = first_ind[1] + round(((second_ind[1] - first_ind[1]) * coef))
                else:
                    y = first_ind[1] - round(((first_ind[1] - second_ind[1]) * coef))
                pos = (x, y)
                ant.draw(pos, current_inds.count(ind), self.screen)

    def game_init(self, values):
        ant_colony = AntColony(**values)
        shortest_path, conditions_of_ant_colony = ant_colony.run()
        print(f"Кратчайший путь: {shortest_path}")

        self.n_iterations = ant_colony.n_iterations
        self.n_inds = len(ant_colony.all_inds)
        self.conditions_of_ant_colony = conditions_of_ant_colony
        self.cur_iter = 0
        self.timer = 0
        self.n_ants = ant_colony.n_ants
        self.distances = ant_colony.distances
        self.coords = dict()
        self.shortest_path = shortest_path

        center = self.screen.get_width() // 2, self.screen.get_height() // 2
        height = 160

        # нахождение основных городов
        angle = 180 - (((self.n_inds - 2) / self.n_inds) * 180)
        const_rad_angle = rad_angle = angle * (math.pi / 180)
        self.coords[0] = center[0], center[1] - height
        for ind in range(1, self.n_inds):
            x1, y1 = center[0] + (self.coords[0][0] - center[0]) * math.cos(rad_angle) - \
                     (self.coords[0][1] - center[1]) * math.sin(rad_angle), \
                     center[1] + (self.coords[0][0] - center[0]) * math.sin(rad_angle) + \
                     (self.coords[0][1] - center[1]) * math.cos(rad_angle)

            rad_angle += const_rad_angle
            self.coords[ind] = x1, y1

        self.is_ready = True

    def loop(self, window):
        if self.is_ready:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return True

            self.screen.fill('White')

            if self.cur_iter >= self.n_iterations:
                write_text((self.screen.get_width() // 2, 50), "Анимация закончилась", self.screen,
                           centered=True)
                path = '; '.join([f'{i[0] + 1}->{i[1] + 1}' for i in self.shortest_path[0]])
                write_text((self.screen.get_width() // 2, 500),
                           f"Короткий путь: {path}",
                           self.screen, centered=True)
                write_text((self.screen.get_width() // 2, 550),
                           f"Длина короткого пути: {self.shortest_path[1]}", self.screen,
                           centered=True)
            elif self.timer == self.n_inds * DURATION and self.cur_iter < self.n_iterations:
                self.timer = 0
                self.cur_iter += 1
            self.draw_net()
            self.draw_ant(min(self.timer, (self.n_inds * DURATION) - 1))

            write_text((0, 0), str(self.cur_iter), self.screen)

            self.clock.tick(self.fps)
            pygame.display.flip()
            if not window.is_pause:
                self.timer += 1
            return False

class AntColony(object):
    def __init__(self, distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=1):
        # избавляемся от нулей в матрице
        i = 0
        j = 0
        while i < distances.shape[0]:
            while j < distances.shape[1]:
                if distances[i][j] == 0:
                    distances[i][j] = np.inf
                    i += 1
                    j += 1
                else:
                    j += 1
                    continue
            i += 1
        self.distances = distances  # матрица растояний
        self.pheromone = np.ones(self.distances.shape) / len(distances)  # матрица феромонов
        self.all_inds = range(len(distances))  # список городов
        self.n_ants = n_ants  # колличество муравьев
        self.n_best_ants = n_best  # колличество элитных муравьев
        self.n_iterations = n_iterations  # колличество итераций
        self.decay = decay  # испарения феромона
        self.alpha = alpha
        self.beta = beta

    def run(self, debug=False):
        conditions_of_ant_colony = []
        conditions_of_ant_colony.append({'all_paths': None,
                                         'pheromone': np.copy(self.pheromone)})
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheronome(all_paths, self.n_best_ants)
            shortest_path = min(all_paths, key=lambda x: x[1])
            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path
            self.pheromone *= self.decay
            if debug:
                self.debug_condition(i)
            conditions_of_ant_colony.append({'all_paths': all_paths,
                                             'pheromone': np.copy(self.pheromone)})
        return all_time_shortest_path, conditions_of_ant_colony

    def spread_pheronome(self, all_paths, n_best):
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for move in path:
                self.pheromone[move] += 1.0 / self.distances[move]

    def gen_path_dist(self, path):
        total_dist = 0
        for ele in path:
            total_dist += self.distances[ele]
        return total_dist

    def gen_all_paths(self):
        all_paths = []
        for ant in range(self.n_ants):
            path = self.gen_path(0)
            all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_path(self, start):
        path = []
        visited = set()
        visited.add(start)
        prev = start
        for i in range(len(self.distances) - 1):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append((prev, move))
            prev = move
            visited.add(move)
        path.append((prev, start))  # возвращаемся к тому, с чего начали
        return path

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0  # посещенные города не должны посещаться снова
        row = pheromone ** self.alpha * ((1.0 / dist) ** self.beta)
        norm_row = row / row.sum()
        move = np_choice(self.all_inds, 1, p=norm_row)[0]
        return move

    def debug_condition(self, n_iteration):
        print(f'------Шаг-{n_iteration + 1}.')
        for y in range(len(self.pheromone)):
            for x in range(len(self.pheromone[0])):
                if x != y:
                    print(f'Узел {y + 1}-{x + 1}: {self.pheromone[y][x]}')

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    game = CitiesNet()
    app = QApplication(sys.argv)
    ex = Ui_interface(game)
    ex.show()
    sys.excepthook = except_hook
    result = app.exec()
    sys.exit(result)

input()
