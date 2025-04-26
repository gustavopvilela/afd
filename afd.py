from copy import deepcopy
from typing import *
import xml.etree.ElementTree as ElementTree
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

    """
        Método toString da classe para mostrar na tela os dados do
        autômato atual: estados, alfabeto, transições, estado inicial e estados finais.
    """
    def __str__(self):
        return (
            f"AFD(\n"
            f"    estados: {sorted(self.estados)}\n"
            f"    alfabeto: {sorted(self.alfabeto)}\n"
            f"    transicoes:\n     "+
            "\n     ".join([f"{k} -> {v}" for k, v in self.transicoes.items()]) + "\n"
            f"    estado_inicial: {self.estado_inicial}\n"
            f"    estados_finais: {sorted(self.estados_finais)}\n"
            f")"
        )

    """
        Método para inverter um dicionário. É usado para exportar para um arquivo JFLAP,
        uma vez que nas transições é usado o ID do estado, e não seu nome. Dessa forma,
        o par (key: value) de (ID: nome) deve ser alterado para (nome: ID).
    """
    @staticmethod
    def inverter_dicionario (d):
        return {v: k for k, v in d.items()}

    """
        Método para criar uma cópia do autômato atual. Nele é usado o deepcopy da biblioteca
        copy para que se crie uma duplicação que seja independente da original (diferente do
        método copy).
    """
    def copiar (self):
        return deepcopy(self)

    """
        Função para verificar se uma certa cadeia de caracteres é aceita no autômato. Caso o úl-
        timo estado a ser passado seja um estado final, a cadeia é válida, caso contrário, não é.
        Além disso, se entrar com uma cadeia que não pertença ao alfabeto, o estado que a transi-
        ção levará será None, e o método retornará falso imediatamente.
    """
    def validar (self, cadeia: str):
        estado_atual = self.estado_inicial

        for simbolo in cadeia:
            estado_atual = self.transicoes.get((estado_atual, simbolo))
            if estado_atual is None:
                return False

        return estado_atual in self.estados_finais

    """
        Método para importar um arquivo JFLAP para o programa. Ele usa a biblioteca de leitura de XML
        do Python e mapeia cada tag do arquivo formando uma instância da classe AFD no final.
    """
    @classmethod
    def importar_jflap (cls, arquivo: str):
        xml = ElementTree.parse(arquivo)
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

    """
        Método para exportar o autômato atual para um arquivo JFLAP (XML). Ele monta o arquivo formatado
        de acordo com as especificações do software. Por fim ele salva o arquivo no computador.
    """
    def exportar_jflap (self, arquivo: str):
        root = ElementTree.Element('structure')

        # Tipo do autômato: fa = finite automaton
        tipo = ElementTree.SubElement(root, 'type')
        tipo.text = 'fa'

        # Subtag dentro de structure: automaton
        automaton = ElementTree.SubElement(root, 'automaton')

        # Para cada estado, colocamos como uma subtag
        # Além disso, precisamos colocar id's únicos para cada estado, então
        # vamos ter que criar novamente um dicionário que relaciona id com estado,
        # assim, poderemos criar as transições depois.
        id_nome = {}
        id = 0
        for estado in self.estados:
            state = ElementTree.SubElement(automaton, 'state')
            state.set('name', estado)
            state.set('id', str(id))
            id_nome[id] = estado
            id += 1

            if self.estado_inicial == estado:
                ElementTree.SubElement(state, 'initial')

            if estado in self.estados_finais:
                ElementTree.SubElement(state, 'final')

        # Agora, vamos colocar as transições
        for (ea, s), ed in self.transicoes.items():
            # Para pegar os IDs a partir do valor, vamos inverter
            # o dicionário
            d_inv = self.inverter_dicionario(id_nome)

            transicao = ElementTree.SubElement(automaton, 'transition')
            from_estado = ElementTree.SubElement(transicao, 'from')
            from_estado.text = str(d_inv[ea])

            to_estado = ElementTree.SubElement(transicao, 'to')
            to_estado.text = str(d_inv[ed])

            read = ElementTree.SubElement(transicao, 'read')
            read.text = s


        # Formatando o arquivo com identação para facilitar a visualização
        para_string = ElementTree.tostring(root, 'utf-8')
        dom = minidom.parseString(para_string)
        arquivo_formatado = dom.toprettyxml(indent="    ")

        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(arquivo_formatado)

    """
        Método para completar um autômato. Este método é necessário para a minimização do AFD, uma vez que
        se nem todas as transições estão no AFD, logo o cálculo de estados equivalentes é falho.
    """
    def completar (self):
        afd = AFD.copiar(self)

        erro = 'E'
        if erro not in afd.estados:
            afd.estados.add(erro)

        for estado in list(afd.estados):
            for simbolo in afd.alfabeto:
                if (estado, simbolo) not in afd.transicoes:
                    afd.transicoes[(estado, simbolo)] = erro

        for simbolo in afd.alfabeto:
            afd.transicoes[(erro, simbolo)] = erro

        return afd

    """
        Método para gerar o complemento do AFD atual. Faz-se a seguinte alteração: se o estado é final,
        logo, ele não é mais. Se ele não é, logo, agora é.
    """
    def complemento (self):
        complemento = AFD.copiar(self)

        for e in complemento.estados:
            if e not in complemento.estados_finais:
                complemento.estados_finais.add(e)
            else:
                complemento.estados_finais.remove(e)

        return complemento

    """
        Funções para realizar o produto de dois autômatos seguindo alguma regra. Essa regra pode ser a
        união, interseção, diferença ou o xor dos dois AFDs. Primeiro, fazemos o produto dos estados,
        eles são armazenados em um dicionário da forma (e1, e2): nome_e1_e2, para que depois se possa
        gerar os estados do novo autômato.
        
        Depois, gera-se o produto dos alfabetos dos autômatos, consistindo na união dos dois.
        
        Assim, geramos as transições. Para isso ocorrer, a transição deve acontecer nos dois
        AFDs simultaneamente: aqui não criamos o estado de erro como na função de completar,
        portanto, as transições devem existir em ambos os casos. Dessa forma, pegamos o nome do estado da
        transição no dicionário de produtos de estados que criamos. Se o estado de destino existir
        no dicionário (do jeito que a função está montada, acredito que é bem difícil ele não existir),
        adicionamos ele no dicionário de novas transições.
        
        Definimos, então, o novo estado inicial e por fim selecionamos os novos estados finais baseados
        na operação que é passada por parâmetro e retornamos o novo AFD.
    """
    def produto (self, other):
        afd1 = self
        afd2 = other

        produto_estados = {}
        for estado_afd1 in afd1.estados:
            for estado_afd2 in afd2.estados:
                nome_estado = f"{estado_afd1}_{estado_afd2}"
                produto_estados[(estado_afd1, estado_afd2)] = nome_estado

        produto_alfabetos = afd1.alfabeto.union(afd2.alfabeto)

        produto_transicoes = {}
        for (estado_afd1, estado_afd2), nome_estado_atual in produto_estados.items():
            for simbolo in produto_alfabetos:
                destino_afd1 = afd1.transicoes.get((estado_afd1, simbolo))
                destino_afd2 = afd2.transicoes.get((estado_afd2, simbolo))

                # Se as duas transições não levarem a None, juntamos elas
                if destino_afd1 is not None and destino_afd2 is not None:
                    estado_destino = produto_estados.get((estado_afd1, estado_afd2))
                    if estado_destino is not None:
                        produto_transicoes[(nome_estado_atual, simbolo)] = estado_destino

        produto_estado_inicial = produto_estados[(afd1.estado_inicial, afd2.estado_inicial)]

        nomes_estados = set(produto_estados.values())

        # Aqui, retornaremos os dados obtidos até o momento para que as funções específicas
        # possam tratá-los de maneira adequada.
        return produto_estados, nomes_estados, produto_alfabetos, produto_transicoes, produto_estado_inicial

    def intersecao (self, other):
        afd1 = self
        afd2 = other

        estados, nomes_estados, alfabeto, transicoes, estado_inicial = AFD.produto(afd1, afd2)

        # Definindo os estados finais para montar o AFD
        produto_estados_finais = set()
        for(estado_afd1, estado_afd2), nome_estado_atual in estados.items():
            is_final_afd1 = estado_afd1 in afd1.estados_finais
            is_final_afd2 = estado_afd2 in afd2.estados_finais

            # Aplicando a operação de interseção
            if is_final_afd1 and is_final_afd2:
                produto_estados_finais.add(nome_estado_atual)

        # Retornando o AFD montado
        return AFD(nomes_estados, alfabeto, transicoes, estado_inicial, produto_estados_finais)

    def diferenca(self, other):
        afd1 = self
        afd2 = other
        afd2 = afd2.complemento()

        estados, nomes_estados, alfabeto, transicoes, estado_inicial = AFD.produto(afd1, afd2)

        # Definindo os estados finais para montar o AFD
        produto_estados_finais = set()
        for (estado_afd1, estado_afd2), nome_estado_atual in estados.items():
            is_final_afd1 = estado_afd1 in afd1.estados_finais
            is_final_afd2 = estado_afd2 in afd2.estados_finais

            # Aplicando a operação de interseção
            if is_final_afd1 and is_final_afd2:
                produto_estados_finais.add(nome_estado_atual)

        # Retornando o AFD montado
        return AFD(nomes_estados, alfabeto, transicoes, estado_inicial, produto_estados_finais)

    def xor(self, other):
        afd1 = self
        afd2 = other

        estados, nomes_estados, alfabeto, transicoes, estado_inicial = AFD.produto(afd1, afd2)

        # Definindo os estados finais para montar o AFD
        produto_estados_finais = set()
        for (estado_afd1, estado_afd2), nome_estado_atual in estados.items():
            is_final_afd1 = estado_afd1 in afd1.estados_finais
            is_final_afd2 = estado_afd2 in afd2.estados_finais

            # Aplicando a operação de interseção
            if is_final_afd1 ^ is_final_afd2:
                produto_estados_finais.add(nome_estado_atual)

        # Retornando o AFD montado
        return AFD(nomes_estados, alfabeto, transicoes, estado_inicial, produto_estados_finais)

    def uniao(self, other):
        afd1 = self
        afd2 = other

        estados, nomes_estados, alfabeto, transicoes, estado_inicial = AFD.produto(afd1, afd2)

        # Definindo os estados finais para montar o AFD
        produto_estados_finais = set()
        for (estado_afd1, estado_afd2), nome_estado_atual in estados.items():
            is_final_afd1 = estado_afd1 in afd1.estados_finais
            is_final_afd2 = estado_afd2 in afd2.estados_finais

            # Aplicando a operação de interseção
            if is_final_afd1 or is_final_afd2:
                produto_estados_finais.add(nome_estado_atual)

        # Retornando o AFD montado
        return AFD(nomes_estados, alfabeto, transicoes, estado_inicial, produto_estados_finais)

    """
        
    """
    def testar_equivalencia (self, other):
        # Copiando os AFDs para evitar interferências nos originais
        afd1 = self.copiar()
        afd2 = other.copiar()

        # Para ter a possibilidade de serem equivalentes, os
        # autômatos devem ter o mesmo alfabeto
        if afd1.alfabeto != afd2.alfabeto:
            return False

        # Uma das condições de dois AFDs serem equivalentes é que
        # se o estado inicial de um deles for final, o do outro deve
        # se comportar da mesma maneira
        if (afd1.estado_inicial in afd1.estados_finais and afd2.estado_inicial not in afd2.estados_finais) or (afd2.estado_inicial in afd2.estados_finais and afd1.estado_inicial not in afd1.estados_finais):
            return False

        # Para qualquer par gerado a partir dos estados iniciais de um autômato
        # na forma {qi, qj}, a transição para a entrada a ∈ Σ é definido por
        # {qa, qb} no qual δ{qi, a} = qa e δ{qj, a} = qb. Dessa forma, os dois
        # autômatos NÃO são equivalentes se para um par {qa, qb}, um dos elementos
        # é um estado intermediário (não final) e o outro é um estado final.
        # Fonte: https://www.youtube.com/watch?v=nX4JrcHgpZY
        estados_verificados = {}

        e1 = afd1.estado_inicial
        e2 = afd2.estado_inicial

        # True = dupla já verificada; False = dupla ainda não verificada
        estados_verificados[(e1, e2)] = False

        while False in estados_verificados.values():
            # Escolhendo a próxima dupla de estados dentro do dicionário
            for (k1, k2), valor in estados_verificados.items():
                if not valor:
                    e1 = k1
                    e2 = k2

            # Olhando as transições da dupla de estados para cada
            # símbolo no alfabeto
            for simbolo in afd1.alfabeto: # Como já foi verificado os dois alfabetos, tanto faz a utilização de qualquer um
                t1 = afd1.transicoes.get((e1, simbolo))
                t2 = afd2.transicoes.get((e2, simbolo))

                if (t1 in afd1.estados_finais and t2 not in afd2.estados_finais) or (t1 not in afd1.estados_finais and t2 in afd2.estados_finais):
                    return False

                if (t1, t2) not in estados_verificados.keys():
                    estados_verificados[(t1, t2)] = False

                estados_verificados[(e1, e2)] = True

        # Caso não for achado nenhum par de estados que satisfaça as condições de não equivalência, retornamos True
        return True

    def estados_equivalentes(self):
        estados_alcancaveis = self.obter_estados_alcancaveis()
        nao_equivalentes = self.encontrar_estados_nao_equivalentes(estados_alcancaveis)
        grupos_equivalentes = self.agrupar_estados_equivalentes(estados_alcancaveis, nao_equivalentes)

        # O resultado dos grupos é uma lista de sets, então filtramos essa lista para que ela retorne
        # somente os sets que possuam mais de um elemento, ou seja, os grupos que possuam estados
        # equivalentes.
        return [s for s in grupos_equivalentes if len(s) > 1]

    def obter_estados_alcancaveis (self):
        # Se um estado não é alcançável a partir do estado inicial,
        # ele não interfere no funcionamento do AFD, logo pode ser retirado
        alcancaveis = {self.estado_inicial}
        pilha = [self.estado_inicial]

        while pilha:
            estado = pilha.pop()
            for simbolo in self.alfabeto:
                if (estado, simbolo) in self.transicoes:
                    proximo_estado = self.transicoes[(estado, simbolo)]
                    if proximo_estado not in alcancaveis:
                        alcancaveis.add(proximo_estado)
                        pilha.append(proximo_estado)

        return alcancaveis

    def encontrar_estados_nao_equivalentes (self, alcancaveis):
        # Encontramos os estados distinguíveis, ou seja, os equivalentes,
        # usando o algoritmo de Myhill-Nerode
        nao_equivalentes = set()

        # Primeiro percorremos o conjunto de estados alcançáveis e adicionamos
        # aqueles que não são equivalentes logo de cara, ou seja: os finais e os
        # não finais
        for q1 in alcancaveis:
            for q2 in alcancaveis:
                if q1 < q2: # Previne a duplicação (q1, q2) e (q2, q1)
                    if (q1 in self.estados_finais) != (q2 in self.estados_finais):
                        nao_equivalentes.add((q1, q2))

        # Agora, encontramos mais pares de estados que não são equivalentes até que
        # estes se esgotem
        mudou = True
        while mudou:
            mudou = False
            for q1 in alcancaveis:
                for q2 in alcancaveis:
                    if q1 < q2 and (q1, q2) not in nao_equivalentes:
                        # Verificamos se são não equivalentes através de algum símbolo
                        for simbolo in self.alfabeto:
                            # Obtendo os próximos estados após a transição
                            prox1 = self.transicoes.get((q1, simbolo))
                            prox2 = self.transicoes.get((q2, simbolo))

                            # Se um tem transição e o outro não, são não equivalentes
                            if (prox1 is None) != (prox2 is None):
                                nao_equivalentes.add((q1, q2))
                                mudou = True
                                break

                            # Se os dois têm transição, verificamos se os próximos estados já são não equivalentes
                            if prox1 is not None and prox2 is not None:
                                if prox1 == prox2:
                                    continue # Mesmo estado

                                if (min(prox1, prox2), max(prox1, prox2)) in nao_equivalentes:
                                    nao_equivalentes.add((q1, q2))
                                    mudou = True
                                    break

        return nao_equivalentes

    def agrupar_estados_equivalentes (self, alcancaveis, nao_equivalentes):
        # Primeiro, inicializamos cada estado no seu próprio grupo
        grupos = {}
        for estado in alcancaveis:
            grupos[estado] = {estado}

        # Agora, unimos os estados equivalentes
        for q1 in alcancaveis:
            for q2 in alcancaveis:
                if q1 != q2 and (min(q1, q2), max(q1, q2)) not in nao_equivalentes:
                    # Os estados q1 e q2 são equivalentes
                    grupo_q1 = None
                    grupo_q2 = None

                    # Encontrando os grupos dos estados
                    for representante, grupo in grupos.items():
                        if q1 in grupo:
                            grupo_q1 = representante
                        if q2 in grupo:
                            grupo_q2 = representante

                    # Se estão em grupos diferentes, são unidos
                    if grupo_q1 != grupo_q2:
                        grupos[grupo_q1].update(grupos[grupo_q2])
                        del grupos[grupo_q2]

                        for estado in grupos[grupo_q1]:
                            if estado != grupo_q1:
                                if estado in grupos:
                                    del grupos[estado]

        # Retornando a lista de conjuntos de estados equivalentes
        return list(grupos.values())

    def construir_afd_minimizado (self, grupos_equivalentes):
        # Com temos vários estados num grupo, escolhemos um para representar todos ao montar as transições e
        # os estados finais. Esse vai ser o representante e é o primeiro na lista ordenada dos estados no grupo de equivalentes.
        estado_para_representante = {}
        for grupo in grupos_equivalentes:
            representante = sorted(grupo)[0]
            for estado in grupo:
                estado_para_representante[estado] = representante

        # Criando os novos estados
        novos_estados = set(estado_para_representante.values())

        # Criando as novas transições
        novas_transicoes = {}
        for estado in novos_estados:
            for simbolo in self.alfabeto:
                if (estado, simbolo) in self.transicoes:
                    alvo = self.transicoes[(estado, simbolo)]
                    # Mapeando para o representante do grupo
                    novas_transicoes[(estado, simbolo)] = estado_para_representante[alvo]

        # Por fim, colocando o novo estado inicial e os novos estados finais
        novo_estado_inicial = estado_para_representante[self.estado_inicial]
        novos_estados_finais = set()
        for estado_final in self.estados_finais:
            novos_estados_finais.add(estado_para_representante[estado_final])

        return AFD(novos_estados, self.alfabeto, novas_transicoes, novo_estado_inicial, novos_estados_finais)

    def minimizar (self):
        estados_alcancaveis = self.obter_estados_alcancaveis()
        nao_equivalentes = self.encontrar_estados_nao_equivalentes(estados_alcancaveis)
        grupos_equivalentes = self.agrupar_estados_equivalentes(estados_alcancaveis, nao_equivalentes)
        return self.construir_afd_minimizado(grupos_equivalentes)