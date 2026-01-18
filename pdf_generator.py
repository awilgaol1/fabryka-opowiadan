from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
import tempfile

class PDFGenerator:
    def __init__(self):
        font_path = "fonts/DejaVuSans.ttf"

        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                self.font_name = "DejaVuSans"
            else:
                print("⚠️ Brak czcionki — używam Helvetica.")
                self.font_name = "Helvetica"
        except:
            self.font_name = "Helvetica"

        self.page_number = 0

    # -----------------------------
    # GŁÓWNY GENERATOR PDF
    # -----------------------------
    def create_pdf(self, story_text, author, cover_image=None, illustrations=None, title=""):
        output_path = os.path.join(tempfile.gettempdir(), 'output.pdf')
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Okładka (tylko jeśli została wygenerowana)
        if cover_image:
            self._add_cover_page(c, cover_image, width, height)
        
        # Strona tytułowa
        self._add_title_page(c, author, title, width, height)
        
        # Treść
        self._add_story_content(c, story_text, illustrations, width, height, title)

        c.save()
        return output_path

    # -----------------------------
    # OKŁADKA
    # -----------------------------
    def _add_cover_page(self, c, cover_image, width, height):
        self.page_number = 0

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
    def _add_title_page(self, c, author, title, width, height):
        self.page_number = 0

        # Tytuł (jeśli jest)
        if title:
            c.setFont(self.font_name, 28)
            c.drawCentredString(width / 2, height - 150, title)
        
        # Autor
        c.setFont(self.font_name, 16)
        c.drawCentredString(width / 2, height - 200, f"Autor: {author}")

        c.showPage()

    # -----------------------------
    # TREŚĆ — wersja książkowa (bez justowania)
    # -----------------------------
    def _add_story_content(self, c, story_text, illustrations, width, height, title):
        self.page_number = 1

        left_margin = 60
        right_margin = 60
        top_margin = height - 60
        bottom_margin = 60
        line_height = 16
        first_line_indent = 25
        font_size = 12

        text_width = width - left_margin - right_margin
        y = top_margin

        paragraphs = self._split_into_paragraphs(story_text)
        illustration_index = 0

        # Nagłówek z tytułem (jeśli jest) zamiast "Opowiadanie"
        header_text = title if title else ""

        for paragraph in paragraphs:
            c.setFont(self.font_name, font_size)

            lines = self._wrap_paragraph(paragraph, font_size, text_width)

            first = True
            for line in lines:
                if y < bottom_margin + line_height:
                    self._draw_page_number(c, width, height)
                    c.showPage()
                    self.page_number += 1
                    if header_text:
                        self._draw_header(c, width, height, header_text)
                    c.setFont(self.font_name, font_size)
                    y = top_margin
                    first = True

                indent = first_line_indent if first else 0
                c.drawString(left_margin + indent, y, line)
                y -= line_height
                first = False

            y -= line_height  # odstęp między akapitami

            # Ilustracja po akapicie
            if illustrations and illustration_index < len(illustrations):
                y = self._add_illustration(c, illustrations[illustration_index], y, width, height)
                illustration_index += 1

        # Ilustracje na końcu
        while illustrations and illustration_index < len(illustrations):
            c.showPage()
            self.page_number += 1
            y = height - 60
            y = self._add_illustration(c, illustrations[illustration_index], y, width, height)
            illustration_index += 1

        self._draw_page_number(c, width, height)

    # -----------------------------
    # NAGŁÓWEK
    # -----------------------------
    def _draw_header(self, c, width, height, title):
        c.setFont(self.font_name, 10)
        c.drawCentredString(width / 2, height - 30, title)

    # -----------------------------
    # NUMER STRONY
    # -----------------------------
    def _draw_page_number(self, c, width, height):
        c.setFont(self.font_name, 10)
        c.drawCentredString(width / 2, 20, f"Strona {self.page_number}")

    # -----------------------------
    # DZIELENIE NA AKAPITY
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
    # ZAWIJANIE TEKSTU PO SZEROKOŚCI STRONY
    # -----------------------------
    def _wrap_paragraph(self, paragraph, font_size, max_width):
        words = paragraph.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = word if not current_line else current_line + " " + word
            line_width = pdfmetrics.stringWidth(test_line, self.font_name, font_size)

            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    # -----------------------------
    # ILUSTRACJE — czyste strony
    # -----------------------------
    def _add_illustration(self, c, img, y, width, height):

        if y < 450:
            c.showPage()
            self.page_number += 1
            y = height - 60

        temp_image_path = os.path.join(tempfile.gettempdir(), 'temp_img.jpg')

        img_resized = img.copy().resize((400, 400))
        img_resized.save(temp_image_path)

        c.drawImage(temp_image_path, 100, y - 400)
        os.remove(temp_image_path)

        return y - 420