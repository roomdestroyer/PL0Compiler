import re

ASSIGN = r"(?P<ASSIGN>(:=){1})"
PLUS = r"(?P<PLUS>(\+){1})"
MINUS = r"(?P<MINUS>(\-))"
TIMES = r"(?P<TIMES>(\*))"
DIVIDE = r"(?P<DIVIDE>(\/))"
NEQUAL = r"(?P<NEQUAL>(#))"
LESS_OR_EQUAL = r"(?P<LESS_OR_EQUAL>(<={1}))"
GREATER_OR_EQUAL = r"(?P<GREATER_OR_EQUAL>(>={1}))"
LESS = r"(?P<LESS>(<{1}))"
GREATER = r"(?P<GREATER>(>{1}))"
EQUAL = r"(?P<EQUAL>(=){1})"

LEFT_PARENTHESES = r"(?P<LEFT_PARENTHESES>(\())"
RIGHT_PARENTHESES = r"(?P<RIGHT_PARENTHESES>(\)))"
SEMICOLON = r"(?P<SEMICOLON>(;))"
COMMA = r"(?P<COMMA>(,))"
DOT = r"(?P<DOT>(\.))"

CONST = r"(?P<CONST>(const))"
VAR = r"(?P<VAR>(var))"
PROCEDURE = r"(?P<PROCEDURE>(procedure))"
BEGIN = r"(?P<BEGIN>(begin))"
END = r"(?P<END>(end))"
ODD = r"(?P<ODD>(odd))"
IF = r"(?P<IF>(if))"
THEN = r"(?P<THEN>(then))"
CALL = r"(?P<CALL>(call))"
WHILE = r"(?P<WHILE>(while))"
DO = r"(?P<DO>(do))"
READ = r"(?P<READ>(read))"
WRITE = r"(?P<WRITE>(write))"

IDENTIFIER = r"(?P<IDENTIFIER>([a-zA-Z][a-zA-Z0-9]*))"
NUMBER = r"(?P<NUMBER>([0-9]+))"

PATTERMS = [ASSIGN, PLUS, MINUS, TIMES, DIVIDE, GREATER_OR_EQUAL, LESS_OR_EQUAL, EQUAL, NEQUAL, LESS, GREATER,
            LEFT_PARENTHESES, RIGHT_PARENTHESES, SEMICOLON, COMMA, DOT, CONST, VAR, PROCEDURE, BEGIN,
            END, ODD, IF, THEN, CALL, WHILE, DO, READ, WRITE, IDENTIFIER, NUMBER]

patterns = re.compile("|".join(PATTERMS))

# 词素类型到值的映射关系，除IDENTIFIER和NUMBER外，其余都和正则匹配的结果保持一致
mapping = dict()
mapping["ASSIGN"] = ":="
mapping["PLUS"] = "+"
mapping["MINUS"] = "-"
mapping["TIMES"] = "*"
mapping["DIVIDE"] = "/"
mapping["EQUAL"] = "="
mapping["NEQUAL"] = "#"
mapping["LESS"] = "<"
mapping["LESS_OR_EQUAL"] = "<="
mapping["GREATER"] = ">"
mapping["GREATER_OR_EQUAL"] = ">="
mapping["LEFT_PARENTHESES"] = "("
mapping["RIGHT_PARENTHESES"] = ")"
mapping["SEMICOLON"] = ";"
mapping["COMMA"] = ","
mapping["DOT"] = "."
mapping["CONST"] = "const"
mapping["VAR"] = "var"
mapping["PROCEDURE"] = "procedure"
mapping["BEGIN"] = "begin"
mapping["END"] = "end"
mapping["ODD"] = "odd"
mapping["IF"] = "if"
mapping["THEN"] = "then"
mapping["CALL"] = "call"
mapping["WHILE"] = "while"
mapping["DO"] = "do"
mapping["READ"] = "read"
mapping["WRITE"] = "write"
mapping["IDENTIFIER"] = "id"
mapping["NUMBER"] = "num"


class Token:
    def __init__(self, token_type, token_value, attach):
        self.token_key = token_type
        self.token_value = token_value
        self.attach = attach

    def __str__(self):
        return "{type: %s id: %s num: %s}" % (self.token_key, self.token_value, self.attach)


def line_get_token(txt):
    for match in re.finditer(patterns, txt):
        type_ = match.lastgroup
        value_ = mapping[type_]
        if value_ in ["id", "num"]:
            attach_ = match.group()
        else:
            attach_ = "-1"
        yield [type_, value_, attach_]


def GenToken(txt, the_output_file):
    with open(the_output_file, "a+") as f:
        for token in line_get_token(txt):
            f.write(str(token))
            f.write("\n")
    f.close()
