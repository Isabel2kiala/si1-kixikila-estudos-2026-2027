"""P1 — Motor das damas clássicas portuguesas, tabuleiro 8×8 (fornecido pelo docente).

Só as 32 casas escuras contam, numeradas de 1 a 32: a casa 1 fica no canto de cima (lado das
Pretas) e a 32 no canto de baixo (lado das Brancas). Cada linha tem 4 casas: 1–4, 5–8, …, 29–32.
tab[casa - 1]: 0 vazia, 1 peão branco, 2 dama branca, -1 peão preto, -2 dama preta.
Jogadores: 0 = Brancas (em baixo, jogam primeiro), 1 = Pretas.

Regras: o peão anda uma casa na diagonal para a frente e só captura para a frente; a captura é
obrigatória e, entre as capturas, só contam as que apanham mais peças (lei da maioria); uma
jogada pode capturar várias peças, que só saem do tabuleiro no fim da jogada; a dama é voadora
(anda e captura à distância e pousa em qualquer casa livre depois da peça capturada); o peão só
é promovido a dama no fim da jogada; quem não tem jogadas perde; 40 jogadas seguidas (20 de cada
lado) só de damas e sem capturas dão empate.
"""
import random
import time
from dataclasses import dataclass
from typing import NamedTuple

LIMITE_EMPATE = 40      # jogadas seguidas só de damas e sem capturas
LIMITE_JOGADAS = 200    # em jogar_partida: atingido este número de jogadas, é empate


@dataclass(frozen=True)
class Estado:
    tab: tuple              # 32 inteiros
    vez: int = 0            # jogador a jogar (0 Brancas, 1 Pretas)
    sem_captura: int = 0    # jogadas seguidas só de damas e sem capturas


class Jogada(NamedTuple):
    caminho: tuple          # casas 1–32: origem primeiro, destino no fim
    capturadas: tuple       # casas 1–32 das peças capturadas, por ordem
    promove: bool           # o peão passa a dama no fim da jogada


SINAL = (1, -1)             # sinal das peças de cada jogador no tabuleiro
ULTIMA = (0, 7)             # linha de promoção de cada jogador
# Direcções: 0 e 1 sobem (frente das Brancas), 2 e 3 descem (frente das Pretas).
DIRECCOES = ((-1, -1), (-1, 1), (1, -1), (1, 1))
FRENTE = ((0, 1), (2, 3))
TODAS = (0, 1, 2, 3)


def linha(i):
    """Linha (0 em cima) do índice i = casa - 1."""
    return i >> 2


def coluna(i):
    """Coluna (0 à esquerda) do índice i = casa - 1."""
    return 2 * (i & 3) + (1 if linha(i) % 2 == 0 else 0)


def _indice(l, c):
    return -1 if not (0 <= l < 8 and 0 <= c < 8) or (l + c) % 2 == 0 else 4 * l + c // 2


def _raio(i, dl, dc):
    r, l, c = [], linha(i) + dl, coluna(i) + dc
    while _indice(l, c) >= 0:
        r.append(_indice(l, c))
        l, c = l + dl, c + dc
    return tuple(r)


# RAIOS[i][d]: índices das casas a partir de i na direcção d, até à borda
RAIOS = tuple(tuple(_raio(i, dl, dc) for dl, dc in DIRECCOES) for i in range(32))


def estado_inicial():
    return Estado((-1,) * 12 + (0,) * 8 + (1,) * 12)


def posicao(b=(), B=(), p=(), P=(), vez=0):
    """Monta uma posição: b peões brancos, B damas brancas, p peões pretos, P damas pretas."""
    tab = [0] * 32
    for casas, valor in ((b, 1), (B, 2), (p, -1), (P, -2)):
        for c in casas:
            tab[c - 1] = valor
    return Estado(tuple(tab), vez)


def _jogadas(e):
    t, v, frente, ultima = list(e.tab), SINAL[e.vez], FRENTE[e.vez], ULTIMA[e.vez]
    capturas, vistas, maximo = [], set(), 0

    def visita(origem, de, dama, caminho, caps):
        nonlocal maximo
        continuou = False
        for d in TODAS if dama else frente:
            raio, k = RAIOS[de][d], 0
            if dama:                        # a dama voa pelas casas livres
                while k < len(raio) and t[raio[k]] == 0:
                    k += 1
            if k >= len(raio) - 1:
                continue
            alvo = raio[k]
            if t[alvo] * v >= 0 or alvo in caps:    # só peças adversárias não capturadas
                continue
            caps.append(alvo)
            # o peão cai logo a seguir; a dama pode cair em qualquer casa livre depois da peça
            for m in range(k + 1, len(raio)):
                if t[raio[m]]:
                    break
                continuou = True
                caminho.append(raio[m])
                visita(origem, raio[m], dama, caminho, caps)
                caminho.pop()
                if not dama:
                    break
            caps.pop()
        if continuou or not caps:
            return
        if len(caps) > maximo:              # lei da maioria
            maximo = len(caps)
            capturas.clear()
            vistas.clear()
        chave = (origem, de, frozenset(caps))   # a dama chega ao mesmo sítio por pousos diferentes
        if len(caps) < maximo or chave in vistas:
            return
        vistas.add(chave)
        # o peão que chega à última linha a meio de uma captura pára (só captura para a frente)
        capturas.append(Jogada(tuple(x + 1 for x in caminho), tuple(x + 1 for x in caps),
                               not dama and linha(de) == ultima))

    for i in range(32):
        peca = t[i]
        if peca * v > 0:
            t[i] = 0                        # a casa de partida fica livre durante a captura
            visita(i, i, peca * v == 2, [i], [])
            t[i] = peca
    if capturas:
        return capturas                     # captura obrigatória

    simples = []
    for i in range(32):
        peca = t[i]
        if peca * v <= 0:
            continue
        dama = peca * v == 2
        for d in TODAS if dama else frente:
            for para in RAIOS[i][d]:
                if t[para]:
                    break
                simples.append(Jogada((i + 1, para + 1), (), not dama and linha(para) == ultima))
                if not dama:
                    break
    return simples


def terminal(e):
    return e.sem_captura >= LIMITE_EMPATE or not _jogadas(e)


def jogadas_legais(e):
    """Lista das jogadas legais (vazia num estado terminal)."""
    return [] if e.sem_captura >= LIMITE_EMPATE else _jogadas(e)


def resultado(e, j):
    """Estado depois da jogada j. Não verifica a legalidade: j deve vir de jogadas_legais(e)."""
    tab = list(e.tab)
    peca = tab[j.caminho[0] - 1]
    tab[j.caminho[0] - 1] = 0
    for c in j.capturadas:
        tab[c - 1] = 0
    tab[j.caminho[-1] - 1] = 2 * SINAL[e.vez] if j.promove else peca
    so_dama = abs(peca) == 2 and not j.capturadas
    return Estado(tuple(tab), 1 - e.vez, e.sem_captura + 1 if so_dama else 0)


def pecas(e):
    """(peças das Brancas, peças das Pretas), contando peões e damas."""
    return sum(x > 0 for x in e.tab), sum(x < 0 for x in e.tab)


def vencedor(e):
    """0 (Brancas), 1 (Pretas) ou None (empate). Só tem significado em estados terminais
    (num estado não terminal devolve None). Quem não tem jogadas perde."""
    if e.sem_captura >= LIMITE_EMPATE or _jogadas(e):
        return None
    return 1 - e.vez


def notacao(j):
    """«11-15» para um movimento, «22x15x8» para uma captura."""
    return ("x" if j.capturadas else "-").join(map(str, j.caminho))


def mostrar(e):
    simbolo = {0: ".", 1: "b", 2: "B", -1: "p", -2: "P"}
    linhas = ["   +-----------------+"]
    for l in range(8):
        casas = [" "] * 8
        for i in range(4 * l, 4 * l + 4):
            casas[coluna(i)] = simbolo[e.tab[i]]
        linhas.append(f"   | {' '.join(casas)} |   {4 * l + 1:2}–{4 * l + 4:2}")
    b, p = pecas(e)
    linhas.append(f"   +-----------------+   (vez: {('Brancas', 'Pretas')[e.vez]}; "
                  f"peças: {b} brancas, {p} pretas; sem captura: {e.sem_captura})")
    return "\n".join(linhas)


# ---------------- agentes e torneio ----------------

def agente_aleatorio(semente=None):
    rng = random.Random(semente)
    return lambda e, tempo_limite=2.0: rng.choice(jogadas_legais(e))


def jogar_partida(agente0, agente1, tempo_limite=2.0):
    """Devolve (vencedor, estado_final). Jogada ilegal ou tempo excedido dá a derrota.
    Ao fim de LIMITE_JOGADAS jogadas sem decisão, é empate."""
    e, agentes = estado_inicial(), (agente0, agente1)
    for _ in range(LIMITE_JOGADAS):
        if terminal(e):
            return vencedor(e), e
        inicio = time.perf_counter()
        try:
            j = agentes[e.vez](e, tempo_limite)
        except Exception:
            return 1 - e.vez, e
        if time.perf_counter() - inicio > tempo_limite or j not in jogadas_legais(e):
            return 1 - e.vez, e
        e = resultado(e, j)
    return vencedor(e), e


def torneio(agentes, tempo_limite=2.0):
    """agentes: {nome: escolher_jogada}. Todos contra todos, 2 jogos por par.
    Vitória = 3 pontos, empate = 1. Devolve a classificação."""
    pontos = {n: 0 for n in agentes}
    nomes = list(agentes)
    for i, a in enumerate(nomes):
        for b in nomes[i + 1:]:
            for j0, j1 in ((a, b), (b, a)):
                v, _ = jogar_partida(agentes[j0], agentes[j1], tempo_limite)
                if v is None:
                    pontos[j0] += 1
                    pontos[j1] += 1
                else:
                    pontos[(j0, j1)[v]] += 3
    return sorted(pontos.items(), key=lambda x: -x[1])


# 5 posições de meio-jogo para as experiências da tarefa B4 (todas com as Brancas a jogar)
POSICOES_TESTE = [
    # 1. meio-jogo calmo, 10 contra 10, sem capturas à vista: 13 jogadas legais
    posicao(b=(19, 21, 22, 23, 24, 28, 29, 30, 31, 32), p=(1, 2, 3, 4, 7, 8, 9, 11, 12, 14)),
    # 2. captura obrigatória: o peão preto de 22 tem de ser capturado (25x18 ou 26x17)
    posicao(b=(21, 23, 24, 25, 26, 27, 28, 29, 30, 31), p=(1, 2, 3, 4, 5, 7, 9, 11, 12, 20, 22)),
    # 3. lei da maioria: 15x6 apanha uma peça, mas só 23x14x5 e 23x14x7 (duas) são legais
    posicao(b=(15, 19, 21, 23, 24, 26, 28, 29, 31, 32), p=(1, 2, 3, 4, 8, 9, 10, 12, 16, 18)),
    # 4. dama branca em 1, 8 contra 8: 13 jogadas legais
    posicao(b=(20, 21, 24, 29, 30, 31, 32), B=(1,), p=(4, 5, 8, 11, 13, 14, 16, 22)),
    # 5. uma dama de cada lado (em 1 e em 32), 7 contra 7
    posicao(b=(15, 21, 25, 28, 29, 30), B=(1,), p=(2, 4, 7, 9, 12, 20), P=(32,)),
]


if __name__ == "__main__":
    # Verificação das regras (as posições de exemplo de lib/damas/motor.ts, na aplicação web)
    notas = lambda e: sorted(notacao(j) for j in jogadas_legais(e))
    e = estado_inicial()
    assert notas(e) == ["21-17", "22-17", "22-18", "23-18", "23-19", "24-19", "24-20"]
    assert len(jogadas_legais(resultado(e, Jogada((22, 18), (), False)))) == 7

    # captura obrigatória: 27 e 31 podiam mexer-se, mas o peão de 22 tem de capturar
    assert notas(posicao(b=(22, 27, 31), p=(18, 3, 5))) == ["22x15"]

    # captura múltipla: uma só jogada captura três peças
    e = posicao(b=(29, 31), p=(25, 18, 11, 1))
    [j] = jogadas_legais(e)
    assert j == Jogada((29, 22, 15, 8), (25, 18, 11), False) and notacao(j) == "29x22x15x8"
    f = resultado(e, j)
    assert f.tab[24] == f.tab[17] == f.tab[10] == 0 and f.tab[7] == 1 and pecas(f) == (2, 1)

    # lei da maioria: só a captura mais longa é legal; capturas do mesmo tamanho ficam todas
    assert notas(posicao(b=(22, 28), p=(17, 18, 11, 24, 1))) == ["22x15x8"]
    assert notas(posicao(b=(22,), p=(17, 18, 1))) == ["22x13", "22x15"]

    # os peões não capturam para trás
    assert notas(posicao(b=(18,), p=(22, 1))) == ["18-14", "18-15"]

    # dama voadora: anda e captura à distância; tem de pousar em 11 para continuar (lei da maioria)
    assert notas(posicao(B=(29,), p=(15, 1))) == ["29x11", "29x4", "29x8"]
    assert notas(posicao(B=(29,), b=(30,), p=(15, 16, 3))) == ["29x11x20"]

    # uma peça capturada fica no tabuleiro até ao fim da jogada e não se salta duas vezes
    assert notas(posicao(B=(26,), p=(22, 14, 15, 23))) == ["26x17x10x19x26", "26x17x10x19x30",
                                                            "26x19x10x17x31"]

    # promoção só no fim da jogada: como dama continuaria 2x9 sobre 6; como peão pára em 2
    e = posicao(b=(11, 30), p=(7, 6, 4))
    [j] = jogadas_legais(e)
    assert notacao(j) == "11x2" and j.promove and resultado(e, j).tab[1] == 2

    # empate: 40 jogadas seguidas só de damas e sem capturas
    e, ciclo = posicao(B=(30,), P=(3,)), ["30-26", "3-7", "26-30", "7-3"]
    for k in range(LIMITE_EMPATE):
        assert not terminal(e)
        e = resultado(e, next(j for j in jogadas_legais(e) if notacao(j) == ciclo[k % 4]))
    assert terminal(e) and vencedor(e) is None and jogadas_legais(e) == []

    # quem não tem jogadas perde: o peão de 29 não anda nem captura (22 tapa o salto)
    e = posicao(b=(29,), p=(25, 22))
    assert terminal(e) and vencedor(e) == 1

    # posições de teste válidas
    assert len(POSICOES_TESTE) == 5
    for p in POSICOES_TESTE:
        assert len(p.tab) == 32 and p.vez == 0 and not terminal(p)
    assert notas(POSICOES_TESTE[1]) == ["25x18", "26x17"]
    assert notas(POSICOES_TESTE[2]) == ["23x14x5", "23x14x7"]

    v, fim = jogar_partida(agente_aleatorio(1), agente_aleatorio(2))
    print("Regras verificadas. Partida aleatória de exemplo:")
    print(mostrar(fim))
    print("Vencedor:", "empate" if v is None else ("Brancas", "Pretas")[v])
