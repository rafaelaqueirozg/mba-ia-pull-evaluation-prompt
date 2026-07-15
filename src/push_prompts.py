"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_KEY = "bug_to_user_story_v2"

def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    print_section_header("PUSH PROMPT")
    
    print(f"[PUSH PROMPT] 🔎 Validando o prompt: {prompt_name}")
    
    is_valid, errors = validate_prompt(prompt_data)
    
    if not is_valid:
        print(f"[PUSH PROMPT] ❌ Erros encontrados no prompt")
        for error in errors:
            print(f"  - {error}")
        return False

    print(f"[PUSH PROMPT] ✅ Prompt validado com sucesso")

    try:
        print(f"[PUSH PROMPT] 📤 Conectando ao LangSmith e enviando o prompt: {prompt_name}")
        
        username = os.getenv("USERNAME_LANGSMITH_HUB")
        
        repo_full_name = f"{username}/{prompt_name}"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_data.get("system_prompt")),
            ("user", prompt_data.get("user_prompt"))
        ])
        
        hub.push(
            repo_full_name=repo_full_name,
            object=prompt,
            tags=prompt_data.get("tags", []),
            new_repo_description=prompt_data.get("description", ""),
            new_repo_is_public=True
        )
        
        print(f"[PUSH PROMPT] ✅ Prompt enviado com sucesso para o LangSmith Hub: {repo_full_name}")
        
        return True
    except Exception as error:
        if "Nothing to commit" in str(error):
            print(f"[PUSH PROMPT] ⚠️ Nenhuma alteração detectada. O prompt já está atualizado no LangSmith Hub.")
            return True
        
        print(f"[PUSH PROMPT] ❌ Erro ao enviar o prompt: {error}")
        return False
        


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """  
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    
    check_env_vars([
        "LANGSMITH_API_KEY",
        "LANGSMITH_ENDPOINT",
        "USERNAME_LANGSMITH_HUB"
    ])
    
    yaml = load_yaml("prompts/bug_to_user_story_v2.yml")
    
    if not yaml or PROMPT_KEY not in yaml:
        print(f"[PUSH PROMPT] ❌ Falha ao carregar o prompt {PROMPT_KEY} do arquivo YAML.")
        return 1
    
    prompt_data = yaml.get(PROMPT_KEY)
    
    success = push_prompt_to_langsmith(
        prompt_name=PROMPT_KEY,
        prompt_data=prompt_data
    )

    if not success:
        
        
        print(f"[PUSH PROMPT] ❌ Processo de push falhou. Verifique os logs acima para detalhes.")
        return 1
    else:
        print(f"[PUSH PROMPT] ✅ Processo concluído com sucesso")
        return 0


if __name__ == "__main__":
    sys.exit(main())
