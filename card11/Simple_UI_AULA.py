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
writer = Agent(
    role='Blog Post Writer',
    backstory='''You are a blog post writer who is capable of writing a travel blog.
                      You generate one iteration of an article once at a time.
                      You never provide review comments.
                      You are open to reviewer's comments and willing to iterate its article based on these comments.
                      ''',
    goal="Write and iterate a decent blog post.",
    # tools=[]  # This can be optionally specified; defaults to an empty list
    llm=llm,
    callbacks=[MyCustomHandler("Writer")],
)
# Agente que analisa e melhora as escritas feitas
reviewer = Agent(
    role='Blog Post Reviewer',
    backstory='''You are a professional article reviewer and very helpful for improving articles.
                 You review articles and give change recommendations to make the article more aligned with user requests.
                 You will give review comments upon reading entire article, so you will not generate anything when the article is not completely delivered.
                  You never generate blogs by itself.''',
    goal="list builtins about what need to be improved of a specific blog post. Do not give comments on a summary or abstract of an article",
    # tools=[]  # Optionally specify tools; defaults to an empty list
    llm=llm,
    callbacks=[MyCustomHandler("Reviewer")],
)

# Configurações do chat

#Título
st.title("💬 CrewAI Writing Studio")

# Carregamento da mensagem inicial no session storage
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What blog post do you want us to write?"}]

# Escrever a mensagem inicial no chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Esperar o prompt para continuar a execução
if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Task do agente escritor
    task1 = Task(
      description=f"""Write a blog post of {prompt}. """,
      agent=writer,
      expected_output="an article under 300 words."
    )

    # Task do editor
    task2 = Task(
      description="""list review comments for improvement from the entire content of blog post to make it more viral on social media""",
      agent=reviewer,
      expected_output="Builtin points about where need to be improved."
    )
    # Establishing the crew with a hierarchical process
    project_crew = Crew(
        tasks=[task1, task2],  # Tasks to be delegated and executed under the manager's supervision
        agents=[writer, reviewer],
        manager_llm=llm,
        process=Process.hierarchical  # Specifies the hierarchical management approach
    )
    final = project_crew.kickoff()

    result = f"## Here is the Final Result \n\n {final}"
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)
