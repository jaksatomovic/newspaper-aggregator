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

    def create_tables(self):
        if self._connection is None:
            raise Exception("Database connection is not established")
            
        cursor = self._connection.cursor()
        
        try:
            # Check if the newspapers table exists
            cursor.execute("SHOW TABLES LIKE 'newspapers'")
            newspapers_table_exists = cursor.fetchone()

            # Check if the journals table exists
            cursor.execute("SHOW TABLES LIKE 'journals'")
            journals_table_exists = cursor.fetchone()

            # Check if the categories table exists
            cursor.execute("SHOW TABLES LIKE 'categories'")
            categories_table_exists = cursor.fetchone()

            if newspapers_table_exists:
                # Table already exists, no need to create
                print("Table 'newspapers' already exists.")
            else:
                # Table doesn't exist, create it
                create_table_query = """
                    CREATE TABLE newspapers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(300) NOT NULL,
                        subtitle VARCHAR(300),
                        newspaper_date VARCHAR(50) NOT NULL,
                        category_id INT NOT NULL,
                        subcategory_id INT,
                        file_name VARCHAR(255) NOT NULL,
                        file_data LONGBLOB NOT NULL,
                        journal_id INT NOT NULL,
                        scraping_date VARCHAR(50) NOT NULL,
                        UNIQUE KEY (title, file_name, journal_id, newspaper_date, scraping_date) -- Unique constraint on these columns
                    )
                """
                cursor.execute(create_table_query)
                
                print("Table 'newspapers' created successfully.")

            if not journals_table_exists:
                # Journals table doesn't exist, create it
                create_journals_table_query = """
                    CREATE TABLE journals (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(300) NOT NULL,
                        site_url VARCHAR(300) NOT NULL,
                        country VARCHAR(50) NOT NULL,
                        rss_url VARCHAR(255) NOT NULL,
                        language VARCHAR(10) NOT NULL
                    )
                """
                cursor.execute(create_journals_table_query)
                print("Table 'journals' created successfully.")

            if not categories_table_exists:
                # Create categories table
                create_categories_table_query = """
                    CREATE TABLE categories (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        parent_id INT,
                        FOREIGN KEY (parent_id) REFERENCES categories(id)
                    )
                """
                cursor.execute(create_categories_table_query)
                print("Table 'categories' created successfully.")
                
                # Insert categories data with parent categories
                categories_data = {
                    'News': None,
                    'World': 'News',
                    'Domestic': 'News',
                    'Region': 'News',
                    'Sport': None,
                    'Business': None,
                    'Future of Business': 'Business',
                    'Technology of Business': 'Business',
                    'Work Culture': 'Business',
                    'Innovation': None,
                    'Technology': 'Innovation',
                    'Science & Health': 'Innovation',
                    'Artificial Intelligence': 'Innovation',
                    'Culture': None,
                    'Film & TV': 'Culture',
                    'Music': 'Culture',
                    'Art & Design': 'Culture',
                    'Style': 'Culture',
                    'Books': 'Culture',
                    'Entertainment News': 'Culture',
                    'Travel': None,
                    'Destinations': 'Travel',
                    'World’s Table': 'Travel',
                    'Culture & Experiences': 'Travel',
                    'Adventures': 'Travel',
                    'The SpeciaList': 'Travel',
                    'Earth': None,
                    'Natural Wonders': 'Earth',
                    'Weather & Science': 'Earth',
                    'Climate Solutions': 'Earth',
                    'Sustainable Business': 'Earth',
                    'Green Living': 'Earth'
                }
                
                for category_name, parent_name in categories_data.items():
                    parent_id = None
                    if parent_name:
                        get_parent_id_query = "SELECT id FROM categories WHERE name = %s"
                        cursor.execute(get_parent_id_query, (parent_name,))
                        parent_id = cursor.fetchone()[0]
                    insert_category_query = "INSERT INTO categories (name, parent_id) VALUES (%s, %s)"
                    cursor.execute(insert_category_query, (category_name, parent_id))
                print("Categories data inserted successfully.")

            self._connection.commit()
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
            print("Query executed successfully.")
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
            cursor.execute("SELECT site_url, rss_url, language FROM journals")
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
                INSERT INTO newspapers 
                (title, subtitle, newspaper_date, category_id, file_name, file_data, journal_id, scraping_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                subtitle = VALUES(subtitle),
                newspaper_date = VALUES(newspaper_date),
                category_id = VALUES(category_id),
                file_name = VALUES(file_name),
                file_data = VALUES(file_data),
                journal_id = VALUES(journal_id),
                scraping_date = VALUES(scraping_date)
            """
        
            cursor.execute(insert_query, (
                newspaper['title'],
                newspaper['subtitle'],
                newspaper['newspaper_date'],
                newspaper['category_id'],
                newspaper['file_name'],
                newspaper['file_data'],
                newspaper['journal_id'],
                newspaper['scraping_date']
            ))
            self._connection.commit()
            print("Newspaper " + newspaper['title'] + " inserted or updated successfully.")
        except mysql.connector.Error as e:
            print(f"Error occurred while inserting newspapaer: {e}")
            self._connection.rollback()
        finally:
            cursor.close()