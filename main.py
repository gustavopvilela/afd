from typing import Iterable, Dict, Tuple
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
    def inverter_dicionario(d):
        return {v: k for k, v in d.items()}

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

    def exportar_xml(self, arquivo: str):
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

    file = "C:\\Users\\gusta\\Desktop\\7-1b.jff"
    novo_afd = AFD.importar_jflap(file)
    print(novo_afd)

    AFD.exportar_xml(novo_afd, "C:\\Users\\gusta\\Desktop\\teste.jff")