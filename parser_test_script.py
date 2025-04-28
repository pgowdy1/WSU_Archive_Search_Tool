from ead_parser import SmartEADXMLReader  # path to your reader
import json
import os

reader = SmartEADXMLReader()

file_name = "NTE2cg1.xml"
file_path = os.path.join("short_collections", file_name)

documents = reader.load_data(file_path)

print(f"\nParsed {len(documents)} documents:\n")
for i, doc in enumerate(documents):
    print(f"--- Document {i+1} ---")
    print("Text:", doc.text.strip()[:200], "...")
    print("Metadata:", json.dumps(doc.metadata, indent=2))
    print()

input("Done. Press Enter to exit...")