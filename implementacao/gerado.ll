; ModuleID = "nkModuloGlobal.bc"
target datalayout = ""

define i32 @"LeiaInteiro"() 
{
LeiaEntry:
  ret i32 5
}

define i32 @"EscrevaInteiro"(i32 %".1") 
{
EscrevaEntry:
  %"escrevaBuffer" = alloca i32, align 4
  ret i32 1
}

define i32 @"soma"(i32 %".1", i32 %".2") 
{
somaEntry:
  br label %"somaEnd"
somaEnd:
  %"retornNksoma" = alloca i32, align 4
  %".5" = load i32, i32* %"retornNksoma"
  ret i32 %".5"
}

define i32 @"main"() 
{
mainEntry:
  %"a" = alloca i32, align 4
  %"b" = alloca i32, align 4
  %"c" = alloca i32, align 4
  %"i" = alloca i32, align 4
  store i32 0, i32* %"i"
  %".3" = load i32, i32* %"i"
  %".4" = icmp eq i32 %".3", 5
  br i1 %".4", label %"principal.rp1", label %"principal.rp1Fim"
principal.rp1:
  %".6" = call i32 @"LeiaInteiro"()
  store i32 %".6", i32* %"a"
  %".8" = call i32 @"LeiaInteiro"()
  store i32 %".8", i32* %"b"
  %".10" = load i32, i32* %"b"
  %".11" = load i32, i32* %"a"
  %".12" = call i32 @"soma"(i32 %".10", i32 %".11")
  store i32 %".12", i32* %"c"
  %".14" = load i32, i32* %"c"
  %".15" = call i32 @"EscrevaInteiro"(i32 %".14")
  %".16" = load i32, i32* %"i"
  br i1 %".4", label %"principal.rp1Fim", label %"principal.rp1Fim"
principal.rp1Fim:
  br label %"principalEnd"
principalEnd:
  %"retornNkprincipal" = alloca i32, align 4
  store i32 0, i32* %"retornNkprincipal"
  %".20" = load i32, i32* %"retornNkprincipal"
  ret i32 %".20"
}
