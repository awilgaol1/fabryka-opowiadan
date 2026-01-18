from openai import OpenAI
import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

class StoryGenerator:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_story(self, params):
        """Generuje opowiadanie na podstawie podanych parametrów"""
        
        # Tworzenie promptu
        prompt = self._create_story_prompt(params)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Jesteś utalentowanym pisarzem opowiadań. Tworzysz kreatywne, wciągające historie dostosowane do grupy wiekowej i gatunku. Piszesz w języku polskim."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=4000
            )
            
            story = response.choices[0].message.content
            return story
            
        except Exception as e:
            raise Exception(f"Błąd podczas generowania opowiadania: {str(e)}")
    
    def _create_story_prompt(self, params):
        """Tworzy szczegółowy prompt dla GPT"""
        
        characters_text = f"Główny bohater: {params['main_character']}\n"
        
        if params['additional_characters']:
            characters_text += "Dodatkowi bohaterowie:\n"
            for char in params['additional_characters']:
                characters_text += f"- {char['name']} (charakter: {char['type']})\n"
        
        location_text = params['location']
        if location_text == "Losowy wybór AI":
            location_text = "Wybierz ciekawe miejsce akcji samodzielnie"
        
        prompt = f"""
Napisz opowiadanie o długości około {params['word_count']} słów z następującymi parametrami:

GRUPA WIEKOWA: {params['age_group']}
GATUNEK: {params['genre']}
MIEJSCE AKCJI: {location_text}
ZAKOŃCZENIE: {params['ending_type']}, {params['ending_mood']}

BOHATEROWIE:
{characters_text}

WYMAGANIA:
- Opowiadanie powinno być wciągające i odpowiednie dla grupy wiekowej
- Stosuj żywy, obrazowy język
- Dodaj dialogi między bohaterami
- Zadbaj o odpowiedni rytm narracji
- Zakończenie powinno być {params['ending_mood'].lower()} i {params['ending_type'].lower()}
- Podziel tekst na naturalne akapity
- Jeśli to opowiadanie dla dzieci, używaj prostego języka i pozytywnych wartości
- Jeśli to horror lub dramat, buduj napięcie stopniowo

Napisz samą historię bez dodatkowych komentarzy.
"""
        return prompt
    
    def modify_story(self, original_story, new_style=None, new_plot=None):
        """Modyfikuje istniejące opowiadanie"""
        
        modifications = []
        if new_style:
            modifications.append(f"Zmień styl na: {new_style}")
        if new_plot:
            modifications.append(f"Wprowadź zmianę w fabule: {new_plot}")
        
        modification_text = "\n".join(modifications)
        
        prompt = f"""
Masz następujące opowiadanie:

{original_story}

Wprowadź następujące modyfikacje:
{modification_text}

Zachowaj ogólną strukturę i długość opowiadania, ale dostosuj je zgodnie z wytycznymi.
Zwróć tylko zmodyfikowane opowiadanie bez dodatkowych komentarzy.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Jesteś redaktorem literackim. Modyfikujesz opowiadania zgodnie z wytycznymi, zachowując ich klimat i jakość."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            modified_story = response.choices[0].message.content
            return modified_story
            
        except Exception as e:
            raise Exception(f"Błąd podczas modyfikacji opowiadania: {str(e)}")
    
    def generate_illustration(self, text_fragment, style):
        """Generuje ilustrację dla fragmentu tekstu"""
        
        style_prompts = {
            "Naturalne": "realistic, natural style, detailed, photorealistic",
            "Komiks": "comic book style, vibrant colors, bold lines, cartoon",
            "Akwarela": "watercolor painting style, soft colors, artistic, flowing",
            "Pixel Art": "pixel art style, 8-bit, retro gaming aesthetic"
        }
        
        style_prompt = style_prompts.get(style, style_prompts["Naturalne"])
        
        prompt = f"""
Create an illustration for this story fragment: {text_fragment[:500]}

Style: {style_prompt}
Make it family-friendly, engaging, and visually appealing.
"""
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Pobierz obraz
            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))
            
            return img
            
        except Exception as e:
            raise Exception(f"Błąd podczas generowania ilustracji: {str(e)}")
    
    def generate_title_suggestions(self, story_text):
        """Generuje 3 propozycje tytułów na podstawie opowiadania"""
        
        prompt = f"""
Na podstawie poniższego opowiadania zaproponuj 3 krótkie, chwytliwe tytuły (maksymalnie 4-5 słów każdy).
Tytuły powinny być intrygujące i oddawać klimat historii.

Opowiadanie (fragment):
{story_text[:1000]}

Zwróć TYLKO 3 tytuły, każdy w nowej linii, bez numeracji i dodatkowych komentarzy.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Jesteś ekspertem od tworzenia chwytliwych tytułów książek."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=200
            )
            
            titles = response.choices[0].message.content.strip().split('\n')
            # Oczyść tytuły z ewentualnych znaków specjalnych
            titles = [t.strip().strip('-').strip() for t in titles if t.strip()]
            
            return titles[:3]  # Zwróć dokładnie 3 tytuły
            
        except Exception as e:
            # Fallback - domyślne tytuły
            return ["Niezwykła Przygoda", "Tajemnicza Historia", "Magiczne Opowiadanie"]
    
    def generate_cover(self, sketch, description, style):
        """Generuje okładkę książki"""
        
        style_prompts = {
            "Naturalne": "realistic, professional book cover, detailed",
            "Komiks": "comic book cover style, vibrant, eye-catching",
            "Akwarela": "watercolor book cover, artistic, elegant",
            "Pixel Art": "pixel art book cover, retro, charming"
        }
        
        style_prompt = style_prompts.get(style, style_prompts["Naturalne"])
        
        prompt = f"""
Create a book cover illustration with these elements:
{sketch}

Description: {description}

Style: {style_prompt}
Make it look like a professional book cover - attractive, centered composition, space for title text at the top.
Leave empty space at the top for the title text overlay.
Family-friendly and engaging.
"""
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # Format książki
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Pobierz obraz
            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))
            
            return img
            
        except Exception as e:
            raise Exception(f"Błąd podczas generowania okładki: {str(e)}")
    
    def add_title_to_cover(self, cover_image, title, author_name):
        """Nakłada tytuł i autora na okładkę"""
        
        # Skopiuj obraz żeby nie modyfikować oryginału
        img = cover_image.copy()
        draw = ImageDraw.Draw(img)
        
        # Rozmiary okładki
        width, height = img.size
        
        # Próbuj użyć różnych czcionek (fallback jeśli nie ma)
        try:
            # Spróbuj załadować czcionkę systemową
            title_font = ImageFont.truetype("arial.ttf", size=int(width * 0.08))
            author_font = ImageFont.truetype("arial.ttf", size=int(width * 0.05))
        except:
            try:
                # Fallback - czcionka domyślna
                title_font = ImageFont.load_default()
                author_font = ImageFont.load_default()
            except:
                title_font = None
                author_font = None
        
        # Dodaj półprzezroczyste tło pod tytuł
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Prostokąt pod tytuł (górna część)
        overlay_draw.rectangle(
            [(0, height * 0.05), (width, height * 0.25)],
            fill=(0, 0, 0, 180)  # Czarne, półprzezroczyste
        )
        
        # Prostokąt pod autora (dolna część)
        overlay_draw.rectangle(
            [(0, height * 0.85), (width, height * 0.95)],
            fill=(0, 0, 0, 180)
        )
        
        # Złącz overlay z obrazem
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img)
        
        # Podziel tytuł na linie jeśli jest długi
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if title_font:
                bbox = draw.textbbox((0, 0), test_line, font=title_font)
                if bbox[2] - bbox[0] > width * 0.85:
                    current_line.pop()
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Narysuj tytuł (wyśrodkowany)
        y_offset = int(height * 0.10)
        for line in lines:
            if title_font:
                bbox = draw.textbbox((0, 0), line, font=title_font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(line) * 10
            
            x = (width - text_width) / 2
            
            # Biały tekst z czarną obwódką
            outline_range = 3
            for adj_x in range(-outline_range, outline_range + 1):
                for adj_y in range(-outline_range, outline_range + 1):
                    draw.text((x + adj_x, y_offset + adj_y), line, font=title_font, fill=(0, 0, 0))
            
            draw.text((x, y_offset), line, font=title_font, fill=(255, 255, 255))
            y_offset += int(height * 0.08)
        
        # Narysuj autora (na dole)
        author_text = f"Autor: {author_name}"
        if author_font:
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            author_width = bbox[2] - bbox[0]
        else:
            author_width = len(author_text) * 8
        
        x = (width - author_width) / 2
        y = int(height * 0.88)
        
        # Obwódka
        outline_range = 2
        for adj_x in range(-outline_range, outline_range + 1):
            for adj_y in range(-outline_range, outline_range + 1):
                draw.text((x + adj_x, y + adj_y), author_text, font=author_font, fill=(0, 0, 0))
        
        draw.text((x, y), author_text, font=author_font, fill=(255, 255, 255))
        
        # Konwertuj z powrotem do RGB
        return img.convert('RGB')