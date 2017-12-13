#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import re
import unicodedata

from Caller import *
from Lexico import *
from Classes import *

file = open('ARQSAIDA.txt','w')
analisador = Lexico()
analisador.run()
Tokens = analisador.Tokens['tokens']
Lexemes = analisador.Tokens['lexeme']
Lines = analisador.Tokens['lines']
index = None
aux1 = 0
aux2 = 1
composer = {}
auxilier = 0
base = 0
type = []
armazem = {}

#Tabela de símbolos, configurando todos os IDs
def SymbolTable():
    for i in range(0,len(Tokens)):
        #Reconhece se é um ID, através da análise obtida do léxico
        if((Tokens[i] == 'INT' and Tokens[i+1] == 'ID') or (Tokens[i] == 'FLOAT' and Tokens[i+1] == 'ID')):
            type = []
            type.append(Tokens[i])
            i += 1
            while(Tokens[i] != 'PCOMMA'):
                if(Tokens[i] == 'ID'):
                    armazem[Lexemes[i]] = (type, 0)
                    composer.update(armazem)
                    if(Tokens[i+1] == 'PCOMMA'):
                        armazem[Lexemes[i]] = (type, 0)
                        composer.update(armazem)
                    if(Tokens[i+1] == 'ATTR' and Tokens[i+2] == 'ID'):
                        armazem[Lexemes[i]] = (type, 0)
                        composer.update(armazem)
                    if((Tokens[i+1] == 'ATTR' and Tokens[i+2] == 'INTEGER_CONST') or (Tokens[i+1] == 'ATTR' or Tokens[i+2] == 'FLOAT_CONST')):
                        armazem[Lexemes[i]] = (type, Lexemes[i+2])
                        composer.update(armazem)
                    if(Tokens[i+1] == 'COMMA'):
                        armazem[Lexemes[i]] = (type, 0)
                        composer.update(armazem)
                i += 1

    return composer
#Cria a base da árvore, como o nó raiz e o passa para todos os outros nós filhos
class AST(object):
    def __init__(self, name, father):
         self.name = name;
         self.father = father         
         self.children = []
         self.address = None
         self.next = None
         self.type = None  
         self.value = None
         self.hasParenthesis = None
    #Define as funções padrões para a árvore, estas nas quais pegamos por predefinição em um fórum de Python para contrução da árvore  
    def __str__(self, level=0):
        ret = "\t"*level+ repr(self) +"\n"
        for child in self.children:
            if (child != None):
                ret += child.__str__(level+1) 
        return ret
    def __repr__(self):
        return self.name
    def __evaluate__(self):
        for child in self.children:
            if (child != None):
                x = child.__evaluate__()
    def __checkTypes__(self):
        for child in self.children:
            if (child != None):
                child.__checkTypes__()
    def generateCode(self):
        for child in self.children:
            child.generateCode();

class Compound(AST):
    def __init__(self,father):
        AST.__init__(self,'Block',father)
    def __repr__(self):
        return self.name

    def __codegen__(self):
        code = " ";
        for child in self.children:
            code += child.__codegen__();
        return "{" + code + "}"

class Assign(AST):
    def __init__(self, left, op, right, father):
        AST.__init__(self,'Assign',father);
        self.children.append(left)
        self.children.append(right)
        self.left = left
        self.token = self.op = op
        self.right = right
        self.isDecl = None
    #Funções padrões de atribução para nós da árvore
    def __repr__(self):
        return self.name

    def __setIsDecl__(self, isDecl):
        self.isDecl = isDecl
    #Criação do evaluate, para caminhar na árvore
    def __evaluate__(self):
        index = self.children[0]
        lex = index.lexeme
        type = composer[lex][0]
        combine = {}
        expr_value = self.children[1].__evaluate__()
        if(expr_value != True or expr_value != False):
        	combine[lex] = (type, expr_value)
        	composer.update(combine)

    def __codegen__(self):
        if (self.isDecl):
            index = self.children[0]
            te = tabSimbolos.getEntry(index.token.lexeme)
            return typeNames[te.type] + " " + self.children[0].__codegen__() + " = " + self.children[1].__codegen__() + ";"
        else:
            return self.children[0].__codegen__() + " = " + self.children[1].__codegen__() + ";"
    #Definição do primeiro tipo de geração de código de três endereços
    def generateCode(self):
        self.children[0].generateCode()
        self.children[1].generateRValueCode()
        self.children[0].address.principalorary = (self.children[1].address.principalorary)
        file.write(self.children[0].lexeme + " = " + self.children[1].address.name + "\n")

class If(AST):
    def __init__(self, exp, c_true, c_false, father):
        AST.__init__(self, 'If', father)
        self.children.append(exp)
        self.children.append(c_true)
        self.children.append(c_false)
        self.exp = exp
        self.c_true = c_true
        self.c_false = c_false
    def __init__(self,name):
    	AST.__init__(self, name, None)
    #Funções padrão    
    def __repr__(self):
        return self.name
    #Faz o evaluate para um nó IF dos filhos da esquerda e da direita
    def __evaluate__(self):
        item = self.children[0].__evaluate__()
        if(item == True):
            self.children[1].__evaluate__()
        else:
        	if(len(self.children) is not 2):
        		self.children[2].__evaluate__()
    #Definição do primeiro tipo de geração de código de três endereços para a classe IF
    def generateCode(self):
        self.next = Label()
        if (len(self.children) == 3): 
            self.children[0].true_label = Label()
            self.children[0].false_label = Label()
            self.children[0].next = self.children[1].next = self.next
            self.children[0].generateBranchCode(); 
            if (self.children[0].address != None):
                #Escreve no arquivo o código do IF comparado à 0
                file.write("if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n")
            else:
                file.write( self.children[0].true_label.name + ":")
            self.children[1].generateCode()
            #Escreve no arquivo o código do goto para um determinado label
            file.write("goto " + self.next.name + "\n")
            file.write(self.children[0].false_label.name + ":")
            self.children[2].generateCode()
        else:
            self.children[0].true_label = Label()
            self.children[0].false_label = self.children[1].next = self.next
            self.children[0].generateBranchCode()
            if (self.children[0].address != None):
                #Escreve no arquivo o código do IF comparado à 0
                file.write("if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n")
            else:
                file.write(self.children[0].true_label.name + ":")
            self.children[1].generateCode()
        file.write(self.next.name + ":")

class While(AST):
    def __init__(self, exp, commands, father):
        AST.__init__(self,'While', father)
        self.children.append(exp)
        self.children.append(commands)
        self.exp = exp;
        self.commands = commands;
    def __init__(self,name):
    	AST.__init__(self, name, None)
    def __repr__(self):
        return self.name
    #Faz o evaluate para um nó WHILE dos filhos da esquerda e da direita    
    def __evaluate__(self):
        item = self.children[0].__evaluate__()
        while(item == True):
        	self.children[1].__evaluate__()
        	item = self.children[0].__evaluate__()
    #Definição do primeiro tipo de geração de código de três endereços para a classe WHILE
    def generateCode(self):
        self.begin = Label()
        self.children[0].true_label = Label()
        self.children[0].false_label = self.next = Label()
        self.children[1].next = self.begin
        file.write(self.begin.name + ":")
        self.children[0].generateBranchCode()  
        if (self.children[0].address != None):
            #Escreve no arquivo o código do If comparado a 0, para quando encontrar um nó WHILE
            file.write("if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n")
        else:
            file.write(self.children[0].true_label.name + ":")
        self.children[1].generateCode()
        file.write("goto " + self.begin.name + "\n")
        file.write(self.next.name + ":")

#Só para árvore, não geramos código de três endereços
class Read(AST):
    def __init__(self, id_, father):
        AST.__init__(self,'Read', father)
        self.children.append(id_)
        self.id = id_;
    def __init__(self,name):
    	AST.__init__(self, name, None)
    def __repr__(self):
        return self.name

#Só para árvore, não geramos código de três endereços
class Print(AST):
    def __init__(self, exp, father):
        AST.__init__(self,'Print', father)
        print('Criando um nó do type Print.')
        self.children.append(exp)
        self.exp = exp;
    def __init__(self,name):
		AST.__init__(self, name, None)

    def __repr__(self):
        return self.name

class BinOp(AST):
    def __init__(self, name, left, op, right, father):
        AST.__init__(self,name, father)
        self.children.append(left)
        self.children.append(right)
        self.left = left
        self.op = op
        self.right = right
    #Funções padrões da árvore para um nó de operador binário
    def __repr__(self):
        return self.op
    def __evaluate__(self):
        for child in self.children:
            if (child != None):
                return child.__evaluate__()
    def __codegen__(self):
        return self.left.__codegen__() + self.op + self.right.__codegen__()

class LogicalOp(BinOp):
    def __init__(self, left, op, right, father):
        BinOp.__init__(self,'LogicalOp',left, op, right, father)
    #Definição do evaluate para caminhamento dos filhos, tanto da esquerda como da direita
    def __evaluate__(self):
    	a = self.children[0].__evaluate__()
        b = self.children[1].__evaluate__()
        #Reconhece primeiro qual é o operador lógico
    	if(self.op == '&&'):
        	if(a is True and b is True):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '||'):
        	if(a is True or b is True):
        		c = True
        		return c
        	else:
        		c = False
        		return c
    #Definição do segundo tipo de geração de código de três endereços para a classe de operadores lógicos, onde esses nós são filhos de um IF ou WHILE
    def generateBranchCode(self):
        if (self.op == "||"):
            #Cria os labels para ambos os filhos do nó
            self.children[0].true_label = self.true_label;
            self.children[0].false_label = Label();
            self.children[1].true_label = self.true_label;
            self.children[1].false_label = self.false_label;
            self.children[0].generateBranchCode();
            if (self.children[0].address != None):
                #Escreve no arquivo o if comparado à não zero para a classe de lógicos
                file.write( "if " + self.children[0].address.name + " != 0 goto " + self.children[0].true_label.name + "\n");
            else:
                file.write( self.children[0].false_label.name + ":");
            self.children[1].generateBranchCode();
            if (self.children[1].address != None):
                #Escreve no arquivo o if comparado à 0 e do goto para o label
                file.write( "if " + self.children[1].address.name + " == 0 goto " + self.children[1].false_label.name + "\n");
                file.write( "goto " + self.children[1].true_label.name + "\n");
        elif (self.op == "&&"):
            self.children[0].true_label = Label();
            self.children[0].false_label = self.false_label;
            self.children[1].true_label = self.true_label;
            self.children[1].false_label = self.false_label;
            self.children[0].generateBranchCode();
            if (self.children[0].address != None): 
                 file.write( "if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n");
            else:
                file.write( self.children[0].true_label.name + ":");
            self.children[1].generateBranchCode() ;
            if (self.children[1].address != None):
                file.write( "if " + self.children[1].address.name + " == 0 goto " + self.children[1].false_label.name + "\n");
                file.write( "goto " + self.children[1].true_label.name + "\n");
    #Geração do terceiro tipo de código de três endereços, para nós filhos de uma expressão de atribuição
    def generateRValueCode(self):
        self.true_label = Label()
        self.false_label = Label()
        self.next = Label()
        self.address = Operand()
        #Compara se é um nó de OR
        if(self.op == "||"):
            self.children[0].generateRValueCode()
            self.children[1].generateRValueCode()
            teste = self.children[0].address.name + " " + "!= 0"
            teste1 = self.children[1].address.name + " " + "!= 0"
            principal = Temp()
            #Escreve no arquivo a geração do if simples para desvio
            file.write("if " + teste + " goto " + self.true_label.name + "\n")
            file.write("if " + teste1 + " goto " + self.true_label.name + "\n")
            file.write(principal.name+"=0\n"+" goto "+self.next.name+"\n");
            file.write(self.true_label.name+":"+principal.name+"=1\n");
            self.address.principalorary = principal
            self.address.name = principal.name
            file.write(self.next.name+":")
        #Compara se é um nó de AND    
        elif(self.op == "&&"):
            self.children[0].generateRValueCode()
            self.children[1].generateRValueCode()
            teste = self.children[0].address.name + " " + "== 0"
            teste1 = self.children[1].address.name + " " + "== 0"
            principal = Temp()
            #Escreve no arquivo a geração do if simples para desvio
            file.write("if " + teste + " goto " + self.false_label.name + "\n")
            file.write("if " + teste1 + " goto " + self.false_label.name + "\n")
            file.write(principal.name+"= 1\n"+" goto "+self.next.name+"\n");
            file.write(self.false_label.name+":"+principal.name+"=0\n");
            self.address.principalorary = principal
            self.address.name = principal.name
            file.write(self.next.name+":") 

class ArithOp(BinOp):
    def __init__(self, left, op, right, father):
        BinOp.__init__(self,'ArithOp',left, op, right, father)
    def __evaluate__(self):
        a = self.children[0].__evaluate__()
        b = self.children[1].__evaluate__()
        #Verifica qual tipo de operador aritmético é o nó em questão 
        if(self.op == '+'):
        	c = float(a) + float(b)
        	return c
        elif(self.op == '-'):
        	c = float(a) - float(b)
        	return c
        elif(self.op == '*'):
            c = float(a) * float(b)
            return c
        elif(self.op == '/'):
            c = float(a) / float(b)
            return c
    def __codegen__(self):
        return self.left.__codegen__() + self.op + self.right.__codegen__()
    #Gera o segundo tipo de geração de código para os dois filhos do nó de operador aritmético, já que pode ser filho de uma expressão de IF ou WHILE    
    def generateBranchCode(self):
        self.children[0].generateBranchCode();
        self.children[1].generateBranchCode();
        principal = Temp();
        self.address = Operand();
        self.address.principalorary = principal;
        self.address.name = principal.name;
        file.write(principal.name + " = " + self.children[0].address.name + " " + self.op + " " + self.children[1].address.name + "\n");
    #Gera o terceiro tipo de geração de código, considerando que podem ser filhos de uma expressão de atribuição
    def generateRValueCode(self):
        self.children[0].generateRValueCode();
        self.children[1].generateRValueCode();
        principal = Temp();
        self.address = Operand();
        self.address.principalorary = principal;
        self.address.name = principal.name;
        file.write(principal.name + " = " + self.children[0].address.name + " " + self.op + " " + self.children[1].address.name + "\n");

class RelOp(BinOp):
    def __init__(self, left, op, right, father):
        BinOp.__init__(self,'RelOp',left, op, right, father)
    def __evaluate__(self):
    	a = self.children[0].__evaluate__()
        b = self.children[1].__evaluate__()
        #Verifica qual o tipo de operador relacional do nó
        if(self.op == '<'):
        	if(float(a) < float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '<='):
        	if(float(a) <= float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '>'):
        	if(float(a) > float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '>='):
        	if(float(a) >= float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '=='):
        	if(float(a) == float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '!='):
        	if(float(a) != float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
    #Gera o segundo tipo de geração de código para os dois filhos do nó de operador relacional, já que pode ser filho de uma expressão de IF ou WHILE
    def generateBranchCode(self):
        self.children[0].generateBranchCode() ;
        self.children[1].generateBranchCode() ;
        test = self.children[0].address.name + self.op + self.children[1].address.name;
        #Escreve no arquivo o if com desvio para um label determinado e depois o goto
        file.write("if " +  test +  " goto " +  self.true_label.name + "\n");
        file.write("goto " + self.false_label.name + "\n");
    #Gera o terceiro tipo de geração de código, considerando que podem ser filhos de uma expressão de atribuição
    def generateRValueCode(self):
        self.true_label = Label()
        self.false_label = Label()
        self.next = Label()
        self.address = Operand()
        principal = Temp()
        self.children[0].generateRValueCode()
        self.children[1].generateRValueCode()
        #Gera o if no arquivo, consequente do goto de um label
        file.write("if "+self.children[0].address.name + self.op + self.children[1].address.name +" goto "+ self.true_label.name+"\n");
        file.write(principal.name+ "= 0\n"+" goto "+self.next.name+"\n")
        file.write(self.true_label.name+":"+principal.name+"=1\n")
        file.write(self.next.name +":")
        self.address.principalorary = principal;
        self.address.name = principal.name;

class Id(AST):
    def __init__(self,token,lexeme,father):
        AST.__init__(self,'Id',father)
        self.token = token
        self.lexeme = lexeme
    #Funções padrão para caminhamento na árvore
    def __repr__(self):
        return self.token
    def __evaluate__(self):
        te = composer[self.lexeme][1]
        if (te != None):
            return te
        else:
            return 0;
    def generateCode(self):
        operand = Operand();
        operand.name =  self.lexeme;
        self.address = operand;
    def generateRValueCode(self):
        return self.generateCode();
    def generateBranchCode(self):
        return self.generateCode();

class Num(AST):
    def __init__(self, token, father, type):
        AST.__init__(self,'Num', father)
        self.token = token
        self.value = token 
        self.type = type
    #Funções padrão
    def __repr__(self):
        return self.value
    def __evaluate__(self):
        return self.value
    def __checkTypes__(self):
        return self.type
    def __convertTo__(self, novotype):
        self.type = novotype
    def __codegen__(self):
        return str(self.value)
    def generateCode(self):
        operand = Operand();
        operand.name = self.value;
        self.address = operand;
    def generateBranchCode(self):
        return self.generateCode();
    def generateRValueCode(self):
        return self.generateCode();

#Definição da função de match, para casar os tokens com a gramática
def match(token):
	if(Tokens[0] == token):
		Tokens.pop(0)
		Lexemes.pop(0)
		Lines.pop(0)
#Programa → INT MAIN LBRACKET RBRACKET LBRACE Decl_Comando RBRACE
def Programa():
	match('INT')
	match('MAIN')
	match('LBRACKET')
	match('RBRACKET')
	match('LBRACE')
	backthrow = AST('decl_comando', None)
   	root = Decl_Comando(backthrow);
	match('RBRACE')
	return root
#Decl_Comando → Declaracao Decl_Comando | Comando Decl_Comando | ε
def Decl_Comando(backthrow):
    if (Tokens[0] == 'INT' or Tokens[0] == 'FLOAT'):
        mont = Declaracao(backthrow);
        return Decl_Comando(mont);
    elif (Tokens[0] == 'ID' or Tokens[0] == 'IF' or Tokens[0] == 'WHILE' or Tokens[0] == 'PRINT'
          or Tokens[0] == 'READ' or Tokens[0] == 'LBRACE'):
       	mont = Comando(backthrow);
       	return Decl_Comando(mont);
    else:
    	return backthrow
#Declaracao → Tipo ID Decl2
def Declaracao(backthrow):
	global index
	Tipo();
	if(Tokens[0] == 'ID'):
		index = Id(Tokens[0],Lexemes[0],None)
		match('ID')
	return Decl2(backthrow);
#Decl2 → COMMA ID Decl2 | PCOMMA | ATTR Expressao Decl2
def Decl2(backthrow):
	global index
	if(Tokens[0] == 'COMMA'):
		match('COMMA')
		index = Id(Tokens[0],Lexemes[0],None)
		match('ID')
		return Decl2(backthrow)
	elif(Tokens[0] == 'PCOMMA'):
		match('PCOMMA')
		return backthrow
	elif(Tokens[0] == 'ATTR'):
		match('ATTR')
		son_x = Expressao()
		attr_node = Assign(index,'=',son_x,None)
		backthrow.children.append(attr_node)
		return Decl2(backthrow);
  	return backthrow;
#Tipo → INT | FLOAT
def Tipo():
	if(Tokens[0] == 'INT'):
		match('INT')
	elif(Tokens[0] == 'FLOAT'):
		match('FLOAT')
#Comando → Bloco | Atribuicao | ComandoSe | ComandoEnquanto | ComandoRead | ComandoPrint
def Comando(backthrow):
	if(Tokens[0] == 'LBRACE'):
		return Bloco(backthrow)
	elif(Tokens[0] == 'ID'):
		return Atribuicao(backthrow)
	elif(Tokens[0] == 'IF'):
		return ComandoSe(backthrow)
	elif(Tokens[0] == 'WHILE'):
		return ComandoEnquanto(backthrow)
	elif(Tokens[0] == 'READ'):
		return ComandoRead(backthrow)
	elif(Tokens[0] == 'PRINT'):
		return ComandoPrint(backthrow)
#Bloco → LBRACE Decl_Comando RBRACE
def Bloco(backthrow):
	match('LBRACE')
	bloco = AST('Bloco',None)
	intro = Decl_Comando(bloco)
	match('RBRACE')
	backthrow.children.append(intro)
	return backthrow
#Atribuicao → ID ATTR Expressao PCOMMA
def Atribuicao(backthrow):
	index = Id(Tokens[0],Lexemes[0],None)
	match('ID')
	match('ATTR')
	son_x = Expressao()
	backthrow.children.append(Assign(index,'=',son_x,None));
	match('PCOMMA')
	return backthrow
#ComandoSe → IF LBRACKET Expressao RBRACKET Comando ComandoSenao
def ComandoSe(backthrow):
    son_i = If('IF')
    match('IF')
    match('LBRACKET')
    son_x = Expressao()
    son_i.children.append(son_x)
    match('RBRACKET')
    c_true = AST('C_TRUE',None)
    intro = Comando(c_true)
    son_i.children.append(intro)
    ComandoSenao(son_i)
    backthrow.children.append(son_i)
    return backthrow
#ComandoSenao → ELSE Comando | ε
def ComandoSenao(son_i):
	if(Tokens[0] == 'ELSE'):
		c_false = AST('C_FALSE',None)
		match('ELSE')
		intro = Comando(c_false)
		son_i.children.append(intro)
		return son_i
	else :
		return son_i
#ComandoEnquanto → WHILE LBRACKET Expressao RBRACKET Comando
def ComandoEnquanto(backthrow):
	while_node = While('WHILE')
	match('WHILE')
	match('LBRACKET')
	son_x = Expressao()
	while_node.children.append(son_x)
	match('RBRACKET')
	c_true = AST('C_TRUE',None)
	intro = Comando(c_true)
	while_node.children.append(intro)
	backthrow.children.append(while_node)
	return backthrow
#ComandoRead → READ ID PCOMMA
def ComandoRead(backthrow):
    read_node = Read('READ')
    match('READ')
    index = Id(Tokens[0],Lexemes[0],None)
    read_node.children.append(index)
    match('ID')
    match('PCOMMA')
    backthrow.children.append(read_node)
    return backthrow
#ComandoPrint → PRINT LBRACKET Expressao RBRACKET PCOMMA
def ComandoPrint(backthrow):
	print_node = Print('PRINT')
	match('PRINT')
	match('LBRACKET')
	expression = Expressao()
	print_node.children.append(expression)
	match('RBRACKET')
	match('PCOMMA')
	backthrow.children.append(print_node)
	return backthrow
#Expressao → Conjuncao ExpressaoOpc
def Expressao():
    expression = Conjuncao();
    return ExpressaoOpc(expression);
#ExpressaoOpc → OR Conjuncao ExpressaoOpc | ε
def ExpressaoOpc(expression):
	if(Tokens[0] == 'OR'):
		match('OR')
		expression_aux = Conjuncao()
		or_node = LogicalOp(expression,'||',expression_aux,None)
		expression_aux = ExpressaoOpc(or_node)
		return expression_aux
	else:
		return expression
#Conjuncao → Igualdade ConjuncaoOpc
def Conjuncao():
	expression = Igualdade()
	return ConjuncaoOpc(expression)
#ConjuncaoOpc → AND Igualdade ConjuncaoOpc | ε
def ConjuncaoOpc(expression):
	if(Tokens[0] == 'AND'):
		match('AND')
		expression_aux= Igualdade()
		and_node = LogicalOp(expression,'&&',expression_aux,None)
		expression_aux = ConjuncaoOpc(and_node)
		return expression_aux
	else :
		return expression
#Igualdade → Relacao IgualdadeOpc
def Igualdade():
	expression = Relacao()
	return IgualdadeOpc(expression)
#IgualdadeOpc → OpIgual Relacao IgualdadeOpc | ε
def IgualdadeOpc(expression):
	if(Tokens[0] == 'EQ'):
		OpIgual()
		expression_aux = Relacao()
		equal = RelOp(expression,'==',expression_aux,None)
		return IgualdadeOpc(equal)
	elif(Tokens[0] == 'NE'):
		OpIgual()
		expression_aux = Relacao()
		diferente_node = RelOp(expression,'!=',expression_aux,None)
		return IgualdadeOpc(diferente_node)
	else :
		return expression
#OpIgual → EQ | NE
def OpIgual():
	if(Tokens[0] == 'EQ'):
		match('EQ')
	elif(Tokens[0] == 'NE'):
		match('NE')
#Relacao → Adicao RelacaoOpc
def Relacao():
	expression = Adicao()
	return RelacaoOpc(expression)
#RelacaoOpc → OpRel Adicao RelacaoOpc | ε
def RelacaoOpc(expression):
	if(Tokens[0] == 'LT'):
		OpRel()
		expression_aux = Adicao()
		aux_min = RelOp(expression,'<',expression_aux,None)
		return RelacaoOpc(aux_min)
	elif(Tokens[0] == 'LE'):
		OpRel()
		expression_aux = Adicao()
		menorequal = RelOp(expression,'<=',expression_aux,None)
		return RelacaoOpc(menorequal)
	elif(Tokens[0] == 'GT'):
		OpRel()
		expression_aux = Adicao()
		aux_max = RelOp(expression,'>',expression_aux,None)
		return RelacaoOpc(aux_max)
	elif(Tokens[0] == 'GE'):
		OpRel()
		expression_aux = Adicao()
		maiorequal = RelOp(expression,'>=',expression_aux,None)
		return RelacaoOpc(maiorequal)
	else :
		return expression
#OpRel → LT | LE | GT | GE
def OpRel():
	if(Tokens[0] == 'LT' ):
		match('LT')
	elif(Tokens[0] == 'LE') :
		match('LE')
	elif(Tokens[0] == 'GT'):
		match('GT')
	elif(Tokens[0] == 'GE'):
		match('GE')
#Adicao → Termo AdicaoOpc
def Adicao():
	expression = Termo()
	return AdicaoOpc(expression)
#AdicaoOpc → OpAdicao Termo AdicaoOpc | ε
def AdicaoOpc(expression):
	if(Tokens[0] == 'PLUS'):
		OpAdicao()
		expression_aux = Termo()
		plus_node = ArithOp(expression,'+',expression_aux,None)
		return AdicaoOpc(plus_node)
	elif(Tokens[0] == 'MINUS'):
		OpAdicao()
		expression_aux = Termo()
		minus_node = ArithOp(expression,'-',expression_aux,None)
		return AdicaoOpc(minus_node)
	else:
		return expression
#OpAdicao → PLUS | MINUS
def OpAdicao():
	if(Tokens[0] == 'PLUS'):
		match('PLUS')
	elif(Tokens[0] == 'MINUS'):
		match('MINUS')
#Termo → Fator TermoOpc
def Termo():
	expression = Fator()
	return TermoOpc(expression)
#TermoOpc → OpMult Fator TermoOpc | ε
def TermoOpc(expression):
	if(Tokens[0] == 'MULT'):
		OpMult()
		expression_aux = Fator()
		mult_node = ArithOp(expression,'*',expression_aux,None)
		return TermoOpc(mult_node)
	elif(Tokens[0] == 'DIV'):
		OpMult()
		expression_aux = Fator()
		div_node = ArithOp(expression,'/',expression_aux,None)
		return TermoOpc(div_node)
	else:
		return expression
#OpMult → MULT | DIV
def OpMult():
	if(Tokens[0] == 'MULT'):
		match('MULT')
	elif(Tokens[0] == 'DIV'):
		match('DIV')
#Fator → ID | INTEGER_CONST | FLOAT_CONST | LBRACKET Expressao RBRACKET
def Fator():
	if(Tokens[0] == 'ID'):
		index = Id(Tokens[0],Lexemes[0],None)
		match('ID')
		return index
	elif(Tokens[0] == 'INTEGER_CONST'):
		num_node = Num(Lexemes[0],None,aux1)
		match('INTEGER_CONST')
		return num_node
	elif(Tokens[0] == 'FLOAT_CONST'):
		num_node = Num(Lexemes[0],None,aux2)
		match('FLOAT_CONST')
		return num_node
	elif(Tokens[0] == 'LBRACKET'):
		match('LBRACKET')
		expression = Expressao()
		match('RBRACKET')
		return expression