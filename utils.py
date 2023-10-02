import os


def get_project_path():
    """得到项目路径"""
    project_path = os.path.join(
        os.path.dirname(__file__)
    )
    return project_path


class Command:
    def __init__(self, cmd: str, level: int, num: int):
        self.cmd = cmd
        self.level = level
        self.num = num


class Logger:
    def __init__(self, path: str):
        self.f = open(path, 'w')
        self.total_line = 0
        self.commands = []

    def flush(self):
        for item in self.commands:
            self.f.write(item.cmd + ' ' + str(item.level) + ' ' + str(item.num) + '\n')

    def insert(self, cmd: str, level: int, num: int):
        self.commands.append(Command(cmd, level, num))
        self.total_line += 1


root_path = get_project_path()
grammar_file = os.path.join(root_path, "Parser", "LR1Table",
                            "grammars", "mygrammar.txt")
lexer_input_dir = os.path.join(root_path, "Lexer", "LexerInput")
lexer_output_dir = os.path.join(root_path, "Lexer", "LexerOutput")
parser_output_dir = os.path.join(root_path, "Parser", "ParserOutput")


# 在过程调用时，首先在栈中开辟三个空间，存放静态链SL、动态链DL（B）和返回地址RA（P）
call_init_offset = 3


if __name__ == '__main__':
    print(get_project_path())
