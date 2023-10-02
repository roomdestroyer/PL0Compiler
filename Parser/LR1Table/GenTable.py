from .Grammar import Grammar
from .LR1Table import LR1Table
import sys
import wx
import wx.grid as gridlib
from .LR1TableUI import LR1TableUI


def GenLR1Table(grammar_file):
    G = Grammar(open(grammar_file).read())
    lr1_parser = LR1Table(G)
    action_ = lr1_parser.action
    goto_ = lr1_parser.goto
    lr1_table_ = lr1_parser.parse_table
    return action_, goto_, lr1_table_

def GenTableUI(action_, goto_, lr1_table_):
    app = wx.App(False)
    w = LR1TableUI(None, action_, goto_, lr1_table_)
    app.MainLoop()
