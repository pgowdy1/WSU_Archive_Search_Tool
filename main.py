from lxml import etree
from sentence_transformers import SentenceTransformer
import os
import json
import logging
import faiss
import numpy as np
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up argument parser
parser = argparse.ArgumentParser(description='Process XML files and generate embeddings')
parser.add_argument('--skip-processing', action='store_true', help='Skip XML processing and use existing processed_chunks.json')
parser.add_argument('--skip-embeddings', action='store_true', help='Skip embedding generation and FAISS indexing')
args = parser.parse_args()

# Method for processing all of the collections files. 
def preprocess_xml(file_path):
    try:
        tree = etree.parse(file_path)
        filename = os.path.basename(file_path)
        chunks = []

        # Extract key sections
        for section in ['bioghist', 'scopecontent', 'dsc', 'controlaccess']:
            text = " ".join(tree.xpath(f"//{section}//text()"))
            if text:
                # Rough chunking by character count
                for i in range(0, len(text), 2500):
                    chunk = f"Collection: {filename}\n{text[i:i+2500]}"
                    chunks.append({"text": chunk, "metadata": {"file": filename, "section": section}})
        
        return chunks
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return []

# Only process XML files if not skipping
if not args.skip_processing:
    # Pointing to the 'collections' folder in the local project. 
    xml_files = [os.path.join("collections", f) for f in os.listdir("collections") if f.endswith(".xml")]
    all_chunks = []

    # Process all files
    for file in xml_files:
        logger.info(f"Processing {file}...")
        chunks = preprocess_xml(file)
        all_chunks.extend(chunks)
        logger.info(f"Processed {len(chunks)} chunks from {file}")

    # Save chunks to a JSON file
    output_file = "processed_chunks.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        logger.info(f"Successfully saved {len(all_chunks)} chunks to {output_file}")
    except Exception as e:
        logger.error(f"Error saving chunks to file: {str(e)}")
else:
    logger.info("Skipping XML processing, using existing processed_chunks.json")

# Load chunks from JSON file
try:
    with open("processed_chunks.json", 'r', encoding='utf-8') as f:
        loaded_chunks = json.load(f)
    logger.info(f"Loaded {len(loaded_chunks)} chunks from processed_chunks.json")
except Exception as e:
    logger.error(f"Error loading chunks from file: {str(e)}")
    loaded_chunks = []

# Generate embeddings and create FAISS index if not skipping
model = SentenceTransformer('all-MiniLM-L6-v2')
if not args.skip_embeddings:
    # Generate the embeddings -- converting the 500 token chunks into semantic vectors for LLM.  
    embeddings = model.encode([chunk["text"] for chunk in loaded_chunks], show_progress_bar=True)

    # Index with FAISS -- store embeddings in a local vector index for fast retrieval.
    dimension = 384  # all-MiniLM-L6-v2 embedding size
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    faiss.write_index(index, "ead_index.faiss")
    logger.info("Successfully generated embeddings and created FAISS index")
else:
    logger.info("Skipping embedding generation and FAISS indexing")

# Final step -- actually load the files and pass the prompt/query.
# Load the FAISS index (embeddings) and JSON (text/metadata)
index = faiss.read_index("ead_index.faiss")
with open("processed_chunks.json", "r", encoding='utf-8') as f:
    all_chunks = json.load(f)

def query_collections(query, top_k=5):
    # Turn your question into an embedding
    query_emb = model.encode([query])
    # Search FAISS for the top 5 matching chunk numbers
    distances, indices = index.search(np.array(query_emb), top_k)
    # Grab the text/metadata for those chunks from JSON
    results = [all_chunks[i] for i in indices[0]]
    # Build the context for the prompt
    context = "\n\n".join([f"{r['metadata']['file']} ({r['metadata']['section']}): {r['text'][:500]}..." for r in results])
    # Create the full prompt with your query
    prompt = f"From these archival finding aid excerpts:\n{context}\nList collections that might contain {query.split('?')[0]}."
    return prompt

# Test it
query = "What collections have information on Washington State's involvement in the Spanish-American war?"
print(query_collections(query))