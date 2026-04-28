import ply.lex as lex 

reserved = {
    'SECOND': 'SECOND',
    'PATTERN': 'PATTERN',
    'USE': 'USE',
    'LOOP': 'LOOP',
    'every': 'EVERY',
    'EP': 'EP',
    'BASS': 'BASS',
    'DRUMS': 'DRUMS',
    'LEAD': 'LEAD',
    'PAD': 'PAD',
    'STRINGS': 'STRINGS',
    'REVERB': 'REVERB',
    'DELAY': 'DELAY'
}

tokens = [
    'NUMBER',
    'FLOAT',
    'NOTE',
    'DRUM_NOTE',
    'ID',
    'AT',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'COLON', 'COMMA', 'DASH',
] + list(reserved.values())

# =========================
# KEYWORDS & IDs
# =========================

# IDs are at the bottom
# =========================
# SYMBOLS
# =========================

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'
t_COMMA = r','
t_DASH = r'-'
t_AT = r'@'

# =========================
# DRUM NOTES
# =========================

def t_DRUM_NOTE(t):
    r'KICK|SNARE|HAT|CRASH'
    return t

# =========================
# NOTES
# =========================

def t_NOTE(t):
    r'[A-G](\#)?\d+'
    return t

# =========================
# NUMBERS
# =========================

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# =========================
# IDs
# =========================

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# =========================
# NEWLINES
# =========================

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t\r'

def t_error(t):
    print("Illegal character:", t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()