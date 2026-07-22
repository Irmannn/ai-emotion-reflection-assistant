from langchain_core.prompts import ChatPromptTemplate

from app.prompts import SYSTEM_PROMPT

REFLECTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{user_prompt}"),
    ]
)
