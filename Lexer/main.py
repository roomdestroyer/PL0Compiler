import os
from Lexer.GenToken import GenToken
from utils import lexer_input_dir, lexer_output_dir


def main():
    for file in os.listdir(lexer_input_dir):
        # with open(lexer_input_dir + "./" + file, "r") as input_file:
        with open(os.path.join(lexer_input_dir, file), "r") as input_file:
            # output_file = lexer_output_dir + "./" + file.split(".")[0] + ".out"
            output_file = os.path.join(lexer_output_dir, file.split(".")[0] + ".out")
            if os.path.exists(output_file):
                os.remove(output_file)
            line = input_file.readline()
            while line:
                GenToken(line, output_file)
                line = input_file.readline()
        print("\033[1;32m", "LEXEME ACCEPTED!", "\033[0m")
        input_file.close()
    print("\033[1;32m", "LEXER DONE SUCCESSFULLY!", "\033[0m", "\n")


if __name__ == "__main__":
    main()
