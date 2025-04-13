"""
aula do card 11
"""


import os
from dotenv import load_dotenv
import streamlit as st

from crewai import Crew, Process, Agent, Task
from langchain_core.callbacks import BaseCallbackHandler
from typing import TYPE_CHECKING, Any, Dict, Optional
from langchain_openai import ChatOpenAI

# Load environment variables from the .env file
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')


llm = ChatOpenAI()

# Ícones para o app web
avators = {"Writer":"https://cdn-icons-png.flaticon.com/512/320/320336.png",
            "Reviewer":"https://cdn-icons-png.freepik.com/512/9408/9408201.png"}


## Classe para gerenciar os callbacks do app
class MyCustomHandler(BaseCallbackHandler):


    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name

    # Função para escrever as mensagens dos agentes
    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        st.session_state.messages.append({"role": "assistant", "content": inputs['input']})
        st.chat_message("assistant").write(inputs['input'])

    # Função para escrever o output final
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        st.session_state.messages.append({"role": self.agent_name, "content": outputs['output']})
        st.chat_message(self.agent_name, avatar=avators[self.agent_name]).write(outputs['output'])


# Agente escritor, responsável pelos textos base que serão escritos
escritor = Agent(
    role='Médico diagnostico',
    backstory='''Você é um médico que faz seleção de possíveis diagnósticos e suas respostas são em português.
                Você gera uma iteração de um possível diagnóstico de cada vez.
                Você nunca fornece comentários de revisão.
                Você está aberto aos comentários dos médicos laudadores e disposto a iterar com o possível diagnóstico com base nesses comentários.
                      ''',
    goal="Escreva um possível diagnóstico decente.",
    # tools=[]  # This can be optionally specified; defaults to an empty list
    llm=llm,
    callbacks=[MyCustomHandler("Escritor")],
)
# Agente que analisa e melhora as escritas feitas
revisor = Agent(
    role='Médico laudador',
    backstory='''Você é um médico laudador e revisor de diagnósticos, suas respostas são em português.
            Você revisa diagnósticos e faz recomendações de alterações para torná-los mais fáceis de ser interpretados pelos usuários.
            Você fará comentários de revisão após ler o diagnóstico inteiro, portanto, não gerará nada enquanto o diagnóstico não for entregue completamente.
            Você nunca cria laudos sozinho.''',
    goal="Liste os itens incorporados sobre o que precisa ser melhorado em um diagnóstico.",
    # tools=[]  # Optionally specify tools; defaults to an empty list
    llm=llm,
    callbacks=[MyCustomHandler("Revisor")],
)

# Configurações do chat

#Título
st.title("💬 Diagnóstico e Laudos médicos")

# Carregamento da mensagem inicial no session storage
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Quais os sintomas você está sentindo?"}]

# Escrever a mensagem inicial no chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Esperar o prompt para continuar a execução
if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Task do agente escritor
    task1 = Task(
      description=f"""Escreva um possível diagnóstico em português sobre : {prompt}. """,
      agent=escritor,
      expected_output="um diagnóstico com no máximo 300 palavras em português."
    )

    # Task do editor
    task2 = Task(
      description="""listar comentários de revisão para melhorias de todo o diagnóstico para torná-lo mais interpretável""",
      agent=revisor,
      expected_output="Pontos incorporados sobre onde precisam ser melhorados em português."
    )
    # Establishing the crew with a hierarchical process
    project_crew = Crew(
        tasks=[task1, task2],  # Tasks to be delegated and executed under the manager's supervision
        agents=[escritor, revisor],
        manager_llm=llm,
        process=Process.hierarchical  # Specifies the hierarchical management approach
    )
    final = project_crew.kickoff()

    result = f"## Aqui está o possível diagnóstico \n\n {final}"
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)
