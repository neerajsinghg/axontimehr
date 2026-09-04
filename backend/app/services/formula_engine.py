import ast
from decimal import Decimal
from typing import Dict, Any


class FormulaEvaluationError(Exception):
    pass


class SafeFormulaEvaluator:
    """
    Evaluates salary calculation formulas securely using Python's AST module.
    Prohibits dangerous dynamic code execution (eval/exec).
    """

    ALLOWED_FUNCTIONS = {
        "min": min,
        "max": max,
        "round": round,
    }

    @classmethod
    def evaluate(cls, expression: str, variables: Dict[str, Decimal]) -> Decimal:
        if not expression or not expression.strip():
            return Decimal("0.00")

        try:
            tree = ast.parse(expression.strip(), mode="eval")
            result = cls._eval_node(tree.body, variables)
            return Decimal(str(result)).quantize(Decimal("0.01"))
        except Exception as e:
            raise FormulaEvaluationError(f"Error evaluating formula '{expression}': {str(e)}")

    @classmethod
    def _eval_node(cls, node: ast.AST, variables: Dict[str, Decimal]) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return Decimal(str(node.value))
            raise FormulaEvaluationError(f"Unsupported constant type: {type(node.value)}")

        elif isinstance(node, ast.Name):
            var_name = node.id.upper()
            if var_name in variables:
                return variables[var_name]
            raise FormulaEvaluationError(f"Unknown variable in formula: {var_name}")

        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand, variables)
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return +operand
            raise FormulaEvaluationError(f"Unsupported unary operator: {type(node.op)}")

        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left, variables)
            right = cls._eval_node(node.right, variables)

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    return Decimal("0.00")
                return left / right
            elif isinstance(node.op, ast.Mod):
                return left % right
            raise FormulaEvaluationError(f"Unsupported binary operator: {type(node.op)}")

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise FormulaEvaluationError("Complex function calls are not allowed")
            func_name = node.func.id.lower()
            if func_name not in cls.ALLOWED_FUNCTIONS:
                raise FormulaEvaluationError(f"Function '{func_name}' is not permitted")

            args = [cls._eval_node(arg, variables) for arg in node.args]
            return Decimal(str(cls.ALLOWED_FUNCTIONS[func_name](*args)))

        else:
            raise FormulaEvaluationError(f"Unsupported expression syntax: {type(node).__name__}")
