import warnings
warnings.filterwarnings("ignore")

from Lexer import lexer
from Parser import lr1_parser
from Parser import lr1_table_ui
from Simulator.main import main as machine
from utils import parser_output_dir, grammar_file
import os


parser_output_file_ = os.path.join(parser_output_dir, "PL0_code0.out")


# 对所有代码执行词法分析
def all_lexer():
    lexer()


# 对所有代码执行语法分析
def all_parser():
    lr1_parser()


# 在执行目标代码时，需要先进行词法分析和语法分析，生成中间代码
def pre_operational():
    all_lexer()
    all_parser()


# 生成 LR1 分析表的可视化 UI
def gen_lr1table_ui(grammar_file_):
    lr1_table_ui(grammar_file_)


if __name__ == '__main__':
    # 执行一次预操作以生成所有PL0代码的中间代码，之后修改 parser_output_file_ 参数就可以执行其它代码
    # pre_operational()
    gen_lr1table_ui(grammar_file)
    # machine(parser_output_file_)
