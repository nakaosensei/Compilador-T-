class SymbolsController:

    def __init__(self):
        self.scopeHash = {} #Cada escopo aponta para uma tabela de simbolos
        self.declarationErrors = []
        self.declarationWarnings = []

    def representsFloat(self,string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def representsInt(self,string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def addError(self,error):
        if error not in self.declarationErrors:
            self.declarationErrors.append(error)

    def addWarning(self,warning):
        if warning not in self.declarationWarnings:
            self.declarationWarnings.append(warning)

    #SymbolType=Que categoria de simbolo, se é if,variavel,funcao,condicional
    #symbolDs=Instancia da classe Simbolo
    def put(self,scope,symbolDs):
        symbolsList = self.scopeHash.get(scope)
        if symbolsList is None:
            symbolsList = []
        if self.checkVarExistsOnSameScope(symbolDs.name,scope)==1:
            if symbolDs.isFunction==1:
                self.addError("DECLARATION ERROR: Função "+symbolDs.name+" declarada no escopo "+scope+" mais que uma vez")
            else:
                self.addWarning("WARNING: Variavel "+symbolDs.name+" ja foi declarada anteriormente no escopo "+scope)
        symbolsList.append(symbolDs)
        self.scopeHash[scope]=symbolsList

    def updateVar(self,scope,symbolDs):
        symbolsList = self.scopeHash.get(scope)
        if symbolsList is None:
            symbolsList = []
        for i,symbol in enumerate(symbolsList):
            if symbol.name==symbolDs.name:
                symbolsList[i]=symbolDs
        self.scopeHash[scope]=symbolsList

    def get(self,scope):
        return self.scopeHash.get(scope)

    def getAllVars(self):
        outVars=[]
        for key in self.scopeHash:
            symbols = self.scopeHash[key]
            for symbol in symbols:
                if symbol.isFunction==0:
                    outVars.append([symbol.name,symbol.scope])
        return outVars

    def getAllVarsFromScope(self,scope):
        return self.scopeHash.get(scope)

    def getAllFunctions(self):
        outVars=[]
        for key in self.scopeHash:
            symbols = self.scopeHash[key]
            for symbol in symbols:
                if symbol.isFunction==1:
                    outVars.append(symbol)
        return outVars

    def checkVarExistsOnSameScope(self,varName,scope):
        symbols = self.get(scope)
        if symbols is not None:
            for symbol in symbols:
                if(symbol.name==varName):
                    return 1
        return 0

    def getVarOnSameScope(self,varName,scope):
        symbols = self.get(scope)
        if symbols is not None:
            for symbol in symbols:
                if(symbol.name==varName):
                    return symbol
        return None

    def getVar(self,varName,scope):
        exists = self.getVarOnSameScope(varName,scope)
        if exists is not None:
            return exists
        if "." in scope:
            charFinal=2
            charMeio=3
            charComeco=4

            extension = scope[len(scope)-charComeco]+scope[len(scope)-charMeio]+scope[len(scope)-charFinal]
            while extension==".se" or extension==".rp":
                newScope = scope[0:len(scope)-charComeco]
                exists = self.getVarOnSameScope(varName,newScope)
                if exists is not None:
                    return exists
                if "." in newScope:
                    charFinal+=4
                    charMeio+=4
                    charComeco+=4
                    extension = scope[len(scope)-charComeco]+scope[len(scope)-charMeio]+scope[len(scope)-charFinal]
                else:
                    extension = ""
        return self.getVarOnSameScope(varName,"global")

    def checkVarExists(self,varName,scope):
        exists = self.checkVarExistsOnSameScope(varName,scope)
        if exists==1:
            return 1
        if "." in scope:
            charFinal=2
            charMeio=3
            charComeco=4         

            extension = scope[len(scope)-charComeco]+scope[len(scope)-charMeio]+scope[len(scope)-charFinal]
            while extension==".se" or extension==".rp":
                newScope = scope[0:len(scope)-charComeco]
                exists = self.checkVarExistsOnSameScope(varName,newScope)
                if exists==1:
                    return 1
                if "." in newScope:
                    charFinal+=4
                    charMeio+=4
                    charComeco+=4            
                    extension = scope[len(scope)-charComeco]+scope[len(scope)-charMeio]+scope[len(scope)-charFinal]
                else:
                    extension = ""
        return self.checkVarExistsOnSameScope(varName,"global")

    def printAll(self):
        for key in self.scopeHash:
            symbols = self.scopeHash[key]
            lineStr = "["+key+":"
            for i in range(0,len(symbols)):
                if i == len(symbols)-1:
                    lineStr+=("'"+symbols[i].name+"']")
                else:
                    lineStr+=("'"+symbols[i].name+"',")
            print(lineStr)

    def printAllComplete(self):
        for key in self.scopeHash:
            symbols = self.scopeHash[key]
            for symbol in symbols:
                symbol.print()

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
                        if self.representsFloat(indexesOutput[0])==True and self.representsInt(indexesOutput[0])==False:
                            self.addError("SEMANTIC ERROR: Erro de indice, indice "+indexesOutput[0]+" de tipo float em dimensao na declaracao do array "+var.children[0])
                        varList.append(Symbol(var.children[0],type,1,indexesOutput[0],0,scope,None))
                    else:
                        if self.representsFloat(indexesOutput[0])==True and self.representsInt(indexesOutput[0])==False:
                            self.addError("SEMANTIC ERROR: Erro de indice, indice "+indexesOutput[0]+" de tipo float em dimensao na declaracao do array "+var.children[0])
                        if self.representsFloat(indexesOutput[1])==True and self.representsInt(indexesOutput[1])==False:
                            self.addError("SEMANTIC ERROR: Erro de indice, indice "+indexesOutput[1]+" de tipo float em dimensao na declaracao do array "+var.children[0])
                        varList.append(Symbol(var.children[0],type,1,indexesOutput[0],indexesOutput[1],scope,None))
                else:
                    varList.append(Symbol(var.children[0],type,0,0,0,scope,None))
        return varList


    def getParamsSymbolsList(self,listaParamsNode,scope):
        varList = []
        for param in listaParamsNode.children:
            if len(param.children)==3:
                #name,type,isArray,qtLines,qtColumns,scope,params
                varList.append(Symbol(param.children[0],param.children[2].type,0,0,0,scope,None))
            elif len(param.children)==5:
                varList.append(Symbol(param.children[0],param.children[2].type,1,1,0,scope,None))
            elif len(param.children)==7:
                varList.append(Symbol(param.children[0],param.children[2].type,1,1,1,scope,None))
        return varList

    #Percorre todos os simbolos, e os que nao forem usados geram um warning
    def generateNotUsedWarnings(self):
        for key in self.scopeHash:
            symbols = self.scopeHash[key]
            for symbol in symbols:
                if symbol.isUsed==0 and symbol.name!="principal":
                    self.addWarning("WARNING: "+symbol.name+" é declarado mas nunca usado no escopo "+symbol.scope)
                elif symbol.isInitialized==0 and symbol.isFunction==0:
                    self.addWarning("WARNING: "+symbol.name+" é declarado mas nunca inicializado no escopo "+symbol.scope)
        return None

    def insertParamVariables(self):
        funcSymbols = self.getAllFunctions()
        for funcao in funcSymbols:
            params = funcao.params
            for param in params:
                self.put(funcao.name,param)

    #corpo = corpoNode
    def processCorpo(self,corpo,scope):
        types = ["declaracao","lista_declaracoes","acao"]
        functionNodes = []
        actuals = []
        nexts = corpo.children
        actuals.append(corpo)
        seCount=1 #Contador dos se's
        repitaCount=1 #Contador dos para
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="declaracao_variaveis":
                        symbols = self.getVarList(next,scope)
                        for symbol in symbols:
                            self.put(scope,symbol)
                    elif next.type=="se":
                        next.sequenceId=seCount
                        self.mountSeTable(next,scope+".se"+str(seCount))
                        seCount+=1
                    elif next.type=="repita":
                        next.sequenceId=repitaCount
                        self.mountRepitaTable(next,scope+".rp"+str(repitaCount))
                        repitaCount+=1
                    elif next.type in types:
                        nexts.append(next)
            actuals = nexts

    def mountRepitaTable(self,repitaNode,scope):
        expressionNode = repitaNode.children[3]
        corpo = repitaNode.children[1]
        self.processCorpo(corpo,scope)

    def mountSeTable(self,seNode,scope):
        corpo1 = seNode.children[3]
        corpo2 = None
        expressionNode = seNode.children[1]
        corposToExplore = [corpo1]
        if len(seNode.children)>5:
            corpo2 = seNode.children[5]
            corposToExplore.append(corpo2)
        for corpo in corposToExplore:
            self.processCorpo(corpo,scope)

    def mountSymbolsTables(self,sourceNode):
        if sourceNode is None:
            return -1
        scope = "global"
        types = ["declaracao","lista_declaracoes"]
        functionNodes = []
        actuals = []
        nexts = sourceNode.children
        actuals.append(sourceNode)
        while len(nexts)!=0:
            nexts=[]
            for node in actuals:
                for next in node.children:
                    if next.type=="declaracao_variaveis":
                        symbols = self.getVarList(next,"global")
                        for symbol in symbols:
                            self.put("global",symbol)
                    elif next.type=="declaracao_funcao":
                        tmpTipo = ""
                        if len(next.children)==2:
                            tmpTipo=next.children[0].type
                            cabecalho = next.children[1]
                        else:
                            tmpTipo=None
                            cabecalho = next.children[0]
                        funcName = cabecalho.children[0]
                        params = self.getParamsSymbolsList(cabecalho.children[2],funcName)
                        funcSymbol = Symbol(funcName,tmpTipo,0,0,0,scope,params)
                        self.put("global",funcSymbol)
                        functionNodes.insert(0,next)
                    elif next.type in types:
                        nexts.append(next)
            actuals = nexts

        for function in functionNodes:
            tmpTipo = ""
            if len(function.children)==2:
                tmpTipo=function.children[0].type
                cabecalho = function.children[1]
            else:
                tmpTipo=None
                cabecalho = function.children[0]
            funcName = cabecalho.children[0]
            corpo = cabecalho.children[4]
            types = ["declaracao","lista_declaracoes","acao"]
            functionNodes = []
            actuals = []
            nexts = corpo.children
            actuals.append(corpo)
            seCount=1 #Contador dos se's
            repitaCount=1 #Contador dos para
            while len(nexts)!=0:
                nexts=[]
                for node in actuals:
                    for next in node.children:
                        if next.type=="declaracao_variaveis":
                            symbols = self.getVarList(next,funcName)
                            for symbol in symbols:
                                self.put(funcName,symbol)
                        elif next.type=="se":
                            next.sequenceId = seCount
                            self.mountSeTable(next,funcName+".se"+str(seCount))
                            seCount+=1
                        elif next.type=="repita":
                            next.sequenceId = repitaCount
                            self.mountRepitaTable(next,funcName+".rp"+str(repitaCount))
                            repitaCount+=1
                        elif next.type in types:
                            nexts.append(next)
                actuals = nexts
        self.insertParamVariables()
        return ""

class Symbol:

    def __init__(self,name,type,isArray,qtLines,qtColumns,scope,params):
        self.name=name
        self.type=type #se inteiro,flutuante
        self.isArray=isArray
        self.dX=qtLines
        self.dY=qtColumns
        self.scope=scope
        self.params=params
        self.isUsed=0
        self.isInitialized=0
        if(self.params is None):
            self.isFunction=0
        else:
            self.isFunction=1
        self.nexts = []
        self.operations=[]
        self.codeObject=None
        self.builder=None
        self.module=None
        self.entryBlock=None
        self.endBlock=None
        self.functionGenCodeType=None

    def paramsToString(self):
        out = []
        if self.params is None:
            return out
        for param in self.params:
            out+=[param.name,param.type]
        return out

    def print(self):
        print("name:"+self.name)
        if self.type is None:
            print("type: None")
        else:
            print("type:"+self.type)
        print("isArray:"+str(self.isArray))
        print("dx:"+str(self.dX))
        print("dy:"+str(self.dY))
        print("scope:"+self.scope)
        print("isUsed:"+str(self.isUsed))
        print("isFunction:"+str(self.isFunction))
        print("params")
        print(self.paramsToString())
        print("Code object")
        print(self.codeObject)
        print("\n")

class Operation:

    #Operation types = sum, sub, mult, div, funcCall
    #leia, escreva, retorna
    def __init__(self,varList,operationType):
        self.varList=varList
        self.operationType=operationType
