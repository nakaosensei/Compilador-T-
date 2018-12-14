import ply.lex as lex
import ply.yacc as yacc

import sys
from nkLexer import tokens
from nkLexer import lexer
from treelib import Tree
from graphviz import Digraph
import tabelaSimbolos as ts
from tabelaSimbolos import Symbol
from llvmlite import ir
class ReturnChecker:

    def __init__(self,value):
        self.value=value

class NkTree:

    def __init__(self, children, type, leaf=None):
        self.type = type
        self.children = children
        self.leaf = leaf
        self.label = ""
        self.sequenceId = 0

    def __str__(self):
        return self.type

    def getNextCount(self):
        self.count += 1
        return str(self.count)

    def setLabelId(self,value):
        self.label = self.type+str(value)

class NkParser:

    def __init__(self):
        self.precedence = (
            ('left', 'EQUAL', 'GREATEREQ', 'GREATER', 'LESSEREQ', 'LESSER'),
            ('left', 'PLUS', 'MINUS'),
            ('left', 'MULT', 'DIV')
        )
        self.lexer=lexer
        self.tokens=tokens
        self.montou=0
        self.exceptions = []
        self.warnings = []
        self.globalModule = ir.Module('nkModuloGlobal.bc')
        self.modules = []
        self.leiaFunTypeInt = ir.FunctionType(ir.IntType(32),[])
        self.leiaFunObjectInt = ir.Function(self.globalModule,self.leiaFunTypeInt,'LeiaInteiro')
        self.leiaFunEntryBlock =  self.leiaFunObjectInt.append_basic_block( name=("LeiaEntry"))
        #funSymbol.endBlock = None
        self.leiaBuilder = ir.IRBuilder(self.leiaFunEntryBlock)
        self.leiaBuilder.ret(ir.Constant(ir.IntType(32),5))

        '''
        self.leiaFloat = ir.FunctionType(ir.FloatType,[])
        self.leiaFunObjectFloat = ir.Function(self.globalModule,self.leiaFloat,'LeiaFloat')
        self.leiaFunEntryBlockF =  self.leiaFunObjectFloat.append_basic_block( name=("LeiaEntryF"))
        #funSymbol.endBlock = None
        self.leiaBuilderF = ir.IRBuilder(self.leiaFunEntryBlockF)
        self.leiaBuilderF.ret(ir.Constant(ir.FloatType(),5.0))
        '''

        self.escrevaTypeInt = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        self.escrevaFunInt = ir.Function(self.globalModule,self.escrevaTypeInt,'EscrevaInteiro')
        self.escrevaFunEntryBlock =  self.escrevaFunInt.append_basic_block( name=("EscrevaEntry"))
        self.escrevaBuilder = ir.IRBuilder(self.escrevaFunEntryBlock)
        self.escrevaVar = self.escrevaBuilder.alloca(ir.IntType(32),name="escrevaBuffer")
        self.escrevaVar.align=4
        self.escrevaBuilder.ret(ir.Constant(ir.IntType(32),1))

        '''self.escrevaFloat = ir.FunctionType(ir.IntType(32), [ir.FloatType()])
        self.escrevaFunFloat = ir.Function(self.globalModule,self.escrevaFloat,'EscrevaFloat')
        self.escrevaFunEntryBlockF =  self.escrevaFunFloat.append_basic_block( name=("EscrevaEntryF"))
        self.escrevaBuilderF = ir.IRBuilder(self.escrevaFunEntryBlockF)
        self.escrevaVarF = self.escrevaBuilder.alloca(ir.FloatType(),name="escrevaBuffer")
        self.escrevaVar.align=4
        self.escrevaBuilder.ret(ir.Constant(ir.IntType(32),1))
'''

    def run(self,string):
        parser = yacc.yacc(module=self,debug=True,optimize=False)
        self.parsed = parser.parse(string)
        self.count = 0
        self.tree = Tree()
        self.uiTree = Digraph()

    def print(self, **kwargs):
        if self.montou==0:
            self.mountVisualTree(self.parsed)
            self.montou=1
        self.tree.show(**kwargs)

    def printUIMode(self,filename):
        if self.montou==0:
            self.mountVisualTree(self.parsed)
            self.montou=1
        self.uiTree.render(filename,view=True)

    def getNextCount(self):
        self.count += 1
        return str(self.count)

    def mountVisualTree(self,nktree):
        if nktree is None:
            return -1
        actuals = []
        nexts = nktree.children
        nktree.setLabelId(self.getNextCount())
        self.tree.create_node(nktree.type,nktree.label)
        self.uiTree.node(nktree.label,nktree.type)
        actuals.append(nktree)

        while len(nexts)!=0:
            nexts = []
            parentName=""
            for node in actuals:
                if(type(node) is NkTree):
                    for next in node.children:
                        if(type(next) is NkTree):
                            next.setLabelId(self.getNextCount())
                            self.uiTree.node(next.label,next.type)
                            self.uiTree.edge(node.label,next.label)
                            self.tree.create_node(next.type,next.label,node.label)
                        else:
                            levelStr=""
                            if(next is None):
                                levelStr += "none "
                            elif (isinstance(next, lex.LexToken)):
                                levelStr += next.type +" "
                            else:
                                levelStr += next +" "
                            tmpLabel = "none"+self.getNextCount()
                            self.uiTree.node(tmpLabel,levelStr)
                            self.uiTree.edge(node.label,tmpLabel)
                            self.tree.create_node(levelStr,tmpLabel,node.label)
                        nexts.append(next)
            actuals = nexts

    def addWarning(self,warning):
        if warning not in self.warnings:
            self.addWarning(warning)

    def getNodesList(self,sourceNode,nodeTypesToFind):
        actuals = []
        outNodes = []
        nexts = sourceNode.children
        actuals.append(sourceNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if(type(next) is NkTree):
                        if next.type in nodeTypesToFind:
                            outNodes.insert(0,next)
                        elif next.type==sourceNode.type:
                            nexts.append(next)
                if (node.type=="expressao_aditiva" or node.type=="expressao_multiplicativa" or node.type=="expressao_logica" or node.type=="expressao_simples" or node.type=="expressao_unaria") and len(node.children)>=3:
                    outNodes[0],outNodes[1]=outNodes[1],outNodes[0]
            actuals = nexts
        return outNodes

    def getListDifferentThantSourceNode(self,sourceNode):
        actuals = []
        outNodes = []
        nexts = sourceNode.children
        actuals.append(sourceNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if(type(next) is NkTree):
                        if next.type != sourceNode.type:
                            outNodes.insert(0,next)
                        elif next.type==sourceNode.type:
                            nexts.append(next)
                    else:
                        outNodes.insert(0,next)
            actuals = nexts
        return outNodes


    def getInitedVars(self,inicializacaoVarsNode,tabelaSimbolos):
        atribNode = inicializacaoVarsNode.children[0]
        var = atribNode.children[0]
        name = var.children[0]
        indx = 0
        indy = 0
        isArray = 0
        if len(var.children)==2:
            isArray=1
            indexNode = var.children[1]
            indx = tabelaSimbolos.getSimpleNumberFromExpressionNode(indexNode[0])
            if len(indexNode.children)==2:
                indy = tabelaSimbolos.getSimpleNumberFromExpressionNode(indexNode[1])

    def printWarningsAndErrors(self,tabelaSimbolos):
        for warning in tabelaSimbolos.declarationWarnings:
            print(warning)
        for warning in self.warnings:
            print("WARNING: "+warning)
        for error in self.exceptions:
            print("SEMANTIC ERROR:"+error)
        for error in tabelaSimbolos.declarationErrors:
            print(error)

    def getIndexValue(self,expressionNode):
        actuals = []
        possibilities = ["expressao_logica","expressao_simples","expressao_aditiva","expressao_multiplicativa","expressao_unaria","fator"]
        nexts = expressionNode.children
        actuals.append(expressionNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type in possibilities:
                        nexts.append(next)
                    elif next.type=="numero":
                        return next.children[0]
                    elif next.type=="var":
                        return next.children[0]
            actuals = nexts

    def representsInt(self,string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def representsFloat(self,string):
        try:
            if float(string) and '.' in string:
                return True
            else:
                return False
        except ValueError:
            return False

    def checkIfIndexIsInteger(self,indexNode,scope,tabelaSimbolos):
        valx = self.getIndexValue(indexNode)

        if isinstance(valx,str):
            if self.representsInt(valx):
                return 1
            elif self.representsFloat(valx):
                self.addException(valx+" e utilizada no escopo "+scope+" como posicao de array sendo que nao e inteiro")
                return 1
            nickNameExists = tabelaSimbolos.checkVarExists(valx,scope)
            if nickNameExists==0:
                self.addException(valx+" e utilizada no escopo "+scope+" como posicao de array sem ter sido declarada")
            else:
                valxSymbol = tabelaSimbolos.getVar(valx,scope)
                if valxSymbol.type!="inteiro":
                    self.addException(valx+" e utilizada no escopo "+scope+" como posicao de array sendo que nao e inteiro")
        elif isinstance(valx,float):
            self.addException(valx+" e utilizada no escopo "+scope+" como posicao de array sendo que nao e inteiro")
        return ""

    def getAllVarsAndNumbersSimple(self,sourceNode):
        nodeTypesToFind = ["var","numero","chamada_funcao"]
        actuals = []
        outNodes = []
        nexts = sourceNode.children
        actuals.append(sourceNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if(type(next) is NkTree):
                        if next.type in nodeTypesToFind:
                            outNodes.insert(0,next)
                        elif next.type!="se" and next.type!="repita":
                            nexts.append(next)
            actuals = nexts
        return outNodes



    def getAllVarsAndNumbers(self,sourceNode,scope,tabelaSimbolos):
        nodeTypesToFind = ["var","numero","chamada_funcao"]
        actuals = []
        outNodes = []
        nexts = sourceNode.children
        actuals.append(sourceNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if(type(next) is NkTree):
                        if next.type in nodeTypesToFind:
                            outNodes.insert(0,next)
                        elif next.type!="se" and next.type!="repita":
                            nexts.append(next)
            actuals = nexts
        for node in outNodes:
            if node.type=="var" or node.type=="chamada_funcao":
                varName = node.children[0]
                exists = tabelaSimbolos.checkVarExists(varName,scope)
                if exists==0:
                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    varSymbol = tabelaSimbolos.getVar(varName,scope)
                    varSymbol.isUsed=1
        return outNodes


    def checkIfAllNodesHaveTheType(self,nodeList,type,scope,tabelaSimbolos):
        for node in nodeList:
            if node.type=="var":
                varName = node.children[0]
                exists = tabelaSimbolos.checkVarExists(varName,scope)
                if exists==0:
                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    varSymbol = tabelaSimbolos.getVar(varName,scope)
                    varType = varSymbol.type
                    varSymbol.isUsed=1
                    if varType!=type:
                        return 0
            elif node.type=="numero":
                if type=="inteiro":
                    if self.representsFloat(node.children[0]):
                        return 0
                elif type=="flutuante":
                    if self.representsInt(node.children[0]):
                        return 0
            elif node.type=="chamada_funcao":
                varName = node.children[0]
                exists = tabelaSimbolos.checkVarExists(varName,"global")
                if exists==0:
                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    varSymbol = tabelaSimbolos.getVar(varName,"global")
                    varSymbol.isUsed=1
                    varType = varSymbol.type
                    if varType!=type:
                        return 0
        return 1

    def checkIfSomeNodeHaveTheType(self,nodeList,type,scope,tabelaSimbolos):
        for node in nodeList:
            if node.type=="var":
                varName = node.children[0]
                exists = tabelaSimbolos.checkVarExists(varName,scope)
                if exists==0:
                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    varSymbol = tabelaSimbolos.getVar(varName,scope)
                    varType = varSymbol.type
                    if varType==type:
                        return 1
            elif node.type=="numero":
                if type=="inteiro":
                    if self.representsInt(node.children[0]):
                        return 1
                elif type=="flutuante":
                    if self.representsFloat(node.children[0]):
                        return 1
            elif node.type=="chamada_funcao":
                varName = node.children[0]
                exists = tabelaSimbolos.checkVarExists(varName,"global")
                if exists==0:
                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    varSymbol = tabelaSimbolos.getVar(varName,"global")
                    varType = varSymbol.type
                    if varType==type:
                        return 1
        return 0

    def addException(self,exception):
        if exception not in self.exceptions:
            self.exceptions.append(exception)

    def addWarning(self,warning):
        if warning not in self.warnings:
            self.warnings.append(warning)

    def checkFunctionReturn(self,returnExpressionNode,function,scope,tabelaSimbolos):
        paramsVarList = self.getAllVarsAndNumbers(returnExpressionNode,scope,tabelaSimbolos)
        exists = tabelaSimbolos.checkVarExists(function,"global")
        if exists==0:
            self.addException(function+"e utilizada no escopo "+scope+" sem ter sido declarada")
        else:
            funcSymbol = tabelaSimbolos.getVar(function,"global")
            retType = funcSymbol.type
            if retType=="inteiro":
                typesOk = self.checkIfAllNodesHaveTheType(paramsVarList,retType,scope,tabelaSimbolos)
            elif retType=="flutuante":
                typesOk = self.checkIfSomeNodeHaveTheType(paramsVarList,retType,scope,tabelaSimbolos)
            else:
                typesOk = 0
            if(typesOk==0):
                if retType is None:
                    retType = "vazio"
                if retType=="inteiro" or retType=="flutuante":
                    if retType=="inteiro":
                        self.addException(""+function+" deve retornar inteiro, mas retorna flutuante")
                    else:
                        self.addWarning(""+function+" deve retornar flutuante, mas retorna inteiro, coercao implicita")
                else:
                    self.addException(""+function+" deve retornar "+retType+", confira o tipo da saida da funcao")


    def checkFunctionParams(self,expVarList,tabelaSimbolos,scope):
        for var in expVarList:
            if var.type=="chamada_funcao":
                function = var.children[0]
                exists = tabelaSimbolos.checkVarExists(function,"global")
                if exists==0:
                    self.addException(function+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    if scope=="principal" and function=="principal":
                        self.addWarning("Chamada recursiva a função principal nao e permitida")
                    elif function=="principal":
                        self.addException("Chamada a função principal nao e permitida")
                    params = var.children[2]
                    paramsVarList = self.getAllVarsAndNumbers(params,scope,tabelaSimbolos)
                    funcSymbol = tabelaSimbolos.getVar(function,"global")

                    if len(funcSymbol.params)!=len(paramsVarList):
                        self.addException("Chamada a função "+function+" contem uma quantidade de parametros diferente da declarada")
                    else:
                        tmpType=""
                        for i in range(0,len(paramsVarList)):
                            if paramsVarList[i].type=="var":
                                varName = paramsVarList[i].children[0]
                                tmpExists = tabelaSimbolos.checkVarExists(varName,scope)
                                if tmpExists==0:
                                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                                else:
                                    varSymbol = tabelaSimbolos.getVar(varName,scope)
                                    tmpType = varSymbol.type
                            elif paramsVarList[i].type=="chamada_funcao":
                                varName = paramsVarList[i].children[0]
                                tmpExists = tabelaSimbolos.checkVarExists(varName,"global")
                                if tmpExists==0:
                                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                                else:
                                    varSymbol = tabelaSimbolos.getVar(varName,"global")
                                    tmpType = varSymbol.type
                            elif self.representsInt(paramsVarList[i].children[0]):
                                tmpType = "inteiro"
                            elif self.representsFloat(paramsVarList[i].children[0]):
                                tmpType = "flutuante"
                            if tmpType!=funcSymbol.params[i].type:
                                self.addException("Chamada a função "+function+" tem um parametro de tipo inesperado, esperado:"+funcSymbol.params[i].type+" obtido:"+tmpType)

    def checkIfVarListExists(self,expressao,scope,tabelaSimbolos,label):
        expVarList = self.getAllVarsAndNumbers(expressao,scope,tabelaSimbolos)
        for node in expVarList:
            if node.type=="var":
                varName = node.children[0]
                exists = tabelaSimbolos.checkVarExists(varName,scope)
                if exists==0:
                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    simbolo = tabelaSimbolos.getVar(varName,scope)
                    simbolo.isUsed=1
            elif node.type=="chamada_funcao":
                varName = node.children[0]
                exists = tabelaSimbolos.checkVarExists(varName,"global")
                if exists==0:
                    self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                else:
                    simbolo = tabelaSimbolos.getVar(varName,scope)
                    simbolo.isUsed=1

    def processCorpo(self,corpo,scope,tabelaSimbolos,checouRetorno):
        types = ["acao","expressao"]
        actuals = []
        nexts = corpo.children
        actuals.append(corpo)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="expressao" and next.children[0].type=="atribuicao":
                        self.processarAtribuicao(next.children[0],scope,tabelaSimbolos)
                    elif next.type=="expressao_logica":
                        expVarList = self.getAllVarsAndNumbers(next,scope,tabelaSimbolos)
                        self.checkFunctionParams(expVarList,tabelaSimbolos,scope)
                    elif next.type=="retorna":
                        self.checkFunctionReturn(next,scope,scope,tabelaSimbolos)
                        checouRetorno.value=1
                    elif next.type=="leia":
                        var = next.children[2]
                        varName = var.children[0]
                        exists = tabelaSimbolos.checkVarExists(varName,scope)
                        if exists==0:
                            self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                        else:
                            simbolo = tabelaSimbolos.getVar(varName,scope)
                            simbolo.isUsed=1
                            simbolo.isInitialized=1
                    elif next.type=="escreva":
                        expressao = next.children[2]
                        self.checkIfVarListExists(expressao,scope,tabelaSimbolos,"ESCREVA")
                    elif next.type=="se":
                        expression = next.children[1]
                        corpo1 = next.children[3]
                        innerScope = scope+".se"+str(next.sequenceId)
                        self.checkIfVarListExists(expression,scope,tabelaSimbolos,"SE")
                        self.processCorpo(corpo1,innerScope,tabelaSimbolos,checouRetorno)
                        self.checkIfVarListExists(corpo1,innerScope,tabelaSimbolos,"SE")
                        if len(next.children)>5:
                            corpo2 = next.children[5]
                            self.processCorpo(corpo2,innerScope,tabelaSimbolos,checouRetorno)
                            self.checkIfVarListExists(corpo2,innerScope,tabelaSimbolos,"SE")
                    elif next.type=="repita":
                        corpo = next.children[1]
                        expressao = next.children[3]
                        innerScope = scope+".rp"+str(next.sequenceId)
                        self.checkIfVarListExists(expressao,scope,tabelaSimbolos,"REPITA")
                        self.checkIfVarListExists(corpo,innerScope,tabelaSimbolos,"REPITA")
                        self.processCorpo(corpo,innerScope,tabelaSimbolos,checouRetorno)
                    elif next.type in types:
                        nexts.append(next)
            actuals = nexts

    def processarRepita(self,repitaNode,scope,tabelaSimbolos):
        return ""



    def processarAtribuicao(self,atribuicaoNode,scope,tabelaSimbolos):
        expressaoDireita = atribuicaoNode.children[2]
        var = atribuicaoNode.children[0]
        varName = var.children[0]
        exists = tabelaSimbolos.checkVarExists(varName,scope)

        if exists==0:
            self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
        else:
            varSymbol = tabelaSimbolos.getVar(varName,scope)
            varType = varSymbol.type
            varIsArray = varSymbol.isArray
            varDx = varSymbol.dX
            varDy = varSymbol.dY

            expVarList = self.getAllVarsAndNumbers(expressaoDireita,scope,tabelaSimbolos)
            if varType=="inteiro":
                typesOk = self.checkIfAllNodesHaveTheType(expVarList,varType,scope,tabelaSimbolos)
            elif varType=="flutuante":
                typesOk = self.checkIfSomeNodeHaveTheType(expVarList,varType,scope,tabelaSimbolos)
            if(typesOk==0):
                self.addWarning(varName+" e do tipo "+varType+" mas recebe um valor de outro tipo no escopo "+scope)
            if len(var.children)==2 and varIsArray==0:
                self.addException(varName+" do escopo "+scope+" nao e um array mas foi invocado como se fosse array.")
            if len(var.children)==2 and varIsArray==1:
                indexesNk = var.children[1]
                self.checkIfIndexIsInteger(indexesNk.children[0],scope,tabelaSimbolos)

            elif len(var.children)==3 and varIsArray==1:
                indexesNk = var.children[1]
                self.checkIfIndexIsInteger(indexesNk.children[0],scope,tabelaSimbolos)
                self.checkIfIndexIsInteger(indexesNk.children[1],scope,tabelaSimbolos)
            self.checkFunctionParams(expVarList,tabelaSimbolos,scope)
            varSymbol.isUsed=1
            varSymbol.isInitialized=1

    def findFunctionSemanticErrors(self,declFuncNode,tabelaSimbolos):
        if len(declFuncNode.children)==2:
            cabecalho = declFuncNode.children[1]
        else:
            cabecalho = declFuncNode.children[0]
        scope = cabecalho.children[0]
        corpo = cabecalho.children[4]
        checouRetorno=ReturnChecker(0)
        self.processCorpo(corpo,scope,tabelaSimbolos,checouRetorno)
        if(checouRetorno.value==0):
            syb = tabelaSimbolos.getVar(scope,"global")
            self.addException("funcao "+scope+" sem retorno, deveria retornar "+syb.type)
        return ""

    def getSimpleNumberFromExpressionNode(self,expressionNode):
        actuals = []
        possibilities = ["expressao_logica","expressao_simples","expressao_aditiva","expressao_multiplicativa","expressao_unaria","fator"]
        nexts = expressionNode.children
        actuals.append(expressionNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type in possibilities:
                        nexts.append(next)
                    elif next.type=="numero":
                        return next.children[0]
            actuals = nexts

    def getVarList(self,declVarNode,scope):
        varList = []
        indexArray = []
        indexesOutput = []
        notGroup = ["[","]"]
        simbolo = None
        type = declVarNode.children[0].type
        listVars = declVarNode.children[2].children
        for var in listVars:
            if var.type=="var":
                if(len(var.children)==2):
                    indexArray = var.children[1].children
                    for expression in indexArray:
                        if expression not in notGroup:
                            indexesOutput.insert(0,self.getSimpleNumberFromExpressionNode(expression))
                    if len(indexesOutput)==1:
                        varList.append(Symbol(var.children[0],type,1,indexesOutput[0],0,scope,None))
                    else:
                        varList.append(Symbol(var.children[0],type,1,indexesOutput[0],indexesOutput[1],scope,None))
                else:
                    varList.append(Symbol(var.children[0],type,0,0,0,scope,None))
        return varList


    def getOperationNode(self,expressionNode):
        actuals = []
        possibilities = ["expressao_logica","expressao_simples","expressao_aditiva","expressao_multiplicativa","expressao_unaria","fator","numero","var"]
        
        nexts = expressionNode.children
        actuals.append(expressionNode)
        toReturn = 1
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="var" or next.type=="numero":
                        toReturn=next
                    elif next.type=="chamada_funcao":
                        return next
                    elif next.type=="expressao_aditiva" or next.type=="expressao_multiplicativa":
                        if len(next.children)>1:
                            return next
                        else:
                            nexts.append(next)
                    elif next.type in possibilities:
                        nexts.append(next)
            actuals = nexts
        return toReturn

    def generateCorpoCode(self,corpo,scope,scopeSymbol,tabelaSimbolos):
        types = ["acao","expressao"]
        actuals = []
        nexts = corpo.children
        actuals.append(corpo)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="declaracao_variaveis":
                        symbols = tabelaSimbolos.getVarList(next,scope)
                        for s in symbols:
                            self.genCodeVarDeclaration(s,scopeSymbol,tabelaSimbolos)
                    elif next.type=="expressao" and next.children[0].type=="atribuicao":
                        self.genCodeAtribuicao(next.children[0],scopeSymbol,tabelaSimbolos)
                    elif next.type=="retorna":
                        funcSymbol = tabelaSimbolos.getVar(scopeSymbol.name,scopeSymbol.name)
                        if len(next.children)==4:
                            expressao = next.children[2]
                        else:
                            expressao = next.children[0]
                        varSymbol = Symbol("retornNk"+scopeSymbol.name,"unknow",0,0,0,scopeSymbol.name,[])
                        varSymbol.type = funcSymbol.type
                        if funcSymbol.endBlock is None:
                            funcSymbol.endBlock = funcSymbol.codeObject.append_basic_block( name=(funcSymbol.name+"End"))
                        funcSymbol.builder.branch(funcSymbol.endBlock)
                        funcSymbol.builder.position_at_end(funcSymbol.endBlock)

                        if varSymbol.type=="inteiro":
                            var = scopeSymbol.builder.alloca(ir.IntType(32),name=varSymbol.name)
                            var.align=4
                            varSymbol.codeObject = var
                        elif type=="flutuante":
                            var = scopeSymbol.builder.alloca(ir.FloatType(),name=varSymbol.name)
                            var.align=4
                            varSymbol.codeObject = var
                        varSymbol = self.genAtributionExpressionNode(varSymbol,expressao,scopeSymbol,tabelaSimbolos)
                        loadVarSymbol = scopeSymbol.builder.load(varSymbol.codeObject,"")

                        scopeSymbol.builder.ret(loadVarSymbol)
                    elif next.type=="leia":
                        var = next.children[2]
                        varName = var.children[0]
                        varSymbol = tabelaSimbolos.getVar(varName,scopeSymbol.name)

                        if varSymbol.type=="inteiro":
                            res = scopeSymbol.builder.call(self.leiaFunObjectInt,[])
                            scopeSymbol.builder.store(res,varSymbol.codeObject)
                        elif varSymbol.type=="flutuante":
                            res = scopeSymbol.builder.call(self.leiaFunObjectFloat,[])
                            scopeSymbol.builder.store(res,varSymbol.codeObject)
                    elif next.type=="escreva":
                        expressao = next.children[2]
                        result = self.genExpressionNode(expressao,scopeSymbol,tabelaSimbolos)
                        if "i32" in str(result):
                            scopeSymbol.builder.call(self.escrevaFunInt,[result])
                        else:
                            scopeSymbol.builder.call(self.escrevaFunFloat,[result])
                    elif next.type=="se":
                        expression = next.children[1]
                        corpo1 = next.children[3]
                        innerScope = scopeSymbol.name+".se"+str(next.sequenceId)
                        expGr = self.genSimpleLogicExpression(expression,scopeSymbol,tabelaSimbolos)
                        newScopeBlock = scopeSymbol.codeObject.append_basic_block(name=innerScope)
                        if scopeSymbol.endBlock is None:
                            scopeSymbol.endBlock = scopeSymbol.codeObject.append_basic_block( name=(scopeSymbol.name+"End"))

                        tmpName = scopeSymbol.name
                        tmpParent = scopeSymbol.scope
                        scopeSymbol.builder.cbranch(expGr,newScopeBlock,scopeSymbol.endBlock)
                        scopeSymbol.builder.position_at_end(newScopeBlock)
                        scopeSymbol.name = innerScope
                        scopeSymbol.scope = tmpName
                        self.generateCorpoCode(corpo1,scopeSymbol.name,scopeSymbol,tabelaSimbolos)
                        scopeSymbol.name = tmpName
                        scopeSymbol.scope = tmpParent

                        if len(next.children)>5:#Caso tem else
                            corpo2 = next.children[5]
                            newElseBlock = scopeSymbol.codeObject.append_basic_block(name=innerScope+"Else")
                            scopeSymbol.builder.cbranch(expGr, newElseBlock, scopeSymbol.endBlock)
                            scopeSymbol.builder.position_at_end(newElseBlock)
                            scopeSymbol.name = innerScope
                            scopeSymbol.scope = tmpName
                            self.generateCorpoCode(corpo2,scopeSymbol.name,scopeSymbol,tabelaSimbolos)
                            scopeSymbol.name = tmpName
                            scopeSymbol.scope = tmpParent


                    elif next.type=="repita":
                        corpo = next.children[1]
                        expressao = next.children[3]
                        innerScope = scope+".rp"+str(next.sequenceId)
                        expGr = self.genSimpleLogicExpression(expressao,scopeSymbol,tabelaSimbolos)
                        newScopeBlock = scopeSymbol.codeObject.append_basic_block(name=innerScope)
                        tmpName = scopeSymbol.name
                        tmpParent = scopeSymbol.scope

                        newEndBlock = scopeSymbol.codeObject.append_basic_block(name=innerScope+"Fim")
                        scopeSymbol.builder.cbranch(expGr,newScopeBlock,newEndBlock)
                        scopeSymbol.builder.position_at_end(newScopeBlock)
                        scopeSymbol.name = innerScope
                        scopeSymbol.scope = tmpName
                        self.generateCorpoCode(corpo,scopeSymbol.name,scopeSymbol,tabelaSimbolos)
                        scopeSymbol.name = tmpName
                        scopeSymbol.scope = tmpParent

                        scopeSymbol.builder.cbranch(expGr,newEndBlock,newEndBlock)
                        scopeSymbol.builder.position_at_end(newEndBlock)

                    elif next.type in types:
                        nexts.append(next)
            actuals = nexts

    def genSimpleLogicExpression(self,logicExpressionNode,scopeSymbol,tabelaSimbolos):
        actuals = []
        possibilities = ["expressao_logica","expressao_simples","expressao_aditiva","expressao_multiplicativa","expressao_unaria","fator"]
        nexts = logicExpressionNode.children
        actuals.append(logicExpressionNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="expressao_simples":
                        exp0 = next.children[0]
                        exp1 = next.children[2]
                        operation = next.children[1]
                        result0 = self.genExpressionNode(exp0,scopeSymbol,tabelaSimbolos)
                        result1 = self.genExpressionNode(exp1,scopeSymbol,tabelaSimbolos)
                        if str(operation)=='=':
                            operation = '=='
                        logicExp = scopeSymbol.builder.icmp_signed(str(operation), result0, result1 )
                        return logicExp
                    elif next.type in possibilities:
                        nexts.append(next)
            actuals = nexts


    def genFunctionCode(self,declFuncNode,tabelaSimbolos):
        if len(declFuncNode.children)==2:
            cabecalho = declFuncNode.children[1]
        else:
            cabecalho = declFuncNode.children[0]
        scope = cabecalho.children[0]
        corpo = cabecalho.children[4]
        funSymbol = tabelaSimbolos.getVar(scope,"global")
        if funSymbol.name=="principal":
            funcName = "main"
        else:
            funcName = funSymbol.name
        paramTypes = []
        for param in funSymbol.params:
            if param.type=="inteiro":
                paramTypes.append(ir.IntType(32))
            elif param.type=="flutuante":
                paramTypes.append(ir.FloatType())
        if funSymbol.type=="inteiro":
            functionType = ir.FunctionType(ir.IntType(32),paramTypes)
        elif funSymbol.type=="flutuante":
            functionType = ir.FunctionType(ir.FloatType(32),paramTypes)
        funSymbol.module = self.globalModule

        funSymbol.codeObject = ir.Function(funSymbol.module,functionType,name=funcName)
        funSymbol.entryBlock =  funSymbol.codeObject.append_basic_block( name=(funcName+"Entry"))
        funSymbol.endBlock = None
        funSymbol.builder = ir.IRBuilder(funSymbol.entryBlock)
        tabelaSimbolos.updateVar("global",funSymbol)
        for i in range (0,len(funSymbol.params)):
            funSymbol.params[i].codeObject=funSymbol.codeObject.args[0]

        self.generateCorpoCode(corpo,scope,funSymbol,tabelaSimbolos)
        #self.modules.append(funSymbol.module)
        return ""

    def genCodeNumber(self,numberNode,tabelaSimbolos):
        numValue=numberNode.children[0]
        if tabelaSimbolos.representsFloat(numValue)==True and tabelaSimbolos.representsInt(numValue)==False:
            const = ir.Constant(ir.FloatType(),float(numValue))
            return [const,"flutuante"]
        else:
            const = ir.Constant(ir.IntType(32),int(numValue))
            return [const,"inteiro"]



    def genCodeVarDeclaration(self,varSymbol,scopeSymbol,tabelaSimbolos):
        if varSymbol.isArray==1:
            if varSymbol.dY is not None and varSymbol.dY!="":
                fatorMultiplicador = int(varSymbol.dX)*int(varSymbol.dY)
            else:
                fatorMultiplicador = int(varSymbol.dX)
            if varSymbol.type=="inteiro":
                tmpType=ir.ArrayType(ir.IntType(32), fatorMultiplicador)
                arrayA = scopeSymbol.alloca(tmpType,name=varSymbol.name)
                arrayA.linkage = "common"
                arrayA.align = 16
                varSymbol.codeObject = arrayA
                tabelaSimbolos.updateVar(scopeSymbol.name,varSymbol)
            elif varSymbol.type=="flutuante":
                tmpType=ir.ArrayType(ir.FloatType(), fatorMultiplicador)
                arrayA = scopeSymbol.alloca(tmpType,name=varSymbol.name)
                arrayA.linkage = "common"
                arrayA.align = 16
                varSymbol.codeObject = arrayA
                tabelaSimbolos.updateVar(scopeSymbol.name,varSymbol)
        else:
            return self.genCodeSimpleVarDeclaration(varSymbol,scopeSymbol,tabelaSimbolos)

    def genCodeSimpleVarDeclaration(self,varSymbol,scopeSymbol,tabelaSimbolos):
        if varSymbol.type=="inteiro":
            var = scopeSymbol.builder.alloca(ir.IntType(32),name=varSymbol.name)
            var.align=4
            varSymbol.codeObject = var
            tabelaSimbolos.updateVar(scopeSymbol.name,varSymbol)
        elif type=="flutuante":
            var = scopeSymbol.builder.alloca(ir.FloatType(),name=varSymbol.name)
            var.align=4
            varSymbol.codeObject = var
            tabelaSimbolos.updateVar(scopeSymbol.name,varSymbol)

    def processNumberGenCode(self,num0,tabelaSimbolos,scopeSymbol):
        tmpNum0 = 0
        type = ""
        if num0.type=="var":
            tmpVarSymbol = tabelaSimbolos.getVar(num0.children[0],scopeSymbol.name)
            try:
                tmpNum0 = scopeSymbol.builder.load(tmpVarSymbol.codeObject,"")
            except:
                tmpNum0 = tmpVarSymbol.codeObject
            type = tmpVarSymbol.type
        elif num0.type=="numero":
            result = self.genCodeNumber(num0,tabelaSimbolos)
            tmpNum0 = result[0]
            type = result[1]
        elif num0.type=="chamada_funcao":
            vars = []
            nums0 = self.getAllVarsAndNumbersSimple(num0.children[2])
            for vari in nums0:
                if vari.type=="numero":
                    result = self.genCodeNumber(vari,tabelaSimbolos)
                    newNumber = result[0]
                    vars.append(newNumber)
                elif vari.type=="var":
                    nextVar = vari.children[0]
                    nextVarSymbol = tabelaSimbolos.getVar(nextVar,scopeSymbol.name)
                    nextVarRepresentation = scopeSymbol.builder.load(nextVarSymbol.codeObject,"")
                    vars.append(nextVarRepresentation)
            tmpFuncSymbol = tabelaSimbolos.getVar(num0.children[0],"global")
            tmpNum0 = scopeSymbol.builder.call(tmpFuncSymbol.codeObject,vars)
            type = tmpFuncSymbol.type
        return [tmpNum0,type]


    def genExpressionNode(self,expressionNode,scopeSymbol,tabelaSimbolos):
        operation = self.getOperationNode(expressionNode)
        if operation.type=="numero":
            numNode = self.genCodeNumber(operation,tabelaSimbolos)
            return numNode[0]
        elif operation.type=="var":
            nextVar = operation.children[0]
            nextVarSymbol = tabelaSimbolos.getVar(nextVar,scopeSymbol.name)
            nextVarRepresentation = scopeSymbol.builder.load(nextVarSymbol.codeObject,"")
            return nextVarRepresentation
        elif operation.type=="expressao_aditiva" or operation.type=="expressao_multiplicativa":
            mathOperation = operation.children[1]
            nums0 = self.getAllVarsAndNumbersSimple(operation.children[0])
            nums1 = self.getAllVarsAndNumbersSimple(operation.children[2])
            num0 = nums0[0]
            num1 = nums1[0]
            tmpNum0 = 0
            result0 = self.processNumberGenCode(num0,tabelaSimbolos,scopeSymbol)
            result1 = self.processNumberGenCode(num1,tabelaSimbolos,scopeSymbol)
            if mathOperation=='+':
                temp = scopeSymbol.builder.add(result0[0],result1[0],name='temp',flags=())
                return temp
            elif mathOperation=='-':
                temp = scopeSymbol.builder.sub(result0[0],result1[0],name='temp',flags=())
                return temp
            elif mathOperation=='*':
                temp = scopeSymbol.builder.mult(result0[0],result1[0],name='temp',flags=())
                return temp
            elif mathOperation=='/':
                temp = scopeSymbol.builder.div(result0[0],result1[0],name='temp',flags=())
                return temp
        elif operation.type=="chamada_funcao":
            result0 = self.processNumberGenCode(operation,tabelaSimbolos,scopeSymbol)
            return result0[0]
        return None

    def genAtributionExpressionNode(self,varSymbol,expressionNode,scopeSymbol,tabelaSimbolos):
        result = self.genExpressionNode(expressionNode,scopeSymbol,tabelaSimbolos)
        if result is not None:
            scopeSymbol.builder.store(result, varSymbol.codeObject)
            tabelaSimbolos.updateVar(scopeSymbol.name,varSymbol)
        return varSymbol


    def genCodeAtribuicao(self,atribuicaoNode,scopeSymbol,tabelaSimbolos):
        expressaoDireita = atribuicaoNode.children[2]
        var = atribuicaoNode.children[0]
        varName = var.children[0]
        varSymbol = tabelaSimbolos.getVar(varName,scopeSymbol.name)

        varType = varSymbol.type
        varIsArray = varSymbol.isArray
        varDx = varSymbol.dX
        varDy = varSymbol.dY
        operation = self.getOperationNode(expressaoDireita)
        self.genAtributionExpressionNode(varSymbol,expressaoDireita,scopeSymbol,tabelaSimbolos)


    def generateCode(self,sourceNode,tabelaSimbolos):
        if sourceNode is None:
            return -1
        scope = "global"
        types = ["declaracao","lista_declaracoes"]
        actuals = []
        nexts = sourceNode.children
        actuals.append(sourceNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="declaracao_variaveis":
                        vars = self.getVarList(next,scope)
                        for var in vars:
                            reference = tabelaSimbolos.getVar(var.name,scope)
                            self.addGlobalVarDeclaration(var,tabelaSimbolos)
                    elif next.type=="declaracao_funcao":
                        self.genFunctionCode(next,tabelaSimbolos)
                    elif next.type in types:
                        nexts.append(next)
            actuals = nexts
        return None

    def findSemanticErrors(self,sourceNode,tabelaSimbolos):
        if sourceNode is None:
            return -1
        scope = "global"
        types = ["declaracao","lista_declaracoes","declaracao_funcao"]
        actuals = []
        nexts = sourceNode.children
        actuals.append(sourceNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="inicializacao_variaveis":
                        atribuicaoNode = next.children[0]
                        expressaoDireita = atribuicaoNode.children[2]
                        var = atribuicaoNode.children[0]
                        varName = var.children[0]
                        exists = tabelaSimbolos.checkVarExists(varName,scope)
                        if exists==0:
                            self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada")
                        else:
                            varSymbol = tabelaSimbolos.getVar(varName,scope)
                            varType = varSymbol.type
                            varIsArray = varSymbol.isArray
                            varDx = varSymbol.dX
                            varDy = varSymbol.dY
                            expVarList = self.getAllVarsAndNumbers(expressaoDireita,scope,tabelaSimbolos)
                            if varType=="inteiro":
                                typesOk = self.checkIfAllNodesHaveTheType(expVarList,varType,scope,tabelaSimbolos)
                            elif varType=="flutuante":
                                typesOk = self.checkIfSomeNodeHaveTheType(expVarList,varType,scope,tabelaSimbolos)
                            if(typesOk==0):
                                self.addWarning(varName+" e do tipo "+varType+" mas recebe um valor de outro tipo no escopo "+scope)
                            if len(var.children)==2 and varIsArray==0:
                                self.addException(varName+" do escopo "+scope+" nao e um array mas foi invocado como se fosse array.")
                            elif len(var.children)==2 and varIsArray==1:
                                indexesNk = var.children[1]
                                self.checkIfIndexIsInteger(indexesNk.children[0],scope,tabelaSimbolos)
                                self.checkIfIndexIsInteger(indexesNk.children[1],scope,tabelaSimbolos)
                            varSymbol.isUsed=1
                            varSymbol.isInitialized=1
                    elif next.type=="declaracao_funcao":
                        self.findFunctionSemanticErrors(next,tabelaSimbolos)
                    elif next.type=="expressao_logica":
                        expVarList = self.getAllVarsAndNumbers(next,scope,tabelaSimbolos)
                        self.checkFunctionParams(expVarList,tabelaSimbolos,scope)
                    elif next.type=="retorna":
                        self.addException("Retorna encontrado fora de um escopo de funcao")
                    elif next.type=="leia":
                        var = next.children[2]
                        varName = var.children[0]
                        exists = tabelaSimbolos.checkVarExists(varName,scope)
                        if exists==0:
                            self.addException(varName+" e utilizada no escopo "+scope+" sem ter sido declarada, funcao leia")
                        else:
                            simbolo = tabelaSimbolos.getVar(self,varName,scope)
                            simbolo.isUsed=1
                            simbolo.isInitialized=1
                    elif next.type=="escreva":
                        self.addException("funcao ESCREVA nao e permitida no escopo global")
                    elif next.type=="se":
                        self.addException("Bloco SE nao e permitido no escopo global")
                    elif next.type=="repita":
                        self.addException("Bloco REPITA nao e permitido no escopo global")
                    elif next.type in types:
                        nexts.append(next)
            actuals = nexts
        declaredVars = tabelaSimbolos.getAllVars()
        principalExists = tabelaSimbolos.checkVarExists("principal",scope)
        if principalExists==0:
            self.addException("Função principal não declarada")
        return ""

    def addGlobalVarDeclaration(self,varSymbol,tabelaSimbolos):
        if varSymbol.isArray==1:
            if varSymbol.dY is not None and varSymbol.dY!="":
                fatorMultiplicador = int(varSymbol.dX)*int(varSymbol.dY)
            else:
                fatorMultiplicador = int(varSymbol.dX)
            if varSymbol.type=="inteiro":
                tmpType=ir.ArrayType(ir.IntType(32), fatorMultiplicador)
                arrayA = ir.GlobalVariable(self.globalModule, tmpType, varSymbol.name)
                arrayA.linkage = "common"
                arrayA.align = 16
                varSymbol.codeObject=arrayA
                tabelaSimbolos.updateVar("global",varSymbol)
            elif varSymbol.type=="flutuante":
                tmpType=ir.ArrayType(ir.FloatType(), fatorMultiplicador)
                arrayA = ir.GlobalVariable(self.globalModule, tmpType, varSymbol.name)
                arrayA.linkage = "common"
                arrayA.align = 16
                varSymbol.codeObject=arrayA
                tabelaSimbolos.updateVar("global",varSymbol)
        else:
            self.addSimpleGlobalVarDeclaration(varSymbol,tabelaSimbolos)

    def addSimpleGlobalVarDeclaration(self,varSymbol,tabelaSimbolos):
        if varSymbol.type=="inteiro":
            g = ir.GlobalVariable(self.globalModule, ir.IntType(32),varSymbol.name)
            g.initializer = ir.Constant(ir.IntType(32), 0)
            g.linkage = "common"
            g.align = 4
            varSymbol.codeObject=g
            tabelaSimbolos.updateVar("global",varSymbol)
        elif varSymbol.type=="flutuante":
            h = ir.GlobalVariable(self.globalModule, ir.FloatType(),varSymbol.name)
            h.initializer =  ir.Constant(ir.FloatType(), 0.0)
            h.linkage = "common"
            h.align = 4
            varSymbol.codeObject=h
            tabelaSimbolos.updateVar("global",varSymbol)



    def reduceTree(self,nktree):
        if nktree is None:
            return -1
        actuals = []
        nexts = nktree.children
        nktree.setLabelId(self.getNextCount())
        actuals.append(nktree)

        while len(nexts)!=0:
            nexts = []
            parentName=""
            for node in actuals:
                if(type(node) is NkTree):
                    for next in node.children:
                        if(type(next) is NkTree):
                            if next.type=="lista_declaracoes":
                                next.children = self.getNodesList(next,["declaracao"])
                            if next.type=="lista_parametros":
                                next.children = self.getNodesList(next,["parametro"])
                            elif next.type=="lista_variaveis":
                                next.children = self.getNodesList(next,["var"])
                            elif next.type=="corpo":
                                next.children = self.getNodesList(next,["acao"])
                            elif next.type=="indice":
                                next.children = self.getNodesList(next,["expressao"])
                            elif next.type=="expressao_logica":
                                next.children = self.getNodesList(next,["operador_logico","expressao_simples","&&","\|\|"])
                            elif next.type=="expressao_simples":
                                next.children = self.getNodesList(next,["operador_relacional","expressao_aditiva",">","<","=","!=",">=","<="])
                            elif next.type=="expressao_aditiva":
                                next.children = self.getNodesList(next,["operador_soma","expressao_multiplicativa","+","-"])
                            elif next.type=="expressao_multiplicativa":
                                next.children = self.getNodesList(next,["operador_multiplicacao","expressao_unaria","*","/"])
                            elif next.type=="expressao_unaria":
                                next.children = self.getNodesList(next,["operador_soma","operador_negacao","fator"])
                            elif next.type=="lista_argumentos":
                                next.children = self.getNodesList(next,["expressao"])
                            elif next.type=="tipo":
                                next.type=next.children[0]
                                next.children = []
                            elif next.type=="operador_soma":
                                next.type=next.children[0]
                                next.children = []
                            elif next.type=="operador_multiplicacao":
                                next.type=next.children[0]
                                next.children = []
                            elif next.type=="operador_logico":
                                next.type=next.children[0]
                                next.children = []
                            elif next.type=="operador_relacional":
                                next.type=next.children[0]
                                next.children = []
                            elif next.type=="parametro":
                                next.children = self.getListDifferentThantSourceNode(next)
                        nexts.append(next)
            actuals = nexts

    def p_programa(self,p):
        '''
            programa : lista_declaracoes
        '''
        p[0] = NkTree([p[1]],'programa')

    def p_lista_declaracoes(self,p):
        '''
            lista_declaracoes : lista_declaracoes declaracao
                              | declaracao
        '''
        if (len(p) == 3):
            p[0] = NkTree([p[1],p[2]],'lista_declaracoes')
        elif (len(p) == 2):
            p[0] = NkTree([p[1]],'lista_declaracoes')

    def p_declaracao(self, p):
        '''
            declaracao : declaracao_variaveis
                       | inicializacao_variaveis
                       | declaracao_funcao
        '''
        p[0] = NkTree([p[1]],'declaracao')

    def  p_declaracao_variaveis(self,p):
        '''
            declaracao_variaveis : tipo DOISPONTOS lista_variaveis
        '''
        p[0] = NkTree([p[1],p[2],p[3]],'declaracao_variaveis')

    def p_inicializacao_variaveis(self,p):
        '''
            inicializacao_variaveis : atribuicao
        '''
        p[0] = NkTree([p[1]],'inicializacao_variaveis')

    def p_lista_variaveis(self,p):
        '''
            lista_variaveis : lista_variaveis VIRGULA var
                            | var
        '''
        if len(p)==4:
            p[0] = NkTree([p[1],p[2],p[3]],'lista_variaveis')
        elif len(p)==2:
            p[0] = NkTree([p[1]],'lista_variaveis')

    def p_var(self,p):
        '''
            var : ID
                | ID indice
        '''
        if len(p)==2:
            p[0] = NkTree([p[1]],'var')
        elif len(p)==3:
            p[0] = NkTree([p[1],p[2]],'var')

    def p_indice(self,p):
        '''
            indice : indice LCOLCHETE expressao RCOLCHETE
                   | LCOLCHETE expressao RCOLCHETE
        '''
        if len(p)==5:
            p[0] = NkTree([p[1],p[2],p[3],p[4]],'indice')
        elif len(p)==4:
            p[0] = NkTree([p[1],p[2],p[3]],'indice')

    def p_tipo(self,p):
        '''
            tipo : INTEIRO
                 | FLUTUANTE
        '''
        p[0] = NkTree([p[1]],'tipo')

    def p_declaracao_funcao(self,p):
        '''
            declaracao_funcao : tipo cabecalho
                              | cabecalho
        '''
        if len(p)==3:
            p[0] = NkTree([p[1],p[2]],'declaracao_funcao')
        else:
            p[0] = NkTree([p[1]],'declaracao_funcao')

    def p_cabecalho(self,p):
        '''
            cabecalho : ID LPARENTHESYS lista_parametros RPARENTHESYS corpo FIM
        '''
        p[0] = NkTree([p[1],p[2],p[3],p[4],p[5],p[6]],'cabecalho')

    def p_lista_parametros(self, p):
        '''
            lista_parametros : lista_parametros VIRGULA parametro
                             | parametro
                             | vazio
        '''
        if len(p)==4:
            p[0] = NkTree([p[1],p[2],p[3]],'lista_parametros')
        elif len(p)==2:
            p[0] = NkTree([p[1]],'lista_parametros')

    def p_parametro(self, p):
        '''
            parametro : tipo DOISPONTOS ID
                      | parametro LCOLCHETE RCOLCHETE
        '''
        p[0] = NkTree([p[1],p[2],p[3]],'parametro')

    def p_corpo(self,p):
        '''
            corpo : corpo acao
                  | vazio
        '''
        if len(p)==3:
            p[0] = NkTree([p[1],p[2]],'corpo')
        else:
            p[0] = NkTree([p[1]],'corpo')

    def p_acao(self,p):
        '''
            acao : expressao
                 | declaracao_variaveis
                 | se
                 | repita
                 | leia
                 | escreva
                 | retorna
                 | error
        '''
        p[0] = NkTree([p[1]],'acao')

    def p_se(self,p):
        '''
            se : SE expressao ENTAO corpo FIM
               | SE expressao ENTAO corpo SENAO corpo FIM
        '''
        if len(p)==6:
            p[0] = NkTree([p[1],p[2],p[3],p[4],p[5]],'se')
        elif len(p)==8:
            p[0] = NkTree([p[1],p[2],p[3],p[4],p[5],p[6],p[7]],'se')

    def p_repita(self,p):
        '''
            repita : REPITA corpo ATE expressao
        '''
        p[0] = NkTree([p[1],p[2],p[3],p[4]],'repita')

    def p_atribuicao(self,p):
        '''
            atribuicao : var ATRIB expressao
        '''
        p[0] = NkTree([p[1],p[2],p[3]],'atribuicao')

    def p_leia(self,p):
        '''
            leia : LEIA LPARENTHESYS var RPARENTHESYS
        '''
        p[0] = NkTree([p[1],p[2],p[3],p[4]],'leia')

    def p_escreva(self,p):
        '''
            escreva : ESCREVA LPARENTHESYS expressao RPARENTHESYS
        '''
        p[0] = NkTree([p[1],p[2],p[3],p[4]],'escreva')

    def p_retorna(self,p):
        '''
            retorna : RETORNA LPARENTHESYS expressao RPARENTHESYS
                    | RETORNA expressao
        '''
        if(len(p))==5:
            p[0] = NkTree([p[1],p[2],p[3],p[4]],'retorna')
        else:
            p[0] = NkTree([p[2]],'retorna')


    def p_expressao(self,p):
        '''
            expressao : expressao_logica
                      | atribuicao
        '''
        p[0] = NkTree([p[1]],'expressao')

    def p_vazio(self,p):
        '''
            vazio :
        '''
        p[0] = None

    def p_expressao_logica(self,p):
        '''
            expressao_logica : expressao_simples
                             | expressao_logica operador_logico expressao_simples
        '''
        if len(p)==2:
            p[0] = NkTree([p[1]],'expressao_logica')
        else:
            p[0] = NkTree([p[1],p[2],p[3]],'repita')

    def p_expressao_simples(self,p):
        '''
            expressao_simples : expressao_aditiva
                              | expressao_simples operador_relacional expressao_aditiva
        '''
        if len(p)==2:
            p[0] = NkTree([p[1]],'expressao_simples')
        else:
            p[0] = NkTree([p[1],p[2],p[3]],'expressao_simples')

    def p_expressao_aditiva(self,p):
        '''
            expressao_aditiva : expressao_multiplicativa
                              | expressao_aditiva operador_soma expressao_multiplicativa
        '''
        if len(p)==2:
            p[0] = NkTree([p[1]],'expressao_aditiva')
        else:
            p[0] = NkTree([p[1],p[2],p[3]],'expressao_aditiva')

    def p_expressao_multiplicativa(self,p):
        '''
            expressao_multiplicativa : expressao_unaria
                                     | expressao_multiplicativa operador_multiplicacao expressao_unaria
        '''
        if len(p)==2:
            p[0] = NkTree([p[1]],'expressao_multiplicativa')
        else:
            p[0] = NkTree([p[1],p[2],p[3]],'expressao_multiplicativa')

    def p_expressao_unaria(self,p):
        '''
            expressao_unaria : fator
                             | operador_soma fator
                             | operador_negacao fator
        '''
        if len(p)==2:
            p[0] = NkTree([p[1]],'expressao_unaria')
        else:
            p[0] = NkTree([p[1],p[2]],'expressao_unaria')

    def p_operador_relacional(self,p):
        '''
            operador_relacional : LESSER
                                | GREATER
                                | EQUAL
                                | DIFF
                                | LESSEREQ
                                | GREATEREQ
        '''
        p[0] = NkTree([p[1]],'operador_relacional')

    def p_operador_soma(self,p):
        '''
            operador_soma : PLUS
                          | MINUS
        '''
        p[0] = NkTree([p[1]],'operador_soma')

    def p_operador_negacao(self,p):
        '''
            operador_negacao : NEGATION
        '''
        p[0] = NkTree([p[1]],'operador_negacao')
    def p_operador_logico(self,p):
        '''
            operador_logico : AND
                            | OR
        '''
        p[0] = NkTree([p[1]],'operador_logico')

    def p_operador_multiplicacao(self,p):
        '''
            operador_multiplicacao : MULT
                                   | DIV
        '''
        p[0] = NkTree([p[1]],'operador_multiplicacao')

    def p_fator(self,p):
        '''
            fator : LPARENTHESYS expressao RPARENTHESYS
                  | var
                  | chamada_funcao
                  | numero
        '''
        if len(p)==4:
            p[0] = NkTree([p[1],p[2],p[3]],'fator')
        else:
            p[0] = NkTree([p[1]],'fator')

    def p_numero(self,p):
        '''
            numero : INT
                   | FLOAT
        '''
        p[0] = NkTree([p[1]],'numero')

    def p_chamada_funcao(self,p):
        '''
            chamada_funcao : ID LPARENTHESYS lista_argumentos RPARENTHESYS
        '''
        p[0] = NkTree([p[1],p[2],p[3],p[4]],'chamada_funcao')

    def p_lista_argumentos(self,p):
        '''
            lista_argumentos : lista_argumentos VIRGULA expressao
                             | expressao
                             | vazio
        '''
        if len(p)==4:
            p[0] = NkTree([p[1],p[2],p[3]],'lista_argumentos')
        else:
            p[0] = NkTree([p[1]],'lista_argumentos')


    def p_error(self,p):
        print("Erro identificado")
        if p:
            print("Valor:")
            print(p.value)
            print("Linha:")
            print(p.lineno)

f  = open(sys.argv[1],'r')
input = f.read()

parser = NkParser()
parser.run(input)
parser.reduceTree(parser.parsed)
parser.printUIMode('outReduced')
tsController = ts.SymbolsController()
tsController.mountSymbolsTables(parser.parsed)
parser.findSemanticErrors(parser.parsed,tsController)
tsController.generateNotUsedWarnings()
tsController.printAll()

parser.generateCode(parser.parsed,tsController)

tsController.printAllComplete()
print("Input:\n"+input)
tsController.printAll()
parser.printWarningsAndErrors(tsController)
outModule = str(parser.globalModule)
outModule = outModule.replace("\ntarget triple = \"unknown-unknown-unknown\"","")
'''for module in parser.modules:
    innerModule = str(module)
    innerModule = innerModule.replace("\ntarget triple = \"unknown-unknown-unknown\"","")
    outModule+=innerModule'''
print(outModule)
arquivo = open('gerado.ll', 'w')
arquivo.write(outModule)
arquivo.close()
print("llc-3.9 gerado.ll")
print("gcc -c gerado.s")
print("gcc -o saidaGeracao gerado.o")
print("./saidaGeracao")
