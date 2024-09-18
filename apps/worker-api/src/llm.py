import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from src.web_scraper import scrape_web_content


class BicepDeployer:
    def __init__(self):
        load_dotenv(Path(__file__).parent / "../.env")

        with open(Path(__file__).parent / "../prompts/system.txt", "r") as f:
            self.system_prompt = f.read()
        self.messages = [
            SystemMessage(content=self.system_prompt)
        ]
        with open(Path(__file__).parent / "../prompts/user_ask.txt", "r") as f:
            self.ask_prompt = f.read()
        with open(Path(__file__).parent / "../prompts/user_fix.txt", "r") as f:
            self.fix_prompt = f.read()

        # https://community.openai.com/t/cheat-sheet-mastering-temperature-and-top-p-in-chatgpt-api/172683
        self.llm = AzureChatOpenAI(azure_deployment="gpt-4o", temperature=0.2, top_p=0.1)

        embeddings = AzureOpenAIEmbeddings(
            azure_deployment="text-embedding-3-large",
            openai_api_version="2023-05-15"
        )
        self.vector_store = AzureSearch(
            azure_search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.environ.get("AZURE_SEARCH_ADMIN_KEY"),
            index_name=os.environ.get("INDEX_NAME"),
            embedding_function=embeddings.embed_query
        )

    def generate_bicep_template(self, mslearn_content):
        similar_doc = self.vector_store.similarity_search(
            query=mslearn_content,
            k=1,
            search_type="hybrid"
        )
        quickstart_path = similar_doc[0].page_content.split("\n")[0].replace("path: ", "")
        print(f"Quickstart path: {quickstart_path}")

        with open(os.path.join(quickstart_path, "main.bicep"), "r") as f:
            bicep_content = f.read()
        with open(os.path.join(quickstart_path, "azuredeploy.parameters.json"), "r") as f:
            parameters_content = f.read()

        user_prompt = self.ask_prompt.replace("MSLEARN_CONTENT", mslearn_content) \
                                     .replace("BICEP_CONTENT", bicep_content) \
                                     .replace("PARAMETERS_CONTENT", parameters_content)
        self.messages.append(HumanMessage(content=user_prompt))

        res = self.llm.invoke(self.messages)
        self.messages.append(AIMessage(content=res.content))
        return res.content

    def fix_bicep_template(self, error_message):
        # If the error_message contains a URL, retrieve the content of that page and add it to the error_message.
        urls = re.findall(r"https?://[^\s]+", error_message)
        for url in urls:
            content = scrape_web_content(url)
            error_message += f"\n\n```{url}\n{content}\n```"

        self.messages.append(HumanMessage(content=self.fix_prompt.replace("ERROR_MESSAGE", error_message)))
        res = self.llm.invoke(self.messages)
        self.messages.append(AIMessage(content=res.content))
        return res.content
