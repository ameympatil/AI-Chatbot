from src.llm import LLM
from src.preprocess_doc import PreprocessDoc
import os
import json


class Utils:
    def __init__(self):
        """
        Initializes the Utils class with instances of LLM and PreprocessDoc.
        """
        self.llm = LLM()
        self.preprocess_doc = PreprocessDoc()
        self.index = None

    def upload_doc(self, doc):
        """
        Uploads a document, preprocesses it, and creates an index for future queries.

        Args:
        - doc (str): The path to the document to be uploaded.

        Returns:
        - str: A success message if the document is uploaded successfully.
        """
        try:
            # Remove the "temp_" prefix from the filename
            original_filename = doc[5:] if doc.startswith("temp_") else doc
            filename = os.path.splitext(os.path.basename(original_filename))[0]
            filename = filename.replace(" ", "_")
            text = self.preprocess_doc.pdf_loader(doc)
            chunks = self.preprocess_doc.create_chunks(text)
            self.index = self.preprocess_doc.create_index(chunks, filename)
            return "Upload Successful!"
        except Exception as e:
            print(f"Error uploading document: {e}")
            return "Upload Failed."

    def similarity_search(self, query, index_name=""):
        """
        Performs a similarity search based on the query and the current index.

        Args:
        - query (str): The query to search for in the documents.
        - index_name (str, optional): The name of the index to use for the search. Defaults to an empty string.

        Returns:
        - list: A list of relevant documents based on the query.
        """
        try:
            if self.index is None:
                self.index = self.preprocess_doc.get_index(index_name)
                print(self.index)
            docs = self.preprocess_doc.get_relevant_documents(query, self.index)
            return docs
        except Exception as e:
            print(f"Error performing similarity search: {e}")
            return []

    def get_conv(self, id):
        """
        Retrieves a conversation history based on the given ID.

        Args:
        - id (str): The ID of the conversation to retrieve.

        Returns:
        - list: A list of conversation history, with each entry being a dictionary containing 'role' and 'content'.
        """
        conv_folder = "conv"
        conv = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello, How can I help you?"},
        ]

        try:
            if os.path.exists(conv_folder):
                files = [f for f in os.listdir(conv_folder) if f.endswith(".json")]
                if id + ".json" in files:
                    with open(os.path.join(conv_folder, id + ".json"), "r") as f:
                        conv = json.load(f)
            return conv[-2:]  # Return the last two entries of the conversation
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            return []

    def save_conv(self, id, conv):
        """
        Saves or updates a conversation history based on the given ID and conversation data.

        Args:
        - id (str): The ID of the conversation to save or update.
        - conv (list): A list of conversation history, with each entry being a dictionary containing 'role' and 'content'.

        Returns:
        - str: A success message if the conversation is saved successfully.
        """
        conv_folder = "conv"
        try:
            if not os.path.exists(conv_folder):
                os.makedirs(conv_folder)

            file_path = os.path.join(conv_folder, id + ".json")

            if os.path.exists(file_path):
                # If file exists, read existing conversation and extend it
                with open(file_path, "r") as f:
                    existing_conv = json.load(f)
                existing_conv.extend(conv)
                conv_to_save = existing_conv
            else:
                # If file doesn't exist, use the new conversation
                conv_to_save = conv

            # Save the conversation (either extended or new)
            with open(file_path, "w") as f:
                json.dump(conv_to_save, f)
            return f"Save Successful for {id}"
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return f"Save Failed for {id}"

    def rephrase(self, data):
        """
        Rephrases a query based on the conversation history.

        Args:
        - data (dict): A dictionary containing 'id' and 'query' for the conversation and query to be rephrased.

        Returns:
        - str: The rephrased query.
        """
        try:
            conv = self.get_conv(data["id"])
            return self.llm.rephrase(data["query"], conv)
        except Exception as e:
            print(f"Error rephrasing query: {e}")
            return "Failed to rephrase query."

    def qa(self, query, context):
        """
        Answers a question based on the given context.

        Args:
        - query (str): The question to be answered.
        - context (str): The context in which the question is asked.

        Returns:
        - str: The answer to the question.
        """
        try:
            return self.llm.qa(query, context)
        except Exception as e:
            print(f"Error answering question: {e}")
            return "Failed to answer question."

    def get_all_indexes(self):
        """
        Retrieve and display all possible indexes present in the 'faiss_index' folder.
        Each index is represented by a subfolder in the 'faiss_index' folder.
        The '.pdf' extension is removed from the index names.

        Returns:
        list: A list of all index names (subfolder names in 'faiss_index' without '.pdf' extension)
        """
        index_folder = "faiss_index"
        try:
            if os.path.exists(index_folder):
                # List all subdirectories in the 'faiss_index' folder
                # Each subdirectory represents an index
                index_names = [
                    f
                    for f in os.listdir(index_folder)
                    if os.path.isdir(os.path.join(index_folder, f))
                ]

                # Remove '.pdf' extension from each index name
                index_names = [os.path.splitext(name)[0] for name in index_names]

                return index_names
            else:
                return []
        except Exception as e:
            print(f"Error retrieving indexes: {e}")
            return []

    def get_all_convs(self):
        """
        Retrieves all conversation files present in the 'conv' folder.

        Returns:
        list: A list of all conversation file names.
        """
        conv_folder = "conv"
        try:
            conv_files = []
            if os.path.exists(conv_folder):
                conv_files = [
                    f
                    for f in os.listdir(conv_folder)
                    if os.path.isfile(os.path.join(conv_folder, f))
                ]
            return conv_files  # This will be an empty list if no files are present
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return []


if __name__ == "__main__":
    utils = Utils()

    # Upload document (only needs to be done once)
    # print(utils.upload_doc(r"D:\Study\gemini-pro\data\understanding_mutualfunds.pdf"))

    # Now you can perform multiple searches without recreating the index
    data = {"id": "1234", "query": "What is mutual funds?"}  # "What is transformer?"
    context = utils.similarity_search(data["query"], "understanding_mutualfunds")
    # print(context)
    print()
    new_query = utils.rephrase(data)
    print("new: ", new_query)
    response = utils.qa(new_query, context)
    conv = [
        {"role": "user", "content": f"{new_query}"},
        {"role": "assistant", "content": f"{response}"},
    ]
    utils.save_conv(data["id"], conv)
    print(response)

    # Another search using the same index
    data2 = {"id": "1234", "query": "Why do I invest in them"}
    context2 = utils.similarity_search(data2["query"], "understanding_mutualfunds")
    # print(context2)
    print()
    new_query = utils.rephrase(data2)
    print("new: ", new_query)
    response2 = utils.qa(new_query, context2)
    print(response2)
    conv = [
        {"role": "user", "content": f"{new_query}"},
        {"role": "assistant", "content": f"{response2}"},
    ]
    utils.save_conv(data2["id"], conv)
    # print(utils.get_all_indexes())
