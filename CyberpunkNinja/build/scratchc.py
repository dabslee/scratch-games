"""
scratchc: a tiny compiler from a Python-syntax DSL to Scratch 3 blocks.

Each sprite's logic is written as Python source and parsed with `ast`.
Top-level functions become Scratch scripts, chosen by decorator:

    @flag                  when green flag clicked
    @on("message")         when I receive [message]
    @clone                 when I start as a clone
    @key("space")          when [space] key pressed
    @proc                  custom block, run without screen refresh
    @proc_yield            custom block that yields (screen refresh)

Statements: assignment (set / change), if / elif / else, `while cond:`
(repeat until not cond), `while True:` (forever), `for _ in range(n):`
(repeat), `for i in range(a, b):` (counter loop), `return` (stop this
script), procedure calls and builtin statement calls (see STMT_BUILTINS).

Lists are 1-based, exactly like Scratch: `L[1]` is the first item.
Names resolve to: procedure parameter, sprite-local variable, global
variable, then compile-time constant. Anything assigned in a sprite that
is not a declared global becomes a sprite-local ("for this sprite only")
variable, which is per-clone in Scratch.
"""
import ast
import json

PRIM = {'num_raw': 4, 'num': 4, 'pos': 5, 'whole': 6, 'int': 7, 'angle': 8, 'text': 10}


class CompileError(Exception):
    pass


_counter = [0]


def new_id(prefix='b'):
    _counter[0] += 1
    n = _counter[0]
    s = ''
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    while True:
        s = alphabet[n % 62] + s
        n //= 62
        if n == 0:
            break
    return prefix + s


def fmt_num(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return repr(v)
    return str(v)


class Val:
    """A compiled expression: literal, variable, list, reporter or boolean."""
    __slots__ = ('kind', 'v', 'name', 'id')

    def __init__(self, kind, v=None, name=None, id=None):
        self.kind = kind  # lit | var | list | rep | bool
        self.v = v
        self.name = name
        self.id = id

    def is_num_lit(self):
        return self.kind == 'lit' and isinstance(self.v, (int, float)) and not isinstance(self.v, bool)


class Project:
    def __init__(self):
        self.gvars = {}      # name -> [id, value]
        self.glists = {}     # name -> [id, items]
        self.broadcasts = {}  # name -> id
        self.targets = []
        self.extensions = []

    def add_global(self, name, value=0):
        if name not in self.gvars:
            self.gvars[name] = [new_id('v'), value]

    def add_global_list(self, name, items=None):
        if name not in self.glists:
            self.glists[name] = [new_id('l'), list(items or [])]
        elif items is not None:
            self.glists[name][1] = list(items)

    def bcast(self, name):
        if name not in self.broadcasts:
            self.broadcasts[name] = new_id('m')
        return self.broadcasts[name]

    def to_json(self):
        targets = []
        for t in self.targets:
            targets.append(t.to_json(self))
        return {
            'targets': targets,
            'monitors': [],
            'extensions': self.extensions,
            'meta': {'semver': '3.0.0', 'vm': '0.2.0', 'agent': 'scratchc (Cyberpunk Ninja build)'},
        }


class Target:
    def __init__(self, project, name, is_stage=False):
        self.project = project
        self.name = name
        self.is_stage = is_stage
        self.vars = {}    # local name -> [id, value]
        self.lists = {}
        self.blocks = {}
        self.procs = {}
        self.costumes = []
        self.sounds = []
        self.current_costume = 0
        self.visible = False
        self.x = 0
        self.y = 0
        self.size = 100
        self.direction = 90
        self.rotation_style = 'left-right'
        self.layer_order = 0
        self.volume = 100
        self.script_y = 0
        project.targets.append(self)

    def to_json(self, project):
        d = {
            'isStage': self.is_stage,
            'name': self.name,
            'variables': {},
            'lists': {},
            'broadcasts': {},
            'blocks': self.blocks,
            'comments': {},
            'currentCostume': self.current_costume,
            'costumes': self.costumes,
            'sounds': self.sounds,
            'volume': self.volume,
            'layerOrder': self.layer_order,
        }
        if self.is_stage:
            for n, (i, v) in project.gvars.items():
                d['variables'][i] = [n, v]
            for n, (i, v) in project.glists.items():
                d['lists'][i] = [n, v]
            for n, i in project.broadcasts.items():
                d['broadcasts'][i] = n
            d.update({'tempo': 60, 'videoTransparency': 50, 'videoState': 'on', 'textToSpeechLanguage': None})
        else:
            d.update({'visible': self.visible, 'x': self.x, 'y': self.y, 'size': self.size,
                      'direction': self.direction, 'draggable': False,
                      'rotationStyle': self.rotation_style})
        for n, (i, v) in self.vars.items():
            d['variables'][i] = [n, v]
        for n, (i, v) in self.lists.items():
            d['lists'][i] = [n, v]
        return d


MATHOPS = {'abs': 'abs', 'floor': 'floor', 'ceil': 'ceiling', 'sqrt': 'sqrt', 'sin': 'sin',
           'cos': 'cos', 'tan': 'tan', 'asin': 'asin', 'acos': 'acos', 'atan': 'atan',
           'ln': 'ln', 'log10': 'log', 'exp': 'e ^', 'pow10': '10 ^'}

# simple zero-arg reporters
REPORTERS0 = {
    'mouse_down': ('sensing_mousedown', True),
    'mouse_x': ('sensing_mousex', False),
    'mouse_y': ('sensing_mousey', False),
    'timer': ('sensing_timer', False),
    'xpos': ('motion_xposition', False),
    'ypos': ('motion_yposition', False),
    'direction': ('motion_direction', False),
    'size_': ('looks_size', False),
    'volume_': ('sound_volume', False),
    'days2000': ('sensing_dayssince2000', False),
}

EFFECTS = {'color': 'COLOR', 'ghost': 'GHOST', 'brightness': 'BRIGHTNESS', 'fisheye': 'FISHEYE',
           'whirl': 'WHIRL', 'pixelate': 'PIXELATE', 'mosaic': 'MOSAIC'}


class SpriteCompiler:
    def __init__(self, target, consts=None):
        self.t = target
        self.p = target.project
        self.consts = consts or {}
        self.params = None  # current proc params: name -> argument id
        self.in_proc = False

    # ------------------------------------------------------------ blocks
    def mk(self, opcode, inputs=None, fields=None, shadow=False, mutation=None, top=False):
        bid = new_id()
        b = {'opcode': opcode, 'next': None, 'parent': None, 'inputs': {}, 'fields': fields or {},
             'shadow': shadow, 'topLevel': top}
        if top:
            b['x'] = 0
            b['y'] = self.t.script_y
        if mutation is not None:
            b['mutation'] = mutation
        self.t.blocks[bid] = b
        for name, spec in (inputs or {}).items():
            if spec[1] == 'stack' and spec[0] is None:
                continue
            b['inputs'][name] = self.inp(spec, bid)
        return bid

    def setparent(self, child, parent):
        self.t.blocks[child]['parent'] = parent

    def inp(self, spec, parent):
        val, kind = spec
        if kind == 'stack':
            if val is None:
                return [2, None]
            self.setparent(val, parent)
            return [2, val]
        if kind == 'bool':
            bid = self.to_bool(val)
            self.setparent(bid, parent)
            return [2, bid]
        if isinstance(kind, tuple) and kind[0] == 'menu':
            _, mop, field, default = kind
            if val.kind == 'lit':
                m = self.mk(mop, fields={field: [str(val.v), None]}, shadow=True)
                self.setparent(m, parent)
                return [1, m]
            m = self.mk(mop, fields={field: [default, None]}, shadow=True)
            self.setparent(m, parent)
            return [3, self.as_reporter_ref(val, parent), m]
        if kind == 'broadcast':
            if val.kind == 'lit':
                name = str(val.v)
                return [1, [11, name, self.p.bcast(name)]]
            first = next(iter(self.p.broadcasts), None) or 'message1'
            return [3, self.as_reporter_ref(val, parent), [11, first, self.p.bcast(first)]]
        prim = PRIM[kind]
        if val.kind == 'bool' and kind != 'num_raw':
            val = Val('rep', id=self.mk('operator_add', {'NUM1': (val, 'num_raw'), 'NUM2': (Val('lit', 0), 'num')}))
        if kind == 'num_raw':
            prim = 4
        if val.kind == 'lit':
            v = val.v
            if isinstance(v, str):
                try:
                    float(v)
                    return [1, [prim, v]]
                except ValueError:
                    return [1, [10 if prim != 10 else prim, v]]
            return [1, [prim, fmt_num(v)]]
        return [3, self.as_reporter_ref(val, parent), [prim, '']]

    def as_reporter_ref(self, val, parent):
        if val.kind == 'var':
            return [12, val.name, val.id]
        if val.kind == 'list':
            return [13, val.name, val.id]
        if val.kind in ('rep', 'bool'):
            self.setparent(val.id, parent)
            return val.id
        raise CompileError('bad reporter %r' % val.kind)

    def to_bool(self, val):
        if val.kind == 'bool':
            return val.id
        if val.kind == 'lit':
            truthy = val.v not in (0, '', '0', False, 'false')
            if truthy:
                return self.mk('operator_not')
            return self.mk('operator_and')
        # number-ish: true when not equal to 0
        eq = self.mk('operator_equals', {'OPERAND1': (val, 'text'), 'OPERAND2': (Val('lit', 0), 'text')})
        return self.mk('operator_not', {'OPERAND': (Val('bool', id=eq), 'bool')})

    def chain(self, ids, parent=None):
        """Link a list of stack block ids; returns first id."""
        if not ids:
            return None
        prev = parent
        for i, bid in enumerate(ids):
            b = self.t.blocks[bid]
            if prev is not None:
                b['parent'] = prev
            if i + 1 < len(ids):
                b['next'] = ids[i + 1]
            prev = bid
        return ids[0]

    # ------------------------------------------------------------ names
    def lookup(self, name, node=None):
        if self.params is not None and name in self.params:
            return ('param', name)
        if name in self.t.vars:
            return ('var', name, self.t.vars[name][0])
        if name in self.p.gvars:
            return ('var', name, self.p.gvars[name][0])
        if name in self.t.lists:
            return ('list', name, self.t.lists[name][0])
        if name in self.p.glists:
            return ('list', name, self.p.glists[name][0])
        if name in self.consts:
            return ('const', self.consts[name])
        raise CompileError('%s: unknown name %r (line %s)' % (self.t.name, name, getattr(node, 'lineno', '?')))

    def var_ref(self, name, node):
        r = self.lookup(name, node)
        if r[0] != 'var':
            raise CompileError('%s: %r is not a variable (line %s)' % (self.t.name, name, node.lineno))
        return r[1], r[2]

    def list_ref(self, node):
        if not isinstance(node, ast.Name):
            raise CompileError('list expected (line %s)' % node.lineno)
        r = self.lookup(node.id, node)
        if r[0] != 'list':
            raise CompileError('%s: %r is not a list (line %s)' % (self.t.name, node.id, node.lineno))
        return r[1], r[2]

    def is_list_name(self, node):
        if not isinstance(node, ast.Name):
            return False
        try:
            return self.lookup(node.id, node)[0] == 'list'
        except CompileError:
            return False

    # ------------------------------------------------------------ expressions
    def expr(self, n):
        if isinstance(n, ast.Constant):
            if isinstance(n.value, bool):
                return Val('lit', 1 if n.value else 0)
            return Val('lit', n.value)
        if isinstance(n, ast.Name):
            r = self.lookup(n.id, n)
            if r[0] == 'param':
                bid = self.mk('argument_reporter_string_number', fields={'VALUE': [n.id, None]})
                return Val('rep', id=bid)
            if r[0] == 'var':
                return Val('var', name=r[1], id=r[2])
            if r[0] == 'list':
                return Val('list', name=r[1], id=r[2])
            return Val('lit', r[1])
        if isinstance(n, ast.BinOp):
            return self.binop(n)
        if isinstance(n, ast.UnaryOp):
            if isinstance(n.op, ast.USub):
                a = self.expr(n.operand)
                if a.is_num_lit():
                    return Val('lit', -a.v)
                return self.arith('operator_subtract', Val('lit', 0), a)
            if isinstance(n.op, ast.UAdd):
                return self.expr(n.operand)
            if isinstance(n.op, ast.Not):
                return Val('bool', id=self.mk('operator_not', {'OPERAND': (self.expr(n.operand), 'bool')}))
        if isinstance(n, ast.BoolOp):
            op = 'operator_and' if isinstance(n.op, ast.And) else 'operator_or'
            vals = [self.expr(v) for v in n.values]
            acc = vals[0]
            for v in vals[1:]:
                acc = Val('bool', id=self.mk(op, {'OPERAND1': (acc, 'bool'), 'OPERAND2': (v, 'bool')}))
            return acc
        if isinstance(n, ast.Compare):
            parts = []
            left = n.left
            for op, right in zip(n.ops, n.comparators):
                parts.append(self.compare(left, op, right))
                left = right
            acc = parts[0]
            for v in parts[1:]:
                acc = Val('bool', id=self.mk('operator_and', {'OPERAND1': (acc, 'bool'), 'OPERAND2': (v, 'bool')}))
            return acc
        if isinstance(n, ast.Call):
            return self.call_expr(n)
        if isinstance(n, ast.Subscript):
            lname, lid = self.list_ref(n.value)
            idx = self.expr(n.slice)
            return Val('rep', id=self.mk('data_itemoflist', {'INDEX': (idx, 'int')}, {'LIST': [lname, lid]}))
        if isinstance(n, ast.JoinedStr):
            parts = []
            for v in n.values:
                if isinstance(v, ast.Constant):
                    parts.append(Val('lit', v.value))
                else:
                    parts.append(self.expr(v.value))
            return self.join(parts)
        if isinstance(n, ast.IfExp):
            # numeric only: (a - b) * cond + b
            a = self.expr(n.body)
            b = self.expr(n.orelse)
            c = self.expr(n.test)
            cb = Val('bool', id=self.to_bool(c))
            diff = self.arith('operator_subtract', a, b)
            prod = self.arith('operator_multiply', diff, cb)
            return self.arith('operator_add', prod, self.expr(n.orelse))
        raise CompileError('%s: unsupported expression %s (line %s)' % (self.t.name, ast.dump(n)[:80], getattr(n, 'lineno', '?')))

    def join(self, parts):
        parts = [p for p in parts if not (p.kind == 'lit' and p.v == '')]
        if not parts:
            return Val('lit', '')
        # merge adjacent literals
        merged = []
        for p in parts:
            if merged and p.kind == 'lit' and merged[-1].kind == 'lit':
                merged[-1] = Val('lit', str(merged[-1].v if not isinstance(merged[-1].v, (int, float)) else fmt_num(merged[-1].v)) + (p.v if isinstance(p.v, str) else fmt_num(p.v)))
            else:
                merged.append(p)
        if len(merged) == 1:
            if merged[0].kind == 'lit':
                return Val('lit', merged[0].v if isinstance(merged[0].v, str) else fmt_num(merged[0].v))
            return self.join2(merged[0], Val('lit', ''))
        acc = merged[-1]
        for p in reversed(merged[:-1]):
            acc = self.join2(p, acc)
        return acc

    def join2(self, a, b):
        return Val('rep', id=self.mk('operator_join', {'STRING1': (a, 'text'), 'STRING2': (b, 'text')}))

    def arith(self, op, a, b):
        return Val('rep', id=self.mk(op, {'NUM1': (a, 'num'), 'NUM2': (b, 'num')}))

    def binop(self, n):
        a = self.expr(n.left)
        b = self.expr(n.right)
        if a.is_num_lit() and b.is_num_lit():
            try:
                if isinstance(n.op, ast.Add):
                    return Val('lit', a.v + b.v)
                if isinstance(n.op, ast.Sub):
                    return Val('lit', a.v - b.v)
                if isinstance(n.op, ast.Mult):
                    return Val('lit', a.v * b.v)
                if isinstance(n.op, ast.Div):
                    return Val('lit', a.v / b.v)
                if isinstance(n.op, ast.FloorDiv):
                    return Val('lit', a.v // b.v)
                if isinstance(n.op, ast.Mod):
                    return Val('lit', a.v % b.v)
            except ZeroDivisionError:
                pass
        if isinstance(n.op, ast.Add):
            if (a.kind == 'lit' and isinstance(a.v, str)) or (b.kind == 'lit' and isinstance(b.v, str)):
                return self.join([a, b])
            return self.arith('operator_add', a, b)
        if isinstance(n.op, ast.Sub):
            return self.arith('operator_subtract', a, b)
        if isinstance(n.op, ast.Mult):
            return self.arith('operator_multiply', a, b)
        if isinstance(n.op, ast.Div):
            return self.arith('operator_divide', a, b)
        if isinstance(n.op, ast.Mod):
            return self.arith('operator_mod', a, b)
        if isinstance(n.op, ast.FloorDiv):
            d = self.arith('operator_divide', a, b)
            return self.mathop('floor', d)
        if isinstance(n.op, ast.Pow):
            if b.is_num_lit() and b.v == 2:
                return self.arith('operator_multiply', a, self.expr(n.left))
        raise CompileError('unsupported binop line %s' % n.lineno)

    def mathop(self, op, v):
        return Val('rep', id=self.mk('operator_mathop', {'NUM': (v, 'num')}, {'OPERATOR': [MATHOPS[op], None]}))

    def compare(self, left, op, right):
        if isinstance(op, ast.In):
            if self.is_list_name(right):
                lname, lid = self.list_ref(right)
                return Val('bool', id=self.mk('data_listcontainsitem', {'ITEM': (self.expr(left), 'text')}, {'LIST': [lname, lid]}))
            return Val('bool', id=self.mk('operator_contains', {'STRING1': (self.expr(right), 'text'), 'STRING2': (self.expr(left), 'text')}))
        if isinstance(op, ast.NotIn):
            inner = self.compare(left, ast.In(), right)
            return Val('bool', id=self.mk('operator_not', {'OPERAND': (inner, 'bool')}))
        a = self.expr(left)
        b = self.expr(right)

        def cmp(opc, x, y):
            return Val('bool', id=self.mk(opc, {'OPERAND1': (x, 'text'), 'OPERAND2': (y, 'text')}))

        def neg(v):
            return Val('bool', id=self.mk('operator_not', {'OPERAND': (v, 'bool')}))
        if isinstance(op, ast.Eq):
            return cmp('operator_equals', a, b)
        if isinstance(op, ast.NotEq):
            return neg(cmp('operator_equals', a, b))
        if isinstance(op, ast.Lt):
            return cmp('operator_lt', a, b)
        if isinstance(op, ast.Gt):
            return cmp('operator_gt', a, b)
        if isinstance(op, ast.LtE):
            return neg(cmp('operator_gt', a, b))
        if isinstance(op, ast.GtE):
            return neg(cmp('operator_lt', a, b))
        raise CompileError('unsupported compare')

    def call_expr(self, n):
        if isinstance(n.func, ast.Attribute):
            meth = n.func.attr
            if meth == 'index':
                lname, lid = self.list_ref(n.func.value)
                return Val('rep', id=self.mk('data_itemnumoflist', {'ITEM': (self.expr(n.args[0]), 'text')}, {'LIST': [lname, lid]}))
            raise CompileError('unknown method %s line %s' % (meth, n.lineno))
        fname = n.func.id
        args = n.args
        if fname in MATHOPS:
            return self.mathop(fname, self.expr(args[0]))
        if fname == 'round':
            return Val('rep', id=self.mk('operator_round', {'NUM': (self.expr(args[0]), 'num')}))
        if fname == 'rand':
            return Val('rep', id=self.mk('operator_random', {'FROM': (self.expr(args[0]), 'num'), 'TO': (self.expr(args[1]), 'num')}))
        if fname == 'join':
            return self.join([self.expr(a) for a in args])
        if fname == 'letter':
            return Val('rep', id=self.mk('operator_letter_of', {'LETTER': (self.expr(args[0]), 'whole'), 'STRING': (self.expr(args[1]), 'text')}))
        if fname == 'strlen':
            return Val('rep', id=self.mk('operator_length', {'STRING': (self.expr(args[0]), 'text')}))
        if fname == 'contains':
            return Val('bool', id=self.mk('operator_contains', {'STRING1': (self.expr(args[0]), 'text'), 'STRING2': (self.expr(args[1]), 'text')}))
        if fname == 'len':
            lname, lid = self.list_ref(args[0])
            return Val('rep', id=self.mk('data_lengthoflist', fields={'LIST': [lname, lid]}))
        if fname in ('min', 'max'):
            # min(a,b) = (a+b-|a-b|)/2 ; max = (a+b+|a-b|)/2
            a1, b1 = self.expr(args[0]), self.expr(args[1])
            if a1.is_num_lit() and b1.is_num_lit():
                return Val('lit', min(a1.v, b1.v) if fname == 'min' else max(a1.v, b1.v))
            s = self.arith('operator_add', a1, b1)
            d = self.mathop('abs', self.arith('operator_subtract', self.expr(args[0]), self.expr(args[1])))
            t = self.arith('operator_subtract' if fname == 'min' else 'operator_add', s, d)
            return self.arith('operator_divide', t, Val('lit', 2))
        if fname == 'key':
            return Val('bool', id=self.mk('sensing_keypressed', {'KEY_OPTION': (self.expr(args[0]), ('menu', 'sensing_keyoptions', 'KEY_OPTION', 'space'))}))
        if fname in REPORTERS0:
            op, isbool = REPORTERS0[fname]
            return Val('bool' if isbool else 'rep', id=self.mk(op))
        if fname == 'costume_num':
            return Val('rep', id=self.mk('looks_costumenumbername', fields={'NUMBER_NAME': ['number', None]}))
        if fname == 'costume_name':
            return Val('rep', id=self.mk('looks_costumenumbername', fields={'NUMBER_NAME': ['name', None]}))
        if fname == 'backdrop_num':
            return Val('rep', id=self.mk('looks_backdropnumbername', fields={'NUMBER_NAME': ['number', None]}))
        if fname == 'backdrop_name':
            return Val('rep', id=self.mk('looks_backdropnumbername', fields={'NUMBER_NAME': ['name', None]}))
        if fname == 'of':
            prop = args[0].value
            obj = self.expr(args[1])
            return Val('rep', id=self.mk('sensing_of', {'OBJECT': (obj, ('menu', 'sensing_of_object_menu', 'OBJECT', '_stage_'))}, {'PROPERTY': [prop, None]}))
        if fname == 'num':
            return self.arith('operator_add', self.expr(args[0]), Val('lit', 0))
        if fname == 'true':
            return Val('bool', id=self.mk('operator_not'))
        raise CompileError('%s: unknown function %s (line %s)' % (self.t.name, fname, n.lineno))

    # ------------------------------------------------------------ statements
    def block_list(self, stmts):
        ids = []
        for s in stmts:
            ids.extend(self.stmt(s))
        return ids

    def substack(self, stmts):
        ids = self.block_list(stmts)
        return self.chain(ids)

    def stmt(self, s):
        if isinstance(s, ast.Expr):
            if isinstance(s.value, ast.Constant):
                return []  # docstring / comment
            if isinstance(s.value, ast.Call):
                return self.call_stmt(s.value)
            raise CompileError('bad expression statement line %s' % s.lineno)
        if isinstance(s, ast.Pass):
            return []
        if isinstance(s, ast.Assign):
            if len(s.targets) != 1:
                raise CompileError('single assignment only line %s' % s.lineno)
            tgt = s.targets[0]
            if isinstance(tgt, ast.Tuple):
                out = []
                vals = s.value.elts
                for tt, vv in zip(tgt.elts, vals):
                    out.extend(self.stmt(ast.Assign(targets=[tt], value=vv, lineno=s.lineno)))
                return out
            if isinstance(tgt, ast.Subscript):
                lname, lid = self.list_ref(tgt.value)
                return [self.mk('data_replaceitemoflist', {'INDEX': (self.expr(tgt.slice), 'int'), 'ITEM': (self.expr(s.value), 'text')}, {'LIST': [lname, lid]})]
            name, vid = self.var_ref(tgt.id, s)
            return [self.mk('data_setvariableto', {'VALUE': (self.expr(s.value), 'text')}, {'VARIABLE': [name, vid]})]
        if isinstance(s, ast.AugAssign):
            tgt = s.target
            if isinstance(tgt, ast.Subscript):
                # L[i] += v  ->  replace item i with (item i + v)
                binop = ast.BinOp(left=tgt, op=s.op, right=s.value, lineno=s.lineno)
                return self.stmt(ast.Assign(targets=[tgt], value=binop, lineno=s.lineno))
            name, vid = self.var_ref(tgt.id, s)
            if isinstance(s.op, (ast.Add, ast.Sub)):
                v = self.expr(s.value)
                if isinstance(s.op, ast.Sub):
                    if v.is_num_lit():
                        v = Val('lit', -v.v)
                    else:
                        v = self.arith('operator_subtract', Val('lit', 0), v)
                elif v.kind == 'lit' and isinstance(v.v, str):
                    raise CompileError('string += line %s' % s.lineno)
                return [self.mk('data_changevariableby', {'VALUE': (v, 'num')}, {'VARIABLE': [name, vid]})]
            binop = ast.BinOp(left=ast.Name(id=tgt.id, lineno=s.lineno), op=s.op, right=s.value, lineno=s.lineno)
            return [self.mk('data_setvariableto', {'VALUE': (self.expr(binop), 'text')}, {'VARIABLE': [name, vid]})]
        if isinstance(s, ast.If):
            cond = self.expr(s.test)
            body = self.substack(s.body)
            if s.orelse:
                other = self.substack(s.orelse)
                return [self.mk('control_if_else', {'CONDITION': (cond, 'bool'), 'SUBSTACK': (body, 'stack'), 'SUBSTACK2': (other, 'stack')})]
            return [self.mk('control_if', {'CONDITION': (cond, 'bool'), 'SUBSTACK': (body, 'stack')})]
        if isinstance(s, ast.While):
            if isinstance(s.test, ast.Constant) and s.test.value is True:
                body = self.substack(s.body)
                return [self.mk('control_forever', {'SUBSTACK': (body, 'stack')})]
            cond = self.expr(s.test)
            notc = Val('bool', id=self.mk('operator_not', {'OPERAND': (cond, 'bool')}))
            body = self.substack(s.body)
            return [self.mk('control_repeat_until', {'CONDITION': (notc, 'bool'), 'SUBSTACK': (body, 'stack')})]
        if isinstance(s, ast.For):
            it = s.iter
            if not (isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == 'range'):
                raise CompileError('for only over range() line %s' % s.lineno)
            if len(it.args) == 1:
                start, stop = ast.Constant(value=0), it.args[0]
            else:
                start, stop = it.args[0], it.args[1]
            var = s.target.id
            if var == '_':
                count = self.expr(stop) if len(it.args) == 1 else self.expr(ast.BinOp(left=stop, op=ast.Sub(), right=start, lineno=s.lineno))
                body = self.substack(s.body)
                return [self.mk('control_repeat', {'TIMES': (count, 'whole'), 'SUBSTACK': (body, 'stack')})]
            name, vid = self.var_ref(var, s)
            init = self.mk('data_setvariableto', {'VALUE': (self.expr(start), 'text')}, {'VARIABLE': [name, vid]})
            count = self.expr(ast.BinOp(left=stop, op=ast.Sub(), right=start, lineno=s.lineno))
            body_ids = self.block_list(s.body)
            body_ids.append(self.mk('data_changevariableby', {'VALUE': (Val('lit', 1), 'num')}, {'VARIABLE': [name, vid]}))
            body = self.chain(body_ids)
            return [init, self.mk('control_repeat', {'TIMES': (count, 'whole'), 'SUBSTACK': (body, 'stack')})]
        if isinstance(s, ast.Return):
            return [self.mk('control_stop', fields={'STOP_OPTION': ['this script', None]},
                            mutation={'tagName': 'mutation', 'children': [], 'hasnext': 'false'})]
        raise CompileError('%s: unsupported statement %s line %s' % (self.t.name, type(s).__name__, s.lineno))

    def call_stmt(self, c):
        if isinstance(c.func, ast.Attribute):
            lname, lid = self.list_ref(c.func.value)
            m = c.func.attr
            F = {'LIST': [lname, lid]}
            if m == 'append':
                return [self.mk('data_addtolist', {'ITEM': (self.expr(c.args[0]), 'text')}, F)]
            if m == 'clear':
                return [self.mk('data_deletealloflist', fields=F)]
            if m == 'delete':
                return [self.mk('data_deleteoflist', {'INDEX': (self.expr(c.args[0]), 'int')}, F)]
            if m == 'insert':
                return [self.mk('data_insertatlist', {'INDEX': (self.expr(c.args[0]), 'int'), 'ITEM': (self.expr(c.args[1]), 'text')}, F)]
            raise CompileError('unknown list method %s line %s' % (m, c.lineno))
        f = c.func.id
        a = c.args
        E = self.expr
        if f in self.t.procs:
            pr = self.t.procs[f]
            if len(a) != len(pr['argids']):
                raise CompileError('%s: wrong arg count calling %s line %s' % (self.t.name, f, c.lineno))
            inputs = {aid: (E(arg), 'text') for aid, arg in zip(pr['argids'], a)}
            return [self.mk('procedures_call', inputs, mutation={
                'tagName': 'mutation', 'children': [], 'proccode': pr['proccode'],
                'argumentids': json.dumps(pr['argids']), 'warp': 'true' if pr['warp'] else 'false'})]
        simple = {
            'show': 'looks_show', 'hide': 'looks_hide', 'next_costume': 'looks_nextcostume',
            'clear_effects': 'looks_cleargraphiceffects', 'stop_sounds': 'sound_stopallsounds',
            'delete_clone': 'control_delete_this_clone', 'reset_timer': 'sensing_resettimer',
            'clear_sound_effects': 'sound_cleareffects', 'next_backdrop': 'looks_nextbackdrop',
        }
        if f in simple:
            return [self.mk(simple[f])]
        if f == 'goto':
            return [self.mk('motion_gotoxy', {'X': (E(a[0]), 'num'), 'Y': (E(a[1]), 'num')})]
        if f == 'setx':
            return [self.mk('motion_setx', {'X': (E(a[0]), 'num')})]
        if f == 'sety':
            return [self.mk('motion_sety', {'Y': (E(a[0]), 'num')})]
        if f == 'changex':
            return [self.mk('motion_changexby', {'DX': (E(a[0]), 'num')})]
        if f == 'changey':
            return [self.mk('motion_changeyby', {'DY': (E(a[0]), 'num')})]
        if f == 'point':
            return [self.mk('motion_pointindirection', {'DIRECTION': (E(a[0]), 'angle')})]
        if f == 'rotation_style':
            return [self.mk('motion_setrotationstyle', fields={'STYLE': [a[0].value, None]})]
        if f == 'costume':
            return [self.mk('looks_switchcostumeto', {'COSTUME': (E(a[0]), ('menu', 'looks_costume', 'COSTUME', self.t.costumes[0]['name'] if self.t.costumes else ''))})]
        if f == 'backdrop':
            return [self.mk('looks_switchbackdropto', {'BACKDROP': (E(a[0]), ('menu', 'looks_backdrops', 'BACKDROP', 'black'))})]
        if f == 'size':
            return [self.mk('looks_setsizeto', {'SIZE': (E(a[0]), 'num')})]
        if f == 'change_size':
            return [self.mk('looks_changesizeby', {'CHANGE': (E(a[0]), 'num')})]
        if f == 'effect':
            return [self.mk('looks_seteffectto', {'VALUE': (E(a[1]), 'num')}, {'EFFECT': [EFFECTS[a[0].value], None]})]
        if f == 'change_effect':
            return [self.mk('looks_changeeffectby', {'CHANGE': (E(a[1]), 'num')}, {'EFFECT': [EFFECTS[a[0].value], None]})]
        if f == 'front':
            return [self.mk('looks_gotofrontback', fields={'FRONT_BACK': ['front', None]})]
        if f == 'back':
            return [self.mk('looks_gotofrontback', fields={'FRONT_BACK': ['back', None]})]
        if f in ('forward', 'backward'):
            return [self.mk('looks_goforwardbackwardlayers', {'NUM': (E(a[0]), 'int')}, {'FORWARD_BACKWARD': [f, None]})]
        if f == 'say':
            return [self.mk('looks_say', {'MESSAGE': (E(a[0]), 'text')})]
        if f in ('play', 'play_wait'):
            op = 'sound_play' if f == 'play' else 'sound_playuntildone'
            default = self.t.sounds[0]['name'] if self.t.sounds else ''
            return [self.mk(op, {'SOUND_MENU': (E(a[0]), ('menu', 'sound_sounds_menu', 'SOUND_MENU', default))})]
        if f == 'volume':
            return [self.mk('sound_setvolumeto', {'VOLUME': (E(a[0]), 'num')})]
        if f == 'change_volume':
            return [self.mk('sound_changevolumeby', {'VOLUME': (E(a[0]), 'num')})]
        if f == 'sound_effect':
            return [self.mk('sound_seteffectto', {'VALUE': (E(a[1]), 'num')}, {'EFFECT': [a[0].value.upper(), None]})]
        if f == 'broadcast':
            return [self.mk('event_broadcast', {'BROADCAST_INPUT': (E(a[0]), 'broadcast')})]
        if f == 'broadcast_wait':
            return [self.mk('event_broadcastandwait', {'BROADCAST_INPUT': (E(a[0]), 'broadcast')})]
        if f == 'wait':
            return [self.mk('control_wait', {'DURATION': (E(a[0]), 'pos')})]
        if f == 'wait_until':
            return [self.mk('control_wait_until', {'CONDITION': (E(a[0]), 'bool')})]
        if f in ('stop_all', 'stop_this', 'stop_other'):
            opt = {'stop_all': 'all', 'stop_this': 'this script', 'stop_other': 'other scripts in sprite'}[f]
            return [self.mk('control_stop', fields={'STOP_OPTION': [opt, None]},
                            mutation={'tagName': 'mutation', 'children': [], 'hasnext': 'true' if f == 'stop_other' else 'false'})]
        if f == 'clone':
            target = Val('lit', '_myself_') if not a else E(a[0])
            return [self.mk('control_create_clone_of', {'CLONE_OPTION': (target, ('menu', 'control_create_clone_of_menu', 'CLONE_OPTION', '_myself_'))})]
        if f == 'show_var':
            name, vid = self.var_ref(a[0].id, c)
            return [self.mk('data_showvariable', fields={'VARIABLE': [name, vid]})]
        raise CompileError('%s: unknown statement function %s line %s' % (self.t.name, f, c.lineno))

    # ------------------------------------------------------------ top level
    def compile(self, src):
        tree = ast.parse(src)
        funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        for n in tree.body:
            if not isinstance(n, (ast.FunctionDef, ast.Expr, ast.Pass)):
                raise CompileError('%s: top-level must be functions (line %s)' % (self.t.name, n.lineno))
        # pass 1: procedures and locals
        for fn in funcs:
            kind, arg = self.decorator(fn)
            if kind in ('proc', 'proc_yield'):
                if fn.name in self.t.procs:
                    raise CompileError('%s: duplicate proc %s' % (self.t.name, fn.name))
                names = [x.arg for x in fn.args.args]
                ids = [new_id('a') for _ in names]
                self.t.procs[fn.name] = {'proccode': fn.name + ''.join(' %s' for _ in names),
                                         'argids': ids, 'argnames': names, 'warp': kind == 'proc'}
        for fn in funcs:
            params = set(x.arg for x in fn.args.args)
            for node in ast.walk(fn):
                tgts = []
                if isinstance(node, ast.Assign):
                    tgts = node.targets
                elif isinstance(node, ast.AugAssign):
                    tgts = [node.target]
                elif isinstance(node, ast.For):
                    tgts = [node.target]
                flat = []
                for t in tgts:
                    flat.extend(t.elts if isinstance(t, ast.Tuple) else [t])
                for t in flat:
                    if isinstance(t, ast.Name) and t.id != '_':
                        if t.id in params:
                            raise CompileError('%s: assigning to parameter %s' % (self.t.name, t.id))
                        if t.id in self.consts:
                            raise CompileError('%s: assigning to constant %s' % (self.t.name, t.id))
                        if t.id not in self.p.gvars and t.id not in self.t.vars:
                            if self.t.is_stage:
                                self.p.add_global(t.id)
                            else:
                                self.t.vars[t.id] = [new_id('v'), 0]
        # pass 2: bodies
        for fn in funcs:
            self.compile_func(fn)

    def decorator(self, fn):
        if not fn.decorator_list:
            raise CompileError('%s: function %s has no decorator' % (self.t.name, fn.name))
        d = fn.decorator_list[0]
        if isinstance(d, ast.Name):
            return d.id, None
        if isinstance(d, ast.Call):
            return d.func.id, [x.value for x in d.args]
        raise CompileError('bad decorator')

    def compile_func(self, fn):
        kind, arg = self.decorator(fn)
        self.params = None
        nstart = len(self.t.blocks)
        if kind == 'flag':
            hat = self.mk('event_whenflagclicked', top=True)
        elif kind == 'on':
            name = arg[0]
            hat = self.mk('event_whenbroadcastreceived', fields={'BROADCAST_OPTION': [name, self.p.bcast(name)]}, top=True)
        elif kind == 'clone':
            hat = self.mk('control_start_as_clone', top=True)
        elif kind == 'key':
            hat = self.mk('event_whenkeypressed', fields={'KEY_OPTION': [arg[0], None]}, top=True)
        elif kind in ('proc', 'proc_yield'):
            pr = self.t.procs[fn.name]
            self.params = {nm: aid for nm, aid in zip(pr['argnames'], pr['argids'])}
            hat = self.mk('procedures_definition', top=True)
            proto_inputs = {}
            proto = new_id()
            for nm, aid in zip(pr['argnames'], pr['argids']):
                sid = new_id()
                self.t.blocks[sid] = {'opcode': 'argument_reporter_string_number', 'next': None, 'parent': proto,
                                      'inputs': {}, 'fields': {'VALUE': [nm, None]}, 'shadow': True, 'topLevel': False}
                proto_inputs[aid] = [1, sid]
            self.t.blocks[proto] = {
                'opcode': 'procedures_prototype', 'next': None, 'parent': hat, 'inputs': proto_inputs,
                'fields': {}, 'shadow': True, 'topLevel': False,
                'mutation': {'tagName': 'mutation', 'children': [], 'proccode': pr['proccode'],
                             'argumentids': json.dumps(pr['argids']),
                             'argumentnames': json.dumps(pr['argnames']),
                             'argumentdefaults': json.dumps(['' for _ in pr['argids']]),
                             'warp': 'true' if pr['warp'] else 'false'}}
            self.t.blocks[hat]['inputs']['custom_block'] = [1, proto]
        else:
            raise CompileError('unknown decorator %s' % kind)
        ids = self.block_list(fn.body)
        self.chain([hat] + ids)
        self.params = None
        self.t.script_y += 60 + 30 * (len(self.t.blocks) - nstart) // 3


def compile_sprite(target, src, consts=None):
    SpriteCompiler(target, consts).compile(src)
