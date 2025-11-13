import os
import pathlib
import sys
from pprint import pprint
from markdown_it import MarkdownIt
import json

def ingest(args): # Ingest the file, process it to json and pass it to toon for token economy
    print(args)
    f = open("README.md", "r", encoding="utf-8")
    md = MarkdownIt()
    chunks = []
    stack = []  # Keeps the current heading path
    id_counter = 1
    tokens = md.parse(f.read())
    for token in tokens:
        if token.type == "heading_open":
            level = int(token.tag[1])
            while stack and stack[-1]["level"] >= level:
                stack.pop()
        elif token.type == "inline" and token.map:
            if stack:
                parent_id = stack[-1]["level"] 
            else:
                parent_id = None
            path = [item["content"] for item in stack]

            if tokens[tokens.index(token) - 1].type.startswith("heading"):
                chunk = {
                    "id": id_counter,
                    "type": "heading",
                    "level": int(tokens[tokens.index(token) - 1].tag[1]),
                    "content": token.content,
                    "parent_id": parent_id,
                    "path": path + [token.content]
                }
                stack.append(chunk)
            else:
                chunk = {
                    "id": id_counter,
                    "type": "paragraph",
                    "content": token.content,
                    "parent_id": parent_id,
                    "path": path
                }

            chunks.append(chunk)
            id_counter += 1
    print(json_to_toon(chunks))

def json_to_toon(data, block_name="chunks"): #Saw on linkedin and looked perfect for this project
    if not data:
        return ""
        
    keys = list(data[0].keys())
    header = f"{block_name}[{len(data)}]{{{','.join(keys)}}}:"
    
    rows = []
    for item in data:
        row = ",".join(str(item.get(k, "")) for k in keys)
        rows.append(row)
    
    return header + "\n" + "\n".join(rows)

def func_switcher(args): # For selecting which functionality I want
    if(args[0]=="ingest"):
        ingest(args[1])
    else:
        print("this functionality is not made yet")

def main():
    args = sys.argv[1:]
    func_switcher(args)


if __name__ == "__main__":
    main()