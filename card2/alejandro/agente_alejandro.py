"""
código do agente para testes, experimentos e customizações
"""

from dotenv import load_dotenv
import os
from groq import Groq
import re


load_dotenv()


# Na primeira tentativa de rodar deu falha em uma biblioteca que precise fazer o donwgrade, a biblioteca foi declarada no arquivo de requirements
# esta função instancia o cliente de llm da plataforma GROQ e executa um teste, pedindo para o modelo llama, versão 3.3 de 70 bilhões de parâmetros para que explique a importância de LLM



client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)


# aqui é gerado a arquitetura do agente.
# primeiro o método construtor recebe o client, neste caso o modelo de LLM ou o provedor de LLM
# ainda no construtor, é recebido como parâmetro o prompt inicial do agente
# esta função da arquitetura do agente não retorna nenhum valor específico, porém há duas funções: call e execute que retornam os devidos valores

class Agent:
    def __init__(self, client: Groq, system: str = "") -> None:
        self.client = client
        self.system = system
        self.messages: list = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
            model="llama3-70b-8192", messages=self.messages
        )
        return completion.choices[0].message.content

    # aqui está o prompt arquitetado para trabalhar no agente.
    # a lógica do prompt segue um fluxo iterativo com pontos de parada, iniciando pelo estado de pensamento, ação, pausa e observação
    # prompt tbm faz menção a funções em python que são executadas como ferramentas para o agente

system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

get_planet_mass:
e.g. get_planet_mass: Earth
returns weight of the planet in kg

Example session:

Question: What is the mass of Earth times 2?
Thought: I need to find the mass of Earth
Action: get_planet_mass: Earth
PAUSE

You will be called again with this:

Observation: 5.972e24

Thought: I need to multiply this by 2
Action: calculate: 5.972e24 * 2
PAUSE

You will be called again with this:

Observation: 1,1944×10e25

If you have the answer, output it as the Answer.

Answer: The mass of Earth times 2 is 1,1944×10e25.

Now it's your turn:
""".strip()

# função responsável por chamar uma operação e executá-la
def calculate(operation: str) -> float:
    return eval(operation)

# função responsável por retornar a massa de uma planeta do sistema solar
def get_planet_mass(planet) -> float:
    match planet.lower():
        case "earth":
            return 5.972e24
        case "jupiter":
            return 1.898e27
        case "mars":
            return 6.39e23
        case "mercury":
            return 3.285e23
        case "neptune":
            return 1.024e26
        case "saturn":
            return 5.683e26
        case "uranus":
            return 8.681e25
        case "venus":
            return 4.867e24
        case _:
            return 0.0



# instanciação de teste do agente
neil_tyson = Agent(client=client, system=system_prompt)

# testando o estado inicial do agente
neil_tyson.execute()




# definição do loop de iterações do agente

def loop(max_iterations=10, query: str = ""):
    # instanciação e parametrização do primeiro agente
    agent = Agent(client=client, system=system_prompt)

    # ferramentas a serem utilizadas pelos agentes
    tools = ["calculate", "get_planet_mass"]

    next_prompt = query

    i = 0

    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        print(result)

        if "PAUSE" in result and "Action" in result:
            action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)
            chosen_tool = action[0][0]
            arg = action[0][1]

            if chosen_tool in tools:
                result_tool = eval(f"{chosen_tool}('{arg}')")
                next_prompt = f"Observation: {result_tool}"

            else:
                next_prompt = "Observation: Tool not found"

            print(next_prompt)
            continue

        if "Answer" in result:
            break


loop(query="What is the mass of Earth plus the mass of Saturn and all of that times 2?")
