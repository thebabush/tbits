#!/usr/bin/env python

from __future__ import print_function

import itertools

from sympy import symbols, simplify_logic

TMPL_ADD = '''def {name}({args}):
    if {body}
    else:
        raise Exception('{name}: Unhandled case "{{}}"'.format({args}))'''


def _sym_to_py(expr):
    try:
        if expr.is_Symbol:
            return expr.name
        elif expr.is_Function:
            name = str(expr.func)
            if name == 'And':
                return '(' + ' & '.join(sym_to_py(a) for a in expr.args) + ')'
            elif name == 'Xor':
                return '(' + ' ^ '.join(sym_to_py(a) for a in expr.args) + ')'
            elif name == 'Or':
                return '(' + ' | '.join(sym_to_py(a) for a in expr.args) + ')'
            elif name == 'Not':
                assert len(expr.args) == 1
                return '(~{})'.format(sym_to_py(expr.args[0]))
            else:
                raise Exception('Operator "{}" missing'.format(name))
        else:
            return str(bool(expr))
    except Exception as e:
        print(e)
        import IPython; IPython.embed()


def sym_to_py(expr):
    expr_simp = simplify_logic(expr)
    # Stupid heuristics
    if expr.count_ops() > expr_simp.count_ops():
        expr = expr_simp
    return _sym_to_py(expr).replace('True', '_one').replace('False', '_zero')


def bool_to_cond(b):
    if b is None:
        return 'X'
    elif b:
        return 'I'
    else:
        return 'O'


TMPL_COND = '''{cond}:
        return {stmts}'''


def mk_funk(funk, vars, exprs_tmpls):
    nn = ['ss[{}]'.format(i) for i in range(vars)]
    ii = ['b{}'.format(i) for i in range(vars)]
    ss = symbols(' '.join(ii))

    conds = []
    body = []

    exprs = []
    for e in exprs_tmpls:
        exprs.append(eval(e.format(*nn)))

    for vv in itertools.product((False, True, None), repeat=3):
        s = dict((si, vi if vi is not None else si) for si, vi in zip(ss, vv))
        cond = ' and '.join('{}.{}'.format(n, bool_to_cond(v)) for n, v in zip(ii, vv))
        conds.append(cond)
        body.append(tuple(sym_to_py(e.subs(s)) for e in exprs))

    stmts = [TMPL_COND.format(cond=cond, stmts=', '.join(stmts)) for cond, stmts in zip(conds, body)]
    stmts = '\n    elif '.join(stmts)

    return TMPL_ADD.format(
        name=funk,
        args=', '.join(ii),
        body=stmts,
    )


def main():
    print('Generating the functions...')
    defs = (
        ('_bit_add', 3, ['{0} ^ {1} ^ {2}', '({0} & {1}) | ({2} & ({0} ^ {1}))']),
    )
    funks = []
    for d in defs:
        print('[+] Making "{}"'.format(d[0]))
        funks.append(mk_funk(*d))
    src = 'from ._tbits import _zero, _one\n\n\n' + '\n\n'.join(funks) + '\n'

    print('Writing to file...')
    with open('./tbits/_gen_tables.py', 'w') as f:
        f.write(src)

    print('End of this giant hack :D')


if __name__ == '__main__':
    main()
