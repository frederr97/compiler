import re

class Lexico:
    x_num = 1

    def token_def(self, code):
        rules = [
            ('MAIN', r'main'),          
            ('INT', r'int'),            
            ('FLOAT', r'float'),        
            ('IF', r'if'),              
            ('ELSE', r'else'),          
            ('WHILE', r'while'),        
            ('READ', r'read'),          
            ('PRINT', r'print'),        
            ('LBRACKET', r'\('),        
            ('RBRACKET', r'\)'),        
            ('LBRACE', r'\{'),         
            ('RBRACE', r'\}'),          
            ('COMMA', r','),            
            ('PCOMMA', r';'),           
            ('EQ', r'=='),              
            ('NE', r'!='),              
            ('LE', r'<='),              
            ('GE', r'>='),              
            ('OR', r'\|\|'),            
            ('AND', r'&&'),             
            ('ATTR', r'\='),            
            ('LT', r'<'),               
            ('GT', r'>'),               
            ('PLUS', r'\+'),            
            ('MINUS', r'-'),            
            ('MULT', r'\*'),            
            ('DIV', r'\/'),             
            ('ID', r'[a-zA-Z]\w*'),    
            ('FLOAT_CONST', r'\d(\d)*\.\d(\d)*'),   
            ('INTEGER_CONST', r'\d(\d)*'),         
            ('NEWLINE', r'\n'),         
            ('SKIP', r'[ \t]+'),        
            ('MISMATCH', r'.'),         
        ]

        tokens_join = '|'.join('(?P<%s>%s)' % i for i in rules)
        x_start = 0
        token = []
        lexema = []
        linha = []

        print('Token - Lexema - Linha')
        for m in re.finditer(tokens_join, code):
            token_type = m.lastgroup
            token_lexema = m.group(token_type)

            if token_type == 'NEWLINE':
                x_start = m.end()
                self.x_num += 1
            elif token_type == 'SKIP':
                continue
            elif token_type == 'MISMATCH':
                raise RuntimeError('Erro na linha %d.' % (token_lexema, self.x_num))
            else:
                token.append(token_type)
                lexema.append(token_lexema)
                linha.append(self.x_num)
                print(token_type, '\t\t', token_lexema,'\t\t', self.x_num)

        return token, lexema, linha
