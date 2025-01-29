import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def chunk_content(input_file, output_file, chunk_size=5000, chunk_overlap=50):
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Load the input data
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Initialize the text splitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []

    # Split each content into chunks
    for data_link, content in data.items():
        chunked_content = splitter.split_text(content)
        for i, chunk in enumerate(chunked_content):
            chunks.append({
                "data_link": data_link,
                "chunk_id": f"{data_link}_chunk_{i}",
                "content": chunk
            })

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save the chunks to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(chunks, file, ensure_ascii=False, indent=4)

    print(f"Chunking complete. {len(chunks)} chunks saved to {output_file}")

if __name__ == "__main__":
    # Define input and output file paths
    input_path = './data/data_links_with_content.json'
    output_path = './data/content_chunks.json'

    # Run the chunking process
    chunk_content(input_path, output_path)
