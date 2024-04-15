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

# Configure logging to write to STDOUT
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


from dotenv import load_dotenv
from database_manager import DatabaseManager

today = datetime.date.today()

# Configure logging to write to STDOUT
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Main:
    def __init__(self):
        notification.send_alert("START", "<h1>Scraping successful!</h1>")
        # Load environment variables from .env file
        load_dotenv()
        self.db_manager = DatabaseManager.get_instance()

        # Setup project
        self.db_manager.connect()
        self.db_manager.create_tables()
        self.db_manager.disconnect()
        utility.build_folder_structure()

    def run(self):
        # Perform operations here
        print("Main class is running")

        self.load_journals()

        self.db_manager.connect()
        journals = self.db_manager.get_journals()
        self.db_manager.disconnect()
        
        for journal in journals:
            site_url = journal['site_url']
            rss_url = journal['rss_url']
            language = journal['language']

            # Call spider.get_news with the fetched data
            spider.get_news(site_url, rss_url, language)                

        self.process_files()
        self.store_files()
        utility.delete_all_files(constants.data_folder_path)
        notification.send_alert("INK", "<h1>Scraping successful!</h1>")

    def process_files(self):
        render.generate()

    def load_journals(self):
        self.db_manager.connect()
        with open('input/init.csv', 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                journal_data = {
                    'name': row['name'],
                    'site_url': row['site_url'],
                    'country': row['country'],
                    'rss_url': row['rss_url'],
                    'language': row['language']
                }
                print(journal_data)
                self.db_manager.insert_journal(journal_data)
        self.db_manager.disconnect()

    def store_files(self):
        epub_files, pdf_files = utility.get_files_by_extension('build/')  
        # Merge epub_data and pdf_data into one list
        file_data = [(os.path.basename(file), open(file, 'rb').read()) for file in epub_files + pdf_files]

        self.db_manager.connect()        
        dummy_values = "dummy"  # Placeholder for dummy values
        yesterday = today - datetime.timedelta(days=1)
        for file_name, file_data in file_data:
            newspaper = {
                'title': file_name.split('.')[0],
                'subtitle': dummy_values,
                'newspaper_date': yesterday.strftime("%d/%m/%Y"),
                'category_id': 1,
                # 'subcategory_id': None,
                'file_name': file_name,
                'file_data': file_data,
                'journal_id': 1,
                'scraping_date': today.strftime("%d/%m/%Y")
            }
            self.db_manager.create_newspaper(newspaper)

        self.db_manager.disconnect()

if __name__ == "__main__":
    # Instantiate and run the main class
    main = Main()
    main.run()


