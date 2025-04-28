from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from typing import List, Dict, Optional
import os
import xml.etree.ElementTree as ET

class SmartEADXMLReader(BaseReader):
    def load_data(self, file_path: str, extra_info: dict = None) -> List[Document]:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            file_name = os.path.basename(file_path)

            # Collection-level metadata
            repo = self._safe_find_text(root, './/{*}repository//{*}corpname')
            collection_unitid = self._safe_find_text(root, './/{*}did//{*}unitid')
            physdesc = self._safe_find_text(root, './/{*}physdesc')
            scopecontent = self._get_section_text(root, './/{*}scopecontent')
            bibliography = self._get_section_text(root, './/{*}bibliography')
            separatedmaterial = self._get_section_text(root, './/{*}separatedmaterial')

            inherited_metadata = {
                "repository": repo,
                "collection_unitid": collection_unitid,
                "physdesc": physdesc,
                "scopecontent": scopecontent,
                "bibliography": bibliography,
                "separatedmaterial": separatedmaterial
            }

            documents = []
            archdesc = root.find(".//{*}archdesc")
            if archdesc is not None:
                components = archdesc.findall(".//{*}dsc/{*}c01")
                for component in components:
                    documents.extend(
                        self._parse_component(
                            component,
                            file_name=file_name,
                            parent_path=[],
                            inherited_metadata=inherited_metadata
                        )
                    )

            return documents

        except Exception as e:
            raise RuntimeError(f"Failed to parse {file_path}: {e}")

    def _parse_component(self, node, file_name: str, parent_path: List[str], inherited_metadata: Dict) -> List[Document]:
        docs = []
        title = self._safe_find_text(node, ".//{*}unittitle")
        unitid = self._safe_find_text(node, ".//{*}unitid")
        date = self._safe_find_text(node, ".//{*}unitdate")

        containers = {}
        for container in node.findall(".//{*}container"):
            ctype = container.attrib.get("type", "unknown")
            containers[ctype] = container.text.strip() if container.text else ""

        context_path = parent_path + [title] if title else parent_path
        hierarchy_str = " > ".join(context_path)

        text_lines = []
        if title:
            text_lines.append(f"Title: {title}")
        if unitid:
            text_lines.append(f"ID: {unitid}")
        if date:
            text_lines.append(f"Date: {date}")
        if hierarchy_str:
            text_lines.append(f"Hierarchy: {hierarchy_str}")
        for key, val in containers.items():
            text_lines.append(f"Container ({key}): {val}")

        for p in node.findall(".//{*}p"):
            content = p.text.strip() if p.text else ""
            if content:
                text_lines.append(f"Description: {content}")

        if text_lines:
            text_content = "\n".join(text_lines)
            doc = Document(
                text=text_content,
                metadata={
                    "file_name": file_name,
                    "unitid": unitid,
                    "title": title,
                    "date": date,
                    "container": containers or None,
                    "context_hierarchy": hierarchy_str,
                    "repository": inherited_metadata.get("repository"),
                    "collection_unitid": inherited_metadata.get("collection_unitid"),
                    "physdesc": inherited_metadata.get("physdesc"),
                    "scopecontent": inherited_metadata.get("scopecontent"),
                    "bibliography": inherited_metadata.get("bibliography"),
                    "separatedmaterial": inherited_metadata.get("separatedmaterial"),
                }
            )
            docs.append(doc)

        for child in node.findall("./{*}c0"):
            docs.extend(
                self._parse_component(
                    child,
                    file_name=file_name,
                    parent_path=context_path,
                    inherited_metadata=inherited_metadata
                )
            )

        return docs

    def _safe_find_text(self, node, xpath: str) -> Optional[str]:
        found = node.find(xpath)
        return found.text.strip() if found is not None and found.text else None

    def _get_section_text(self, node, xpath: str) -> Optional[str]:
        section = node.find(xpath)
        if section is not None:
            paragraphs = [p.text.strip() for p in section.findall(".//{*}p") if p.text]
            return "\n".join(paragraphs) if paragraphs else None
        return None
