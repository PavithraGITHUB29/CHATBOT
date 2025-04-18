# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from database import store_pages_in_faiss, search_relevant_page, load_index_from_disk
# from crew_module import process_page_with_langchain
# import os

# app = Flask(__name__)
# CORS(app)

# # Initialize variables
# index = None
# titles = None
# contents = None
# initialized = False

# def initialize():
#     global index, titles, contents, initialized
#     if not initialized:
#         print("Loading FAISS index from disk...")
#         index, titles, contents = load_index_from_disk()
#         if index is not None:
#             initialized = True
#             print("FAISS index loaded successfully.")
#         else:
#             print("Error: Could not load index from disk")

# # Initialize during first request
# @app.before_request
# def before_first_request():
#     if not initialized:
#         initialize()

# @app.route("/api/chat", methods=["POST"])
# def chat():
#     # Ensure initialization happene
#     if not initialized:
#         return jsonify({"error": "Service not initialized yet"}), 503
    
#     data = request.get_json()
#     if not data or "query" not in data:
#         return jsonify({"error": "No query provided"}), 400

#     try:
#         title, content = search_relevant_page(data["query"], index, titles, contents)
#         if not title:
#             return jsonify({"answer": "❌ No relevant documentation found."})

#         answer = process_page_with_langchain(title, content, data["query"])
#         return jsonify({
#             "title": title,
#             "answer": answer
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import store_pages_in_faiss, search_relevant_page, load_index_from_disk
from crew_module import process_page_with_langchain
import os
from config import Config
app = Flask(__name__)
CORS(app)

class DataStore:
    def __init__(self):
        self.index = None
        self.titles = None
        self.contents = None
        self.last_modified = 0
        self.load_data()

    def load_data(self):
        print("Loading FAISS index from disk...")
        self.index, self.titles, self.contents = load_index_from_disk()
        if self.index is not None:
            print("FAISS index loaded successfully.")
            # Update last modified time
            config = Config()
            self.last_modified = max(
                os.path.getmtime(config.INDEX_FILE),
                os.path.getmtime(config.TITLES_FILE),
                os.path.getmtime(config.CONTENTS_FILE)
            )
        else:
            print("Error: Could not load index from disk")

    def check_and_reload(self):
        config = Config()
        current_modified = max(
            os.path.getmtime(config.INDEX_FILE),
            os.path.getmtime(config.TITLES_FILE),
            os.path.getmtime(config.CONTENTS_FILE)
        )
        if current_modified > self.last_modified:
            print("Data files changed - reloading...")
            self.load_data()

# Initialize data store
data_store = DataStore()

@app.route("/api/chat", methods=["POST"])
def chat():
    # Check for updates before processing each request
    data_store.check_and_reload()
    
    if data_store.index is None:
        return jsonify({"error": "Service not initialized yet"}), 503
    
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400

    try:
        title, content = search_relevant_page(data["query"], data_store.index, data_store.titles, data_store.contents)
        if not title:
            return jsonify({"answer": "❌ No relevant documentation found."})

        answer = process_page_with_langchain(title, content, data["query"])
        return jsonify({
            "title": title,
            "answer": answer
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)  # Disable Flask's reloader