import wx
import wx.grid as gridlib

class LR1TableUI(wx.Frame):
    def __init__(self, parent, action, goto, table):
        super(LR1TableUI, self).__init__(parent, title="LR1分析表", size=(860, 560))

        self.action = sorted(action)
        self.goto = sorted(goto)
        self.table = table

        self.grid = gridlib.Grid(self)
        self.grid.CreateGrid(len(self.table) + 1, len(self.action) + len(self.goto) + 1)
        self.grid.SetRowLabelSize(0)  # Hide row labels

        self.initUI()
        self.Centre()
        self.Show()

    def initUI(self):
        self.grid.SetCellValue(0, 0, '状态')

        for i in range(len(self.action) + len(self.goto) - 1):
            if i < len(self.action):
                self.grid.SetCellValue(0, i + 1, self.action[i])
            else:
                self.grid.SetCellValue(0, i + 1, self.goto[i - len(self.action)])

        for i in range(len(self.table)):
            self.grid.SetCellValue(i + 1, 0, str(i))
            for item in self.action:
                if self.table[i][item] != ' ':
                    self.grid.SetCellValue(i + 1, self.action.index(item) + 1, self.table[i][item])
            for item in self.goto:
                if self.table[i][item]:
                    self.grid.SetCellValue(i + 1, self.goto.index(item) + 1 + len(self.action), str(self.table[i][item]))

        self.grid.SetCellValue(9, 0, str(9))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
