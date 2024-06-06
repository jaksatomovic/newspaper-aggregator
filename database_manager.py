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
            # Check if the publications table exists
            cursor.execute("SHOW TABLES LIKE 'publication'")
            publication_table_exists = cursor.fetchone()

            # Check if the periodicals table exists
            cursor.execute("SHOW TABLES LIKE 'periodical'")
            periodical_table_exists = cursor.fetchone()

            # Check if the categories table exists
            cursor.execute("SHOW TABLES LIKE 'category'")
            category_table_exists = cursor.fetchone()

            # Check if the temp_data table exists
            cursor.execute("SHOW TABLES LIKE 'temp_data'")
            temp_data_table_exists = cursor.fetchone()

            if not temp_data_table_exists:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS temp_data (
                        periodical_id INTEGER,
                        category_id INTEGER,
                        title TEXT,
                        content TEXT,
                        image_url TEXT
                    )
                ''')

            if not publication_table_exists or not periodical_table_exists or not category_table_exists:
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
    
    def get_periodicals(self):
        if self._connection is None:
            raise Exception("Database connection is not established")

        cursor = self._connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT j.id AS periodical_id, j.name AS periodical_name, j.site_url, j.language, j.country, j.image, j.image_content_type, f.rss_url, f.category_id FROM periodical j LEFT JOIN periodical_source f ON j.id = f.periodical_id")
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
            cursor.execute("SELECT periodical_id, category_id, title, content, image_url FROM temp_data")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error occurred while executing query: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def get_periodical_name(self, periodical_id):
        if self._connection is None:
            raise Exception("Database connection is not established")

        cursor = self._connection.cursor(dictionary=True)

        try:
            cursor.execute(''' SELECT j.name AS periodical_name FROM periodical j WHERE j.id =  ''' + str(periodical_id))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error occurred while executing query: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def periodical_exists(self, periodical_name):
        if self._connection is None:
            raise Exception("Database connection is not established")
        
        try:
            cursor = self._connection.cursor()

            query = "SELECT COUNT(*) FROM periodical WHERE name = %s"
            cursor.execute(query, (periodical_name,))
            count = cursor.fetchone()[0]
            
            return count > 0
        except mysql.connector.Error as e:
            print(f"Error occurred while inserting periodical: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def create_publication(self, publication):
        if self._connection is None:
            raise Exception("Database connection is not established")

        try:
            cursor = self._connection.cursor()
            cursor.execute("LOCK TABLES publication WRITE")

            # Insert or update the publication
            insert_query = """
                INSERT INTO publication 
                (title, publication_date, file_name, file_data, file_data_content_type, periodical_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                publication_date = VALUES(publication_date),
                file_name = VALUES(file_name),
                file_data_content_type = VALUES(file_data_content_type),
                periodical_id = VALUES(periodical_id)
            """
        
            cursor.execute(insert_query, (
                publication['title'],
                publication['publication_date'],
                publication['file_name'],
                publication['file_data'],
                publication['file_data_content_type'],
                publication['periodical_id']
            ))
            self._connection.commit
            cursor.execute("UNLOCK TABLES")
        except mysql.connector.Error as e:
            print(f"Error occurred while inserting newspapaer: {e}")
            self._connection.rollback()
        finally:
            cursor.close()
