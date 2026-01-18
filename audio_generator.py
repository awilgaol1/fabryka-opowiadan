from openai import OpenAI
import os
import tempfile
from pydub import AudioSegment

class AudioGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
    
    def create_audiobook(self, story_text, voice="alloy", speed=1.0, split_chapters=False):
        """Tworzy audiobook z opowiadania"""
        
        if split_chapters:
            return self._create_chapters_audiobook(story_text, voice, speed)
        else:
            return self._create_single_audiobook(story_text, voice, speed)
    
    def _create_single_audiobook(self, story_text, voice, speed):
        """Tworzy audiobook jako jeden plik MP3"""
        
        # OpenAI TTS ma limit długości tekstu, więc dzielimy na fragmenty
        max_chars = 4000
        text_chunks = self._split_text(story_text, max_chars)
        
        audio_segments = []
        
        for i, chunk in enumerate(text_chunks):
            try:
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=chunk,
                    speed=speed
                )
                
                # Zapisz fragment tymczasowo
                temp_file = os.path.join(tempfile.gettempdir(), f"audio_chunk_{i}.mp3")
                response.stream_to_file(temp_file)
                
                # Wczytaj fragment
                audio_segment = AudioSegment.from_mp3(temp_file)
                audio_segments.append(audio_segment)
                
                # Usuń tymczasowy plik
                os.remove(temp_file)
                
            except Exception as e:
                raise Exception(f"Błąd podczas generowania audio: {str(e)}")
        
        # Połącz wszystkie fragmenty
        combined = audio_segments[0]
        for segment in audio_segments[1:]:
            combined += segment
        
        # Zapisz finalny plik
        output_path = os.path.join(tempfile.gettempdir(), "audiobook.mp3")
        combined.export(output_path, format="mp3")
        
        return output_path
    
    def _create_chapters_audiobook(self, story_text, voice, speed):
        """Tworzy audiobook podzielony na rozdziały (zwraca ZIP)"""
        
        # Dzielimy tekst na rozdziały (po podwójnych enterach lub większych fragmentach)
        chapters = self._split_into_chapters(story_text)
        
        chapter_files = []
        
        for i, chapter in enumerate(chapters):
            try:
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=chapter,
                    speed=speed
                )
                
                # Zapisz rozdział
                chapter_file = os.path.join(tempfile.gettempdir(), f"rozdzial_{i+1}.mp3")
                response.stream_to_file(chapter_file)
                chapter_files.append(chapter_file)
                
            except Exception as e:
                raise Exception(f"Błąd podczas generowania rozdziału {i+1}: {str(e)}")
        
        # Połącz rozdziały w jeden plik (można też zwrócić ZIP)
        # Na potrzeby uproszczenia zwrócimy pierwszy plik
        # W pełnej implementacji można stworzyć ZIP z wszystkimi rozdziałami
        
        if chapter_files:
            # Połącz wszystkie rozdziały
            audio_segments = [AudioSegment.from_mp3(f) for f in chapter_files]
            combined = audio_segments[0]
            for segment in audio_segments[1:]:
                combined += AudioSegment.silent(duration=1000)  # 1s ciszy między rozdziałami
                combined += segment
            
            output_path = os.path.join(tempfile.gettempdir(), "audiobook_rozdzialy.mp3")
            combined.export(output_path, format="mp3")
            
            # Usuń tymczasowe pliki
            for f in chapter_files:
                if os.path.exists(f):
                    os.remove(f)
            
            return output_path
        
        return None
    
    def _split_text(self, text, max_chars=4000):
        """Dzieli tekst na mniejsze fragmenty"""
        
        chunks = []
        current_chunk = ""
        
        # Dziel po zdaniach
        sentences = text.replace('\n', ' ').split('. ')
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_into_chapters(self, text, target_chapter_length=2000):
        """Dzieli tekst na rozdziały"""
        
        # Próbujemy dzielić po podwójnych enterach (akapitach)
        paragraphs = text.split('\n\n')
        
        chapters = []
        current_chapter = ""
        
        for para in paragraphs:
            if len(current_chapter) + len(para) < target_chapter_length:
                current_chapter += para + "\n\n"
            else:
                if current_chapter:
                    chapters.append(current_chapter.strip())
                current_chapter = para + "\n\n"
        
        if current_chapter:
            chapters.append(current_chapter.strip())
        
        return chapters if chapters else [text]