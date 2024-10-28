import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.prompts import rephrase_prompt, system_prompt


class LLM:
    """
    A class to interact with the LangChain model for generating human-like text.
    """

    def __init__(self):
        """
        Initializes the LLM with a ChatGoogleGenerativeAI instance.
        """
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.environ.get("GOOGLE_API_KEY"),
        )

    def rephrase(self, new_query, conv) -> str:
        """
        Rephrases a given query based on the conversation history.

        Args:
        - new_query (str): The new query to be rephrased.
        - conv (list): A list of conversation history.

        Returns:
        - str: The rephrased query.
        """
        try:
            messages = [
                ("system", f"{rephrase_prompt.format(conv)}"),
                (
                    "human",
                    f"User: {new_query}\nRephrased Query: ",
                ),
            ]

            ai_msg = self.llm.invoke(messages)
            return ai_msg.content
        except Exception as e:
            print(f"Error rephrasing query: {e}")
            return "Failed to rephrase query."

    def qa(self, query, context) -> str:
        """
        Answers a question based on the given context.

        Args:
        - query (str): The question to be answered.
        - context (str): The context in which the question is asked.

        Returns:
        - str: The answer to the question.
        """
        try:
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
        except Exception as e:
            print(f"Error answering question: {e}")
            return "Failed to answer question."


if __name__ == "__main__":
    try:
        llm_instance = LLM()
        print(
            llm_instance.qa(
                "What is the capital of India?", "Delhi is capital of India"
            )
        )
        conv = [
            {
                "role": "system",
                "content": "Act like an AI Assistant to answer all the questions",
            },
            {"role": "user", "content": "What is the capital of India?"},
            {"role": "assistant", "content": "Delhi is capital of India"},
        ]
        print(llm_instance.rephrase("where is it situated?", conv))
    except Exception as e:
        print(f"Error in main execution: {e}")
