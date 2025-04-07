'''
card 9
'''

import os
from crewai_tools import TXTSearchTool

from dotenv import load_dotenv
import os


load_dotenv()

os.environ['OPENAI_API_KEY'] = os.environ.get("OPENAI_API_KEY")

# Initialize the tool with a specific text file, so the agent can search within the given text file's content
tool = TXTSearchTool(txt='ai.txt')


from crewai import Agent, Task, Crew

context = tool.run('What is natural language processing?')

data_analyst = Agent(
    role='Educator',
    goal=f'Based on the context provided, answer the question - What is Natural Language Processing? Context - {context}',
    backstory='You are a data expert',
    verbose=True,
    allow_delegation=False,
    tools=[tool]
)

test_task = Task(
    description="Understand the topic and give the correct response",
    tools=[tool],
    agent=data_analyst,
    expected_output='Give a correct response'
)

crew = Crew(
    agents=[data_analyst],
    tasks=[test_task]
)

output = crew.kickoff()
print(output)