from copy import deepcopy
from typing import *
from collections import deque
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class AFD:
    def __init__(self,
                 estados: Iterable[str],
                 alfabeto: Iterable[str],
                 transicoes: Dict[Tuple[str, str], str],
                 estado_inicial: str,
                 estados_finais: Iterable[str]):

        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.transicoes = dict(transicoes)
        self.estado_inicial = estado_inicial
        self.estados_finais = set(estados_finais)

    def __str__(self):
        return (
            f"AFD(\n"
            f"    estados: {self.estados}\n"
            f"    alfabeto: {self.alfabeto}\n"
            f"    transicoes:\n     "+
            "\n     ".join([f"{k} -> {v}" for k, v in self.transicoes.items()]) + "\n"
            f"    estado_inicial: {self.estado_inicial}\n"
            f"    estados_finais: {self.estados_finais}\n"
            f")"
        )

    @staticmethod
    def inverter_dicionario (d):
        return {v: k for k, v in d.items()}

    def copiar (self):
        return deepcopy(self)

    def validar (self, cadeia: str):
        estado_atual = self.estado_inicial

        for simbolo in cadeia:
            estado_atual = self.transicoes.get((estado_atual, simbolo))
            if estado_atual is None:
                return False

        return estado_atual in self.estados_finais

    @classmethod
    def importar_jflap (cls, arquivo: str):
        xml = ET.parse(arquivo)
        afd = xml.getroot().find('automaton') # Acha a tag do AFD no XML

        estados = set()
        alfabeto = set()
        transicoes = {}
        finais = set()
        inicial = None

        # Mapeando IDs e nomes dos estados do AFD, já que nas tags de
        # transição tem só o ID.
        id_nome = {}
        for estado in afd.findall('state'):
            id, nome = estado.get('id'), estado.get('name')
            id_nome[id] = nome

            # Adicionando o estado no set de estados, caso não haja
            estados.add(id_nome[id])

            # Adicionando o estado no set de estados finais, caso ele seja
            if estado.find('final') is not None:
                finais.add(id_nome[id])

            # Colocando o estado na variável de inicial, caso ele seja
            if estado.find('initial') is not None:
                inicial = id_nome[id]

        # Encontrando as transições
        for t in afd.findall('transition'):
            from_id = t.find('from').text
            to_id = t.find('to').text
            simbolo = t.find('read').text

            from_estado = id_nome[from_id]
            to_estado = id_nome[to_id]

            alfabeto.add(simbolo)
            transicoes[(from_estado, simbolo)] = to_estado

        return cls(estados, alfabeto, transicoes, inicial, finais)

    def exportar_jflap (self, arquivo: str):
        root = ET.Element('structure')

        # Tipo do autômato: fa = finite automaton
        type = ET.SubElement(root, 'type')
        type.text = 'fa'

        # Subtag dentro de structure: automaton
        automaton = ET.SubElement(root, 'automaton')

        # Para cada estado, colocamos como uma subtag
        # Além disso, precisamos colocar id's únicos para cada estado, então
        # vamos ter que criar novamente um dicionário que relaciona id com estado,
        # assim, poderemos criar as transições depois.
        id_nome = {}
        id = 0
        for estado in self.estados:
            state = ET.SubElement(automaton, 'state')
            state.set('name', estado)
            state.set('id', str(id))
            id_nome[id] = estado
            id += 1

            if self.estado_inicial == estado:
                inicial = ET.SubElement(state, 'initial')

            if estado in self.estados_finais:
                final = ET.SubElement(state, 'final')

        # Agora, vamos colocar as transições
        for (ea, s), ed in self.transicoes.items():
            # Para pegar os IDs a partir do valor, vamos inverter
            # o dicionário
            d_inv = self.inverter_dicionario(id_nome)

            transicao = ET.SubElement(automaton, 'transition')
            from_estado = ET.SubElement(transicao, 'from')
            from_estado.text = str(d_inv[ea])

            to_estado = ET.SubElement(transicao, 'to')
            to_estado.text = str(d_inv[ed])

            read = ET.SubElement(transicao, 'read')
            read.text = s


        # Formatando o arquivo com identação para facilitar a visualização
        para_string = ET.tostring(root, 'utf-8')
        dom = minidom.parseString(para_string)
        arquivo_formatado = dom.toprettyxml(indent="    ")

        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(arquivo_formatado)

    # Precisamos completar o autômato para que o processo de minimização
    # dê certo
    def completar (self):
        erro = 'E'
        if erro not in self.estados:
            self.estados.add(erro)

        for q in list(self.estados):
            for a in self.alfabeto:
                if (q, a) not in self.transicoes:
                    self.transicoes[(q, a)] = erro

        for a in self.alfabeto:
            self.transicoes[(erro, a)] = erro

        return self

    def complemento (self):
        for e in self.estados:
            if e not in self.estados_finais:
                self.estados_finais.add(e)
            else:
                self.estados_finais.remove(e)

        return self

    def produto (self, other, operacao):
        operacoes_aceitas = ["uniao", "intersecao", "diferenca", "xor"]
        if operacao not in operacoes_aceitas:
            return None

        afd1 = self
        afd2 = other

        if operacao == "diferenca":
            afd2 = afd2.complemento()

        produto_estados = {}

        # Vamos mapear a junção dos estados, pois assim conseguiremos retornar o AFD corretamente
        for estado_afd1 in afd1.estados:
            for estado_afd2 in afd2.estados:
                nome_estado = f"{estado_afd1}_{estado_afd2}"
                produto_estados[(estado_afd1, estado_afd2)] = nome_estado

        # Agora, vamos juntar os alfabetos dos dois AFDs
        produto_alfabetos = afd1.alfabeto.union(afd2.alfabeto)

        # Agora, vamos mapear as transições dos estados juntos de acordo com cada símbolo no novo alfabeto
        produto_transicoes = {}

        for (estado_afd1, estado_afd2), nome_estado_atual in produto_estados.items():
            for simbolo in produto_alfabetos:
                destino_afd1 = afd1.transicoes.get((estado_afd1, simbolo))
                destino_afd2 = afd2.transicoes.get((estado_afd2, simbolo))

                # Se as duas transições não levarem a None, então juntamos elas
                if destino_afd1 is not None and destino_afd2 is not None:
                    estado_destino = produto_estados.get((destino_afd1, destino_afd2))
                    if estado_destino is not None:
                        produto_transicoes[(nome_estado_atual, simbolo)] = estado_destino

        # Definindo o novo estado inicial
        produto_estado_inicial = produto_estados[(afd1.estado_inicial, afd2.estado_inicial)]

        # Definindo os estados finais
        produto_estados_finais = set()

        for (estado_afd1, estado_afd2), nome_estado_atual in produto_estados.items():
            is_final_afd1 = estado_afd1 in afd1.estados_finais
            is_final_afd2 = estado_afd2 in afd2.estados_finais

            if operacao == "uniao":
                if is_final_afd1 or is_final_afd2:
                    produto_estados_finais.add(nome_estado_atual)

            if operacao in ("intersecao", "diferenca"):
                # Se a operação for "diferença", o autômato já está invertido no começo da função
                # então podemos usar somente o operador "and" que teremos os mesmos resultados
                if is_final_afd1 and is_final_afd2:
                    produto_estados_finais.add(nome_estado_atual)

            if operacao == "xor":
                if is_final_afd1 and not is_final_afd2:
                    produto_estados_finais.add(nome_estado_atual)

        # Definindo o nome dos estados para o retorno do AFD
        nomes_estados = set(produto_estados.values())

        return AFD(nomes_estados, produto_alfabetos, produto_transicoes, produto_estado_inicial, produto_estados_finais)

    def minimizar(self):
        afd1 = self.completar()

        particoes = [afd1.estados_finais, afd1.estados - afd1.estados_finais]
        lista_trabalho = [afd1.estados_finais.copy()]

        # Refinamento Hopcroft
        while lista_trabalho:
            bloco_atual = lista_trabalho.pop()
            for simbolo in afd1.alfabeto:
                antecessores = {
                    estado
                    for estado in afd1.estados
                    if afd1.transicoes.get((estado, simbolo)) in bloco_atual
                }

                for bloco in particoes[:]:
                    intersecao = bloco & antecessores
                    diferenca = bloco - antecessores

                    if intersecao and diferenca:
                        particoes.remove(bloco)
                        particoes.extend([intersecao, diferenca])

                        if bloco in lista_trabalho:
                            lista_trabalho.remove(bloco)
                            lista_trabalho.extend([intersecao, diferenca])
                        else:
                            menor = intersecao if len(intersecao) <= len(diferenca) else diferenca
                            lista_trabalho.append(menor)

        # Criar nomes legíveis para os novos estados
        bloco_para_nome = {}
        for i, bloco in enumerate(particoes):
            nome = "_".join(sorted(bloco))
            bloco_para_nome[frozenset(bloco)] = nome

        # Mapear estados antigos para o novo nome do bloco
        estado_para_bloco = {}
        for bloco_frozen, nome in bloco_para_nome.items():
            for estado in bloco_frozen:
                estado_para_bloco[estado] = nome

        novos_estados = set(bloco_para_nome.values())
        novo_estado_inicial = estado_para_bloco[afd1.estado_inicial]
        novos_estados_finais = {
            estado_para_bloco[e] for e in afd1.estados_finais
        }

        novas_transicoes = {}
        for bloco_frozen, nome in bloco_para_nome.items():
            representante = next(iter(bloco_frozen))
            for simbolo in afd1.alfabeto:
                destino = afd1.transicoes[(representante, simbolo)]
                destino_nome = estado_para_bloco[destino]
                novas_transicoes[(nome, simbolo)] = destino_nome

        return AFD(
            novos_estados,
            afd1.alfabeto,
            novas_transicoes,
            novo_estado_inicial,
            novos_estados_finais
        )
