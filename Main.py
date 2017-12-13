#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Gerador import *
from Caller import *
from Lexico import *
from Classes import *

SymbolTable()

while(len(Tokens)>0):

	root = Programa()
	root.__evaluate__()
	root.generateCode()

file.close()

print "Arquivo com o código de 3 endereços gerado."