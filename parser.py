import ply.yacc as yacc
from lexer import tokens

def p_program(p):
    'program : blocks'
    p[0] = {
        "type": "program",
        "blocks": p[1]
    }

def p_blocks(p):
    '''blocks : block
              | block blocks'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_block(p):
    '''block : second_block
             | pattern_block
             | loop_block'''
    p[0] = p[1]

# =========================
# PATTERN
# =========================

def p_pattern_block(p):
    'pattern_block : PATTERN ID LBRACE instrument_blocks RBRACE'
    tracks = {}
    for instr, notes in p[4]:
        if instr not in tracks:
            tracks[instr] = []
        tracks[instr].extend(notes)
    
    p[0] = {
        "type": "pattern",
        "name": p[2],
        "tracks": tracks
    }

# =========================
# LOOP
# =========================

def p_loop_block(p):
    'loop_block : LOOP NUMBER LBRACE blocks RBRACE'
    p[0] = {
        "type": "loop",
        "count": p[2],
        "blocks": p[4]
    }

# =========================
# SECOND
# =========================

def p_second_block(p):
    'second_block : SECOND NUMBER LBRACE second_body RBRACE'
    p[0] = {
        "type": "second",
        "second": p[2],
        "body": p[4]
    }

def p_second_body(p):
    '''second_body : second_item
                   | second_item second_body'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_second_item(p):
    '''second_item : USE ID
                   | instrument_block'''
    if len(p) == 3:
        p[0] = {"type": "use", "name": p[2]}
    else:
        p[0] = {"type": "instrument", "data": p[1]}

# =========================
# INSTRUMENT BLOCKS
# =========================

def p_instrument_blocks(p):
    '''instrument_blocks : instrument_block
                         | instrument_block instrument_blocks'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_instrument_type(p):
    '''instrument_type : EP
                       | BASS
                       | DRUMS
                       | LEAD
                       | PAD
                       | STRINGS'''
    p[0] = p[1]

def p_instrument_block(p):
    'instrument_block : instrument_type COLON note_list'
    p[0] = (p[1], p[3])

# =========================
# NOTE LIST & EFFECTS
# =========================

def p_effect_list_opt(p):
    '''effect_list_opt : effect_list
                       | empty'''
    p[0] = p[1] if p[1] else []

def p_effect_list(p):
    '''effect_list : effect
                   | effect effect_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_effect(p):
    '''effect : REVERB
              | DELAY'''
    p[0] = p[1]

def p_note_list(p):
    '''note_list : note_item
                 | note_item COMMA note_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_note_item(p):
    '''note_item : note effect_list_opt
                 | drum effect_list_opt'''
    note = p[1]
    if p[2]:
        note['effects'] = p[2]
    p[0] = note

# =========================
# NOTE / DRUM
# =========================

def p_note(p):
    '''note : NOTE LBRACKET FLOAT DASH FLOAT RBRACKET
            | NOTE LBRACKET FLOAT DASH FLOAT RBRACKET AT NUMBER
            | NOTE EVERY FLOAT
            | NOTE EVERY FLOAT AT NUMBER'''
    if len(p) == 7:
        p[0] = {"note": p[1], "start": p[3], "end": p[5], "velocity": 64}
    elif len(p) == 9:
        p[0] = {"note": p[1], "start": p[3], "end": p[5], "velocity": p[8]}
    elif len(p) == 4:
        p[0] = {"note": p[1], "every": p[3], "velocity": 64}
    elif len(p) == 6:
        p[0] = {"note": p[1], "every": p[3], "velocity": p[6]}

def p_drum(p):
    '''drum : DRUM_NOTE LBRACKET FLOAT DASH FLOAT RBRACKET
            | DRUM_NOTE LBRACKET FLOAT DASH FLOAT RBRACKET AT NUMBER
            | DRUM_NOTE EVERY FLOAT
            | DRUM_NOTE EVERY FLOAT AT NUMBER'''
    if len(p) == 7:
        p[0] = {"note": p[1], "start": p[3], "end": p[5], "velocity": 64}
    elif len(p) == 9:
        p[0] = {"note": p[1], "start": p[3], "end": p[5], "velocity": p[8]}
    elif len(p) == 4:
        p[0] = {"note": p[1], "every": p[3], "velocity": 64}
    elif len(p) == 6:
        p[0] = {"note": p[1], "every": p[3], "velocity": p[6]}

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type}, value '{p.value}' at line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()