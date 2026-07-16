"""
Testes automatizados para validação de prompts.
"""
import pytest
import re
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="class")
def prompt_data():
    """Carrega o prompt otimizado (v2) usado em todos os testes."""
    data = load_prompts(PROMPT_FILE)
    assert PROMPT_KEY in data, f"Chave '{PROMPT_KEY}' não encontrada em {PROMPT_FILE}"
    return data[PROMPT_KEY]

class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        assert prompt_data["system_prompt"].strip(), "'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_data["system_prompt"]
        assert re.search(r"você é um\w*\b", system_prompt, re.IGNORECASE), \
            "Prompt não define uma persona (esperado algo como 'Você é um ...')"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"].lower()
        mentions_markdown = "markdown" in system_prompt
        mentions_user_story = (
            "user story" in system_prompt
            and "como um" in system_prompt
            and "eu quero" in system_prompt
            and "para que" in system_prompt
        )
        assert mentions_markdown or mentions_user_story, \
            "Prompt não exige formato Markdown nem o formato padrão de User Story"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"]
        num_inputs = system_prompt.count("Entrada:")
        num_outputs = system_prompt.count("Saída:")
        assert num_inputs >= 2 and num_outputs >= 2, (
            "Few-shot requer pelo menos 2 pares de entrada/saída, "
            f"encontrados: {num_inputs} entrada(s) e {num_outputs} saída(s)"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        for field in ("system_prompt", "user_prompt", "description"):
            text = prompt_data.get(field, "")
            assert not re.search(r"\[?\bTODO\b\]?", text), \
                f"Campo '{field}' ainda contém TODO"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, \
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"

        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Estrutura do prompt inválida: {errors}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])