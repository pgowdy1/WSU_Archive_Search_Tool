# Add global exception handler to keep window open on any error
import sys

def global_exception_handler(exctype, value, traceback):
    print(f"\nERROR: {exctype.__name__}: {value}")
    print("\nSee full traceback above.")
    input("\nPress Enter to exit...")
    sys.__excepthook__(exctype, value, traceback)  # Call the default handler to show traceback

sys.excepthook = global_exception_handler

try:
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext, load_index_from_storage
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.huggingface import HuggingFaceLLM
    from huggingface_hub import login
    import getpass
    import torch
    import os
    import logging
    from typing import List
except Exception as e:
    print(f"Error importing required modules: {str(e)}")
    input("\nPress Enter to exit...")
    exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# HuggingFace Authentication
def authenticate_huggingface():
    # First check for environment variable
    token = os.environ.get("HUGGINGFACE_TOKEN")
    
    if token:
        logger.info("Found HuggingFace token in environment variables")
    else:
        print("\n=== Hugging Face Authentication ===")
        print("No HUGGINGFACE_TOKEN environment variable found.")
        print("You need to login to access gated models like Mistral-7B-Instruct-v0.1")
        print("Please enter your Hugging Face token (find it at https://huggingface.co/settings/tokens)")
        
        # Ask for token securely (won't show on screen)
        token = getpass.getpass("Enter your Hugging Face token: ")
    
    try:
        # Attempt to login with the provided token
        login(token=token)
        logger.info("Authentication successful!")
        return True
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        print("Authentication failed. Check your token and try again.")
        print("You can set the HUGGINGFACE_TOKEN environment variable to avoid typing it each time.")
        
        retry = input("Do you want to try again? (y/n): ")
        if retry.lower() == 'y':
            return authenticate_huggingface()
        return False

# Authenticate before model initialization
print("Authenticating with Hugging Face...")
if not authenticate_huggingface():
    print("Cannot proceed without authentication to access gated models.")
    input("\nPress Enter to exit...")
    exit(1)

# Step 1: Configure Local Models with Error Handling
try:
    logger.info("Initializing embedding model...")
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-roberta-large-v1",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    logger.info("Embedding model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {str(e)}")
    input("\nPress Enter to continue after error...")
    raise

try:
    logger.info("Initializing LLM...")
    Settings.llm = HuggingFaceLLM(
        model_name="mistralai/Mistral-7B-Instruct-v0.1",
        tokenizer_name="mistralai/Mistral-7B-Instruct-v0.1",
        context_window=4096,
        max_new_tokens=256,
        model_kwargs={"load_in_4bit": True, "torch_dtype": torch.float16},
        device_map="auto"
    )
    logger.info("LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {str(e)}")
    input("\nPress Enter to continue after error...")
    raise

# Step 2: Batch Load and Index with Error Handling
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
    all_files: List[str] = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".xml")]
    if not all_files:
        raise ValueError(f"No XML files found in {input_dir}")
    logger.info(f"Found {len(all_files)} XML files")
except Exception as e:
    logger.error(f"Failed to list XML files in {input_dir}: {str(e)}")
    input("\nPress Enter to continue after error...")
    raise

if os.path.exists(os.path.join(persist_dir, "vector_store.json")):
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
            documents = SimpleDirectoryReader(input_files=batch_files).load_data()
            logger.info(f"Loaded {len(documents)} documents in batch {i // batch_size + 1}")
        except Exception as e:
            logger.error(f"Failed to load documents in batch {i // batch_size + 1}: {str(e)}")
            input("\nPress Enter to continue after error...")
            continue  # Skip this batch, move to next

        try:
            if index is None:
                index = VectorStoreIndex.from_documents(documents)
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

# Step 3: Query with Error Handling
try:
    logger.info("Setting up query engine...")
    query_engine = index.as_query_engine(similarity_top_k=3)
    logger.info("Query engine ready")
except Exception as e:
    logger.error(f"Failed to set up query engine: {str(e)}")
    input("\nPress Enter to continue after error...")
    raise

try:
    query = "What records relate to Ernest O. Holland from 1924?"
    logger.info(f"Running sample query: {query}")
    response = query_engine.query(query)
    print(f"Query: {query}")
    print(f"Response: {response}")
except Exception as e:
    logger.error(f"Sample query failed: {str(e)}")
    input("\nPress Enter to continue after error...")

# Step 4: Interactive Query Loop with Error Handling
while True:
    try:
        user_query = input("Enter your query (or 'exit' to quit): ")
        if user_query.lower() == "exit":
            break
        logger.info(f"Running user query: {user_query}")
        response = query_engine.query(user_query)
        print(f"Response: {response}")
    except Exception as e:
        logger.error(f"User query failed: {str(e)}")
        print(f"Error: {str(e)}")
        input("\nPress Enter to continue after error...")
        continue

logger.info("Script completed")

# Keep window open
input("\nPress Enter to exit...")