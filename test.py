from ebooklib import epub
from io import BytesIO
from database_manager import DatabaseManager
from dotenv import load_dotenv
import datetime

# Create a new ePub book
book = epub.EpubBook()

# Set metadata
book.set_identifier('id123456')
book.set_title('Sample ePub Book')
book.set_language('en')

# Create chapter
chapter = epub.EpubHtml(title='Chapter 1', file_name='chap_1.xhtml', lang='en')
chapter.content = '<h1>Chapter 1</h1><p>This is the content of Chapter 1.</p>'

# Add chapter to book
book.add_item(chapter)

# Create Table of Contents
book.toc = [epub.Link('chap_1.xhtml', 'Chapter 1', 'chap_1')]

book.spine = ["newspaper_title", chapter]

# Add navigation files
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# Define CSS style
style = 'body { font-family: Times, Times New Roman, serif; }'
# book.add_css('body { font-family: Times, Times New Roman, serif; }')

# Add cover page
book.add_item(epub.EpubItem(uid="cover_style", file_name="style/default.css", media_type="text/css", content=style))
# book.set_cover("image.jpg", open("image.jpg", "rb").read())

# Create BytesIO object to hold the binary data
epub_bytes = BytesIO()

# Write ePub book to BytesIO object
epub.write_epub(epub_bytes, book, {})
epub.write_epub("build/" + "test" + '.epub', book, {})

print(epub_bytes.getvalue)

# Now you can use 'epub_bytes' to store the binary data in the database

db_manager = DatabaseManager.get_instance()


load_dotenv()

# Convert BytesIO object to bytes
epub_bytes.seek(0)
epub_binary_data = epub_bytes.read()

# Setup project
db_manager.connect()

today = datetime.datetime.now()
formatted_date = today.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
newspaper = {
    'journal_id': 1,
    'title': "test",
    'newspaper_date': formatted_date,
    'file_name': "test",
    'file_data': epub_binary_data,
    'file_data_content_type': "test",
    'epub_file': epub_binary_data,
    'epub_file_content_type': "test"
}
db_manager.create_newspaper(newspaper)

db_manager.disconnect()
