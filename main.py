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

    file1 = "C:\\Users\\gusta\\Desktop\\d.jff"

    a1 = AFD.importar_jflap(file1)
    a2 = AFD.minimizar(a1)
    print(a2)
    AFD.exportar_jflap(a2, "C:\\Users\\gusta\\Desktop\\e.jff")


