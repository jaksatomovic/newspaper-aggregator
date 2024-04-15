import constants
import os
import random
import re

def build_folder_structure():
    if not os.path.exists(constants.data_folder_path):
        os.makedirs(constants.data_folder_path)
    if not os.path.exists(constants.build_folder_path):
        os.makedirs(constants.build_folder_path)

def split_article(article):
    # Split the article into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', article)
    
    # Shuffle the sentences randomly
    random.shuffle(sentences)
    
    # Calculate the number of sentences in each part
    num_sentences = len(sentences)
    part_size = num_sentences // 3
    
    # Divide the sentences into three parts
    part1 = sentences[:part_size]
    part2 = sentences[part_size:2 * part_size]
    part3 = sentences[2 * part_size:]
    
    # Join the sentences back into strings
    part1_text = ' '.join(part1)
    part2_text = ' '.join(part2)
    part3_text = ' '.join(part3)
    
    return part1_text, part2_text, part3_text

def get_files_by_extension(folder_path):
    """
    Retrieve files from a folder, sort them, and separate them into two arrays based on their extensions.

    Args:
    - folder_path (str): The path to the folder containing the files.

    Returns:
    - Tuple: A tuple containing two arrays:
        - The first array contains file names with the '.epub' extension.
        - The second array contains file names with the '.pdf' extension.
    """
    # Initialize arrays to store file names
    epub_files = []
    pdf_files = []

    # Retrieve all files from the folder
    files = os.listdir(folder_path)

    # Sort the files
    files.sort()

    # Separate files based on their extensions
    for file in files:
        if file.endswith('.epub'):
            epub_files.append(folder_path + file)
        elif file.endswith('.pdf'):
            pdf_files.append(folder_path + file)

    return epub_files, pdf_files


def delete_all_files(folder_path):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)
    
    # Iterate over each file and delete it
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {file_path}, {e}")


def list_csv_files(folder_path):
    csv_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            csv_files.append(os.path.join(folder_path, file))
    return csv_files


