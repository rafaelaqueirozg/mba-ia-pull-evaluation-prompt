"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path("prompts/bug_to_user_story_v1.yml")

def _extract_message_template(message) -> str:
    """
    Extrai o template de uma mensagem, lidando com diferentes estruturas possíveis.
    
    Args:
        message: Objeto de mensagem do LangSmith
        
    Returns:
        String com o template da mensagem ou seu conteúdo.
    """
    
    prompt = getattr(message, "prompt", None)
        
    if prompt is None:
        print(f"[PULL PROMPTS] ⚠️  Mensagem sem prompt encontrado.")
        return ""
    
    if hasattr(prompt, "template"):
        return getattr(prompt, "template", None)
    elif hasattr(prompt, "content"):
        print(f"[PULL PROMPTS] ⚠️  Prompt sem template, usando conteúdo.")
        return prompt.content
    elif isinstance(prompt, list):
        print(f"[PULL PROMPTS] ⚠️  Prompt é uma lista, extraindo templates.")
        return "\n".join([getattr(item, "template", "") for item in prompt if hasattr(item, "template")])
    
    print(f"[PULL PROMPTS] ⚠️  Estrutura de prompt desconhecida para mensagem.")
    return ""
        

def _extract_prompts_from_prompt(prompt) -> dict:
    """
    Extrai os prompts de um objeto de prompt do LangSmith.
    
    Args:
        prompt: Objeto de prompt do LangSmith
        
    Returns:
        Dicionário com os prompts extraídos
    """
    
    extracted = {"system_prompt": "", "user_prompt": ""}
    
    for message in getattr(prompt, "messages", []):
        if isinstance(message, SystemMessagePromptTemplate):
            print(f"[PULL PROMPTS] 🖥️  Extraindo prompt do SystemMessagePromptTemplate.")
            extracted["system_prompt"] = _extract_message_template(message)
        elif isinstance(message, HumanMessagePromptTemplate):
            print(f"[PULL PROMPTS] 👤  Extraindo prompt do HumanMessagePromptTemplate.")
            extracted["user_prompt"] = _extract_message_template(message)
    
    print(f"[PULL PROMPTS] ✅  Prompts extraídos com sucesso")
    return extracted

def pull_prompts_from_langsmith() -> bool:
    """
    Função para puxar prompts do LangSmith Hub e salvar localmente.
    """
    print_section_header("PULL PROMPTS")
    
    print(f"[PULL PROMPTS] 📥  Conectando ao LangSmith Hub e puxando prompts...")
    
    try:
        prompt = hub.pull(PROMPT_NAME)
        
        if prompt is None:
            print("[PULL PROMPTS] ❌  Falha ao puxar o prompt do Hub.")
            return
        
        print(f"[PULL PROMPTS] ✅  Prompt puxado com sucesso")
        
        extracted_prompts = _extract_prompts_from_prompt(prompt)
        
        if not extracted_prompts["system_prompt"] and not extracted_prompts["user_prompt"]:
            print(f"[PULL PROMPTS] ⚠️  Nenhum prompt extraído. Verifique a estrutura do prompt no Hub.")
            return False
        
        
        print(f"[PULL PROMPTS] 📂  Prompts extraídos")
        
        print(f"[PULL PROMPTS] 📂  Montando conteúdo YAML para salvar localmente...")
        
        yaml_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter descrição de bug em user story, puxado do LangSmith Hub.",
                "system_prompt": extracted_prompts["system_prompt"],
                "user_prompt": extracted_prompts["user_prompt"],
                "version": "v1",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }
        
        print(f"[PULL PROMPTS] 📂  Salvando prompts localmente")
        
        success = save_yaml(yaml_data, OUTPUT_PATH)
        
        if not success:
            print(f"[PULL PROMPTS] ❌  Falha ao salvar os prompts em {OUTPUT_PATH}")
            return False
                
        print(f"[PULL PROMPTS] ✅  Prompts salvos com sucesso em {OUTPUT_PATH}")
        return True
    
    except Exception as error:
        print(f"[PULL PROMPTS] ❌  Erro ao puxar ou processar o prompt: {error}")
        return False

def main():
    """Função principal"""
    
    check_env_vars(["LANGSMITH_API_KEY"])
    
    return 0 if pull_prompts_from_langsmith() else 1

if __name__ == "__main__":
    sys.exit(main())
