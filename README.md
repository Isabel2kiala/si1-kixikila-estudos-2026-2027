# Rotas entre capitais provinciais e jogo de Damas

Projecto 1 de **Sistemas Inteligentes I**, Engenharia Informática (3.º ano, 1.º semestre, 2026/2027).
Docente: Arlindo Almada.

O projecto tem duas partes:

- **Parte A, pesquisa de rotas.** Planeia viagens entre as capitais provinciais de Angola com BFS, UCS e A* (heurística geodésica de haversine).
- **Parte B, Damas.** Escolhe jogadas nas damas clássicas portuguesas com Minimax e com poda alfa-beta, usando uma função de avaliação própria.

![Grafo das capitais e rota óptima Luanda → Ondjiva](figuras/grafo_capitais.png)

## Autores

| Nome | Número de estudante |
|---|---|
| _Nome 1_ | _00000_ |
| _Nome 2_ | _00000_ |

## Requisitos

- Python **3.10 ou mais recente** (testado com 3.13)
- Só a biblioteca padrão para o código principal
- **matplotlib** (testado com 3.11), apenas para as figuras

```bash
# Ubuntu / Debian
sudo apt install python3 python3-matplotlib
# ou, em qualquer sistema
pip install matplotlib
```

> Em Linux, o comando é `python3`. Se `python` der "not found", usa `python3` em todos os comandos abaixo.

## Como executar

Todos os comandos correm **dentro da pasta do projecto**, porque os ficheiros CSV são lidos a partir da pasta actual.

```bash
git clone <url-do-repositório>
cd <pasta-do-repositório>

python3 rotas.py                                  # BFS, UCS e A* de Luanda a Ondjiva
python3 grafo.py                                  # lista das capitais e respectivas ligações
python3 damas.py                                  # verifica as regras e joga uma partida aleatória
python3 mapa_rotas.py                             # gera as figuras em figuras/

python3 -m unittest testes_p1 -v                  # testes do docente
python3 -m unittest testes_proprios -v            # testes próprios
python3 -m unittest testes_p1 testes_proprios     # todos os testes
```

Resultado esperado de `python3 rotas.py`:

```
BFS     1338 km   11 expandidos  Luanda → Sumbe → Benguela → Lubango → Ondjiva
UCS     1338 km   17 expandidos  Luanda → Sumbe → Benguela → Lubango → Ondjiva
A*      1338 km   10 expandidos  Luanda → Sumbe → Benguela → Lubango → Ondjiva
```

## Estrutura

| Ficheiro | Origem | Conteúdo |
|---|---|---|
| `capitais.csv` | docente | província, capital, latitude, longitude (21 capitais) |
| `estradas.csv` | docente | origem, destino, distancia_km (27 ligações, válidas nos dois sentidos) |
| `grafo.py` | docente | `carregar_grafo()` → `(coordenadas, adjacências)` |
| `damas.py` | docente | motor das Damas: regras, jogadas legais, fim de jogo, agente aleatório, torneio e 5 posições de teste |
| `testes_p1.py` | docente | testes básicos da interface |
| `rotas.py` | **nosso** | `haversine`, `bfs`, `ucs`, `a_estrela` |
| `jogos.py` | **nosso** | `minimax`, `alfabeta`, `avaliar`, `escolher_jogada` |
| `testes_proprios.py` | **nosso** | 23 testes adicionais (pesquisa, minimax, alfa-beta, avaliação, agente) |
| `mapa_rotas.py` | **nosso** | desenha o grafo e compara a ordem de expansão da UCS e do A* |
| `figuras/` | gerado | imagens produzidas por `mapa_rotas.py` |

## Parte A: pesquisa de rotas

**Formulação.**

| Elemento | Definição |
|---|---|
| Estado | a capital onde o veículo se encontra |
| Estado inicial | a capital de origem |
| Acções | seguir por uma estrada até uma capital vizinha |
| Modelo de transição | `resultado(n, ir_para(m)) = m` |
| Teste de objectivo | `estado == destino` |
| Custo de caminho | soma das `distancia_km` dos troços percorridos |

**Algoritmos.** Todos são pesquisas em grafo, com registo dos estados já atingidos.

| Algoritmo | Fronteira | Ordena por | Garante |
|---|---|---|---|
| BFS | fila FIFO (`deque`) | ordem de chegada | menor número de troços |
| UCS | `heapq` | g(n), km percorridos | menor distância |
| A* | `heapq` | f(n) = g(n) + h(n) | menor distância, se h for admissível |

A heurística do A* é **h(n) = haversine(n, destino)**, a distância geodésica com raio terrestre de 6371 km. O A* e a UCS testam o objectivo quando o estado **sai** da fronteira. Usam também remoção preguiçosa: as entradas obsoletas são ignoradas, e um estado volta a ser aberto se for atingido por um caminho mais curto.

![UCS contra A*: ordem de expansão](figuras/ucs_vs_aestrela.png)

## Parte B: Damas

- **`minimax`**: pesquisa com limite de profundidade. Os valores são sempre calculados na perspectiva do jogador da raiz. Os nós contados incluem a raiz.
- **`alfabeta`**: o mesmo valor que o Minimax, com poda. As jogadas são ordenadas (capturas maiores e promoções primeiro) para podar mais cedo.
- **`avaliar`**: diferença entre os dois jogadores em quatro características:

| Característica | Peso | Justificação |
|---|---|---|
| Peão | 100 | unidade base |
| Dama | 300 | a dama voadora anda e captura à distância |
| Avanço do peão | 4 por linha | aproxima o peão da promoção; nunca vale mais do que um peão |
| Peão na fila de trás | 12 | guarda as casas de promoção do adversário |
| Peça no centro (casas 14, 15, 18, 19) | 8 | mais mobilidade |
| Vitória / derrota / empate | ±10 000 / 0 | domina qualquer outra soma |

- **`escolher_jogada`**: aprofundamento iterativo com alfa-beta, dentro do limite de tempo do torneio (2 s por jogada).

## Dados

Os ficheiros `capitais.csv` e `estradas.csv` foram fornecidos pelo docente. Contêm as 21 capitais provinciais, segundo a divisão administrativa em vigor, e 27 ligações rodoviárias. As distâncias são **aproximadas e para fins didácticos**: não correspondem a medições oficiais nem ao estado real das estradas.

## Hipóteses e limitações

- O custo de uma rota é só a distância em km. Não entram o estado da estrada, o tempo de viagem, o combustível nem a segurança.
- Cabinda não tem ligações no grafo, por isso qualquer pesquisa com origem ou destino em Cabinda devolve `None`.
- A estrada **Malanje–Cuíto** (259 km) é mais curta do que a distância geodésica entre as duas capitais (≈ 324 km). Nessa aresta, a heurística deixa de ser admissível e consistente. O A* reabre estados para se proteger, e nos dados fornecidos encontra a rota óptima em todos os pares (verificado em `testes_proprios.py`), mas isso não está garantido em teoria.
- Nas Damas, a pesquisa tem profundidade limitada, e a qualidade do jogo depende da função de avaliação. O tempo de `escolher_jogada` depende da máquina.

## Uso de ferramentas de IA

Foi usado um assistente de IA (Claude, da Anthropic) como apoio a explicações e a dúvidas de programação, tal como permitido pelo enunciado. Todo o código foi revisto, testado e compreendido pelos autores. A declaração completa está no anexo do relatório.

## Referências

- S. Russell e P. Norvig, *Artificial Intelligence: A Modern Approach*, 4.ª ed., capítulos 3 e 5.
- D. Poole e A. Mackworth, *Artificial Intelligence: Foundations of Computational Agents*, capítulos 3 e 14.
