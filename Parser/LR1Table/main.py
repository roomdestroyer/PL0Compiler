from Parser.LR1Table.GenTable import GenLR1Table, GenTableUI
from utils import grammar_file


def main(grammar_file_):
    action, goto, lr1_table = GenLR1Table(grammar_file_)
    GenTableUI(action, goto, lr1_table)


if __name__ == "__main__":
    main(grammar_file)
