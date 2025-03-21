from lxml import etree
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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