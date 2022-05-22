from PyQt5.QtWidgets import *


class LR1TableUI(QWidget):
    def __init__(self, action, goto, table):

        super().__init__()
        self.setWindowTitle("LR1分析表")
        self.action = action
        self.goto = goto
        self.resize(860, 560)
        self.action = sorted(self.action)
        self.goto = sorted(self.goto)
        self.table = table
        self.Table = QTableWidget(len(self.table) + 1, len(self.action) + len(self.goto) + 1)
        self.Table.verticalHeader().setHidden(True)
        self.initUI()

    def initUI(self):
        self.Table.setItem(0, 0, QTableWidgetItem('状态'))
        for i in range(len(self.action) + len(self.action) - 1):
            if i < len(self.action):
                self.Table.setItem(0, i + 1, QTableWidgetItem(self.action[i]))
            else:
                self.Table.setItem(0, i + 1, QTableWidgetItem(self.goto[i - len(self.action)]))
        for i in range(len(self.table)):
            self.Table.setItem(i + 1, 0, QTableWidgetItem(str(i)))
            for item in self.action:
                if self.table[i][item] != ' ':
                    self.Table.setItem(i + 1, self.action.index(item) + 1, QTableWidgetItem(self.table[i][item]))
            for item in self.goto:
                if self.table[i][item]:
                    self.Table.setItem(i + 1, self.goto.index(item) + 1 + len(self.action), QTableWidgetItem(str(self.table[i][item])))
        self.Table.setItem(9, 0, QTableWidgetItem(str(9)))
        mainlayout = QVBoxLayout()
        mainlayout.addWidget(self.Table)
        self.setLayout(mainlayout)
        self.show()
