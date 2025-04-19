from afd import *

if __name__ == '__main__':
    """
    estados = ['q0', 'q1']
    alfabeto = ['a', 'b']
    transicoes = {
        ('q0', 'a'): 'q1',
        ('q1', 'b'): 'q0'
    }
    inicial = 'q0'
    finais = ['q1']

    novo_afd = AFD(estados, alfabeto, transicoes, inicial, finais)

    print(novo_afd)
    """

    file1 = "C:\\Users\\gusta\\Desktop\\a-impar.jff"
    file2 = "C:\\Users\\gusta\\Desktop\\b-impar.jff"

    a1 = AFD.importar_jflap(file1)
    a2 = AFD.importar_jflap(file2)

    print(a1)
    print("=============================================")
    print(a2)
    print("=============================================")

    operacoes_aceitas = ["uniao", "intersecao", "diferenca"]


    a3 = AFD.produto(a1, a2, operacoes_aceitas[2])
    print(a3)

    AFD.exportar_jflap(a3, "C:\\Users\\gusta\\Desktop\\c.jff")
