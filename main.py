#!/usr/bin/env python3
import csv
import spider
import render
import utility
import os
import datetime
import constants
import notification
import logging
import sys
from pathlib import Path

# Configure logging to write to STDOUT
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


from dotenv import load_dotenv
from database_manager import DatabaseManager

today = datetime.date.today()

# Configure logging to write to STDOUT
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Main:
    def __init__(self):
        # Load environment variables from .env file
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        self.db_manager = DatabaseManager.get_instance()

        # Setup project
        self.db_manager.connect()
        database_ok = self.db_manager.check_database()
        self.db_manager.disconnect()

        if not database_ok:
            print("Database is not set!")
            return

        utility.build_folder_structure()

    def run(self):
        # Perform operations here
        print("Main class is running")

        self.db_manager.connect()
        journals = self.db_manager.get_journals()
        self.db_manager.disconnect()
        
        for journal in journals:
            # Call spider.get_news with the fetched data  
            spider.get_news(journal, self.db_manager)          

        self.process_files()
         
        self.db_manager.connect()
        self.db_manager.execute_query(''' DROP TABLE temp_data ''')
        self.db_manager.disconnect()

        self.store_files()
        utility.delete_all_files(constants.build_folder_path)
        notification.send_alert("INK", "<h1>Scraping successful!</h1>")

    def process_files(self):
        render.generate(self.db_manager)

    # Function to detect content type based on file extension
    def detect_content_type(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == '.pdf':
            return "application/pdf"
        elif file_extension.lower() == '.epub':
            return "application/epub+zip"
        else:
            return "unknown"  # Or handle other content types as needed


    def store_files(self):
        epub_files, pdf_files = utility.get_files_by_extension('build/')  
        # Merge epub_data and pdf_data into one list
        file_data = [(os.path.basename(file), open(file, 'rb').read(), self.detect_content_type(file)) for file in pdf_files + epub_files]

        # Separate PDF files and EPUB files based on content type
        pdf_files = [(file_name, file_data) for file_name, file_data, content_type in file_data if content_type == 'application/pdf']
        epub_files = [(file_name, file_data) for file_name, file_data, content_type in file_data if content_type == 'application/epub+zip']

        self.db_manager.connect()    

        formatted_date = today.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Map PDF file data to file_data and EPUB file data to epub_file
        for file_name, file_data, content_type in file_data:
            newspaper = {
                'journal_id': int(file_name.split(".")[0]),
                'title': None,
                'newspaper_date': formatted_date,
                'file_name': file_name,
                'file_data': file_data if content_type == 'application/pdf' else None,
                'file_data_content_type': 'application/pdf' if content_type == 'application/pdf' else None,
                'epub_file': file_data if content_type == 'application/epub+zip' else None,
                'epub_file_content_type': 'application/epub+zip' if content_type == 'application/epub+zip' else None
            }

            self.db_manager.create_newspaper(newspaper)

        self.db_manager.disconnect()

if __name__ == "__main__":
    # Instantiate and run the main class
    main = Main()
    main.run()


