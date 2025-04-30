import sys
import argparse
import os
import logging
import getpass
import json
import torch
import openai
from ead_parser import SmartEADXMLReader

def global_exception_handler(exctype, value, traceback):
    print(f"\nERROR: {exctype.__name__}: {value}")
    print("\nSee full traceback above.")
    input("\nPress Enter to exit...")
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = global_exception_handler

try:
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext, load_index_from_storage
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
except Exception as e:
    print(f"Error importing required modules: {str(e)}")
    input("\nPress Enter to exit...")
    exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# OpenAI Authentication
def authenticate_openai():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        logger.info("Found OpenAI API key in environment variables")
    else:
        print("\n=== OpenAI Authentication ===")
        print("No OPENAI_API_KEY environment variable found.")
        api_key = getpass.getpass("Enter your OpenAI API key: ")
    
    try:
        openai.api_key = api_key
        openai.models.list()  # Test API key
        logger.info("OpenAI authentication successful!")
        return api_key
    except Exception as e:
        logger.error(f"OpenAI authentication failed: {str(e)}")
        print("Authentication failed. Check your API key and try again.")
        return None

# Parse command-line arguments
parser = argparse.ArgumentParser(description="RAG Query over EAD XML files with ChatGPT")
parser.add_argument("--rebuild", action="store_true", help="Force rebuild of the VectorStore index")
parser.add_argument("--show_retrieved", action="store_true", help="Print retrieved documents during queries")
args = parser.parse_args()

# Authenticate
print("Authenticating with OpenAI...")
openai_api_key = authenticate_openai()
if not openai_api_key:
    print("Cannot proceed without OpenAI authentication.")
    input("\nPress Enter to exit...")
    exit(1)
openai.api_key = openai_api_key

# Step 1: Configure Embedding Model
try:
    logger.info("Initializing embedding model...")
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-large-en-v1.5",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    Settings.chunk_size = 4096
    logger.info("Embedding model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {str(e)}")
    input("\nPress Enter to continue after error...")
    raise

# Step 2: Load and Index
input_dir = "./collections/"
persist_dir = "./index_storage"
batch_size = 100

try:
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)
        logger.info(f"Created persist directory: {persist_dir}")
except Exception as e:
    logger.error(f"Failed to create persist directory {persist_dir}: {str(e)}")
    input("\nPress Enter to continue after error...")
    raise

try:
    all_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".xml")]
    if not all_files:
        raise ValueError(f"No XML files found in {input_dir}")
    logger.info(f"Found {len(all_files)} XML files")
except Exception as e:
    logger.error(f"Failed to list XML files in {input_dir}: {str(e)}")
    input("\nPress Enter to continue after error...")
    raise

# Decide whether to rebuild the index
index_exists = os.path.exists(os.path.join(persist_dir, "index_store.json"))
rebuild_index = args.rebuild or not index_exists

if index_exists and not rebuild_index:
    try:
        logger.info("Loading existing index...")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        logger.info("Existing index loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load existing index from {persist_dir}: {str(e)}")
        input("\nPress Enter to continue after error...")
        raise
else:
    logger.info("Building new index...")
    index = None
    for i in range(0, len(all_files), batch_size):
        batch_files = all_files[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1} ({len(batch_files)} files)...")
        
        try:
            reader = SimpleDirectoryReader(input_files=batch_files, file_extractor={".xml": SmartEADXMLReader()})
            documents = reader.load_data()
            logger.info(f"Loaded {len(documents)} documents in batch {i // batch_size + 1}")
        except Exception as e:
            logger.error(f"Failed to load documents in batch {i // batch_size + 1}: {str(e)}")
            input("\nPress Enter to continue after error...")
            continue

        try:
            if index is None:
                index = VectorStoreIndex.from_documents(documents, store_metadata=True)
                logger.info("Initialized index with first batch")
            else:
                for doc in documents:
                    index.insert(doc)
                logger.info(f"Inserted {len(documents)} documents into index")
        except Exception as e:
            logger.error(f"Failed to build/index documents in batch {i // batch_size + 1}: {str(e)}")
            input("\nPress Enter to continue after error...")
            continue

        try:
            index.storage_context.persist(persist_dir=persist_dir)
            logger.info(f"Batch {i // batch_size + 1} saved to {persist_dir}")
        except Exception as e:
            logger.error(f"Failed to save batch {i // batch_size + 1} to {persist_dir}: {str(e)}")
            input("\nPress Enter to continue after error...")
            continue

    if index is None:
        logger.error("Index building failed entirely - no batches succeeded")
        input("\nPress Enter to continue after error...")
        raise ValueError("Index creation failed")

# Step 3: RAG Query Function
def run_rag_query(query, index, top_k=30, show_retrieved=False):
    try:       
        # Step 1: Retrieve DISTINCT documents. We don't want a bunch from the same collection.
        nodes = retrieve_distinct_documents(query, index, top_k=30)

        # Step 2: Build a clean context
        selected_contexts = []

        for idx, node in enumerate(nodes, start=1):
            # Only include important metadata fields
            metadata = node.metadata or {}
            display_metadata = {
                k: v for k, v in metadata.items()
                if k.lower() in ("collection_unitid", "title", "date", "scopecontent", "bibliography")
            }

            formatted_doc = (
                f"Document {idx}:\n"
                f"Metadata:\n{json.dumps(display_metadata, indent=2)}\n"
                f"Content:\n{node.text.strip()}\n"
            )
            selected_contexts.append(formatted_doc)

        # If show_retrieved flag is enabled, print documents
        if show_retrieved:
            print("\n=== Retrieved Documents (after filtering) ===")
            for doc in selected_contexts:
                print(doc[:300])
                print("\n---\n")
            print("\n============================================\n")

        if not selected_contexts:
            logger.warning("No documents selected after token filtering.")
            return "No relevant documents found or context budget too small."

        context_text = "\n\n".join(selected_contexts)

        # Step 3: Build the prompt
        prompt = (
            "You are an expert archivist.\n\n"
            "Based on the following retrieved archival documents, select the collections that are most relevant to the user's research question.\n\n"
            "Do not invent new information. Only suggest collections or items found in the retrieved documents. Do not retrieve multiple items with the same collection_unitid\n\n"
            "For each recommended document, provide:\n"
            "- The collection_unitid\n"
            "- Container (box)\n"
            "- The title\n"
            "- Any available date\n"
            "- A score from 1-10 on how relevant you think it is to the user's query\n"
            "- A brief reason (1-2 sentences) why this document might help with the research query.\n\n"
            f"Query: '{query}'\n\n"
            f"Retrieved Documents:\n{context_text}\n\n"
        )

        # Step 4: Query the LLM
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise and factual archivist."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4096,
            temperature=0.5
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"RAG query failed: {str(e)}")
        return f"Error: {str(e)}"

def retrieve_distinct_documents(query, index, top_k=30, overfetch_k=150):
    retriever = index.as_retriever(
        similarity_top_k=overfetch_k,
        retriever_mode="hybrid"
    )
    
    nodes = retriever.retrieve(query)

    # Deduplicate by collection_unitid
    seen_collections = set()
    distinct_nodes = []
    for node in nodes:
        collection_unitid = node.metadata.get('collection_unitid')
        if not collection_unitid:
            continue  # If missing collection ID, skip it
        if collection_unitid not in seen_collections:
            seen_collections.add(collection_unitid)
            distinct_nodes.append(node)
        if len(distinct_nodes) >= top_k:
            break

    return distinct_nodes


# Step 4: Interactive Query Loop
print("\nRAG query engine is ready!")
while True:
    try:
        user_query = input("Enter your query (or 'exit' to quit): ")
        if user_query.lower() == "exit":
            break
        logger.info(f"Running user query: {user_query}")
        response = run_rag_query(user_query, index, show_retrieved=args.show_retrieved)
        print(f"Response:\n{response}")
    except Exception as e:
        logger.error(f"User query failed: {str(e)}")
        print(f"Error: {str(e)}")
        input("\nPress Enter to continue after error...")
        continue

logger.info("Script completed")
input("\nPress Enter to exit...")