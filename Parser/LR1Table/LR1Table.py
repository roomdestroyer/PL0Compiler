from .Grammar import Grammar

end_sign = '#'
dot_sign = '•'

def first_follow(G):
    def union(set_1, set_2):
        set_1_len = len(set_1)
        set_1 |= set_2
        return set_1_len != len(set_1)
    first = {symbol: set() for symbol in G.symbols}
    first.update((terminal, {terminal}) for terminal in G.terminals)  # first terminal 加入
    follow = {symbol: set() for symbol in G.nonterminals}
    follow[G.start].add(end_sign)
    while True:
        updated = False
        for head, bodies in G.grammar.items():
            for body in bodies:
                for symbol in body:
                    if symbol != '^':
                        updated |= union(first[head], first[symbol] - set('^'))
                        if '^' not in first[symbol]:
                            break
                    else:
                        updated |= union(first[head], set('^'))
                else:
                    updated |= union(first[head], set('^'))
                aux = follow[head]
                for symbol in reversed(body):
                    if symbol == '^':
                        continue
                    if symbol in follow:
                        updated |= union(follow[symbol], aux - set('^'))
                    if '^' in first[symbol]:
                        aux = aux | first[symbol]
                    else:
                        aux = first[symbol]
        if not updated:
            return first, follow


class LR1Table:
    def __init__(self, G):
        # 扩展文法
        self.G_prime = Grammar(f"{G.start}' -> {G.start}\n{G.grammar_str}")
        # 开始符号的长度 + 1
        self.max_G_prime_len = len(max(self.G_prime.grammar, key=len))
        self.G_indexed = []

        # 语法规范化，去除 |
        for head, bodies in self.G_prime.grammar.items():
            for body in bodies:
                self.G_indexed.append([head, body])

        # 求 first follow 集合
        self.first, self.follow = first_follow(self.G_prime)

        # 构建项目集规范族
        self.Collection = self.LR1_items(self.G_prime)

        # 构建LR1分析表
        self.action = sorted(list(self.G_prime.terminals)) + [end_sign]
        self.goto = sorted(list(self.G_prime.nonterminals - {self.G_prime.start}))
        self.parse_table_symbols = self.action + self.goto
        self.parse_table = self.LR1_construct_table()
        
        self.print_info()

    def construct_follow(self, s: tuple, extra: str) -> set:
        ret = set()
        flag = True
        for x in s:
            ret = ret | self.first[x]
            if '^' not in self.first[x]:
                flag = False
                break
        ret.discard('^')
        if flag:
            ret = ret | {extra}
        return ret

    def LR1_CLOSURE(self, dict_of_trans: dict) -> dict:
        ret = dict_of_trans
        while True:
            item_len = len(ret)
            for head, bodies in dict_of_trans.copy().items():
                for body in bodies.copy():
                    if dot_sign in body[:-1]:
                        symbol_after_dot = body[body.index(dot_sign) + 1]
                        if symbol_after_dot in self.G_prime.nonterminals:
                            symbol_need_first_loc = body.index(dot_sign) + 2
                            if symbol_need_first_loc == len(body):
                                # A -> ... .B
                                for G_body in self.G_prime.grammar[symbol_after_dot]:
                                    ret.setdefault((symbol_after_dot, head[1]), set()).add(
                                        (dot_sign,) if G_body == ('^',) else (dot_sign,) + G_body
                                    )
                            else:
                                # A -> ... .BC
                                for j in self.construct_follow(body[symbol_need_first_loc:], head[1]):
                                    for G_body in self.G_prime.grammar[symbol_after_dot]:
                                        ret.setdefault((symbol_after_dot, j), set()).add(
                                            (dot_sign,) if G_body == ('^',) else (dot_sign,) + G_body
                                        )
            if item_len == len(ret):
                break
        return ret

    def LR1_GOTO(self, state: dict, c: str) -> dict:
        goto = {}

        for head, bodies in state.items():
            for body in bodies:
                if dot_sign in body[:-1]:
                    dot_pos = body.index(dot_sign)
                    if body[dot_pos + 1] == c:
                        replaced_dot_body = body[:dot_pos] + (c, dot_sign) + body[dot_pos + 2:]
                        for C_head, C_bodies in self.LR1_CLOSURE({head: {replaced_dot_body}}).items():
                            goto.setdefault(C_head, set()).update(C_bodies)

        return goto

    def LR1_items(self, G_prime):
        start_item = {(G_prime.start, end_sign): {(dot_sign, G_prime.start[:-1])}}
        # 求 I0 的闭包
        C = [self.LR1_CLOSURE(start_item)]
        while True:
            item_len = len(C)
            for item in C.copy():

                for X in G_prime.symbols:
                    goto = self.LR1_GOTO(item, X)
                    if goto and goto not in C:
                        C.append(goto)

            if item_len == len(C):
                return C

    def LR1_construct_table(self):
        parse_table = {r: {c: '' for c in self.parse_table_symbols} for r in range(len(self.Collection))}

        for i, I in enumerate(self.Collection):
            for head, bodies in I.items():
                for body in bodies:
                    if dot_sign in body[:-1]:  # CASE 2 a
                        symbol_after_dot = body[body.index(dot_sign) + 1]
                        if symbol_after_dot in self.G_prime.terminals:
                            s = f's{self.Collection.index(self.LR1_GOTO(I, symbol_after_dot))}'

                            if s not in parse_table[i][symbol_after_dot]:
                                if 'r' in parse_table[i][symbol_after_dot]:
                                    parse_table[i][symbol_after_dot] += '/'

                                parse_table[i][symbol_after_dot] += s

                    elif body[-1] == dot_sign and head[0] != self.G_prime.start:  # CASE 2 b
                        for j, (G_head, G_body) in enumerate(self.G_indexed):
                            if G_head == head[0] and (G_body == body[:-1] or G_body == ('^',) and body == (dot_sign,)):
                                if parse_table[i][head[1]]:
                                    exit(-1)
                                    parse_table[i][head[1]] += '/'
                                parse_table[i][head[1]] += f'r{j}'
                                break

                    else:  # CASE 2 c
                        parse_table[i][end_sign] = 'acc'

            for A in self.G_prime.nonterminals:  # CASE 3
                j = self.LR1_GOTO(I, A)

                if j in self.Collection:
                    parse_table[i][A] = self.Collection.index(j)
        return parse_table

    def print_info(self):
        print('AUGMENTED GRAMMAR:')

        for i, (head, body) in enumerate(self.G_indexed):
            print(f'{i:>{len(str(len(self.G_indexed) - 1))}}: {head:>{self.max_G_prime_len}} -> {" ".join(body)}')

        print()
        print('TERMINALS', self.G_prime.terminals)
        print('NONTERMINALS', self.G_prime.nonterminals)
        print('SYMBOLS', self.G_prime.symbols)
        print()

        for i, item in enumerate(self.Collection):
            print("I" + str(i) + ":")
            for key in item:
                left_sign = key[0]
                follow_sign = key[1]
                candidates = item[key]
                for candidate in candidates:
                    print('  ', left_sign, '-> ', end='')
                    for character in candidate:
                        print(character, end='')
                    print(',', follow_sign)
