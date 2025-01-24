from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

class Ui_interface(QtWidgets.QMainWindow):
    def __init__(self, game):
        super(Ui_interface, self).__init__()
        self.setupUi()
        self.init_pygame(game)

    def setupUi(self):
        interface = self
        interface.setObjectName("interface")
        interface.resize(404, 300)
        self.centralwidget = QtWidgets.QWidget(interface)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.alpha_label = QtWidgets.QLabel(self.centralwidget)
        self.alpha_label.setObjectName("alpha_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.alpha_label)
        self.beta_label = QtWidgets.QLabel(self.centralwidget)
        self.beta_label.setObjectName("beta_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.beta_label)
        self.decay_label = QtWidgets.QLabel(self.centralwidget)
        self.decay_label.setObjectName("decay_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.decay_label)
        self.best_label = QtWidgets.QLabel(self.centralwidget)
        self.best_label.setObjectName("best_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.best_label)
        self.alpha_box = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.alpha_box.setMaximum(1.0)
        self.alpha_box.setSingleStep(0.05)
        self.alpha_box.setProperty("value", 1.0)
        self.alpha_box.setObjectName("alpha_box")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.alpha_box)
        self.beta_box = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.beta_box.setSingleStep(0.05)
        self.beta_box.setProperty("value", 1.0)
        self.beta_box.setObjectName("beta_box")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.beta_box)
        self.decay_box = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.decay_box.setMaximum(1.0)
        self.decay_box.setSingleStep(0.05)
        self.decay_box.setProperty("value", 0.9)
        self.decay_box.setObjectName("decay_box")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.decay_box)
        self.best_box = QtWidgets.QSpinBox(self.centralwidget)
        self.best_box.setMaximum(10)
        self.best_box.setProperty("value", 5)
        self.best_box.setObjectName("best_box")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.best_box)
        self.gridLayout.addLayout(self.formLayout, 0, 1, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setRowCount(6)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.horizontalHeader().setDefaultSectionSize(39)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setObjectName("start")
        self.gridLayout.addWidget(self.start, 1, 0, 1, 1)
        interface.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(interface)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 404, 21))
        self.menubar.setObjectName("menubar")
        interface.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(interface)
        self.statusbar.setObjectName("statusbar")
        interface.setStatusBar(self.statusbar)

        self.retranslateUi(interface)
        QtCore.QMetaObject.connectSlotsByName(interface)

        self.is_ready = False

    def init_pygame(self, game):
        self.game = game
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.pygame_loop())
        self.timer.start(0)

    def pygame_loop(self):
        if self.game.loop(self):
            self.close()

    def retranslateUi(self, interface):
        _translate = QtCore.QCoreApplication.translate
        interface.setWindowTitle(_translate("interface", "interface"))
        self.alpha_label.setText(_translate("interface", "alpha"))
        self.beta_label.setText(_translate("interface", "beta"))
        self.decay_label.setText(_translate("interface", "decay"))
        self.best_label.setText(_translate("interface", "best"))
        self.start.setText(_translate("interface", "Начать анимацию"))

    def setup_buttons(self):
        self.start.clicked.connect(self.start_animation)

    def start_animation(self):

        try:
            vals_dicty = dict()

            vals_dicty['alpha'] = float(self.alpha_box.value())
            vals_dicty['beta'] = float(self.beta_box.value())
            vals_dicty['decay'] = float(self.decay_box.value())
            vals_dicty['n_best'] = float(self.best_box.value())

            distance = []

            for row in range(self.tableWidget.rowCount()):
                distance.append(list())
                for column in range(self.tableWidget.columnCount()):
                    item_val = int(self.tableWidget.item(row, column).text())
                    if row == column:
                        if item_val != 0:
                            raise ValueError(
                                'Расстояние города между собой должно быть равно нулю')
                    if item_val:
                        distance[row].append(item_val)
                    else:
                        break

            vals_dicty['distances'] = np.array(distance)
            vals_dicty['n_ants'] = len(distance) * 2
            vals_dicty['n_iterations'] = len(distance) * 4

            self.game.game_init(vals_dicty)
        except Exception as e:
            print(e)
