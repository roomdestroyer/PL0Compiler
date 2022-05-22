from utils import call_init_offset


# 记录过程信息，包括过程名，父过程名，过程所含变量表，所含常量表，过程嵌套深度
class ProcedureInfo:
    def __init__(self, name: str, level: int):
        self.father = ""
        self.name = name
        self.const_dict = dict()
        self.var_dict = dict()
        self.base_offset = call_init_offset
        self.var_offset_counter = self.base_offset
        self.level = level
        self.address = -1

    def add_const(self, name: str, value: int):
        if name in self.const_dict:
            print("Error: redefinition in procedure " + self.name + ' of const ' + name)
            exit(-1)
        self.const_dict[name] = value

    def add_var(self, name: str):
        if name in self.var_dict:
            print("Error: redefinition in procedure " + self.name + ' of var ' + name)
            exit(-1)
        self.var_dict[name] = (0, self.var_offset_counter)
        self.var_offset_counter += 1

    def __str__(self):
        return str(dict({
            'father': self.father,
            'name': self.name,
            'const_dict': self.const_dict,
            'var_dict': self.var_dict,
            'level': self.level
        }))

    def __repr__(self):
        return self.__str__()


class Procedure:
    def __init__(self):
        self.procedure_dict = dict()
        self.current_procedure = ProcedureInfo("", 0)

    # 添加一个过程，构造新过程对象，切换过程上下文
    def add_procedure(self, procedure_name: str, level: int):
        father = self.current_procedure.name
        self.procedure_dict[procedure_name] = ProcedureInfo(procedure_name, level)
        self.current_procedure = self.procedure_dict[procedure_name]
        self.current_procedure.father = father

    # 当前过程新增const数据
    def add_const(self, name: str, value: int):
        self.current_procedure.add_const(name, value)

    # 当前过程新增var数据
    def add_var(self, name: str):
        self.current_procedure.add_var(name)

    # 按照父亲边寻找var或const, 找到var记为1, 找到const记为0
    # level差 (value, offset) 1/0
    def find_by_name(self, key: str) -> (int, (int, int), int):
        target_procedure = self.current_procedure
        while True:
            if key in target_procedure.var_dict:
                return [self.current_procedure.level - target_procedure.level, target_procedure.var_dict[key], 1]
            if key in target_procedure.const_dict:
                return [self.current_procedure.level - target_procedure.level, target_procedure.const_dict[key], 0]
            if target_procedure.father == "":
                return None
            else:
                target_procedure = self.procedure_dict[target_procedure.father]

    def __repr__(self):
        return str(dict({
            'procedure_dict': self.procedure_dict,
            'current_procedure': self.current_procedure
        }))

    def __str__(self):
        return self.__repr__()
