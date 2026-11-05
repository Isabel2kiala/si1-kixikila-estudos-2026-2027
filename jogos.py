"""P1 — Parte B: Minimax e alfa-beta para as damas. Implemente as funções marcadas com TODO.

Convenção: os valores são sempre calculados na perspectiva do jogador que joga na raiz (e.vez).
"Nós avaliados" = número de estados visitados pela pesquisa, incluindo a raiz.
"""
from damas import jogadas_legais, resultado, terminal, vencedor, pecas


def diferenca_pecas(e, jogador):
    """Avaliação de base (B1): peças próprias menos peças do adversário (peão e dama valem 1).
    Em estados terminais: +100 (vitória), -100 (derrota) ou 0 (empate)."""
    if terminal(e):
        v = vencedor(e)
        return 0 if v is None else (100 if v == jogador else -100)
    b, p = pecas(e)
    return (b - p) if jogador == 0 else (p - b)


def minimax(e, prof, avaliar):
    """Devolve (valor, melhor_jogada, nos_avaliados). avaliar(e, jogador) -> float."""
    raise NotImplementedError  # TODO


def alfabeta(e, prof, avaliar):
    """Como minimax, com poda alfa-beta. Deve devolver o mesmo valor que minimax."""
    raise NotImplementedError  # TODO


def avaliar(e, jogador):
    """A sua função de avaliação (B3), com pelo menos 3 características."""
    raise NotImplementedError  # TODO


def escolher_jogada(e, tempo_limite=2.0):
    """Interface do torneio facultativo: devolve uma jogada legal em menos de tempo_limite segundos."""
    return alfabeta(e, 4, avaliar)[1]
