#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Buffer import Buffer
from Lexico import Lexico

if __name__ == '__main__':
    Buffer = Buffer()
    Lexico = Lexico()

    token = []
    lexema = []
    linha = []

    for i in Buffer.load_buffer():
        recept, ident, x = Lexico.token_def(i)
        token += recept
        lexema += ident
        linha += x