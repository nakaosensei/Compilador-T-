from llvmlite import ir

class CodeGenerator:

    def __init__(self):
        self.globalModule = ir.Module('nkModuloGlobal.bc')
        self.ir = ir


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
            g = ir.GlobalVariable(self.globalModule, ir.IntType(32),varName)
            g.initializer = ir.Constant(ir.IntType(32), 0)
            g.linkage = "common"
            g.align = 4
            varSymbol.codeObject=g
            tabelaSimbolos.updateVar("global",varSymbol)
        elif varSymbol.type=="flutuante":
            h = ir.GlobalVariable(self.globalModule, ir.FloatType(),varName)
            h.initializer =  ir.Constant(ir.FloatType(), 0.0)
            h.linkage = "common"
            h.align = 4
            varSymbol.codeObject=g
            tabelaSimbolos.updateVar("global",varSymbol)




class FunctionModule:

    def __init__(self,nome,module,returnType,returnValue):
        self.retValue=None
        self.functionType=None
        self.functionDeclaration=None
        self.entryBlock=None
        self.endBlock=None
        self.builder=None
        self.variables={}
        if returnType=="inteiro":
            self.retValue = ir.Constant(ir.IntType(32),returnValue)
            self.functionType = ir.FunctionType(ir.IntType(32),())
        elif returnType=="flutuante":
            self.retValue = ir.Constant(ir.FloatType(),returnValue)
            self.functionType = ir.FunctionType(ir.FloatType,())
        self.functionDeclaration = ir.Function(module,self.functionType,name=nome)
        self.entryBlock = self.functionDeclaration.append_basic_block('entry')
        self.endBlock = self.functionDeclaration.append_basic_block('exit')
        self.builder = ir.IRBuilder(self.entryBlock)

    def addVariableSingleMode(self,varName,varType,varValue):
        if varType=="inteiro":
            tmpVar = self.builder.alloca(ir.IntType(32),name=varName)
            tmpVar.align=4
            if varValue is not None:
                num = ir.Constant(ir.IntType(32),varValue)
                self.builder.store(num,tmpVar)
        elif varType=="flutuante":
            tmpVar = self.builder.alloca(ir.FloatType(),name=varName)
            tmpVar.align=4
            if varValue is not None:
                num = ir.Constant(ir.FloatType(),varValue)
                self.builder.store(num,tmpVar)
        self.variables[varName]=tmpVar
