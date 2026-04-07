import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Thieu OPENAI_API_KEY. Hay tao file .env truoc khi chay test_api.py")

llm = ChatOpenAI(model="gpt-4o-mini")
print(llm.invoke("Xin chao!").content)
