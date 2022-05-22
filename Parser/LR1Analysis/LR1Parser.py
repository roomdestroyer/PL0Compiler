from Parser.LR1Table.LR1Table import LR1Table
from Parser.LR1Table.Grammar import Grammar
from .Procedure import Procedure
from utils import grammar_file


class LR1Parser:
    def __init__(self, grammar_file_):
        # 记录过程调用
        self.procedure = Procedure()
        self.procedure.add_procedure("_global", 0)
        # LR1分析对象
        self.lr1_table = LR1Table(Grammar(open(grammar_file).read()))
        # LR1分析表
        self.parse_table = self.lr1_table.parse_table
        # 记录生成的地址
        self.global_address_counter = 0
        # 状态栈
        self.state_stack = [0]
        # 符号栈
        self.symbol_stack = []
        # 输入栈
        self.readable_stack = []

    def process_const(self, generative):
        if generative == 'CONST -> CONST_ ;':
            # pop掉[const ;], 规约为CONST, 栈顶为[], 分析完毕
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'CONST_ -> CONST_ , CONST_DEF':
            # pop掉[, id], 规约为CONST_, 栈顶为[const]
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'CONST_ -> const CONST_DEF':
            # pop掉[id], 规约为CONST_, 栈顶为[const]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'CONST_DEF -> ID = UINT':
            # pop掉[= num], 规约为CONST_DEF, 栈顶为[const id]
            self.procedure.add_const(self.symbol_stack[-3][2], self.symbol_stack[-1][2])
            self.symbol_stack = self.symbol_stack[:-2]

    def process_var(self, generative):
        if generative == 'VARIABLE -> VARIABLE_ ;':
            # pop掉[var ;], 规约为VARIABLE, 栈顶为[], 分析完毕
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'VARIABLE_ -> var ID':
            # pop掉[id], 规约为VARIABLE_, 栈顶为[var]
            self.procedure.add_var(self.symbol_stack[-1][2])
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'VARIABLE_ -> VARIABLE_ , ID':
            # pop掉[, id], 规约为VARIABLE_, 栈顶为[var]
            self.procedure.add_var(self.symbol_stack[-1][2])
            self.symbol_stack = self.symbol_stack[:-2]

    def process_procedure(self, generative):
        if generative == 'PROCEDURE -> PROCEDURE_':
            # pop掉[begin end], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'PROCEDURE -> ^':
            pass
        elif generative == 'PROCEDURE_ -> PROCEDURE_ PROC_HEAD SUBPROG ;':
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'PROCEDURE_ -> PROC_HEAD SUBPROG ;':
            # pop掉[;], 栈顶为[begin end]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == "PROC_HEAD -> procedure ID ;":
            # pop掉[procedure id ;], 栈顶为[]
            self.procedure.add_procedure(self.symbol_stack[-2][2],
                                         self.procedure.current_procedure.level + 1)
            self.symbol_stack = self.symbol_stack[:-3]

    def process_assign(self, generative, logger):
        if generative == 'ASSIGN -> ID := EXPR':
            # 赋值语句右边的值通过规约计算出, 将其赋给变量
            ret = self.procedure.find_by_name(self.symbol_stack[-3][2])
            if not ret[2]:
                print("\033[0;31m", "ERROR: Assign to CONST number!", "\033[0m")
                exit(-1)
            # ret[0]是嵌套深度, ret[1][1]是offset
            logger.insert('STO', ret[0], ret[1][1])
            # pop掉[id := num], 栈顶为[] (注: begin体内除最后一条语句外都要加; 最后一条可加可不加，走的是不同的规约路线)
            self.symbol_stack = self.symbol_stack[:-3]

    def process_comp(self, generative):
        # 读取到一个begin后, 把begin pop掉, 规约为状态COMP_BEGIN, 之后每遇到一条带;的语句,
        # 就通过第三条产生式规约为COMP_BEGIN, 直到遇到一条不带;的语句, 就通过第一条产生式规约为COMP
        # 如果;之后是end, 则所用产生式为 STATEMENT -> ^
        if generative == 'COMP -> COMP_BEGIN end':
            # pop掉[end], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'COMP_BEGIN -> begin STATEMENT':
            # pop掉[begin], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'COMP_BEGIN -> COMP_BEGIN ; STATEMENT':
            # pop掉[;], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-1]

    def process_factor(self, generative, logger):
        if generative == 'FACTOR -> ID':
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            if ret is None:
                print("\033[0;31m", "ERROR: Can't find variable ", self.symbol_stack[-1][2], "!\033[0m")
                exit(-1)
            if ret[2] == 0:
                # 找到 CONST
                logger.insert('LIT', 0, ret[1])
            else:
                logger.insert("LOD", ret[0], ret[1][1])
        elif generative == 'FACTOR -> UINT':
            # 栈顶为num的值
            logger.insert('LIT', 0, self.symbol_stack[-1][2])
        elif generative == 'FACTOR -> ( EXPR )':
            # 去除括号, 只留下 EXPR
            tmp = self.symbol_stack[-2]
            self.symbol_stack = self.symbol_stack[:-3]
            self.symbol_stack.append(tmp)

    def process_item(self, generative, logger):
        if generative == 'ITEM -> FACTOR':
            pass
        elif generative == 'ITEM -> ITEM MUL_DIV FACTOR':
            if self.symbol_stack[-2][0] == 'TIMES':
                logger.insert('OPR', 0, 4)
            elif self.symbol_stack[-2][0] == 'DIVIDE':
                logger.insert('OPR', 0, 5)
            # pop掉[*or/ num], 栈顶为[num]
            self.symbol_stack = self.symbol_stack[:-2]

    def process_expr(self, generative, logger):
        if generative == 'EXPR -> EXPR PLUS_MINUS ITEM':
            if self.symbol_stack[-2][0] == 'MINUS':
                logger.insert('OPR', 0, 3)
            else:
                logger.insert('OPR', 0, 2)
            # pop掉[+or- num], 栈顶为[num]
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'EXPR -> PLUS_MINUS ITEM':
            if self.symbol_stack[-2][0] == 'MINUS':
                logger.insert('OPR', 0, 1)
            # pop掉[+or-], 栈顶为[num]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'EXPR -> ITEM':
            pass

    def process_call(self, generative, logger):
        if generative == 'CALL -> call ID':
            cur_p = self.procedure.current_procedure
            while True:
                childen_procedures = [self.procedure.procedure_dict[x] for x in
                                      self.procedure.procedure_dict.keys() if
                                      self.procedure.procedure_dict[x].father == cur_p.name]
                target_p = [p for p in childen_procedures if p.name == self.symbol_stack[-1][2]]
                if len(target_p) == 0:
                    if cur_p.father == "":
                        # 寻找到根路径都没有找到合适的调用
                        print("\033[0;31m", "ERROR: Wrong procedure call!\033[0m")
                        exit(-1)
                    # 去父目录寻找有无过程名可以调用
                    cur_p = self.procedure.procedure_dict[cur_p.father]
                else:
                    # 找到合适的过程调用
                    target_p = target_p[0]
                    logger.insert('CALL', self.procedure.current_procedure.level + 1 - target_p.level, target_p.address)
                    break
            # pop掉[call id], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-2]

    def process_read(self, generative, logger):
        if generative == 'READ -> READ_BEGIN )':
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'READ_BEGIN -> read ( ID':
            logger.insert('OPR', 0, 16)
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            if ret[2] == 0:
                print("\033[0;31m", "ERROR: Assign to CONST number!", "\033[0m")
                exit(-1)
            else:
                logger.insert('STO', ret[0], ret[1][1])
            self.symbol_stack = self.symbol_stack[:-3]
        elif generative == 'READ_BEGIN -> READ_BEGIN , ID':
            logger.insert('OPR', 0, 16)
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            if ret[2] == 0:
                print("\033[0;31m", "ERROR: Assign to CONST number!", "\033[0m")
                exit(-1)
            else:
                logger.insert('STO', ret[0], ret[1][1])
            self.symbol_stack = self.symbol_stack[:-2]

    def process_write(self, generative, logger):
        if generative == 'WRITE -> WRITE_BEGIN )':
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'WRITE_BEGIN -> write ( ID':
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            if ret is None:
                print("\033[0;31m", "ERROR: Can't find variable ", self.symbol_stack[-1][2], "!\033[0m")
                exit(-1)
            if ret[2] == 0:
                logger.insert('LIT', 0, ret[1])
                logger.insert('OPR', 0, 14)
            else:
                logger.insert('LOD', ret[0], ret[1][1])
                logger.insert('OPR', 0, 14)
            self.symbol_stack = self.symbol_stack[:-3]
        elif generative == 'WRITE_BEGIN -> WRITE_BEGIN , ID':
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            if ret is None:
                print("\033[0;31m", "ERROR: Can't find variable ", self.symbol_stack[-1][2], "!\033[0m")
                exit(-1)
            if ret[2] == 0:
                logger.insert('LIT', 0, ret[1])
                logger.insert('OPR', 0, 14)
            else:
                logger.insert('LOD', ret[0], ret[1][1])
                logger.insert('OPR', 0, 14)
            self.symbol_stack = self.symbol_stack[:-2]

    def process_cond(self, generative, logger):
        if generative == 'COND -> if CONDITION then M_COND STATEMENT':
            ret = self.symbol_stack[-1]
            logger.commands[int(ret[2]) - 1].num = logger.total_line
            self.symbol_stack = self.symbol_stack[:-4]
        elif generative == 'M_COND -> ^':
            logger.insert('JPC', 0, logger.total_line + 2)
            logger.insert('JMP', 0, -1)

            self.symbol_stack.append(['NUMBER', 'JMP', str(logger.total_line)])
        elif generative == 'CONDITION -> EXPR REL EXPR':
            if self.symbol_stack[-2][0] == 'EQUAL':
                logger.insert('OPR', 0, 8)
            elif self.symbol_stack[-2][0] == 'NEQUAL':
                logger.insert('OPR', 0, 9)
            elif self.symbol_stack[-2][0] == 'LESS':
                logger.insert('OPR', 0, 10)
            elif self.symbol_stack[-2][0] == 'LESS_OR_EQUAL':
                logger.insert('OPR', 0, 13)
            elif self.symbol_stack[-2][0] == 'GREATER':
                logger.insert('OPR', 0, 12)
            elif self.symbol_stack[-2][0] == 'GREATER_OR_EQUAL':
                logger.insert('OPR', 0, 11)
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'CONDITION -> odd EXPR':
            logger.insert('OPR', 0, 6)
            self.symbol_stack = self.symbol_stack[:-1]

    def process_while(self, generative, logger):
        if generative == 'WHILE -> while M_WHILE_FORE CONDITION do M_WHILE_TAIL STATEMENT':
            logger.insert('JMP', 0, self.symbol_stack[-4][2])
            logger.commands[int(self.symbol_stack[-1][2]) - 1].num = logger.total_line
            self.symbol_stack = self.symbol_stack[:-5]
        elif generative == 'M_WHILE_FORE -> ^':
            self.symbol_stack.append(['NUMBER', 'while_head', str(logger.total_line)])
        elif generative == 'M_WHILE_TAIL -> ^':
            logger.insert('JPC', 0, logger.total_line + 2)
            logger.insert('JMP', 0, -1)
            self.symbol_stack.append(['NUMBER', 'while_tail JMP', str(logger.total_line)])

    def process_generative(self, generative, token, logger):
        if generative in [
            'CONST -> CONST_ ;',
            'CONST_ -> const CONST_DEF',
            'CONST_ -> CONST_ , CONST_DEF',
            'CONST_DEF -> ID = UINT'
        ]:
            self.process_const(generative)

        elif generative in [
            'VARIABLE -> VARIABLE_ ;',
            'VARIABLE -> ^',
            'VARIABLE_ -> var ID',
            'VARIABLE_ -> VARIABLE_ , ID'
        ]:
            self.process_var(generative)

        elif generative in [
            'PROCEDURE -> PROCEDURE_',
            'PROCEDURE -> ^',
            'PROCEDURE_ -> PROCEDURE_ PROC_HEAD SUBPROG ;',
            'PROCEDURE_ -> PROC_HEAD SUBPROG ;',
            'PROC_HEAD -> procedure ID ;'
        ]:
            self.process_procedure(generative)

        elif generative in [
            'SUBPROG -> CONST VARIABLE PROCEDURE M_STATEMENT STATEMENT'
        ]:
            if self.procedure.current_procedure.father != "":
                self.procedure.current_procedure = self.procedure.procedure_dict[
                    self.procedure.current_procedure.father]
            logger.insert('OPR', 0, 0)

        elif generative in [
            'ASSIGN -> ID := EXPR'
        ]:
            self.process_assign(generative, logger)

        elif generative in [
            'COMP -> COMP_BEGIN end',
            'COMP_BEGIN -> begin STATEMENT',
            'COMP_BEGIN -> COMP_BEGIN ; STATEMENT'
        ]:
            self.process_comp(generative)

        elif generative in [
            'FACTOR -> ID',
            'FACTOR -> UINT',
            'FACTOR -> ( EXPR )'
        ]:
            self.process_factor(generative, logger)

        elif generative in [
            'ITEM -> FACTOR',
            'ITEM -> ITEM MUL_DIV FACTOR'
        ]:
            self.process_item(generative, logger)

        elif generative in [
            'EXPR -> PLUS_MINUS ITEM',
            'EXPR -> EXPR PLUS_MINUS ITEM',
            'EXPR -> ITEM'
        ]:
            self.process_expr(generative, logger)

        elif generative in ['CALL -> call ID']:
            self.process_call(generative, logger)

        elif generative in [
            'READ -> READ_BEGIN )',
            'READ_BEGIN -> read ( ID',
            'READ_BEGIN -> READ_BEGIN , ID'
        ]:
            self.process_read(generative, logger)

        elif generative in [
            'WRITE -> WRITE_BEGIN )',
            'WRITE_BEGIN -> write ( ID',
            'WRITE_BEGIN -> WRITE_BEGIN , ID'
        ]:
            self.process_write(generative, logger)

        elif generative in [
            'COND -> if CONDITION then M_COND STATEMENT',
            'M_COND -> ^',
            'CONDITION -> EXPR REL EXPR',
            'CONDITION -> odd EXPR'
        ]:
            self.process_cond(generative, logger)

        elif generative in [
            'WHILE -> while M_WHILE_FORE CONDITION do M_WHILE_TAIL STATEMENT',
            'M_WHILE_FORE -> ^',
            'M_WHILE_TAIL -> ^'
        ]:
            self.process_while(generative, logger)

        elif generative in [
            'M_STATEMENT -> ^'
        ]:
            # 基准的 base_offset == 3，因为至少需要有2个空间来完成临时变量的计算，至少还要一个空间来保存返回地址
            volume = self.procedure.current_procedure.base_offset + len(self.procedure.current_procedure.var_dict)
            self.procedure.current_procedure.address = logger.total_line
            logger.insert('INI', 0, volume)

    # param:  待入栈的符号，需要和状态栈栈顶以及lr1_table确定下一步的动作
    # token_: 下一个待分析的词法单元的token
    def process_token(self, param, token_, logger_):
        cmd = str(self.parse_table[self.state_stack[-1]][param])
        if cmd == 'acc':
            print("\033[1;32m", "SYNTAX ACCEPTED!", "\033[0m")
            return True
        if not cmd:
            print("\033[0;31m", "ERROR:  ", token_, "  ", cmd, "\033[0m")
            exit(-1)
        # 移入
        elif cmd[0] == 's':
            self.state_stack.append(int(cmd[1:]))
            self.readable_stack.append(param)
            self.symbol_stack.append(token_)
        # 规约
        elif cmd[0] == 'r':
            # generative_left / right
            gl = self.lr1_table.G_indexed[int(cmd[1:])][0]
            gr = self.lr1_table.G_indexed[int(cmd[1:])][1]
            # 所用产生式
            generative = gl + " -> " + " ".join(gr)
            self.process_generative(generative, token_, logger_)
            if gr[0] != '^':
                # 状态栈栈顶出栈
                self.state_stack = self.state_stack[0:len(self.state_stack) - len(gr)]
                # 符号栈栈顶出栈
                self.readable_stack = self.readable_stack[0:len(self.readable_stack) - len(gr)]
            # gr出栈后，待入栈的符号为gl
            self.process_token(gl, token_, logger_)
            # 规约完后，param还没有得到处理，需要继续处理param
            self.process_token(param, token_, logger_)
        # goto
        else:
            self.state_stack.append(int(cmd))
            self.readable_stack.append(token_[1])
