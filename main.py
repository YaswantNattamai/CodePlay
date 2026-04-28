from lexer import lexer
from parser import parser
from semantic import compile_ast
import json
import os
import subprocess

data = """
PATTERN groove {
    DRUMS: KICK every 0.5, HAT every 0.25
    BASS: C2 [0.0-0.5] @90
}

LOOP 2 {
    SECOND 1 {
        USE groove
        LEAD: C5 [0.0-0.5] @80 REVERB DELAY
        PAD: E4 [0.0-1.0] @70 REVERB
    }
}
"""

def main():
    print("---- PARSER OUTPUT ----")
    ast = parser.parse(data, lexer=lexer)

    print("\n---- SEMANTIC EXPANSION ----")
    ir = compile_ast(ast)
    
    with open("ir.json", "w") as f:
        json.dump(ir, f, indent=2)
    print("Saved to ir.json")
    
    print("\n---- AUDIO SYNTHESIS ----")
    from gen_audio import generate_audio
    generate_audio("ir.json", "output.wav")
    
    print("\n---- FFMPEG EFFECTS & MP3 EXPORT ----")
    # Determine effects from IR
    global_effs = ir.get('effects', {}).get('global', [])
    track_effs = ir.get('effects', {}).get('per_track', {})
    
    has_reverb = "REVERB" in global_effs or any("REVERB" in effs for effs in track_effs.values())
    has_delay = "DELAY" in global_effs or any("DELAY" in effs for effs in track_effs.values())
    
    filters = []
    if has_reverb:
        filters.append("aecho=0.8:0.88:60:0.4")
    if has_delay:
        filters.append("aecho=0.8:0.9:500:0.3")
        
    filter_str = f"-af {','.join(filters)}" if filters else ""
    
    # Run ffmpeg to convert to MP3
    cmd = f"ffmpeg -y -i output.wav {filter_str} final_track.mp3"
    print(f"Running: {cmd}")
    
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Success! Saved as final_track.mp3")
    except subprocess.CalledProcessError:
        print("Error running ffmpeg. Make sure ffmpeg is installed and in PATH.")

if __name__ == "__main__":
    main()