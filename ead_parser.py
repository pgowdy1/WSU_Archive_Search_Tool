# ead_parser.py
import os
import xml.etree.ElementTree as ET
from llama_index.core import Document

def ead_xml_loader(file_path):
    """
    Parse an EAD XML file into multiple Document objects for collection and components.
    
    Args:
        file_path (str): Path to the EAD XML file.
    
    Returns:
        List[Document]: Documents for collection and components (series, folders, items).
    """
    documents = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Collection-level document
        collection_id = root.findtext(".//eadid") or os.path.basename(file_path)
        collection_title = root.findtext(".//archdesc/did/unittitle") or "Unknown Collection"
        collection_scope = "".join(
            p.text or "" for p in root.findall(".//archdesc/scopecontent//p")
        ) or "No description"
        collection_subjects = [
            s.text for s in root.findall(".//archdesc/controlaccess/subject")
            if s.text
        ]

        documents.append(Document(
            text=f"{collection_title}. {collection_scope} {' '.join(collection_subjects)}",
            metadata={
                "file_name": os.path.basename(file_path),
                "type": "collection",
                "collection_id": collection_id,
                "title": collection_title,
                "subjects": ";".join(collection_subjects),
                "level": "collection"
            }
        ))

        # Component-level documents (series, folders, items)
        for component in root.findall(".//dsc//c01 | .//dsc//c02 | .//dsc//c03"):
            level = component.get("level") or "unknown"
            unitid = component.findtext(".//did/unitid") or f"{component.tag}_{len(documents)}"
            unittitle = component.findtext(".//did/unittitle") or "Untitled"
            scopecontent = "".join(
                p.text or "" for p in component.findall(".//scopecontent//p")
            ) or "No description"
            subjects = [
                s.text for s in component.findall(".//controlaccess/subject")
                if s.text
            ]
            dates = component.findtext(".//did/unitdate") or "undated"

            text_content = f"{unittitle}. {scopecontent} {' '.join(subjects)} {dates}"

            documents.append(Document(
                text=text_content,
                metadata={
                    "file_name": os.path.basename(file_path),
                    "type": level,
                    "collection_id": collection_id,
                    "unitid": unitid,
                    "title": unittitle,
                    "subjects": ";".join(subjects),
                    "dates": dates,
                    "level": level
                }
            ))

    except ET.ParseError as e:
        print(f"Error parsing XML file {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error processing {file_path}: {e}")
        return []

    return documents