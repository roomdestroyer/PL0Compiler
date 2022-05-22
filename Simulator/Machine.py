class StackEntry:
    def __init__(self, num: int, hint: str):
        self.value = num
        self.hint = hint


class Machine:
    def __init__(self, code_: [str]):

        self.codes = [(x.split(" ")[0],
                       int(x.split(" ")[1]),
                       int(x.split(" ")[2])) for x in code_]
        self.stack = []
        self.init_counter = []
        self.pc = 0
        self.base_register = 0

    def step(self):
        # 取指
        cmd = self.codes[self.pc]
        self.pc += 1
        # 跳转
        if cmd[0] == 'JMP':
            self.pc = cmd[2]
        elif cmd[0] == 'LOD':
            tmp_base = self.base_register
            for i in range(cmd[1]):
                tmp_base = self.stack[tmp_base].value
            self.stack.append(StackEntry(self.stack[tmp_base + cmd[2]].value, 'LOD'))
        elif cmd[0] == 'STO':
            # store to, 当前栈顶是数字, 需要把栈顶的字面值赋给sto指令给出的变量地址
            # ret[0]是变量的嵌套深度, ret[1][1]是offset
            # 从第0层开始找, 直到找到目标level的入口
            tmp_base = self.base_register
            for i in range(cmd[1]):
                tmp_base = self.stack[tmp_base].value
            # 到达目标level后, 根据offset去找变量的地址, 把右值赋给左值
            self.stack[tmp_base + cmd[2]] = self.stack[-1]
            self.stack[tmp_base + cmd[2]].hint = 'STO'
            # pop掉栈顶的右值, 只保存变量的地址
            self.stack = self.stack[:-1]
        elif cmd[0] == 'LIT':
            self.stack.append(StackEntry(cmd[2], 'LIT'))
        elif cmd[0] == 'JPC':
            # JMP condition
            if self.stack[-1].value == 0:
                self.pc = cmd[2]
            self.stack.pop()
        elif cmd[0] == 'CALL':
            tmp_base = self.base_register
            for i in range(cmd[1]):
                tmp_base = self.stack[tmp_base].value
            # 静态链，指向定义该过程的直接外过程运行时数据段的基地址
            self.stack.append(StackEntry(tmp_base, 'SL'))
            # 动态链，指向调用该过程前正在运行过程的数据段的基地址B
            self.stack.append(StackEntry(self.base_register, 'DL'))
            # 返回地址，记录调用该过程时目标程序的断点
            self.stack.append(StackEntry(self.pc, 'RA'))
            # 返回地址表入口地址
            self.base_register = len(self.stack) - 3
            self.pc = cmd[2]

        elif cmd[0] == 'INI':
            for i in range(cmd[2]):
                self.stack.append(StackEntry(0, 'INI'))
            self.init_counter.append(cmd[2])
        elif cmd[0] == 'OPR' and cmd[2] == 0:
            # 过程结束的标识符
            if self.base_register == 0 and self.stack[self.base_register].value == 0:
                print("\033[1;32m", "MACHINE DONE SUCCESSFULLY!", "\033[0m", "\n")
                exit(0)
            self.pc = self.stack[self.base_register + 2].value
            self.base_register = self.stack[self.base_register + 1].value
            self.stack = self.stack[:-self.init_counter[-1]]
            self.init_counter.pop()
            self.stack = self.stack[:-3]

        elif cmd[0] == 'OPR' and cmd[2] == 1:  # contrary
            self.stack[-1].value = -self.stack[-1].value
        elif cmd[0] == 'OPR' and cmd[2] == 2:  # +
            self.stack[-2].value = self.stack[-2].value + self.stack[-1].value
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 3:  # -
            self.stack[-2].value = self.stack[-2].value - self.stack[-1].value
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 4:  # *
            self.stack[-2].value = self.stack[-2].value * self.stack[-1].value
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 5:  # /
            self.stack[-2].value = self.stack[-2].value // self.stack[-1].value
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 6:  # odd
            self.stack[-1].value = self.stack[-1].value % 2
            self.stack[-1].value = 1 - self.stack[-1].value
        elif cmd[0] == 'OPR' and cmd[2] == 8:  # eq
            self.stack[-2].value = self.stack[-2].value - self.stack[-1].value
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 9:  # neq
            self.stack[-2].value = self.stack[-2].value - self.stack[-1].value
            if self.stack[-2].value != 0:
                self.stack[-2].value = 0
            elif self.stack[-2].value == 0:
                self.stack[-2].value = 1
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 10:  # less than
            self.stack[-2].value = self.stack[-2].value - self.stack[-1].value
            if self.stack[-2].value < 0:
                self.stack[-2].value = 0
            else:
                self.stack[-2].value = 1
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 11:  # greater than or qe
            self.stack[-2].value = - self.stack[-2].value + self.stack[-1].value
            if self.stack[-2].value <= 0:
                self.stack[-2].value = 0
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 12:  # greater than
            self.stack[-2].value = - self.stack[-2].value + self.stack[-1].value
            if self.stack[-2].value < 0:
                self.stack[-2].value = 0
            else:
                self.stack[-2].value = 1
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 13:  # less than or qe
            self.stack[-2].value = self.stack[-2].value - self.stack[-1].value
            if self.stack[-2].value <= 0:
                self.stack[-2].value = 0
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 14:  # write
            print(self.stack[-1].value)
            self.stack.pop()
        elif cmd[0] == 'OPR' and cmd[2] == 16:  # read
            print('read:  ', end='')
            x = int(input())
            self.stack.append(StackEntry(x, 'READ'))
        return True

    def run(self):
        while True:
            _r = self.step()
