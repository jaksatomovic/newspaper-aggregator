import newspaper
import feedparser
import csv
import datetime
import re

from newspaper import Config
from newspaper.mthreading import fetch_news
from constants import csv_extension, data_folder_path

# Define content types for video files
ignore_defaults = {
    "video/mp4": "mp4",
    "video/mpeg": "mpeg",
    "video/ogg": "ogg",
    "video/quicktime": "quicktime",
    "video/webm": "webm",
    "video/x-ms-wmv": "wmv",
    "audio/mpeg": "mp3",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "application/pdf": "%PDF-",
    "application/x-pdf": "%PDF-",
    "application/x-bzpdf": "%PDF-",
    "application/x-gzpdf": "%PDF-"
}

# Create a custom configuration
config = Config()
config.min_sent_count = 20
config.ignored_content_types_defaults = ignore_defaults

def check_empty(article_urls):
    if len(article_urls) == 0:
        return True
    else:
        return False

def get_news(journal, db_manager):

    journal_id = journal['journal_id']
    journal_name = journal['journal_name']
    journal_image = journal['image']
    country = journal['country']
    site_url = journal['site_url']
    rss_url = journal['rss_url']
    category_id = journal['category_id']
    language = journal['language']

    # Check if rss_url is not None or an empty string
    if not rss_url:
        print("RSS URL is null or empty for journal:", journal_name)
        return
    
    brand = journal_name.lower().strip().replace(" ", "")

    feed = feedparser.parse(rss_url)

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    csv_file_path = data_folder_path + brand + csv_extension

    article_urls = []
    for entry in feed.entries:
        format_string = '%a, %d %b %Y %H:%M:%S %z'
        date_object = datetime.datetime.strptime(entry.published, format_string)
        date_only = date_object.date()
        if date_only == yesterday:
            article_urls.append(entry.link)

    print('number of fetched links: ' + str(len(article_urls)))

    if check_empty(article_urls):
        return

    # Create and open CSV file in write mode
    # with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    #     # Define CSV writer
    #     csv_writer = csv.writer(csvfile)
        
    #     # Write header row
    #     csv_writer.writerow(['journal_id', 'category_id', 'title', 'content', 'image'])

    articles = [newspaper.Article(url=u, language=language, config=config) for u in article_urls]

    results = fetch_news(articles, threads=4)

    for article in results:
        # Check if title starts with "VIDEO" in all capital letters
        if article.title and (article.title.strip().startswith('VIDEO') or article.title.strip().startswith('ANKETA') or article.title.strip().startswith('UŽIVO') or article.title.strip().startswith('LIVE')):
            continue  # Skip this article if the title starts with "VIDEO"
            
        # Extract data
        title = ' ' + article.title.strip() if article.title else ''
        content = ' ' + article.text if article.text else ''
        top_image = article.top_image if article.top_image else ''

        # Write data to CSV
        # csv_writer.writerow([journal_id, category_id, title, re.sub(r'\s+', ' ', content), top_image])

        insert_query = """ INSERT INTO temp_data (journal_id, category_id, title, content, image_url) VALUES (%s, %s, %s, %s, %s) """
        # Define the values to be inserted
        values = (journal_id, category_id, title, re.sub(r'\s+', ' ', content), top_image)

        db_manager.connect()
        db_manager.execute_query(insert_query, values)
        db_manager.disconnect()

    print("Data for '" + journal_name + "' has been written into temporary table.")


