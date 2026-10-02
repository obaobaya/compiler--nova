# lexer.py

import re

# یک توکن ساده با نوع و مقدار
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"{self.type}: {self.value}"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.position = 0

    # الگوهای ساده برای مثال: اعداد، کلمات کلیدی، شناسه‌ها و عملیات ساده
    token_specification = [
        ("NUMBER",  r"d+"),
        ("ID",      r"[A-Za-z_]w*"),
        ("PLUS",    r"+"),
        ("MINUS",   r"-"),
        ("MUL",     r"*"),
        ("DIV",     r"/"),
        ("LPAREN",  r"("),
        ("RPAREN",  r")"),
        ("SKIP",    r"[ t]+"),
        ("MISMATCH",r"."),
    ]

    def tokenize(self):
        tokens = []
        patterns = "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.token_specification)
        regex = re.compile(patterns)

        for match in regex.finditer(self.text):
            kind = match.lastgroup
            value = match.group()
            if kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                raise RuntimeError(f"Unexpected character: {value}")
            else:
                tokens.append(Token(kind, value))
        return tokens 