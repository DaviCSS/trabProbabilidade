"""Confere que cada experimento do notebook funciona sem executar os demais."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path


class TestNotebook(unittest.TestCase):
    def test_experimentos_independentes(self):
        # Lemos o .ipynb como JSON, sem precisar instalar Jupyter para testar.
        caminho = Path(__file__).resolve().parents[1] / "Maquina_Estatistica.ipynb"
        notebook = json.loads(caminho.read_text(encoding="utf-8"))
        celulas = notebook["cells"]
        self.assertEqual(notebook["nbformat"], 4)
        self.assertEqual(sum(c["cell_type"] == "code" for c in celulas), 9)

        preparacao = "".join(celulas[2]["source"])
        # Cada experimento pode ser executado apenas com a preparação.
        # A pasta temporária evita alterar o repositório durante os testes.
        origem = Path.cwd()
        with tempfile.TemporaryDirectory() as temp:
            try:
                os.chdir(temp)
                with contextlib.redirect_stdout(io.StringIO()):
                    for indice in (8, 11, 14, 17, 20):
                        contexto = {}
                        exec(preparacao, contexto)
                        exec("".join(celulas[indice]["source"]), contexto)
                for numero in range(1, 6):
                    self.assertTrue(Path(f"resultados_notebook/experimento{numero}.csv").is_file())
            finally:
                os.chdir(origem)


if __name__ == "__main__":
    unittest.main()
