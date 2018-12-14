inteiro: k
inteiro: n

inteiro funcao2(inteiro: m)
  inteiro : nakao
  nakao := 3 + 2
  nakao := nakao * 2
  nakao := nakao - 1
  retorna 5
fim

inteiro funcao3(inteiro: pos)
  inteiro : a
  a := 8
  se a > 5 então
        a := 1
    senão
        a := 4
    fim
  retorna a
fim

inteiro principal()
  inteiro : zoador
  inteiro : soma
  soma := 2
  n := 5

  zoador := funcao2(n)
  repita
    soma := soma + n
    n := n - 1
  até n = 0
  retorna 0
fim
