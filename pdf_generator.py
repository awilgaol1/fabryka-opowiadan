from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from PIL import Image
import os
import tempfile
import textwrap
import urllib.request

class PDFGenerator:
    def __init__(self):
        self.font_name = self._setup_font()
    
    def _setup_font(self):
        """Konfiguruje czcionkę z obsługą polskich znaków"""
        try:
            # Ścieżka do czcionki w temp
            temp_dir = tempfile.gettempdir()
            font_path = os.path.join(temp_dir, 'DejaVuSans.ttf')
            
            # Jeśli nie ma czcionki, pobierz ją
            if not os.path.exists(font_path):
                font_url = 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf'
                urllib.request.urlretrieve(font_url, font_path)
            
            # Zarejestruj czcionkę
            pdfmetrics.registerFont(TTFont('DejaVu', font_path))
            return 'DejaVu'
        except Exception as e:
            # Fallback - użyj Helvetica (ale nie obsługuje polskich znaków)
            print(f"Nie udało się załadować czcionki: {e}")
            return 'Helvetica'
    
    def create_pdf(self, story_text, author_name, cover_image=None, illustrations=None):
        """Tworzy PDF z opowiadaniem"""
        
        output_path = os.path.join(tempfile.gettempdir(), "opowiadanie.pdf")
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Dodaj okładkę jeśli istnieje
        if cover_image:
            self._add_cover_page(c, cover_image, width, height)
        
        # Dodaj stronę tytułową
        self._add_title_page(c, author_name, width, height)
        
        # Dodaj treść opowiadania
        self._add_story_content(c, story_text, illustrations, width, height)
        
        # Zapisz PDF
        c.save()
        
        return output_path
    
    def _add_cover_page(self, c, cover_image, width, height):
        """Dodaje okładkę"""
        
        # Zapisz obraz tymczasowo
        temp_image_path = os.path.join(tempfile.gettempdir(), "cover_temp.png")
        
        if hasattr(cover_image, 'save'):
            # Dostosuj rozmiar do A4
            img_resized = cover_image.copy()
            img_resized = img_resized.resize((int(width), int(height)), Image.Resampling.LANCZOS)
            img_resized.save(temp_image_path)
            
            # Dodaj obraz na całą stronę
            c.drawImage(temp_image_path, 0, 0, width=width, height=height)
            
            # Usuń tymczasowy plik
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        
        c.showPage()
    
    def _add_title_page(self, c, author_name, width, height):
        """Dodaje stronę tytułową"""
        
        # Tytuł
        c.setFont(self.font_name, 24)
        title_text = 'Opowiadanie'
        c.drawCentredString(width / 2, height - 200, title_text)
        
        # Autor
        c.setFont(self.font_name, 16)
        author_text = f'Autor: {author_name}'
        c.drawCentredString(width / 2, height - 280, author_text)
        
        c.showPage()
    
    def _add_story_content(self, c, story_text, illustrations, width, height):
        """Dodaje treść opowiadania"""
        
        c.setFont(self.font_name, 12)
        
        # Marginesy
        left_margin = 50
        right_margin = width - 50
        top_margin = height - 50
        bottom_margin = 50
        line_height = 18
        
        # Podziel tekst na akapity
        paragraphs = story_text.split('\n')
        
        y_position = top_margin
        illustration_index = 0
        paragraph_count = 0
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            
            # Zawijanie tekstu - większa szerokość dla tekstu
            max_chars_per_line = int((right_margin - left_margin) / 6)
            wrapper = textwrap.TextWrapper(width=max_chars_per_line)
            lines = wrapper.wrap(paragraph.strip())
            
            for line in lines:
                # Sprawdź czy trzeba dodać nową stronę
                if y_position < bottom_margin + 50:
                    c.showPage()
                    c.setFont(self.font_name, 12)
                    y_position = top_margin
                
                # Narysuj linię tekstu
                try:
                    c.drawString(left_margin, y_position, line)
                except Exception as e:
                    # Jeśli błąd z czcionką, spróbuj bez polskich znaków
                    safe_line = line.encode('ascii', 'ignore').decode('ascii')
                    c.drawString(left_margin, y_position, safe_line)
                
                y_position -= line_height
            
            # Dodatkowa przerwa między akapitami
            y_position -= line_height * 0.5
            paragraph_count += 1
            
            # Co kilka akapitów dodaj ilustrację
            if illustrations and illustration_index < len(illustrations):
                if paragraph_count % 5 == 0:
                    c.showPage()
                    self._add_illustration(c, illustrations[illustration_index], width, height)
                    c.showPage()
                    c.setFont(self.font_name, 12)
                    y_position = top_margin
                    illustration_index += 1
        
        # Dodaj pozostałe ilustracje na końcu
        while illustrations and illustration_index < len(illustrations):
            c.showPage()
            self._add_illustration(c, illustrations[illustration_index], width, height)
            illustration_index += 1
    
    def _add_illustration(self, c, image, width, height):
        """Dodaje ilustrację do PDF"""
        
        # Zapisz obraz tymczasowo
        temp_image_path = os.path.join(tempfile.gettempdir(), f"illustration_{id(image)}.png")
        
        # Zmień rozmiar obrazu
        img_resized = image.copy()
        img_resized.thumbnail((400, 400), Image.Resampling.LANCZOS)
        img_resized.save(temp_image_path)
        
        # Wycentruj obraz
        img_width = 150 * mm
        img_height = 150 * mm
        x_pos = (width - img_width) / 2
        y_pos = (height - img_height) / 2
        
        c.drawImage(temp_image_path, x_pos, y_pos, width=img_width, height=img_height, preserveAspectRatio=True)
        
        # Usuń tymczasowy plik
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)