import openai
import base64
import io
from PIL import Image

class StoryGenerator:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    # ---------------------------------------------------------
    # GENEROWANIE OPOWIADANIA
    # ---------------------------------------------------------
    def generate_story(self, params):
        prompt = (
            f"Napisz opowiadanie o długości około {params['word_count']} słów.\n"
            f"Grupa wiekowa: {params['age_group']}.\n"
            f"Gatunek: {params['genre']}.\n"
            f"Miejsce akcji: {params['location']}.\n"
            f"Zakończenie: {params['ending_type']} – {params['ending_mood']}.\n"
            f"Główny bohater: {params['main_character']}.\n"
            f"Dodatkowi bohaterowie: {params['additional_characters']}.\n"
            f"Styl narracji: płynny, obrazowy, emocjonalny.\n"
            f"Unikaj wulgaryzmów i treści nieodpowiednich.\n"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )

        return response.choices[0].message.content

    # ---------------------------------------------------------
    # GENEROWANIE TYTUŁÓW - POPRAWIONA WERSJA
    # ---------------------------------------------------------
    def generate_title_suggestions(self, story_text):
        prompt = (
            "Na podstawie poniższego opowiadania wygeneruj 5 krótkich, chwytliwych tytułów.\n"
            "Tytuły mają być maksymalnie 5 słów.\n"
            "WAŻNE: Zwróć tylko same tytuły, bez numeracji, bez myślników, bez kropek.\n"
            "Każdy tytuł w nowej linii.\n\n"
            f"{story_text}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )

        titles = response.choices[0].message.content.split("\n")
        
        # POPRAWKA: Czyszczenie tytułów z numeracji i znaków
        cleaned_titles = []
        for t in titles:
            if t.strip():
                # Usuń numerację (1., 2., itp.), myślniki, gwiazdki
                cleaned = t.strip()
                cleaned = cleaned.lstrip('0123456789.-•* ')
                cleaned = cleaned.strip('"\'')
                if cleaned:
                    cleaned_titles.append(cleaned)
        
        return cleaned_titles[:5]

    # ---------------------------------------------------------
    # ILUSTRACJE — GPT-IMAGE-1 (z bezpieczniejszym promptem)
    # ---------------------------------------------------------
    def generate_illustration(self, fragment, style):
        # Skróć i uogólnij fragment do 200 znaków
        safe_fragment = self._sanitize_prompt(fragment, max_length=200)
        
        prompt = (
            f"A beautiful {style.lower()} style illustration depicting: {safe_fragment}. "
            "Family-friendly, artistic, without any text or letters."
        )

        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )

            if not response or not response.data or not response.data[0].b64_json:
                return None

            image_bytes = base64.b64decode(response.data[0].b64_json)
            return Image.open(io.BytesIO(image_bytes))
        
        except Exception as e:
            # Jeśli nadal blokuje, spróbuj ogólniejszego promptu
            if "moderation" in str(e).lower():
                return self._generate_generic_illustration(style)
            raise e

    # ---------------------------------------------------------
    # OKŁADKA — GPT-IMAGE-1 (z bezpieczniejszym promptem)
    # ---------------------------------------------------------
    def generate_cover(self, sketch, description, style):
        # Skróć i uogólnij opis
        safe_description = self._sanitize_prompt(description, max_length=150)
        
        prompt = (
            f"Book cover art in {style.lower()} style. "
            f"Theme: {safe_description}. "
            "Beautiful, artistic, family-friendly book cover. "
            "No text, no title, no author name on the image."
        )

        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )

            if not response or not response.data or not response.data[0].b64_json:
                return None

            image_bytes = base64.b64decode(response.data[0].b64_json)
            return Image.open(io.BytesIO(image_bytes))
        
        except Exception as e:
            # Jeśli nadal blokuje, spróbuj ogólniejszego promptu
            if "moderation" in str(e).lower():
                return self._generate_generic_cover(style)
            raise e

    # ---------------------------------------------------------
    # NAKŁADANIE TYTUŁU NA OKŁADKĘ — POPRAWIONA WERSJA
    # ---------------------------------------------------------
    def add_title_to_cover(self, cover_image, title, author):
        from PIL import ImageDraw, ImageFont

        img = cover_image.copy()
        draw = ImageDraw.Draw(img)

        # Załaduj czcionki
        try:
            font_title = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 90)
        except:
            try:
                font_title = ImageFont.truetype("fonts/DejaVuSans.ttf", 90)
            except:
                font_title = ImageFont.load_default()

        try:
            font_author = ImageFont.truetype("fonts/DejaVuSans.ttf", 50)
        except:
            font_author = ImageFont.load_default()

        W, H = img.size

        # ---------------------------------------------------------
        # TYTUŁ - wycentrowany w górnej części
        # ---------------------------------------------------------
        # Jeśli tytuł jest długi, zmniejsz czcionkę
        if len(title) > 20:
            try:
                font_title = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 70)
            except:
                try:
                    font_title = ImageFont.truetype("fonts/DejaVuSans.ttf", 70)
                except:
                    pass

        # Zawijanie tytułu jeśli jest za długi
        words = title.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = word if not current_line else current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font_title)
            w = bbox[2] - bbox[0]
            
            if w <= W * 0.9:  # 90% szerokości
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)

        # Rysuj tytuł (w górnej części, około 15% wysokości)
        y_position = H * 0.15
        line_height = 100

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_title)
            w = bbox[2] - bbox[0]
            
            # Cień dla lepszej czytelności
            draw.text(
                ((W - w) / 2 + 3, y_position + 3),
                line,
                fill="black",
                font=font_title
            )
            
            # Właściwy tekst
            draw.text(
                ((W - w) / 2, y_position),
                line,
                fill="white",
                font=font_title
            )
            
            y_position += line_height

        # ---------------------------------------------------------
        # AUTOR - na dole
        # ---------------------------------------------------------
        bbox_author = draw.textbbox((0, 0), author, font=font_author)
        w_author = bbox_author[2] - bbox_author[0]

        # Cień
        draw.text(
            ((W - w_author) / 2 + 2, H * 0.88 + 2),
            author,
            fill="black",
            font=font_author
        )
        
        # Właściwy tekst
        draw.text(
            ((W - w_author) / 2, H * 0.88),
            author,
            fill="white",
            font=font_author
        )

        return img

    # ---------------------------------------------------------
    # MODYFIKACJA OPOWIADANIA
    # ---------------------------------------------------------
    def modify_story(self, story_text, new_style, new_plot):
        prompt = (
            "Zmodyfikuj poniższe opowiadanie zgodnie z instrukcjami.\n"
            f"Nowy styl: {new_style or 'bez zmian'}.\n"
            f"Zmiana fabuły: {new_plot or 'bez zmian'}.\n"
            f"{story_text}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )

        return response.choices[0].message.content
    
    # ---------------------------------------------------------
    # POMOCNICZE FUNKCJE BEZPIECZEŃSTWA
    # ---------------------------------------------------------
    def _sanitize_prompt(self, text, max_length=200):
        """Czyści i skraca prompt, aby był bezpieczniejszy"""
        # Usuń potencjalnie wrażliwe słowa
        sensitive_words = ['krew', 'śmierć', 'zabić', 'przemoc', 'broń', 'walka']
        
        text_lower = text.lower()
        for word in sensitive_words:
            if word in text_lower:
                # Zamień na bardziej neutralne
                replacements = {
                    'krew': 'czerwień',
                    'śmierć': 'koniec',
                    'zabić': 'pokonać',
                    'przemoc': 'konflikt',
                    'broń': 'narzędzie',
                    'walka': 'pojedynek'
                }
                text = text.replace(word, replacements.get(word, ''))
        
        # Skróć do max_length znaków
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        return text.strip()
    
    def _generate_generic_illustration(self, style):
        """Generuje ogólną ilustrację gdy główny prompt jest zablokowany"""
        generic_prompts = [
            f"A beautiful {style.lower()} landscape with trees and sky",
            f"An artistic {style.lower()} scene with nature and light",
            f"A peaceful {style.lower()} illustration of a magical forest"
        ]
        
        for prompt in generic_prompts:
            try:
                response = self.client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size="1024x1024"
                )
                if response and response.data and response.data[0].b64_json:
                    image_bytes = base64.b64decode(response.data[0].b64_json)
                    return Image.open(io.BytesIO(image_bytes))
            except:
                continue
        
        return None
    
    def _generate_generic_cover(self, style):
        """Generuje ogólną okładkę gdy główny prompt jest zablokowany"""
        prompt = f"Beautiful book cover art in {style.lower()} style, magical and artistic"
        
        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )
            if response and response.data and response.data[0].b64_json:
                image_bytes = base64.b64decode(response.data[0].b64_json)
                return Image.open(io.BytesIO(image_bytes))
        except:
            pass
        
        return None