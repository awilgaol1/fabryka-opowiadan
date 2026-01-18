from ebooklib import epub
import os
import tempfile
from PIL import Image
import io

class EbookGenerator:
    def __init__(self):
        pass
    
    def create_ebook(self, story_text, author_name, format_type="epub", cover_image=None, illustrations=None):
        """Tworzy eBook w formacie EPUB lub MOBI"""
        
        if format_type.lower() == "epub":
            return self._create_epub(story_text, author_name, cover_image, illustrations)
        elif format_type.lower() == "mobi":
            # MOBI wymaga konwersji z EPUB (można użyć Calibre CLI)
            epub_file = self._create_epub(story_text, author_name, cover_image, illustrations)
            # W prawdziwej implementacji tutaj byłaby konwersja do MOBI
            # Na potrzeby demonstracji zwracamy EPUB
            return epub_file
        else:
            raise ValueError("Nieobsługiwany format. Użyj 'epub' lub 'mobi'")
    
    def _create_epub(self, story_text, author_name, cover_image, illustrations):
        """Tworzy eBook w formacie EPUB"""
        
        book = epub.EpubBook()
        
        # Metadane
        book.set_identifier('id_fabryka_opowiadan_001')
        book.set_title('Opowiadanie')
        book.set_language('pl')
        book.add_author(author_name)
        
        # Okładka
        if cover_image:
            # Konwertuj PIL Image do bajtów
            img_byte_arr = io.BytesIO()
            cover_image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            book.set_cover("cover.jpg", img_byte_arr)
        
        # Strona tytułowa
        title_page = epub.EpubHtml(
            title='Strona tytułowa',
            file_name='title.xhtml',
            lang='pl'
        )
        title_page.content = f'''
        <html>
        <head>
            <title>Strona tytułowa</title>
        </head>
        <body>
            <h1 style="text-align: center; margin-top: 100px;">Opowiadanie</h1>
            <p style="text-align: center; margin-top: 50px; font-size: 1.2em;">Autor: {author_name}</p>
        </body>
        </html>
        '''
        book.add_item(title_page)
        
        # Treść opowiadania
        content_chapter = epub.EpubHtml(
            title='Opowiadanie',
            file_name='story.xhtml',
            lang='pl'
        )
        
        # Konwertuj tekst do HTML
        html_content = self._text_to_html(story_text, illustrations)
        content_chapter.content = html_content
        book.add_item(content_chapter)
        
        # Dodaj ilustracje jako oddzielne pliki
        if illustrations:
            for idx, img in enumerate(illustrations):
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                img_item = epub.EpubImage()
                img_item.file_name = f'illustration_{idx}.jpg'
                img_item.content = img_byte_arr
                book.add_item(img_item)
        
        # Spis treści
        book.toc = (
            epub.Link('title.xhtml', 'Strona tytułowa', 'title'),
            epub.Link('story.xhtml', 'Opowiadanie', 'story')
        )
        
        # Dodaj podstawową nawigację
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Kolejność stron
        book.spine = ['nav', title_page, content_chapter]
        
        # Zapisz EPUB
        output_path = os.path.join(tempfile.gettempdir(), "opowiadanie.epub")
        epub.write_epub(output_path, book)
        
        return output_path
    
    def _text_to_html(self, text, illustrations=None):
        """Konwertuje tekst opowiadania do HTML"""
        
        paragraphs = text.split('\n')
        
        html = '''
        <html>
        <head>
            <title>Opowiadanie</title>
            <style>
                body {
                    font-family: Georgia, serif;
                    line-height: 1.6;
                    margin: 20px;
                }
                p {
                    text-indent: 2em;
                    margin: 1em 0;
                    text-align: justify;
                }
                .illustration {
                    text-align: center;
                    margin: 2em 0;
                }
                .illustration img {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
        '''
        
        illustration_index = 0
        paragraph_count = 0
        
        for paragraph in paragraphs:
            if paragraph.strip():
                html += f'<p>{paragraph.strip()}</p>\n'
                paragraph_count += 1
                
                # Co kilka akapitów dodaj ilustrację
                if illustrations and illustration_index < len(illustrations):
                    if paragraph_count % 5 == 0:
                        html += f'''
                        <div class="illustration">
                            <img src="illustration_{illustration_index}.jpg" alt="Ilustracja {illustration_index + 1}" />
                        </div>
                        '''
                        illustration_index += 1
        
        html += '</body></html>'
        
        return html