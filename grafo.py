"""P1 — Leitura do grafo didáctico das capitais provinciais (fornecido pelo docente)."""
import csv


def carregar_grafo(f_capitais="capitais.csv", f_estradas="estradas.csv"):
    """Devolve (coordenadas, adjacencias).

    coordenadas: {capital: (latitude, longitude)}
    adjacencias: {capital: {vizinha: distancia_km}}  (grafo não orientado)
    """
    coords, adj = {}, {}
    with open(f_capitais, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            coords[r["capital"]] = (float(r["latitude"]), float(r["longitude"]))
            adj[r["capital"]] = {}
    with open(f_estradas, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = float(r["distancia_km"])
            adj[r["origem"]][r["destino"]] = d
            adj[r["destino"]][r["origem"]] = d
    return coords, adj


if __name__ == "__main__":
    coords, adj = carregar_grafo()
    print(f"{len(coords)} capitais, {sum(len(v) for v in adj.values()) // 2} ligações")
    for c in sorted(adj):
        print(f"  {c}: {', '.join(sorted(adj[c])) or '(sem ligações)'}")
