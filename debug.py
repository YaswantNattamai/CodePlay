from lexer import lexer
from parser import parser
from semantic import compile_ast
import json

with open("test_snippet.txt", "r") as f:
    data = f.read()

try:
    print("Parsing...")
    ast = parser.parse(data, lexer=lexer)
    print("Parsed AST:")
    print(json.dumps(ast, indent=2))
    print("Compiling...")
    ir = compile_ast(ast)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
