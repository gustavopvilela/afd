from afd import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os

def print_menu ():
    print("=== OPÇÕES ===")
    print("1. Importar arquivo JFLAP")
    print("2. Exportar autômato para arquivo JFLAP")
    print("3. Minimizar AFD")
    print("4. Fazer união de dois AFDs")
    print("5. Fazer interseção de dois AFDs")
    print("6. Fazer diferença de dois AFDs")
    print("7. Fazer complemento de AFD")
    print("8. Testar equivalência de dois AFDs")
    print("9. Testar estados equivalentes de um AFD")
    print("10. Ver AFDs disponíveis")
    print("11. Visualizar AFD")
    print("12. Fazer cópia do AFD")
    print("13. Validar cadeia de caracteres")
    print("0. Sair")

def solicitar_um_automato (automatos: dict) -> str | None:
    if len(automatos) == 0:
        print("Nenhum autômato importado.")
        return None

    nome = input("Digite o nome do autômato: ")
    if nome not in automatos:
        print("Autômato não existe")
        return None

    return nome

def solicitar_dois_automatos (automatos: dict) -> tuple[str, str] | None:
    if len(automatos) < 2:
        print("É necessário no mínimo 2 AFDs para realizar essa opção.")
        return None

    nome1 = input("Digite o nome do primeiro autômato: ")
    if nome1 not in automatos:
        print("Autômato não existe")
        return None

    nome2 = input("Digite o nome do segundo autômato: ")
    if nome2 not in automatos:
        print("Autômato não existe")
        return None

    return nome1, nome2

def main():
    try:
        automatos: Dict[str, AFD] = {}

        root = Tk()
        root.wm_attributes("-topmost", 1)
        root.withdraw()

        while True:
            print_menu()
            opcao = int(input("Digite a opção: "))

            if opcao == 0:
                root.destroy()
                break

            match opcao:
                case 1:
                    arquivo = askopenfilename(title="Selecione um arquivo")
                    if arquivo[-4:] != ".jff":
                        print("Escolha um arquivo válido (.jff)!")
                        continue

                    afd = AFD.importar_jflap(arquivo)

                    if afd is None:
                        print("AFD importado não possui estado inicial. Verifique e tente novamente.\n\n")
                        continue

                    nome = input(f"Digite o nome do autômato ({arquivo}): ")
                    automatos[nome] = afd
                    print(f"Arquivo importado com sucesso. Seu nome é {nome}")

                case 2:
                    res = solicitar_um_automato(automatos)
                    if res is None:
                        continue

                    nome = res

                    arquivo = asksaveasfilename(
                        title="Salvar AFD em",
                        defaultextension=".jff",
                        filetypes=[
                            ("Arquivo JFLAP", "*.jff"),
                            ("Todos os arquivos", "*.*")
                        ],
                    )

                    if arquivo == "":
                        print("Nenhum local para salvar escolhido. Operação cancelada.")
                        continue

                    AFD.exportar_jflap(automatos[nome], arquivo)
                    print("Autômato exportado com sucesso.")

                case 3:
                    res = solicitar_um_automato(automatos)
                    if res is None:
                        continue

                    nome = res

                    """
                        Caso o autômato não possua nenhum estado equivalente, significa que ele já está minimizado.
                        Se houvesse um ou mais estados equivalentes, eles poderiam ser condensados em um só.
                    """
                    estados_equivalentes = AFD.estados_equivalentes(automatos[nome])

                    if len(estados_equivalentes) == 0:
                        print("O autômato já está em sua forma mínima.")
                        continue

                    salvar_novo = input("O autômato a ser minimizado deve ser salvo como novo autômato? (S/N) ")

                    if salvar_novo == 'S' or salvar_novo == 's':
                        afd = AFD.minimizar(automatos[nome])
                        novo_nome = f"{nome}-min"
                        automatos[novo_nome] = afd
                        print(f"Autômato minimizado com sucesso e salvo com o nome \"{novo_nome}\".")

                    elif salvar_novo == 'N' or salvar_novo == 'n':
                        automatos[nome] = AFD.minimizar(automatos[nome])
                        print(f"Autômato foi minimizado e substituiu o original.")

                case 4 | 5 | 6:
                    res = solicitar_dois_automatos(automatos)
                    if res is None:
                        continue

                    nome1, nome2 = res

                    if opcao == 4:  # União de AFDs
                        nome_uniao = f"{nome1}-uni-{nome2}"
                        afd = AFD.uniao(automatos[nome1], automatos[nome2])
                        automatos[nome_uniao] = afd
                        print(f"Autômato salvo com sucesso com o nome \"{nome_uniao}\".")
                    elif opcao == 5:  # Intersecao de AFDs
                        nome_int = f"{nome1}-int-{nome2}"
                        afd = AFD.intersecao(automatos[nome1], automatos[nome2])
                        automatos[nome_int] = afd
                        print(f"Autômato salvo com sucesso com o nome \"{nome_int}\".")
                    elif opcao == 6:  # Diferença de AFDs
                        nome_dif = f"{nome1}-dif-{nome2}"
                        afd = AFD.diferenca(automatos[nome1], automatos[nome2])
                        automatos[nome_dif] = afd
                        print(f"Autômato salvo com sucesso com o nome \"{nome_dif}\".")

                case 7:
                    res = solicitar_um_automato(automatos)
                    if res is None:
                        continue

                    nome = res

                    salvar_novo = input("O autômato a ser complementado deve ser salvo como novo autômato? (S/N) ")

                    if salvar_novo == 'S' or salvar_novo == 's':
                        afd = AFD.complemento(automatos[nome])
                        novo_nome = f"{nome}-comp"
                        automatos[novo_nome] = afd
                        print(f"Autômato complementado com sucesso e salvo com o nome \"{novo_nome}\".")

                    elif salvar_novo == 'N' or salvar_novo == 'n':
                        automatos[nome] = AFD.complemento(automatos[nome])
                        print(f"Autômato complementado e substituiu o original.")

                case 8:
                    res = solicitar_dois_automatos(automatos)
                    if res is None:
                        continue

                    nome1, nome2 = res

                    resultado = AFD.testar_equivalencia(automatos[nome1], automatos[nome2])

                    if resultado:
                        print("Os autômatos são equivalentes.")
                    else:
                        print("Os autômatos não são equivalentes.")

                case 9:
                    res = solicitar_um_automato(automatos)
                    if res is None:
                        continue

                    nome = res

                    estados_equivalentes = AFD.estados_equivalentes(automatos[nome])

                    if len(estados_equivalentes) > 0:
                        for grupo in estados_equivalentes:
                            print("O seguinte conjunto de estados é equivalente:", ", ".join(sorted(grupo)))
                    else:
                        print("Não há estados equivalentes neste AFD.")

                case 10:
                    if len(automatos) == 0:
                        print("Nenhum AFD disponível.")
                        continue

                    id_afd: int = 1
                    for nome, afd in automatos.items():
                        print(f"{id_afd}. {nome}")
                        id_afd += 1

                case 11:
                    res = solicitar_um_automato(automatos)
                    if res is None:
                        continue

                    nome = res

                    print(automatos[nome])

                case 12:
                    res = solicitar_um_automato(automatos)
                    if res is None:
                        continue

                    nome = res

                    afd = AFD.copiar(automatos[nome])

                    novo_nome = f"{nome}-copia"
                    automatos[novo_nome] = afd
                    print(f"AFD copiado com sucesso. Está salvo com o nome \"{novo_nome}\".")

                case 13:
                    res = solicitar_um_automato(automatos)
                    if res is None:
                        continue

                    nome = res

                    cadeia = input("Digite a cadeia de caracteres a ser validada: ")

                    resultado = AFD.validar(automatos[nome], cadeia)

                    print(f"A cadeia de caracteres {cadeia} {'é aceita.' if resultado else 'não é aceita.'}")

                case _:
                    print("Opção inválida!")

            input("\n\nAperte Enter para continuar...")
            os.system('cls' if os.name == 'nt' else 'clear')

    except KeyboardInterrupt:
        print("\n\nPrograma finalizado abruptamente.")


if __name__ == '__main__':
    main()