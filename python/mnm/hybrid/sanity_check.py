import ast
from sys import version_info

from .utils import NodeVisitor, SUPPORTED_OPS


SUPPORTED = {
    ########## Module ##########
    ast.Module: "check_Module",
    ########## Literals ##########
    ast.Num: "generic_visit",
    # ast.Str,
    # ast.FormattedValue,
    # ast.JoinedStr,
    # ast.Bytes,
    # ast.List,
    # ast.Tuple,
    # ast.Set,
    # ast.Dict,
    ast.Ellipsis: "generic_visit",
    ast.NameConstant: "generic_visit",
    ########## Variables ##########
    ast.Name: "generic_visit",
    ast.Load: "generic_visit",          # TODO
    ast.Store: "generic_visit",         # TODO
    # ast.Starred,
    # ast.Del,
    ########## Expressions ##########
    ast.Expr: "generic_visit",          # TODO
    ast.UnaryOp: "check_ArithOp",
    ast.BinOp: "check_ArithOp",
    ast.BoolOp: "generic_visit",
    ast.Compare: "check_Compare",
    # ast.Call,
    # ast.keyword,
    # ast.IfExp,
    # ast.Attribute,
    # ast.Subscript,
    # ast.Index,
    # ast.Slice,
    # ast.ExtSlice,
    ########## Comprehensions ##########
    # ast.ListComp,
    # ast.SetComp,
    # ast.GeneratorExp,
    # ast.DictComp,
    # ast.comprehension,
    ########## Imports ##########
    # ast.Import,
    # ast.ImportFrom,
    # ast.alias,
    ########## Statements ##########
    ast.Assign: "check_Assign",
    # ast.AnnAssign,
    # ast.AugAssign,                    # TODO
    # ast.Print,
    # ast.Raise,
    # ast.Assert,
    # ast.Delete,
    ast.Pass: "generic_visit",
    ast.If: "generic_visit",
    # ast.For,
    ast.While: "check_While",
    ast.Break: "generic_visit",
    ast.Continue: "generic_visit",
    ast.Return: "check_Return",
    # ast.Yield,
    # ast.YieldFrom,
    # ast.Try,
    # ast.ExceptHandler,
    # ast.With,
    # ast.withitem,
    ########## Function and class definitions ##########
    ast.FunctionDef: "check_FunctionDef",
    ast.arguments: "check_arguments",
    ast.arg: "generic_visit",
    # ast.Lambda,
    # ast.Global,
    # ast.Nonlocal,
    # ast.ClassDef,
    # ast.AsyncFunctionDef,
    # ast.Await,
    # ast.AsyncFor,
    # ast.AsyncWith,
}


class SanityCheck(NodeVisitor):

    def __init__(self):
        super(SanityCheck, self).__init__()
        self.n_func_defs = 0
        self.loop_nest_depth = 0
        self.return_in_loop = False

    def run(self, node: ast.AST) -> None:
        self.visit(node)

    def visit(self, node: ast.AST):
        if type(node) in SUPPORTED_OPS:
            return
        name = SUPPORTED.get(type(node), None)
        if name is None:
            raise NotImplementedError(node.__class__.__name__)
        getattr(self, name)(node)

    def check_Module(self, node: ast.Module):
        if len(node.body) != 1:
            raise NotImplementedError("Support only module with one body.")
        body = node.body[0]
        if not isinstance(body, ast.FunctionDef):
            raise NotImplementedError("Require body to be a function")
        self.generic_visit(node)

    def check_Assign(self, node: ast.Assign):
        if len(node.targets) != 1:
            raise NotImplementedError(
                "Multi-target assignment is not supported.")
        self.generic_visit(node)

    def check_While(self, node: ast.While):
        if node.orelse:
            raise NotImplementedError(
                "While loop with else branch is not supported.")
        self.loop_nest_depth += 1
        self.generic_visit(node)
        self.loop_nest_depth -= 1

    def check_FunctionDef(self, node: ast.FunctionDef):
        if self.n_func_defs > 0:
            raise NotImplementedError("Nested function is not supported.")
        self.n_func_defs += 1
        if len(node.decorator_list) > 1:
            raise NotImplementedError("Extra decorators are not supported.")
        self.generic_visit(node)

    def check_arguments(self, node: ast.arguments):
        if node.vararg:
            raise NotImplementedError("Var argument is not supported.")
        if node.kwonlyargs or node.kwarg:
            raise NotImplementedError("Keyword argument is not supported.")
        if node.defaults or node.kw_defaults:
            raise NotImplementedError("Default value is not supported.")
        self.generic_visit(node)

    def check_ArithOp(self, node: ast.UnaryOp):
        if type(node.op) not in SUPPORTED_OPS:
            raise NotImplementedError(
                "{} is not supported.".format(node.op.__class__.__name__))
        self.generic_visit(node)

    def check_Compare(self, node: ast.Compare):
        if len(node.comparators) != len(node.ops):
            raise ValueError
        if len(node.comparators) != 1:
            raise NotImplementedError("Only support comparing 2 values.")
        if type(node.ops[0]) not in SUPPORTED_OPS:
            raise NotImplementedError(
                "{} is not supported.".format(node.op.__class__.__name__))
        self.generic_visit(node)

    def check_Return(self, node: ast.Return):
        if self.loop_nest_depth > 0 and not self.return_in_loop:
            self.return_in_loop = True
            # TODO: replace with logger
            print("Warning: return statement in loops may affect performance.")
        self.generic_visit(node)


def sanity_check(node: ast.AST) -> None:
    assert version_info >= (3, 5), "Only support Python >= 3.5."
    SanityCheck().run(node)
