from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
import tempfile
import textwrap

class PDFGenerator:
    def __init__(self):
        # Absolutna ścieżka do czcionki — działa w Streamlit Cloud
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")

        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                self.font_name = "DejaVuSans"
            else:
                print("⚠️ Brak czcionki — używam Helvetica.")
                self.font_name = "Helvetica"
        except:
            self.font_name = "Helvetica"

        self.page_number = 0  # licznik stron

    # -----------------------------
    # NUMERACJA STRON
    # -----------------------------
    def _draw_page_number(self, c, width, height):
        """Rysuje numer strony na dole."""
        c.setFont(self.font_name, 10)
        c.drawCentredString(width / 2, 20, f"Strona {self.page_number}")

    # -----------------------------
    # GŁÓWNY GENERATOR PDF
    # -----------------------------
    def create_pdf(self, story_text, author, cover_image=None, illustrations=None):
        output_path = os.path.join(tempfile.gettempdir(), 'output.pdf')
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        self._add_cover_page(c, cover_image, width, height)
        self._add_title_page(c, author, width, height)
        self._add_story_content(c, story_text, illustrations, width, height)

        c.save()
        return output_path

    # -----------------------------
    # OKŁADKA
    # -----------------------------
    def _add_cover_page(self, c, cover_image, width, height):
        self.page_number = 0  # okładka bez numeru

        if hasattr(cover_image, 'save'):
            img_resized = cover_image.copy().resize((int(width), int(height)))
            temp_image_path = os.path.join(tempfile.gettempdir(), 'temp_cover.jpg')
            img_resized.save(temp_image_path)
            c.drawImage(temp_image_path, 0, 0)
            os.remove(temp_image_path)

        c.showPage()

    # -----------------------------
    # STRONA TYTUŁOWA
    # -----------------------------
    def _add_title_page(self, c, author, width, height):
        self.page_number = 0  # strona tytułowa bez numeru

        c.setFont(self.font_name, 24)
        c.drawCentredString(width / 2, height - 150, "Opowiadanie")

        c.setFont(self.font_name, 16)
        c.drawCentredString(width / 2, height - 200, f"Autor: {author}")

        c.showPage()

    # -----------------------------
    # TREŚĆ OPOWIADANIA
    # -----------------------------
    def _add_story_content(self, c, story_text, illustrations, width, height):
        self.page_number = 1  # numeracja zaczyna się tutaj

        left_margin = 50
        right_margin = 50
        max_width = width - left_margin - right_margin

        top_margin = height - 50
        bottom_margin = 50
        line_height = 15
        y = top_margin

        paragraphs = self._split_into_paragraphs(story_text)
        illustration_index = 0
        paragraph_count = 0

        for paragraph in paragraphs:
            c.setFont(self.font_name, 12)

            # Łamanie tekstu na podstawie liczby znaków (bez justowania)
            wrapper = textwrap.TextWrapper(width=85)
            lines = wrapper.wrap(paragraph)

            for line in lines:
                if y < bottom_margin:
                    self._draw_page_number(c, width, height)
                    c.showPage()
                    self.page_number += 1
                    c.setFont(self.font_name, 12)
                    y = top_margin

                # NORMALNE RYSOWANIE TEKSTU (bez justowania)
                c.drawString(left_margin, y, line)
                y -= line_height

            y -= line_height  # odstęp między akapitami
            paragraph_count += 1

            # Ilustracja co 3 akapity
            if illustrations and illustration_index < len(illustrations):
                if paragraph_count % 3 == 0:
                    y = self._add_illustration(c, illustrations[illustration_index], y, width, height)
                    illustration_index += 1

        # Ilustracje po zakończeniu tekstu
        while illustrations and illustration_index < len(illustrations):
            self._draw_page_number(c, width, height)
            c.showPage()
            self.page_number += 1
            self._add_illustration(c, illustrations[illustration_index], top_margin, width, height)
            illustration_index += 1

        self._draw_page_number(c, width, height)

    # -----------------------------
    # AUTOMATYCZNE AKAPITY
    # -----------------------------
    def _split_into_paragraphs(self, text):
        raw = text.split("\n")
        paragraphs = []
        buffer = ""

        for line in raw:
            if line.strip() == "":
                if buffer.strip():
                    paragraphs.append(buffer.strip())
                    buffer = ""
            else:
                buffer += " " + line.strip()

        if buffer.strip():
            paragraphs.append(buffer.strip())

        return paragraphs

    # -----------------------------
    # ILUSTRACJE
    # -----------------------------
    def _add_illustration(self, c, img, y, width, height):
        """Dodaje ilustrację i zwraca nową pozycję Y."""
        if y < 450:  # za mało miejsca
            self._draw_page_number(c, width, height)
            c.showPage()
            self.page_number += 1
            y = height - 50

        temp_image_path = os.path.join(tempfile.gettempdir(), 'temp_img.jpg')
        img_resized = img.copy().resize((400, 400))
        img_resized.save(temp_image_path)

        c.drawImage(temp_image_path, 100, y - 400)
        os.remove(temp_image_path)

        return y - 420
