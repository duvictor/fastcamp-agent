'''
código do card 9
'''

# Step 1: Scraping a website

from crewai_tools import ScrapeWebsiteTool, FileWriterTool, TXTSearchTool
import requests

# Initialize the tool, potentially passing the session
tool = ScrapeWebsiteTool(website_url='https://pt.wikipedia.org/wiki/Intelig%C3%AAncia_artificial')

# Extract the text
text = tool.run()
print(text)


# Step2: Write the extracted text to a file

# Initialize the tool
file_writer_tool = FileWriterTool()

# Write content to a file in a specified directory
result = file_writer_tool.run(filename='ai.txt', content = text, directory = r'D:\Users\paulo\PycharmProjects\fastcamp-agent\card9', overwrite=True)
print(result)



