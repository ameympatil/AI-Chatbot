from src.llm import LLM
from src.preprocess_doc import PreprocessDoc
import os
import json


class Utils:
    def __init__(self):
        self.llm = LLM()
        self.preprocess_doc = PreprocessDoc()
        self.index = None

    def upload_doc(self, doc):
        # Remove the "temp_" prefix from the filename
        original_filename = doc[5:] if doc.startswith("temp_") else doc
        filename = os.path.splitext(os.path.basename(original_filename))[0]
        filename = filename.replace(" ", "_")
        text = self.preprocess_doc.pdf_loader(doc)
        chunks = self.preprocess_doc.create_chunks(text)
        self.index = self.preprocess_doc.create_index(chunks, filename)
        return "Upload Successful!"

    def similarity_search(self, query, index_name=""):
        if self.index is None:
            self.index = self.preprocess_doc.get_index(index_name)
            print(self.index)
        docs = self.preprocess_doc.get_relevant_documents(query, self.index)
        return docs

    def get_conv(self, id):
        conv_folder = "conv"
        conv = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello, How can I help you?"},
        ]

        if os.path.exists(conv_folder):
            files = [f for f in os.listdir(conv_folder) if f.endswith(".json")]
            if id + ".json" in files:
                with open(os.path.join(conv_folder, id + ".json"), "r") as f:
                    conv = json.load(f)

        return conv[-2:]

    def save_conv(self, id, conv):
        conv_folder = "conv"
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

    def rephrase(self, data):
        conv = self.get_conv(data["id"])
        return self.llm.rephrase(data["query"], conv)

    def qa(self, query, context):
        return self.llm.qa(query, context)

    def get_all_indexes(self):
        """
        Retrieve and display all possible indexes present in the 'chroma_db' folder.
        Each index is represented by a subfolder in the 'chroma_db' folder.
        The '.pdf' extension is removed from the index names.

        Returns:
        list: A list of all index names (subfolder names in 'chroma_db' without '.pdf' extension)
        """
        index_folder = "faiss_index"
        if os.path.exists(index_folder):
            # List all subdirectories in the 'chroma_db' folder
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

    def get_all_convs(self):
        conv_folder = "conv"
        conv_files = []
        if os.path.exists(conv_folder):
            conv_files = [
                f
                for f in os.listdir(conv_folder)
                if os.path.isfile(os.path.join(conv_folder, f))
            ]
        return conv_files  # This will be an empty list if no files are present


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
