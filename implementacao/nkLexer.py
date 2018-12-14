import ply.lex as lex
import re as re
import sys

reservedList = {
   'se' : 'SE' ,
   'então' : 'ENTAO',
   'senão' : 'SENAO',
   'fim' : 'FIM',
   'repita' : 'REPITA',
   'até' : 'ATE',
   'inteiro' : 'INTEIRO',
   'flutuante' : 'FLUTUANTE',
   'leia' : 'LEIA',
   'escreva' : 'ESCREVA',
   'retorna' : 'RETORNA'
}

tokens = [ 'NEGATION','PLUS','MINUS','MULT','DIV','ATRIB','GREATEREQ','LESSEREQ','DIFF','DOISPONTOS','VIRGULA','LESSER','GREATER','EQUAL','LPARENTHESYS','RPARENTHESYS','LCOLCHETE','RCOLCHETE','AND','OR','FLOAT','INT','ID']+list(reservedList.values())

#t_SYB    = r'\+|-|:=|>=|<=|<>|:|\*|<|>|}|=|\(|\)|,|\[|\]|&&|\|\|'DOISPONTOS
t_PLUS  = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_ATRIB = r':='
t_GREATEREQ = r'>='
t_LESSEREQ = r'<='
t_VIRGULA = r','
t_DIFF = r'<>'
t_DOISPONTOS = r':'
t_LESSER = r'<'
t_GREATER = r'>'
t_NEGATION = r'!'

t_EQUAL = r'='
t_LPARENTHESYS=r'\('
t_RPARENTHESYS=r'\)'
t_LCOLCHETE=r'\['
t_RCOLCHETE=r'\]'
t_AND = r'&&'
t_OR = r'\|\|'
t_FLOAT = r'\d+\.\d+'
t_INT = r'\d+'
t_ignore  = ' \t\r\n'

def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_ID(t):
    r'_|([a-zA-ZáàÀÁâÂéèÈÉêÊíìÍÌóÓõÕôÕúÚçÇ])\w*_*\w*'
    t.type = reservedList.get(t.value,'ID')    # Check for reserved words
    return t

def t_COMMENT(t):
    r'{[^}]*}'
    

def applyLexer():
    f  = open(sys.argv[1],'r')
    input = f.read()
    f.close()

    lexer = lex.lex()
    lexer.input(input)
    file = open('output.txt','w');
    while True:
        tok = lexer.token()
        if (not tok):
            break      # No more input
        file.write("<"+tok.type+","+tok.value+">\n")
    file.close()
    print("Arquivo tokenizado output.txt gerado")

def start():
    if len(sys.argv)!=2:
        print("Digite o caminho do codigo de entrada apos a chamada do programa")
        sys.exit(0)

#start()
lexer = lex.lex()
#applyLexer()
