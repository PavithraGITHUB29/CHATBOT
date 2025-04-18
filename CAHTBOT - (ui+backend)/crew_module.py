import os
from langchain_sambanova import ChatSambaNovaCloud
from langchain_core.prompts import ChatPromptTemplate

sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")
os.environ["SAMBANOVA_API_KEY"] = sambanova_api_key

# llm = ChatSambaNovaCloud(
#     model="Meta-Llama-3.3-70B-Instruct",
#     max_tokens=1024,
#     temperature=0.3,
#     top_p=0.9,
# )
llm = ChatSambaNovaCloud(
    model="Llama-3.2-90B-Vision-Instruct",  # adjust as per actual model
    max_tokens=1024,
    temperature=0.3,
    top_p=0.9,
)
prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant answering questions about a documentation page.\n"
     "ONLY use the following page content to answer the user's question.\n"
     "if the {question} is common gestures like hello or thank you, then dont display the source\n"
     "If the answer is not found in the content, respond with:\n"
     "'Sorry, I couldn't find an answer in the provided page.'\n\n"
     "PAGE CONTENT:\n{doc_content}"),
    ("human", "{question}")
])

chain = prompt_template | llm

def process_page_with_langchain(title, content, question):
    response = chain.invoke({
        "doc_content": content,
        "question": question,
    })
    return response.content.strip()