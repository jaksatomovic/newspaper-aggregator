import ebooklib

from weasyprint import HTML


def epub_to_pdf(epub_file, pdf_file):
    book = ebooklib.epub.read_epub(epub_file)

    # Initialize HTML content string
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        @namespace epub "http://www.idpf.org/2007/ops";

        img{
            width:100%;
        }

        .date {
            font: 1em "Roboto Mono", monospace;
            text-align: center;
            width: 280px;
            margin: auto;
            margin-top: 10px;
            border-left: 1px solid black;
            border-right: 1px solid black;
        }

        header{
            font-size: 3em;
            color: #111;
            font-weight: bold;
            text-align: center;
            margin-top: 30px;
            padding-bottom: 15px;
            text-shadow: -1px 1px 0 white, -2px 2px 0 #111;
        }

        hr{
            margin-bottom: 50px;
            font: 1em "Roboto Mono", monospace;
            text-align: center;
            margin: auto;
            margin-top: 10px;
            border-left: 1px solid black;
            border-right: 1px solid black;
        }

        section{
            margin-top: 50px;
            -webkit-column-count: 3;
            -webkit-column-gap: 20px;
            -webkit-column-rule: 1px solid #A1A1A1;
            -moz-column-count: 3;
            -moz-column-gap: 20px;
            -moz-column-rule: 1px solid #A1A1A1;
            column-count: 3;
            column-gap: 20px;
            column-rule: 1px solid #A1A1A1;
            text-align: justify;
        }

        h1{
            margin-top:0;
            text-align: center;
        }
        </style>
    </head>
    <body>
    """

    # Iterate over items in EPUB book
    for item in book.get_items():
        # Check if the item is a document
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Get body content and decode it
            body_content = item.get_body_content().decode('utf-8')
            # Append body content to HTML content string
            html_content += body_content

    # Close body and HTML tags
    html_content += """
    </body>
    </html>
    """
    # Convert HTML content to PDF
    HTML(string=html_content).write_pdf(pdf_file)