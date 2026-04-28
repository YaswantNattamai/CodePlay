from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from lexer import lexer
from parser import parser
from semantic import compile_ast
import json
from gen_audio import generate_audio
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str

@app.post("/compile")
def compile_code(input_data: CodeInput):
    try:
        ast = parser.parse(input_data.code, lexer=lexer)
        if not ast:
            raise HTTPException(status_code=400, detail="Syntax error in code")
            
        ir = compile_ast(ast)
        
        with open("ir.json", "w") as f:
            json.dump(ir, f)
            
        generate_audio("ir.json", "output.wav")
        
        return {"status": "success", "ir": ir}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/audio")
def get_audio():
    return FileResponse("output.wav", media_type="audio/wav", headers={"Cache-Control": "no-cache"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
