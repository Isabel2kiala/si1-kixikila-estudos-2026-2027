"""P1 — Testes básicos da interface. Executar na pasta do projecto: python -m unittest testes_p1 -v"""
import unittest

from grafo import carregar_grafo
from damas import estado_inicial, posicao, jogadas_legais, notacao, POSICOES_TESTE
import rotas
import jogos

PEQUENO = {"A": {"B": 1, "C": 4}, "B": {"A": 1, "C": 1, "D": 5},
           "C": {"A": 4, "B": 1, "D": 1}, "D": {"B": 5, "C": 1}}


def caminho_valido(adj, r, origem, destino):
    return (r.caminho[0] == origem and r.caminho[-1] == destino
            and all(b in adj[a] for a, b in zip(r.caminho, r.caminho[1:]))
            and abs(r.custo - sum(adj[a][b] for a, b in zip(r.caminho, r.caminho[1:]))) < 1e-6)


class TestRotas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coords, cls.adj = carregar_grafo()

    def test_haversine(self):
        self.assertAlmostEqual(rotas.haversine((0, 0), (0, 1)), 111.19, places=1)
        a, b = self.coords["Luanda"], self.coords["Benguela"]
        self.assertAlmostEqual(rotas.haversine(a, b), rotas.haversine(b, a))
        self.assertEqual(rotas.haversine(a, a), 0)

    def test_bfs_minimiza_trocos(self):
        r = rotas.bfs(PEQUENO, "A", "D")
        self.assertTrue(caminho_valido(PEQUENO, r, "A", "D"))
        self.assertEqual(len(r.caminho), 3)

    def test_ucs_minimiza_custo(self):
        r = rotas.ucs(PEQUENO, "A", "D")
        self.assertEqual(r.caminho, ["A", "B", "C", "D"])
        self.assertEqual(r.custo, 3)

    def test_a_estrela_optimo_no_grafo_real(self):
        h = lambda n: rotas.haversine(self.coords[n], self.coords["Ondjiva"])
        u = rotas.ucs(self.adj, "Luanda", "Ondjiva")
        a = rotas.a_estrela(self.adj, "Luanda", "Ondjiva", h)
        self.assertTrue(caminho_valido(self.adj, a, "Luanda", "Ondjiva"))
        self.assertAlmostEqual(a.custo, u.custo)
        self.assertLessEqual(a.expandidos, u.expandidos)

    def test_sem_caminho(self):
        # Cabinda não tem ligações rodoviárias no grafo didáctico
        self.assertIsNone(rotas.bfs(self.adj, "Luanda", "Cabinda"))
        self.assertIsNone(rotas.ucs(self.adj, "Luanda", "Cabinda"))


class TestJogos(unittest.TestCase):
    def test_captura_obrigatoria(self):
        # 27 e 31 podiam mexer-se, mas o peão de 22 tem de capturar o de 18
        e = posicao(b=(22, 27, 31), p=(18, 3, 5))
        self.assertEqual([notacao(j) for j in jogadas_legais(e)], ["22x15"])

    def test_minimax_devolve_jogada_legal(self):
        e = estado_inicial()
        v, j, nos = jogos.minimax(e, 2, jogos.diferenca_pecas)
        self.assertIn(j, jogadas_legais(e))
        self.assertGreater(nos, 7)

    def test_alfabeta_igual_a_minimax(self):
        for e in POSICOES_TESTE[:3]:
            for prof in (1, 2, 3):
                vm, _, nm = jogos.minimax(e, prof, jogos.diferenca_pecas)
                va, ja, na = jogos.alfabeta(e, prof, jogos.diferenca_pecas)
                self.assertEqual(vm, va)
                self.assertIn(ja, jogadas_legais(e))
                self.assertLessEqual(na, nm)


if __name__ == "__main__":
    unittest.main(verbosity=2)
