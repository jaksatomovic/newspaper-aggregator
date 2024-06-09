import csv
import spider
import render
import utility
import os
import datetime
import constants
import notification
import logging
import signal

from dotenv import load_dotenv
from database_manager import DatabaseManager
from apscheduler.schedulers.blocking import BlockingScheduler

def job_function():
    # Instantiate and run the main class
    main = Main().get_instance()
    main.run()

def stop_scheduler(signum, frame):
    print("Received termination signal. Stopping scheduler.")
    scheduler.shutdown()

class Main:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
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
        periodicals = self.db_manager.get_periodicals()
        self.db_manager.disconnect()
        
        for periodical in periodicals:
            # Call spider.get_news with the fetched data  
            spider.get_news(periodical, self.db_manager)          

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

        today = datetime.date.today()
        formatted_date = today.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Map PDF file data to file_data and EPUB file data to epub_file
        for file_name, file_data, content_type in file_data:
            publication = {
                'periodical_id': int(file_name.split(".")[0]),
                'publication_date': formatted_date,
                'file_name': file_name,
                'file_data': file_data,
                'file_data_content_type': 'application/pdf' if content_type == 'application/pdf' else 'application/epub+zip'
            }

            self.db_manager.create_publication(publication)

        self.db_manager.disconnect()

if __name__ == "__main__":

    main = Main().get_instance()
    main.run()
    
    # scheduler = BlockingScheduler()
    # scheduler.add_job(job_function, 'cron', hour=3)
    
    # # Register signal handler for termination signal (SIGTERM)
    # signal.signal(signal.SIGTERM, stop_scheduler)
    
    # try:
    #     scheduler.start()
    # except KeyboardInterrupt:
    #     pass


