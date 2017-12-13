#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import re
import unicodedata

from Lexico import *

auxilier = 0
base = 0

class Operand():
    def __init__(self):
        self.name = None;
        self.principalorary = None;
        self.tableEntry = None;
#Classe para gerar Label Ln
class Label(Operand):
    def __init__(self):
        global auxilier;
        self.name = "L"+str(auxilier);
        auxilier= auxilier+1;
#Classe para gerar os principalorários Tn
class Temp():
    def __init__(self):
        global base;
        self.name = "T" + str(base);
        base = base + 1;
