from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from PIL import Image
import os
import tempfile
import textwrap

class PDFGenerator:
    def __init__(self):
        # Ścieżka do czcionki w katalogu projektu
        font_path = os.path.join("fonts", "DejaVuSans.ttf")

        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                self.font_name = "DejaVuSans"
            else:
                print("⚠️ Brak czcionki w katalogu fonts/. Używam Helvetica.")
                self.font_name = "Helvetica"
        except Exception as e:
            print("⚠️ Błąd ładowania czcionki:", e)
            self.font_name = "Helvetica"

    def create_pdf(self, story_text, author, cover_image=None, illustrations=None):
        output_path = os.path.join(tempfile.gettempdir(), 'output.pdf')
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        self._add_cover_page(c, cover_image)
        self._add_title_page(c, author, width, height)
        self._add_story_content(c, story_text, illustrations, width, height)
        c.save()
        return output_path

    def _add_cover_page(self, c, cover_image):
        if hasattr(cover_image, 'save'):
            img_resized = cover_image.copy().resize((int(A4[0]), int(A4[1])))
            temp_image_path = os.path.join(tempfile.gettempdir(), 'temp_cover.jpg')
            img_resized.save(temp_image_path)
            c.drawImage(temp_image_path, 0, 0)
            os.remove(temp_image_path)
            c.showPage()

    def _add_title_page(self, c, author, width, height):
        c.setFont(self.font_name, 20)
        c.drawCentredString(width / 2, height - 100, "Opowiadanie")
        c.setFont(self.font_name, 16)
        c.drawCentredString(width / 2, height - 130, f"Autor: {author}")
        c.showPage()

    def _add_story_content(self, c, story_text, illustrations, width, height):
        c.setFont(self.font_name, 12)
        left_margin = 50
        top_margin = height - 50
        bottom_margin = 50
        line_height = 15
        y_position = top_margin
        paragraphs = story_text.split('\n')
        illustration_index = 0
        paragraph_count = 0

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            wrapper = textwrap.TextWrapper(width=90)
            lines = wrapper.wrap(paragraph)
            for line in lines:
                if y_position < bottom_margin:
                    c.showPage()
                    c.setFont(self.font_name, 12)
                    y_position = top_margin
                c.drawString(left_margin, y_position, line)
                y_position -= line_height
            y_position -= line_height
            paragraph_count += 1
            if illustrations and illustration_index < len(illustrations):
                if paragraph_count % 3 == 0:
                    self._add_illustration(c, illustrations[illustration_index])
                    illustration_index += 1

        while illustrations and illustration_index < len(illustrations):
            c.showPage()
            self._add_illustration(c, illustrations[illustration_index])
            illustration_index += 1

    def _add_illustration(self, c, img):
        temp_image_path = os.path.join(tempfile.gettempdir(), 'temp_img.jpg')
        img_resized = img.copy().resize((400, 400))
        img_resized.save(temp_image_path)
        c.drawImage(temp_image_path, 100, 300)
        os.remove(temp_image_path)
