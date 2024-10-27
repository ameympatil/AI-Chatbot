import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.prompts import rephrase_prompt, system_prompt


class LLM:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.environ.get("GOOGLE_API_KEY"),
        )

    def rephrase(self, new_query, conv) -> str:
        messages = [
            ("system", f"{rephrase_prompt.format(conv)}"),
            (
                "human",
                f"User: {new_query}\nRephrased Query: ",
            ),
        ]

        ai_msg = self.llm.invoke(messages)
        return ai_msg.content

    def qa(self, query, context) -> str:
        messages = [
            (
                "system",
                f"{system_prompt.format(context)}",
            ),
            (
                "human",
                f"{query}",
            ),
        ]
        ai_msg = self.llm.invoke(messages)
        return ai_msg.content


if __name__ == "__main__":
    print(LLM().qa("What is the capital of India?", "Delhi is capital of India"))
    conv = [
        {
            "role": "system",
            "content": "Act like an AI Assistant to answer all the questions",
        },
        {"role": "user", "content": "What is the capital of India?"},
        {"role": "assistant", "content": "Delhi is capital of India"},
    ]
    print(LLM().rephrase("where is it situated?", conv))
