from lxml import etree
from sentence_transformers import SentenceTransformer
import os
import json
import logging
import faiss
import numpy as np
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig  # For quantization

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Argument parser
parser = argparse.ArgumentParser(description='Process XML files and generate embeddings')
parser.add_argument('query', help='The search query to find relevant collections')
parser.add_argument('--process', action='store_true', help='Process XML files and generate new chunks')
parser.add_argument('--generate-embeddings', action='store_true', help='Generate new embeddings and FAISS index')
args = parser.parse_args()

# Load Llama-3.3-70B-Instruct with 4-bit quantization for efficiency
llm_model_name = "meta-llama/Meta-Llama-3.3-70B-Instruct"  # Check exact name on HF
hf_token = os.environ.get('HF_TOKEN')  # Get token from environment variable

if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it before running the script.")

# Quantization config to fit on modest hardware
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16"
)

tokenizer = AutoTokenizer.from_pretrained(llm_model_name, token=hf_token)
llm = AutoModelForCausalLM.from_pretrained(
    llm_model_name,
    token=hf_token,
    quantization_config=bnb_config,
    device_map="auto"  # Auto-maps to GPU/CPU
)
logger.info(f"Loaded LLM: {llm_model_name}")

# Your preprocess_xml function (unchanged)
def preprocess_xml(file_path):
    try:
        tree = etree.parse(file_path)
        filename = os.path.basename(file_path)
        chunks = []
        for section in ['bioghist', 'scopecontent', 'dsc', 'controlaccess']:
            text = " ".join(tree.xpath(f"//{section}//text()"))
            if text:
                for i in range(0, len(text), 2500):
                    chunk = f"Collection: {filename}\n{text[i:i+2500]}"
                    chunks.append({"text": chunk, "metadata": {"file": filename, "section": section}})
        return chunks
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return []

# Process XML files if requested (unchanged)
if args.process:
    xml_files = [os.path.join("collections", f) for f in os.listdir("collections") if f.endswith(".xml")]
    all_chunks = []
    for file in xml_files:
        logger.info(f"Processing {file}...")
        chunks = preprocess_xml(file)
        all_chunks.extend(chunks)
        logger.info(f"Processed {len(chunks)} chunks from {file}")
    output_file = "processed_chunks.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        logger.info(f"Successfully saved {len(all_chunks)} chunks to {output_file}")
    except Exception as e:
        logger.error(f"Error saving chunks to file: {str(e)}")
else:
    logger.info("Using existing processed_chunks.json")

# Load chunks (unchanged)
try:
    with open("processed_chunks.json", 'r', encoding='utf-8') as f:
        loaded_chunks = json.load(f)
    logger.info(f"Loaded {len(loaded_chunks)} chunks from processed_chunks.json")
except Exception as e:
    logger.error(f"Error loading chunks from file: {str(e)}")
    loaded_chunks = []

# Generate embeddings if requested (unchanged)
model = SentenceTransformer('all-MiniLM-L6-v2')
if args.generate_embeddings:
    embeddings = model.encode([chunk["text"] for chunk in loaded_chunks], show_progress_bar=True)
    dimension = 384
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    faiss.write_index(index, "ead_index.faiss")
    logger.info("Successfully generated embeddings and created FAISS index")
else:
    logger.info("Using existing FAISS index")

# Query function with Llama
try:
    index = faiss.read_index("ead_index.faiss")
    with open("processed_chunks.json", "r", encoding='utf-8') as f:
        all_chunks = json.load(f)

    def query_collections(query, top_k=20):
        query_emb = model.encode([query])
        distances, indices = index.search(np.array(query_emb), top_k)
        results = [all_chunks[i] for i in indices[0]]
        
        collections = {}
        for r in results:
            file = r['metadata']['file']
            if file not in collections:
                collections[file] = {'sections': set(), 'excerpts': []}
            collections[file]['sections'].add(r['metadata']['section'])
            text_content = r['text'].split('\n', 1)[1] if '\n' in r['text'] else r['text']
            preview = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
            collections[file]['excerpts'].append(preview)

        context = ""
        for file, data in collections.items():
            context += f"Collection: {file} (Sections: {', '.join(data['sections'])})\n"
            context += "Excerpts:\n" + "\n".join([f"- {e}" for e in data['excerpts']]) + "\n\n"

        # Prompt for Llama
        prompt = (
            f"You are an expert archivist. From these archival finding aid excerpts:\n{context}\n"
            f"List collections that might contain {query.split('?')[0]} and explain why in a concise manner."
        )
        
        # Tokenize and generate
        inputs = tokenizer(prompt, return_tensors="pt").to(llm.device)
        outputs = llm.generate(
            **inputs,
            max_new_tokens=300,  # Adjust based on desired response length
            temperature=0.7,     # Controls creativity
            do_sample=True       # Enables sampling for varied responses
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return response

    # Run the query
    print(query_collections(args.query))
except Exception as e:
    logger.error(f"Error during query: {str(e)}")
    logger.error("Ensure --process and --generate-embeddings have been run")