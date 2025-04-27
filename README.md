
# Trabalho Prático 1 de *Fundamentos Teóricos da Computação*: Simulação de AFDs - *Autômatos Finitos Determinísticos*  
  
![FTC](https://img.shields.io/badge/IFMG-Fundamentos%20Te%C3%B3ricos%20da%20Computa%C3%A7%C3%A3o-0b3f9e)  [![Python](https://img.shields.io/badge/python-3.13.2-blue)](https://www.python.org/)  
  
## Introdução  
O código deste repositório representa o primeiro trabalho prático da disciplina de Fundamentos Teóricos da Computação.  Seu intuito é simular as funções e propriedades de autômatos finitos determinísticos (AFDs), como minimização, equivalência e produto - com as operações de união, interseção e diferença.

## Funções do programa
A seguir, serão apresentadas as funções principais dos algoritmos presentes neste trabalho.

### 1. Importação de arquivos JFLAP (.jff)
O trabalho permite importar arquivos de AFDs diretamente do programa JFLAP no formato XML (.jff, no caso do software) para maior facilidade de utilização. A biblioteca `Tkinter` é usada para abrir uma janela de diálogo para a escolha do arquivo.
O usuário pode importar quantos autômatos desejar, uma vez que eles ficam armazenados em memória em um dicionário que relaciona seus nomes (que o usuário dá) com as classes montadas pelo programa no momento da importação. Dessa forma, para qualquer operação que se deseja fazer, basta digitar o nome do autômato dentro do algoritmo, e ele será usado.

### 2. Exportação de arquivos JFLAP
Depois de realizar as funcionalidades com o autômato, o usuário pode salvá-lo em seu computador como um arquivo JFLAP para posterior utilização e visualização. Essa funcionalidade também utiliza a biblioteca `Tkinter` para a janela de seleção de arquivos.

### 3. Minimização de AFDs
A minimização de um AFD é o processo de diminuir a quantidade de estados necessários para processar uma cadeia de caracteres sem alterar o seu funcionamento. Dessa forma, o autômato minimizado aceitará e rejeitará as mesmas cadeias de caracteres que seu original.
O processo de minimização de um autômato no programa ocorre da seguinte forma:
**a. Encontrar os estados alcançáveis:**  se um estado não é alcançável a partir do estado final, ele não faz diferença para o funcionamento do autômato, logo, pode ser retirado sem maiores problemas.

**b. Encontrar estados não equivalentes:** este processo utiliza do teorema de _Myhill-Nerode_ (link nos próximos tópicos), no qual é possível identificar os estados que não são equivalentes dentro do autômato.

**c. Agrupar estados equivalentes:** ainda no mesmo teorema, agrupamos os estados equivalentes seguindo o seguinte pensamento: esse processo é a formação de "estados minimizados" (grupos) a partir dos estados originais do AFD. Inicialmente, cada estado original forma seu próprio estado minimizado. Depois, quando descobrimos que dois estados são equivalentes (não pertencendo ao conjunto de estados não equivalentes anteriormente descoberto), unimos seus estados minimizados correspondentes. Se o estado $q_1$ está representado pelo estado minimizado representante $r_1$ e o estado $q_2$ pelo estado minimizado $r_2$, unimos o grupo de $r_2$ ao grupo de $r_1$ e mantemos apenas $r_1$ como representante do grupo unificado. Depois, atualizamos o dicionário de grupos para que as referências a $r_2$ sejam, removidas, já que agora todos os estados que pertenciam a $r_2$ foram movidos para $r_1$.

**d. Construir o AFD minimizado:** com os grupos de estados equivalentes em mãos, simplesmente construímos um dicionário que relaciona um estado para o representante do seu grupo (o com o primeiro nome na ordem alfabética). Assim, os novos estados do AFD mínimo excluirão os demais estados do grupo de equivalentes. Para as transições, substituímos cada estado pelo representante de seu grupo, bem como acontece com o estado inicial e os estados finais. Dessa forma, retornamos o autômato montado e minimizado.
O autômato minimizado pode substituir o original ou ser salvo com o nome automático `[nome-original]-min`, dependendo da escolha do usuário.

### 4. União de AFDs
A união de dois AFDs é dada pelo seguinte: $L(A) \cup L(B)$, ou seja, é um AFD em que as palavras de entrada podem ser aceitas no primeiro, no segundo ou nos dois autômatos ao mesmo tempo.
Então, o programa fará o produto dos dois e a união do segundo com o primeiro, atribuindo os novos estados finais onde os estados de pelo menos um dos AFDs são finais. Logo, ele será salvo como um novo AFD de nome automático `[nome-afd1]-uni-[nome-afd2]`.

### 5. Interseção de AFDs
A interseção de dois AFDs é dada pelo seguinte: $L(A)\cap L(B)$, ou seja, é um AFD em que as palavras de entrada devem ser aceitas nos dois autômatos simultaneamente.
Então, o programa fará o produto dos dois e a interseção do segundo com o primeiro, atribuindo os novos estados finais onde os estados de ambos os autômatos são finais. Logo, ele será salvo como um novo AFD de nome automático `[nome-afd1]-int-[nome-afd2]`.

### 6. Diferença de AFDs
A diferença de dois AFDs é dada pelo seguinte: $L(A-B) = L(A) ∖ L(B)$, isto é, todas as palavras pertencentes a $A$ e não pertencentes a $B$, sendo basicamente $L(A)\cap \overline{L(B)}$.
Então, o programa fará o complemento do segundo autômato e, posteriormente, o produto dos dois e a interseção do segundo com o primeiro, atribuindo os novos estados finais onde os estados de ambos os autômatos são finais. Logo, ele será salvo como um novo AFD de nome automático `[nome-afd1]-dif-[nome-afd2]`.

### 7. Complemento de AFD
O complemento de um AFD é feito quando atribuímos o _status_ de final aos estados que não são, e tiramos esse atributo dos estados que são. No programa, o usuário pode escolher se o autômato complementado será atribuído a um novo autômato ou se substituirá o original. Caso um novo AFD seja gerado, ele terá o nome automático de `[nome-original]-comp`.

### 8. Equivalência de AFDs
O programa testa se dois AFDs são equivalentes ou não retornando `True` ou `False` para cada um dos casos, respectivamente. As condições para que dois autômatos sejam equivalentes são as seguintes:
**a.** Os alfabetos precisam ser iguais;

**b.** Se o estado inicial de um deles for final, o estado inicial do outro necessariamente precisa ser final também.

**c.** Para qualquer par de estados gerado a partir dos estados iniciais de dois autômatos na forma $(q_i, q_j)$, a transição para a entrada $a \in \Sigma$ é definida por $(q_a, q_b)$ na qual $\delta(q_i,a)=q_a$ e $\delta(q_j,a)=q_b$. Dessa forma, os dois autômatos **_não_** são equivalentes se para um par $(q_a, q_b)$ um dos elementos é um estado intermediário (não final) e o outro é um estado final. Fonte: https://www.youtube.com/watch?v=nX4JrcHgpZY

### 9. Estados equivalentes
O programa também consegue identificar quais grupos de estados são equivalentes dentro de um autômato. Isso acontece usando basicamente usando o teorema de _Myhill-Nerode_, o método da tabela que é usado no processo de minimização de autômatos finitos determinísticos. Fonte: https://www.youtube.com/watch?v=UiXkJUTkp44
Ao usar essa função, ela retorna algo parecido com o seguinte:
```text
O seguinte conjunto de estados é equivalente: q11, q14
O seguinte conjunto de estados é equivalente: q1, q5, q6, q8
```
Mas, _atenção_, essa função não vai juntar os estados equivalentes em um só. Isso é cargo da função de minimização, que também utiliza do mesmo teorema em seu funcionamento.

### 10. Visualização de AFDs disponíveis
Dado pelo menos um autômato importado no sistema, será possível visualizar todos os AFDs disponíveis no programa. O resultado será parecido com o a seguir:
```text
1. a-impar
2. b-impar
```

### 11. Visualização de AFD
Dado pelo menos um autômato importado no sistema, será possível visualizar seus estados, alfabeto, transições, estado inicial e estados finais dentro do programa. Basta selecioná-lo e aparecerá um resultado parecido com o a seguir:
```text
AFD(
    estados: ['q0', 'q1']
    alfabeto: ['a', 'b']
    transicoes:
	    ('q0', 'b') -> q0
	    ('q1', 'b') -> q1
	    ('q0', 'a') -> q1
	    ('q1', 'a') -> q0
    estado_inicial: q0
    estados_finais: ['q1']
)
```

### 12. Cópia de AFD
Caso seja necessário uma nova instância de certo autômato, basta copiá-lo que haverá uma cópia independente do original, nomeada automaticamente como `[nome-original]-copia`.
  
---  
  
*Desenvolvido com ❤️ para o professor Walace.*