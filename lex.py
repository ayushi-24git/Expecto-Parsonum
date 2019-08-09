from __future__ import print_function
import sys, shlex, operator,struct
 
tk_EOI, tk_Mul, tk_Div, tk_Mod, tk_Add, tk_Sub, tk_Negate, tk_Not, tk_Lss, tk_Leq, tk_Gtr, \
tk_Geq, tk_Eq, tk_Neq, tk_Assign, tk_And, tk_Or, tk_If, tk_Else, tk_While, tk_Print,       \
tk_Putc, tk_Lparen, tk_Rparen, tk_Lbrace, tk_Rbrace, tk_Semi, tk_Comma, tk_Ident,          \
tk_Integer, tk_String = range(31)
 
all_syms = ["End_of_input", "Op_multiply", "Op_divide", "Op_mod", "Op_add", "Op_subtract",
    "Op_negate", "Op_not", "Op_less", "Op_lessequal", "Op_greater", "Op_greaterequal",
    "Op_equal", "Op_notequal", "Op_assign", "Op_and", "Op_or", "Keyword_if",
    "Keyword_else", "Keyword_while", "Keyword_print", "Keyword_putc", "LeftParen",
    "RightParen", "LeftBrace", "RightBrace", "Semicolon", "Comma", "Identifier",
    "Integer", "String"]
 
# single character only symbols
symbols = { '{': tk_Lbrace, '}': tk_Rbrace, '(': tk_Lparen, ')': tk_Rparen, '+': tk_Add, '-': tk_Sub,
    '*': tk_Mul, '%': tk_Mod, ';': tk_Semi, ',': tk_Comma }
 
key_words = {'if': tk_If, 'else': tk_Else, 'print': tk_Print, 'putc': tk_Putc, 'while': tk_While}
 
the_ch = " "    # dummy first char - but it must be a space
the_col = 0
the_line = 1
input_file = None
 
#*** show error and exit
def error(line, col, msg):
    print(line, col, msg)
    exit(1)
 
#*** get the next character from the input
def next_ch():
    global the_ch, the_col, the_line
 
    the_ch = input_file.read(1)
    the_col += 1
    if the_ch == '\n':
        the_line += 1
        the_col = 0
    return the_ch
 
#*** 'x' - character constants
def char_lit(err_line, err_col):
    n = ord(next_ch())              # skip opening quote
    if the_ch == '\'':
        error(err_line, err_col, "empty character constant")
    elif the_ch == '\\':
        next_ch()
        if the_ch == 'n':
            n = 10
        elif the_ch == '\\':
            n = ord('\\')
        else:
            error(err_line, err_col, "unknown escape sequence \\%c" % (the_ch))
    if next_ch() != '\'':
        error(err_line, err_col, "multi-character constant")
    next_ch()
    return tk_Integer, err_line, err_col, n
 
#*** process divide or comments
def div_or_cmt(err_line, err_col):
    if next_ch() != '*':
        return tk_Div, err_line, err_col
 
    # comment found
    next_ch()
    while True:
        if the_ch == '*':
            if next_ch() == '/':
                next_ch()
                return gettok()
        elif len(the_ch) == 0:
            error(err_line, err_col, "EOF in comment")
        else:
            next_ch()
 
#*** "string"
def string_lit(start, err_line, err_col):
    text = ""
 
    while next_ch() != start:
        if len(the_ch) == 0:
            error(err_line, err_col, "EOF while scanning string literal")
        if the_ch == '\n':
            error(err_line, err_col, "EOL while scanning string literal")
        text += the_ch
 
    next_ch()
    return tk_String, err_line, err_col, text
 
#*** handle identifiers and integers
def ident_or_int(err_line, err_col):
    is_number = True
    text = ""
 
    while the_ch.isalnum() or the_ch == '_':
        text += the_ch
        if not the_ch.isdigit():
            is_number = False
        next_ch()
 
    if len(text) == 0:
        error(err_line, err_col, "ident_or_int: unrecognized character: (%d) '%c'" % (ord(the_ch), the_ch))
 
    if text[0].isdigit():
        if not is_number:
            error(err_line, err_col, "invalid number: %s" % (text))
        n = int(text)
        return tk_Integer, err_line, err_col, n
 
    if text in key_words:
        return key_words[text], err_line, err_col
 
    return tk_Ident, err_line, err_col, text
 
#*** look ahead for '>=', etc.
def follow(expect, ifyes, ifno, err_line, err_col):
    if next_ch() == expect:
        next_ch()
        return ifyes, err_line, err_col
 
    if ifno == tk_EOI:
        error(err_line, err_col, "follow: unrecognized character: (%d) '%c'" % (ord(the_ch), the_ch))
 
    return ifno, err_line, err_col
 
#*** return the next token type
def gettok():
    while the_ch.isspace():
        next_ch()
 
    err_line = the_line
    err_col  = the_col
 
    if len(the_ch) == 0:    return tk_EOI, err_line, err_col
    elif the_ch == '/':     return div_or_cmt(err_line, err_col)
    elif the_ch == '\'':    return char_lit(err_line, err_col)
    elif the_ch == '<':     return follow('=', tk_Leq, tk_Lss,    err_line, err_col)
    elif the_ch == '>':     return follow('=', tk_Geq, tk_Gtr,    err_line, err_col)
    elif the_ch == '=':     return follow('=', tk_Eq,  tk_Assign, err_line, err_col)
    elif the_ch == '!':     return follow('=', tk_Neq, tk_Not,    err_line, err_col)
    elif the_ch == '&':     return follow('&', tk_And, tk_EOI,    err_line, err_col)
    elif the_ch == '|':     return follow('|', tk_Or,  tk_EOI,    err_line, err_col)
    elif the_ch == '"':     return string_lit(the_ch, err_line, err_col)
    elif the_ch in symbols:
        sym = symbols[the_ch]
        next_ch()
        return sym, err_line, err_col
    else: return ident_or_int(err_line, err_col)


 
tk_EOI, tk_Mul, tk_Div, tk_Mod, tk_Add, tk_Sub, tk_Negate, tk_Not, tk_Lss, tk_Leq, tk_Gtr, \
tk_Geq, tk_Eql, tk_Neq, tk_Assign, tk_And, tk_Or, tk_If, tk_Else, tk_While, tk_Print,      \
tk_Putc, tk_Lparen, tk_Rparen, tk_Lbrace, tk_Rbrace, tk_Semi, tk_Comma, tk_Ident,          \
tk_Integer, tk_String = range(31)
 
nd_Ident, nd_String, nd_Integer, nd_Sequence, nd_If, nd_Prtc, nd_Prts, nd_Prti, nd_While, \
nd_Assign, nd_Negate, nd_Not, nd_Mul, nd_Div, nd_Mod, nd_Add, nd_Sub, nd_Lss, nd_Leq,     \
nd_Gtr, nd_Geq, nd_Eql, nd_Neq, nd_And, nd_Or = range(25)
 
# must have same order as above
Tokens = [
    ["EOI"             , False, False, False, -1, -1        ],
    ["*"               , False, True,  False, 13, nd_Mul    ],
    ["/"               , False, True,  False, 13, nd_Div    ],
    ["%"               , False, True,  False, 13, nd_Mod    ],
    ["+"               , False, True,  False, 12, nd_Add    ],
    ["-"               , False, True,  False, 12, nd_Sub    ],
    ["-"               , False, False, True,  14, nd_Negate ],
    ["!"               , False, False, True,  14, nd_Not    ],
    ["<"               , False, True,  False, 10, nd_Lss    ],
    ["<="              , False, True,  False, 10, nd_Leq    ],
    [">"               , False, True,  False, 10, nd_Gtr    ],
    [">="              , False, True,  False, 10, nd_Geq    ],
    ["=="              , False, True,  False,  9, nd_Eql    ],
    ["!="              , False, True,  False,  9, nd_Neq    ],
    ["="               , False, False, False, -1, nd_Assign ],
    ["&&"              , False, True,  False,  5, nd_And    ],
    ["||"              , False, True,  False,  4, nd_Or     ],
    ["if"              , False, False, False, -1, nd_If     ],
    ["else"            , False, False, False, -1, -1        ],
    ["while"           , False, False, False, -1, nd_While  ],
    ["print"           , False, False, False, -1, -1        ],
    ["putc"            , False, False, False, -1, -1        ],
    ["("               , False, False, False, -1, -1        ],
    [")"               , False, False, False, -1, -1        ],
    ["{"               , False, False, False, -1, -1        ],
    ["}"               , False, False, False, -1, -1        ],
    [";"               , False, False, False, -1, -1        ],
    [","               , False, False, False, -1, -1        ],
    ["Ident"           , False, False, False, -1, nd_Ident  ],
    ["Integer literal" , False, False, False, -1, nd_Integer],
    ["String literal"  , False, False, False, -1, nd_String ]
    ]
 
all_syms_parser = {"End_of_input"   : tk_EOI,     "Op_multiply"    : tk_Mul,
            "Op_divide"      : tk_Div,     "Op_mod"         : tk_Mod,
            "Op_add"         : tk_Add,     "Op_subtract"    : tk_Sub,
            "Op_negate"      : tk_Negate,  "Op_not"         : tk_Not,
            "Op_less"        : tk_Lss,     "Op_lessequal"   : tk_Leq,
            "Op_greater"     : tk_Gtr,     "Op_greaterequal": tk_Geq,
            "Op_equal"       : tk_Eql,     "Op_notequal"    : tk_Neq,
            "Op_assign"      : tk_Assign,  "Op_and"         : tk_And,
            "Op_or"          : tk_Or,      "Keyword_if"     : tk_If,
            "Keyword_else"   : tk_Else,    "Keyword_while"  : tk_While,
            "Keyword_print"  : tk_Print,   "Keyword_putc"   : tk_Putc,
            "LeftParen"      : tk_Lparen,  "RightParen"     : tk_Rparen,
            "LeftBrace"      : tk_Lbrace,  "RightBrace"     : tk_Rbrace,
            "Semicolon"      : tk_Semi,    "Comma"          : tk_Comma,
            "Identifier"     : tk_Ident,   "Integer"        : tk_Integer,
            "String"         : tk_String}
 
Display_nodes = ["Identifier", "String", "Integer", "Sequence", "If", "Prtc", "Prts",
    "Prti", "While", "Assign", "Negate", "Not", "Multiply", "Divide", "Mod", "Add",
    "Subtract", "Less", "LessEqual", "Greater", "GreaterEqual", "Equal", "NotEqual",
    "And", "Or"]
 
TK_NAME         = 0
TK_RIGHT_ASSOC  = 1
TK_IS_BINARY    = 2
TK_IS_UNARY     = 3
TK_PRECEDENCE   = 4
TK_NODE         = 5
 
input_file = None
err_line   = None
err_col    = None
tok        = None
tok_text   = None
 
#*** show error and exit
def error(msg):
    print("(%d, %d) %s" % (int(err_line), int(err_col), msg))
    exit(1)
 
#***
def gettok_parser():
    global err_line, err_col, tok, tok_text, tok_other
    line = input_file.readline()
    if len(line) == 0:
        error("empty line")
 
    line_list = shlex.split(line, False, False)
    # line col Ident var_name
    # 0    1   2     3
 
    err_line = line_list[0]
    err_col  = line_list[1]
    tok_text = line_list[2]
 
    tok = all_syms_parser.get(tok_text)
    if tok == None:
        error("Unknown token %s" % (tok_text))
 
    tok_other = None
    if tok in [tk_Integer, tk_Ident, tk_String]:
        tok_other = line_list[3]
 
class Node:
    def __init__(self, node_type, left = None, right = None, value = None):
        self.node_type  = node_type
        self.left  = left
        self.right = right
        self.value = value
 
#***
def make_node(oper, left, right = None):
    return Node(oper, left, right)
 
#***
def make_leaf(oper, n):
    return Node(oper, value = n)
 
#***
def expect(msg, s):
    if tok == s:
        gettok_parser()
        return
    error("%s: Expecting '%s', found '%s'" % (msg, Tokens[s][TK_NAME], Tokens[tok][TK_NAME]))
 
#***
def expr(p):
    x = None
 
    if tok == tk_Lparen:
        x = paren_expr()
    elif tok in [tk_Sub, tk_Add]:
        op = (tk_Negate if tok == tk_Sub else tk_Add)
        gettok_parser()
        node = expr(Tokens[tk_Negate][TK_PRECEDENCE])
        x = (make_node(nd_Negate, node) if op == tk_Negate else node)
    elif tok == tk_Not:
        gettok_parser()
        x = make_node(nd_Not, expr(Tokens[tk_Not][TK_PRECEDENCE]))
    elif tok == tk_Ident:
        x = make_leaf(nd_Ident, tok_other)
        gettok_parser()
    elif tok == tk_Integer:
        x = make_leaf(nd_Integer, tok_other)
        gettok_parser()
    else:
        error("Expecting a primary, found: %s" % (Tokens[tok][TK_NAME]))
 
    while Tokens[tok][TK_IS_BINARY] and Tokens[tok][TK_PRECEDENCE] >= p:
        op = tok
        gettok_parser()
        q = Tokens[op][TK_PRECEDENCE]
        if not Tokens[op][TK_RIGHT_ASSOC]:
            q += 1
 
        node = expr(q)
        x = make_node(Tokens[op][TK_NODE], x, node)
 
    return x
 
#***
def paren_expr():
    expect("paren_expr", tk_Lparen)
    node = expr(0)
    expect("paren_expr", tk_Rparen)
    return node
 
#***
def stmt():
    t = None
 
    if tok == tk_If:
        gettok_parser()
        e = paren_expr()
        s = stmt()
        s2 = None
        if tok == tk_Else:
            gettok_parser()
            s2 = stmt()
        t = make_node(nd_If, e, make_node(nd_If, s, s2))
    elif tok == tk_Putc:
        gettok_parser()
        e = paren_expr()
        t = make_node(nd_Prtc, e)
        expect("Putc", tk_Semi)
    elif tok == tk_Print:
        gettok_parser()
        expect("Print", tk_Lparen)
        while True:
            if tok == tk_String:
                e = make_node(nd_Prts, make_leaf(nd_String, tok_other))
                gettok_parser()
            else:
                e = make_node(nd_Prti, expr(0))
 
            t = make_node(nd_Sequence, t, e)
            if tok != tk_Comma:
                break
            gettok_parser()
        expect("Print", tk_Rparen)
        expect("Print", tk_Semi)
    elif tok == tk_Semi:
        gettok_parser()
    elif tok == tk_Ident:
        v = make_leaf(nd_Ident, tok_other)
        gettok_parser()
        expect("assign", tk_Assign)
        e = expr(0)
        t = make_node(nd_Assign, v, e)
        expect("assign", tk_Semi)
    elif tok == tk_While:
        gettok_parser()
        e = paren_expr()
        s = stmt()
        t = make_node(nd_While, e, s)
    elif tok == tk_Lbrace:
        gettok_parser()
        while tok != tk_Rbrace and tok != tk_EOI:
            t = make_node(nd_Sequence, t, stmt())
        expect("Lbrace", tk_Rbrace)
    elif tok == tk_EOI:
        pass
    else:
        error("Expecting start of statement, found: %s" % (Tokens[tok][TK_NAME]))
 
    return t
 
#***
def parse():
    t = None
    gettok_parser()
    while True:
        t = make_node(nd_Sequence, t, stmt())
        if tok == tk_EOI or t == None:
            break
    return t
 
def prt_ast(t):
    
    if t == None:
        parse_output.write(";\n")
        #print(";")
    else:
        parse_output.write("%-14s" % (Display_nodes[t.node_type]))
        #print("%-14s" % (Display_nodes[t.node_type]), end='')
        if t.node_type in [nd_Ident, nd_Integer]:
            parse_output.write("%s\n" % (t.value))            
            #print("%s" % (t.value))
        elif t.node_type == nd_String:
            parse_output.write("%s\n" % (t.value))	    
            #print("%s" %(t.value))
        else:
            parse_output.write("\n")	    
            #print("")
            prt_ast(t.left)
            prt_ast(t.right)
nd_Ident, nd_String, nd_Integer, nd_Sequence, nd_If, nd_Prtc, nd_Prts, nd_Prti, nd_While, \
nd_Assign, nd_Negate, nd_Not, nd_Mul, nd_Div, nd_Mod, nd_Add, nd_Sub, nd_Lss, nd_Leq,     \
nd_Gtr, nd_Geq, nd_Eql, nd_Neq, nd_And, nd_Or = range(25)
 
all_syms_codegen = {
    "Identifier"  : nd_Ident,    "String"      : nd_String,
    "Integer"     : nd_Integer,  "Sequence"    : nd_Sequence,
    "If"          : nd_If,       "Prtc"        : nd_Prtc,
    "Prts"        : nd_Prts,     "Prti"        : nd_Prti,
    "While"       : nd_While,    "Assign"      : nd_Assign,
    "Negate"      : nd_Negate,   "Not"         : nd_Not,
    "Multiply"    : nd_Mul,      "Divide"      : nd_Div,
    "Mod"         : nd_Mod,      "Add"         : nd_Add,
    "Subtract"    : nd_Sub,      "Less"        : nd_Lss,
    "LessEqual"   : nd_Leq,      "Greater"     : nd_Gtr,
    "GreaterEqual": nd_Geq,      "Equal"       : nd_Eql,
    "NotEqual"    : nd_Neq,      "And"         : nd_And,
    "Or"          : nd_Or}
 
FETCH, STORE, PUSH, ADD, SUB, MUL, DIV, MOD, LT, GT, LE, GE, EQ, NE, AND, OR, NEG, NOT, \
JMP, JZ, PRTC, PRTS, PRTI, HALT = range(24)
 
operators = {nd_Lss: LT, nd_Gtr: GT, nd_Leq: LE, nd_Geq: GE, nd_Eql: EQ, nd_Neq: NE,
    nd_And: AND, nd_Or: OR, nd_Sub: SUB, nd_Add: ADD, nd_Div: DIV, nd_Mul: MUL, nd_Mod: MOD}
 
unary_operators = {nd_Negate: NEG, nd_Not: NOT}
 
input_file  = None
code        = bytearray()
string_pool = {}
globals     = {}
string_n    = 0
globals_n   = 0
word_size   = 4
 
#*** show error and exit
def error(msg):
    print("%s" % (msg))
    exit(1)
 
def int_to_bytes(val):
    return struct.pack("<i", val)
 
def bytes_to_int(bstr):
    return struct.unpack("<i", bstr)
 
class Node:
    def __init__(self, node_type, left = None, right = None, value = None):
        self.node_type  = node_type
        self.left  = left
        self.right = right
        self.value = value
 
#***
def make_node(oper, left, right = None):
    return Node(oper, left, right)
 
#***
def make_leaf(oper, n):
    return Node(oper, value = n)
 
#***
def emit_byte(x):
    code.append(x)
 
#***
def emit_word(x):
    s = int_to_bytes(x)
    for x in s:
        code.append(x)
 
def emit_word_at(at, n):
    code[at:at+word_size] = int_to_bytes(n)
 
def hole():
    t = len(code)
    emit_word(0)
    return t
 
#***
def fetch_var_offset(name):
    global globals_n
 
    n = globals.get(name, None)
    if n == None:
        globals[name] = globals_n
        n = globals_n
        globals_n += 1
    return n
 
#***
def fetch_string_offset(the_string):
    global string_n
 
    n = string_pool.get(the_string, None)
    if n == None:
        string_pool[the_string] = string_n
        n = string_n
        string_n += 1
    return n
 
#***
def code_gen(x):
    if x == None: return
    elif x.node_type == nd_Ident:
        emit_byte(FETCH)
        n = fetch_var_offset(x.value)
        emit_word(n)
    elif x.node_type == nd_Integer:
        emit_byte(PUSH)
        emit_word(x.value)
    elif x.node_type == nd_String:
        emit_byte(PUSH)
        n = fetch_string_offset(x.value)
        emit_word(n)
    elif x.node_type == nd_Assign:
        n = fetch_var_offset(x.left.value)
        code_gen(x.right)
        emit_byte(STORE)
        emit_word(n)
    elif x.node_type == nd_If:
        code_gen(x.left)              # expr
        emit_byte(JZ)                 # if false, jump
        p1 = hole()                   # make room for jump dest
        code_gen(x.right.left)        # if true statements
        if (x.right.right != None):
            emit_byte(JMP)            # jump over else statements
            p2 = hole()
        emit_word_at(p1, len(code) - p1)
        if (x.right.right != None):
            code_gen(x.right.right)   # else statements
            emit_word_at(p2, len(code) - p2)
    elif x.node_type == nd_While:
        p1 = len(code)
        code_gen(x.left)
        emit_byte(JZ)
        p2 = hole()
        code_gen(x.right)
        emit_byte(JMP)                       # jump back to the top
        emit_word(p1 - len(code))
        emit_word_at(p2, len(code) - p2)
    elif x.node_type == nd_Sequence:
        code_gen(x.left)
        code_gen(x.right)
    elif x.node_type == nd_Prtc:
        code_gen(x.left)
        emit_byte(PRTC)
    elif x.node_type == nd_Prti:
        code_gen(x.left)
        emit_byte(PRTI)
    elif x.node_type == nd_Prts:
        code_gen(x.left)
        emit_byte(PRTS)
    elif x.node_type in operators:
        code_gen(x.left)
        code_gen(x.right)
        emit_byte(operators[x.node_type])
    elif x.node_type in unary_operators:
        code_gen(x.left)
        emit_byte(unary_operators[x.node_type])
    else:
        error("error in code generator - found %d, expecting operator" % (x.node_type))
 
#***
def code_finish():
    emit_byte(HALT)
 
#***
def list_code():
    #print("Datasize: %d Strings: %d" % (len(globals), len(string_pool)))
 
    #for k in sorted(string_pool, key=string_pool.get):
        #print(k)
 
    pc = 0
    while pc < len(code):
        print("%4d " % (pc), end='')
        op = code[pc]
        pc += 1
        if op == FETCH:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            print("fetch [%d]" % (x));
            pc += word_size
        elif op == STORE:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            print("store [%d]" % (x));
            pc += word_size
        elif op == PUSH:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            print("push  %d" % (x));
            pc += word_size
        elif op == ADD:   print("add")
        elif op == SUB:   print("sub")
        elif op == MUL:   print("mul")
        elif op == DIV:   print("div")
        elif op == MOD:   print("mod")
        elif op == LT:    print("lt")
        elif op == GT:    print("gt")
        elif op == LE:    print("le")
        elif op == GE:    print("ge")
        elif op == EQ:    print("eq")
        elif op == NE:    print("ne")
        elif op == AND:   print("and")
        elif op == OR:    print("or")
        elif op == NEG:   print("neg")
        elif op == NOT:   print("not")
        elif op == JMP:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            print("jmp    (%d) %d" % (x, pc + x));
            pc += word_size
        elif op == JZ:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            print("jz     (%d) %d" % (x, pc + x));
            pc += word_size
        elif op == PRTC:  print("prtc")
        elif op == PRTI:  print("prti")
        elif op == PRTS:  print("prts")
        elif op == HALT:  print("halt")
        else: error("list_code: Unknown opcode %d", (op));
 
def load_ast():
    line = input_file.readline()
    line_list = shlex.split(line, False, False)
 
    text = line_list[0]
    if text == ";":
        return None
    node_type = all_syms_codegen[text]
 
    if len(line_list) > 1:
        value = line_list[1]
        if value.isdigit():
            value = int(value)
        return make_leaf(node_type, value)
 
    left = load_ast()
    right = load_ast()
    return make_node(node_type, left, right)

 
#*** main driver lexing phase
input_file = sys.stdin
if len(sys.argv) > 1:
    try:
        input_file = open(sys.argv[1], "r", 4096)
    except IOError as e:
        error(0, 0, "Can't open %s" % sys.argv[1])

lex_output = open("parser_input","a+")
lex_output.truncate(0)
 
while True:
    t = gettok()
    tok  = t[0]
    line = t[1]
    col  = t[2]
    



 
    #print("%5d  %5d   %-14s" % (line, col, all_syms[tok]), end='')
    #lex_output.write("test")
    #a = str(line) + str(col) + str(all_syms[tok])
    
          #lex_output.write("     ")
    b = str(line)
    lex_output.write("%5s" % b)
    c = str(col)
    lex_output.write("%5s" % c)
    d = all_syms[tok]
    lex_output.write(" ")
    lex_output.write("%-14s" % d)
    #print("correct")
    x = "check"
    #lex_output.write("%5s" % x)
    #lex_output.write("%5d  %5d   %-14s" % (line, col, all_syms[tok]), end='')
 
    if tok == tk_Integer:  lex_output.write("   %5d\n" % (t[3]))#print("   %5d" % (t[3]))
    elif tok == tk_Ident:  lex_output.write("  %s\n" %   (t[3]))#print("  %s" %   (t[3]))
    elif tok == tk_String: lex_output.write( "%s\n" % (t[3]))#print('  "%s"' % (t[3]))
    else:                  lex_output.write("\n")#print("")
 
    if tok == tk_EOI:
        break

#print("lex complete")
lex_output.seek(0)
#*** main driver parser
input_file = sys.stdin
if len(sys.argv) > 1:
    try:
        input_file = open("parser_input", "r", 4096)
    except IOError as e:
        error(0, 0, "Can't open %s" % sys.argv[2])
t = parse()
parse_output = open("generator_input","a+")
parse_output.truncate(0) 
prt_ast(t)
parse_output.seek(0)

#*** main driver
input_file = sys.stdin
if len(sys.argv) > 1:
    try:
        input_file = open("generator_input", "r", 4096)
    except IOError as e:
        error("Can't open %s" % sys.argv[3])
 
n = load_ast()
code_gen(n)
code_finish()
list_code()
