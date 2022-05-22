from utils import grammar_file, lexer_output_dir, parser_output_dir, Logger
from .LR1Parser import LR1Parser
import os


def main():
    input_dir = lexer_output_dir
    output_dir = parser_output_dir
    # 遍历每一个代码的词法分析结果文件
    for file in os.listdir(input_dir):
        # 读入代码的词法分析结果
        lr1_parser = LR1Parser(grammar_file)
        with open(input_dir + "/" + file, "r") as input_file:
            # 定义语法分析结果输出文件
            output_file = output_dir + "\\" + file.split(".")[0] + ".out"
            if os.path.exists(output_file):
                os.remove(output_file)
            # 写日志文件
            logger = Logger(output_file)
            logger.insert('JMP', 0, -1)
            # 读入词法文件的每一行
            line = input_file.readline()
            while line:
                # 按行处理词法单元
                key = line.split('\'')[1]
                value = line.split('\'')[3]
                attach = line.split('\'')[5]
                token = [key, value, attach]
                lr1_parser.process_token(value, token, logger)
                line = input_file.readline()
            logger.commands[0].num = lr1_parser.procedure.procedure_dict['_global'].address
            logger.flush()
    print("\033[1;32m", "PARSER DONE SUCCESSFULLY!", "\033[0m", "\n")


if __name__ == '__main__':
    main()
