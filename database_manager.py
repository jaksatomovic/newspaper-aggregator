import os
import mysql.connector

class DatabaseManager:
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

    def connect(self):
        if self._connection is not None:
            return  # If connection is already established, return
        
        host = os.getenv('DB_HOST')
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_DATABASE')

        if not all([host, username, password, database]):
            raise Exception("Database connection details are missing")

        self._connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

    def check_database(self):
        if self._connection is None:
            raise Exception("Database connection is not established")
            
        cursor = self._connection.cursor()
        
        try:
            # Check if the newspapers table exists
            cursor.execute("SHOW TABLES LIKE 'newspaper'")
            newspaper_table_exists = cursor.fetchone()

            # Check if the journals table exists
            cursor.execute("SHOW TABLES LIKE 'journal'")
            journal_table_exists = cursor.fetchone()

            # Check if the categories table exists
            cursor.execute("SHOW TABLES LIKE 'category'")
            journal_table_exists = cursor.fetchone()

            # Check if the temp_data table exists
            cursor.execute("SHOW TABLES LIKE 'temp_data'")
            temp_data_table_exists = cursor.fetchone()

            if not temp_data_table_exists:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS temp_data (
                        journal_id INTEGER,
                        category_id INTEGER,
                        title TEXT,
                        content TEXT,
                        image_url TEXT
                    )
                ''')

            if not newspaper_table_exists or not journal_table_exists or not journal_table_exists:
                return False
            
            self._connection.commit()

            return True

        except mysql.connector.Error as e:
            print(f"Error occurred while executing query: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def disconnect(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, query, values=None):
        if self._connection is None:
            raise Exception("Database connection is not established")

        cursor = self._connection.cursor()

        try:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            self._connection.commit()
            # print("Query executed successfully.")
        except mysql.connector.Error as e:
            print(f"Error occurred while executing query: {e}")
            self._connection.rollback()
        finally:
            cursor.close()
    
    def get_journals(self):
        if self._connection is None:
            raise Exception("Database connection is not established")

        cursor = self._connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT j.id AS journal_id, j.name AS journal_name, j.site_url, j.language, j.country, j.image, j.image_content_type, f.rss_url, f.category_id FROM journal j LEFT JOIN feed f ON j.id = f.journal_id")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error occurred while executing query: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def get_temporary_data(self):
        if self._connection is None:
            raise Exception("Database connection is not established")

        cursor = self._connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT journal_id, category_id, title, content, image_url FROM temp_data")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error occurred while executing query: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def get_journal_name(self, journal_id):
        if self._connection is None:
            raise Exception("Database connection is not established")

        cursor = self._connection.cursor(dictionary=True)

        try:
            cursor.execute(''' SELECT j.name AS journal_name FROM journal j WHERE j.id =  ''' + str(journal_id))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error occurred while executing query: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def journal_exists(self, journal_name):
        if self._connection is None:
            raise Exception("Database connection is not established")
        
        try:
            cursor = self._connection.cursor()

            query = "SELECT COUNT(*) FROM journals WHERE name = %s"
            cursor.execute(query, (journal_name,))
            count = cursor.fetchone()[0]
            
            return count > 0
        except mysql.connector.Error as e:
            print(f"Error occurred while inserting newspapaer: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def insert_journal(self, newspaper):
        if self._connection is None:
            raise Exception("Database connection is not established")

        if self.journal_exists(newspaper['name']):
            print("Newspaper " + newspaper['name'] + " already exists in the database.")
            return

        try:
            cursor = self._connection.cursor()

            insert_query = """
                INSERT INTO journals (name, site_url, country, rss_url, language)
                VALUES (%s, %s, %s, %s, %s)
            """       

            cursor.execute(insert_query, (
                newspaper['name'],
                newspaper['site_url'],
                newspaper['country'],
                newspaper['rss_url'],
                newspaper['language']
            ))
            self._connection.commit()
            print("Journal inserted successfully.")
        except mysql.connector.Error as e:
            print(f"Error occurred while inserting journal: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def create_newspaper(self, newspaper):
        if self._connection is None:
            raise Exception("Database connection is not established")

        try:
            cursor = self._connection.cursor()

            # Insert or update the newspaper
            insert_query = """
                INSERT INTO newspaper 
                (title, newspaper_date, file_name, file_data, file_data_content_type, epub_file, epub_file_content_type, journal_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                newspaper_date = VALUES(newspaper_date),
                file_name = VALUES(file_name),
                file_data = VALUES(file_data),
                file_data_content_type = VALUES(file_data_content_type),
                epub_file = VALUES(epub_file),
                epub_file_content_type = VALUES(epub_file_content_type),
                journal_id = VALUES(journal_id)
            """

                    # id	title	newspaper_date	file_name	file_data	file_data_content_type	epub_file	epub_file_content_type	journal_id	

        
            cursor.execute(insert_query, (
                newspaper['title'],
                newspaper['newspaper_date'],
                newspaper['file_name'],
                newspaper['file_data'],
                newspaper['file_data_content_type'],
                newspaper['epub_file'],
                newspaper['epub_file_content_type'],
                newspaper['journal_id']
            ))
            self._connection.commit()
            print("Newspaper " + newspaper['title'] + " inserted or updated successfully.")
        except mysql.connector.Error as e:
            print(f"Error occurred while inserting newspapaer: {e}")
            self._connection.rollback()
        finally:
            cursor.close()