#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import unicodedata

from Caller import *

class Lexico(object):
	def __init__(self):
		self.Buffer = []
		self.SymbolTable = []
		self.Tokens = {'tokens':[],
					  	    'lexeme':[],
					  	    'lines':[],
							'reserveds':['main','if','else','while','read','print','int','float'],
							'separators':[' ', '\n', '\t', '(', ')','{','}',',',';','\r'],
						    'operators':['+','-','*','/','=','<','<=','>','>=','==','!=','&&','||'],				  	    
							'identifiers':[],					  	    
					    	'integer': [], 
							'float': [], 
							'reserves1':[],
					  	    'reserves2':[],
					  	    'reserves3':[],
							'reserves4':[],	
					  	    'ocorrencias':[],
					  	    'errors':[]}
		self.anexer = ['<', '>', '=', '!', '|', '&']
		self.lister = ['=', '|', '&']
		file = open('entrada.txt', 'r')
		self.index = list(file.read())
		self.line = 0
	
	def run(self):
		while(len(self.index)):
			c = self.index[0]
			self.index.pop(0)

			if(self.separator(c) or self.operator(c)):
				token = ''.join(self.Buffer)
				if (token is not ''):
					self.LookUp(token)

				self.LookUp(c)
				self.Buffer = []
			else:
				self.Buffer.append(c)	

	def separator(self, token):	
		if (token in self.Tokens['separators']):
			return True
				
		return False

	def operator(self, token):						
			if (token in self.Tokens['operators'] or (token == '!' and self.index[0] == '=') or 
				(token == '&' and self.index[0] == '&') or (token == '|' and self.index[0] == '|')  ):
				return True
			return False

	def convert(self, token):
		result = [False, '']
		if (token in self.Tokens['operators'] or token == '!' or token == '&' or token == '|'):
			result = [True, str(token)]
			if (token in self.anexer and self.index[0] in self.lister):
				result = [True, str(token) + str(self.index[0])]
				self.index.pop(0)

		return result

	def reserveds(self, token):
		if (token in self.Tokens['reserveds']):
			return True
		return False

	def conversion1(self, token):
		result = re.match("^-?\\d*(\\d+)?$", token)

		if (result is not None):
			return True
		return False

	def conversion2(self, token):
		result = re.match("([0-9]+[.])+[0-9]+", token)
		if (result is not None):
			return True
		return False

	def addToken(self, token, named):
		self.Tokens[named].append(token)

	def LookUp(self, token):
		named = ''
		timed = ''
		line = ''

		if (self.operator(token)):
			result = self.convert(token)
			if (result[0]):
				token = result[1]
			#Identifica = e gera um token ATTR
			if (token == "="):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')	
				lexeme = "ATTR"
				self.addToken(lexeme,'tokens')	
			#Identifica < e gera um token LT
			if (token == "<"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "LT"
				self.addToken(lexeme,'tokens')
			#Identifica <= e gera um token LE	
			if (token == "<="):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "LE"
				self.addToken(lexeme,'tokens')
			#Identifica > e gera um token GT
			if (token == ">"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "GT"
				self.addToken(lexeme,'tokens')
			#Identifica >= e gera um token GE	
			if (token == ">="):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "GE"
				self.addToken(lexeme,'tokens')	
			#Identifica == e gera um token EQ	
			if (token == "=="):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "EQ"
				self.addToken(lexeme,'tokens')	
			#Identifica != e gera um token NE	
			if (token == "!="):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "NE"
				self.addToken(lexeme,'tokens')
			#Identifica || e gera um token OR
			if (token == "||"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "OR"
				self.addToken(lexeme,'tokens')
			#Identifica && e gera um token AND
			if (token == "&&"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "AND"
				self.addToken(lexeme,'tokens')
			#Identifica + e gera um token PLUS	
			if (token == "+"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "PLUS"
				self.addToken(lexeme,'tokens')
			#Identifica - e gera um token MINUS	
			if (token == "-"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "MINUS"
				self.addToken(lexeme,'tokens')
			#Identifica * e gera um token MULT
			if (token == "*"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "MULT"
				self.addToken(lexeme,'tokens')
			#Identifica / e gera um token DIV	
			if (token == "/"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "DIV"
				self.addToken(lexeme,'tokens')
				
			named = 'operators'
			self.addToken(token, 'reserves1')

			if (token != '!'):
				timed = self.Tokens[named].index(token)
				ocorrencia = List(named, timed, self.line)
			else :
				ocorrencia = List(named, 10, self.line)
			if (token != '&'):
				timed = self.Tokens[named].index(token)
				ocorrencia = List(named, timed, self.line)
			else :
				ocorrencia = List(named, 10, self.line)	
			if (token != '|'):
				timed = self.Tokens[named].index(token)
				ocorrencia = List(named, timed, self.line)
			else :
				ocorrencia = List(named, 10, self.line)

		elif (self.separator(token)):
			#Identifica quebra de line
			if(token == '\n'):				
				self.line +=1;
			#Identifica ( e gera um token LBRACKET	
			if (token == "("):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "LBRACKET"
				self.addToken(lexeme,'tokens')
			#Identifica ) e gera um token RBRACKET	
			if (token == ")"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "RBRACKET"
				self.addToken(lexeme,'tokens')
			#Identifica { e gera um token LBRACE	
			if (token == "{"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "LBRACE"
				self.addToken(lexeme,'tokens')
			#Identifica } e gera um token RBRACE	
			if (token == "}"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "RBRACE"
				self.addToken(lexeme,'tokens')
			#Identifica , e gera um token COMMA	
			if (token == ","):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "COMMA"
				self.addToken(lexeme,'tokens')
			#Identifica ; e gera um token PCOMMA	
			if (token == ";"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "PCOMMA"
				self.addToken(lexeme,'tokens')	

			named = 'separators'
			self.addToken(token, 'reserves2')
			timed = self.Tokens[named].index(token)
			ocorrencia = List(named, timed, self.line)
		

		elif(self.reserveds(token)):
			#Identifica read e gera um token READ	
			if (token == "read"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "READ"
				self.addToken(lexeme,'tokens')	
			#Identifica print e gera um token PRINT	
			if (token == "print"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "PRINT"
				self.addToken(lexeme,'tokens')
			#Identifica int e gera um token INT
			if (token == "int"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "INT"
				self.addToken(lexeme,'tokens')
			#Identifica float e gera um token FLOAT	
			if (token == "float"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "FLOAT"
				self.addToken(lexeme,'tokens')	
			#Identifica main e gera um token MAIN	
			if (token == "main"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "MAIN"
				self.addToken(lexeme,'tokens')
			#Identifica if e gera um token IF	
			if (token == "if"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "IF"
				self.addToken(lexeme,'tokens')
			#Identifica else e gera um token ELSE	
			if (token == "else"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "ELSE"
				self.addToken(lexeme,'tokens')
			#Identifica while e gera um token WHILE	
			if (token == "while"):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "WHILE"
				self.addToken(lexeme,'tokens')		
							
			named = 'reserveds'
			self.addToken(token, 'reserves3')
			timed = self.Tokens[named].index(token)
			ocorrencia = List(named, timed, self.line)

		elif(self.conversion2(token)):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "FLOAT_CONST"
				self.addToken(lexeme,'tokens')
				named = 'float'
				self.addToken(token, named)
				timed = self.Tokens[named].index(token)
				ocorrencia = List(named, timed, self.line)

		elif(self.conversion1(token)):
			self.addToken(token,'lexeme')
			self.addToken(self.line,'lines')
			lexeme = "INTEGER_CONST"
			self.addToken(lexeme,'tokens')
			named = 'integer'
			self.addToken(token, named)
			timed = self.Tokens[named].index(token)
			ocorrencia = List(named, timed, self.line)

		else:
			result = re.match('[A-Za-z]([A-Za-z]|[0-9])*', token)
			if (result is None):
				named = 'errors'
				self.addToken(token, named)
				timed = self.Tokens[named].index(token)
				
			named = 'reserves4'		
			if(token not in self.Tokens['errors']):
				self.addToken(token,'lexeme')
				self.addToken(self.line,'lines')
				lexeme = "ID"
				self.addToken(lexeme,'tokens')
				self.addToken(token, named)
				timed = self.Tokens[named].index(token)

		ocorrencia = List(named, timed, self.line)
		self.addToken(ocorrencia, 'ocorrencias')

class List(object):
	def __init__(self, fax, indexer, line):
		self.named = fax
		self.timed = indexer
		self.line = line