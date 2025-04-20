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

    file1 = "C:\\Users\\gusta\\Desktop\\7-1b.jff"
    file2 = "C:\\Users\\gusta\\Desktop\\minimizei.jff"

    a1 = AFD.importar_jflap(file1)
    a2 = AFD.importar_jflap(file2)

    #print(a1.estados)
    b = a1.estados_equivalentes()
    for bloco in b:
        print(", ".join(sorted(bloco)))

    #a1 = a1.minimizar()
    #AFD.exportar_jflap(a1, "C:\\Users\\gusta\\Desktop\\minimizei.jff")

    #print(AFD.testar_equivalencia(a1, a2))


