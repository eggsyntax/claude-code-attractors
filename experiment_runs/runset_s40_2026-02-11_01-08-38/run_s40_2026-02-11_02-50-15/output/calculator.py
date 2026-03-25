#!/usr/bin/env python3
"""
A collaborative calculator implementation by Dave and Tara
Supports variables, functions, and basic arithmetic
"""

from typing import Dict, List, Union, Callable
from enum import Enum
import re

class TokenType(Enum):
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    ASSIGN = "ASSIGN"
    EOF = "EOF"

class Token:
    def __init__(self, type_: TokenType, value: str, position: int = 0):
        self.type = type_
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def error(self, message: str):
        raise ValueError(f"Lexer error at position {self.pos}: {message}")

    def advance(self):
        """Move to next character"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self) -> str:
        """Parse a number (integer or float)"""
        result = ''
        while (self.current_char is not None and
               (self.current_char.isdigit() or self.current_char == '.')):
            result += self.current_char
            self.advance()
        return result

    def identifier(self) -> str:
        """Parse an identifier (variable or function name)"""
        result = ''
        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        return result