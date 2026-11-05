"""P1 — Parte A: pesquisa de rotas. Implemente as funções marcadas com TODO.

O grafo vem de grafo.carregar_grafo(): adj = {capital: {vizinha: distancia_km}}.
"""
import heapq
import math
import time
from dataclasses import dataclass


@dataclass
class Resultado:
    caminho: list        # capitais, da origem ao destino
    custo: float         # km
    expandidos: int      # estados retirados da fronteira e expandidos
    tempo_s: float


def haversine(a, b):
    """Distância geodésica em km entre a = (lat, lon) e b = (lat, lon). Raio da Terra: 6371 km."""
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    s = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371 * math.asin(min(1.0, math.sqrt(s)))


def _reconstruir(pai, destino):
    """Anda de pai em pai desde o destino até à origem e inverte."""
    caminho, n = [], destino
    while n is not None:
        caminho.append(n)
        n = pai[n]
    return caminho[::-1]


def bfs(adj, origem, destino):
    """Pesquisa em largura, em grafo. Devolve Resultado ou None se não houver caminho."""
    raise NotImplementedError  # TODO


def ucs(adj, origem, destino):
    """Pesquisa de custo uniforme com fila de prioridade (heapq). Devolve Resultado ou None."""
    raise NotImplementedError  # TODO


def a_estrela(adj, origem, destino, h):
    """A*. h(capital) devolve a estimativa em km até ao destino. Devolve Resultado ou None."""
    inicio = time.perf_counter()
    g = {origem: 0.0}                          # menor custo conhecido (km) da origem até cada capital
    pai = {origem: None}                       # de onde vim, para reconstruir o caminho
    fronteira = [(h(origem), 0.0, 0, origem)]  # (f = g + h, g, desempate, capital)
    expandidos = 0
    contador = 0

    while fronteira:
        _, gn, _, n = heapq.heappop(fronteira)  # sai o de menor f: o mais promissor no total
        if gn > g[n]:
            continue                            # entrada obsoleta: já há caminho melhor para n
        if n == destino:                        # teste na RETIRADA → óptimo se h for admissível
            return Resultado(_reconstruir(pai, destino), gn, expandidos,
                             time.perf_counter() - inicio)
        expandidos += 1
        for m, d in adj[n].items():             # vizinha m, a d km
            gm = gn + d
            if gm < g.get(m, math.inf):         # caminho novo ou mais curto (pode reabrir m)
                g[m] = gm
                pai[m] = n
                contador += 1
                heapq.heappush(fronteira, (gm + h(m), gm, contador, m))
    return None                                 # fronteira vazia: não há caminho


if __name__ == "__main__":
    from grafo import carregar_grafo
    coords, adj = carregar_grafo()
    origem, destino = "Luanda", "Ondjiva"
    h = lambda n: haversine(coords[n], coords[destino])
    h2 = lambda n: 1.5 * haversine(coords[n], coords[destino])
    for nome, heur in [("A*", h), ("A* h2", h2)]:
        r = a_estrela(adj, origem, destino, heur)
        print(f"{nome:6} {r.custo:7.0f} km  {r.expandidos:3} expandidos  {' → '.join(r.caminho)}")