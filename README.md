📚 Fabryka Opowiadań
Aplikacja do tworzenia spersonalizowanych opowiadań z wykorzystaniem AI

Generuj unikalne historie z ilustracjami, okładkami i eksportuj je do PDF, EPUB lub audiobooka MP3!

Show Image
Show Image
Show Image

✨ Funkcje
📝 Generowanie opowiadań - wybierz parametry i stwórz unikalną historię
🎨 Ilustracje AI - automatyczne tworzenie obrazów w różnych stylach
📖 Okładki książkowe - profesjonalne okładki z tytułem i autorem
📄 Eksport do PDF - pięknie sformatowane dokumenty
📚 eBook (EPUB/MOBI) - gotowe do czytania na e-readerach
🎧 Audiobooki MP3 - synteza mowy z OpenAI TTS
✏️ Edycja i modyfikacja - poprawiaj i dostosuj opowiadanie
🚀 Instalacja
1. Sklonuj repozytorium
bash
git clone https://github.com/awilgaol1/fabryka-opowiadan.git

cd fabryka-opowiadan
2. Utwórz środowisko wirtualne
bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
3. Zainstaluj zależności
bash
pip install -r requirements.txt
4. Dodaj czcionkę DejaVuSans
Pobierz czcionkę DejaVuSans.ttf i umieść ją w folderze fonts/

🔑 Konfiguracja
Klucz API OpenAI
Aplikacja wymaga klucza API OpenAI. Możesz go uzyskać na platform.openai.com.

Opcja 1: Wprowadź w aplikacji

Uruchom aplikację i wpisz klucz w panelu bocznym
Opcja 2: Plik .env (opcjonalnie)

bash
cp .env.example .env
# Edytuj .env i dodaj swój klucz
OPENAI_API_KEY=sk-...
💻 Uruchomienie
bash
streamlit run app.py
Aplikacja otworzy się w przeglądarce pod adresem http://localhost:8501

📖 Jak używać
1. Tworzenie opowiadania
Podłącz klucz API OpenAI
Wybierz parametry (gatunek, grupa wiekowa, długość)
Dodaj bohaterów
Opcjonalnie: włącz generowanie ilustracji i okładki
Kliknij "Generuj opowiadanie"
2. Edycja
Wybierz tytuł z propozycji lub wpisz własny
Nałóż tytuł na okładkę
Edytuj tekst opowiadania
Generuj dodatkowe ilustracje dla fragmentów
3. Export
Wybierz ilustracje do PDF
Eksportuj do wybranego formatu:
📄 PDF
📚 EPUB/MOBI
🎧 MP3 (wymaga FFmpeg)
🎧 Audiobooki (opcjonalnie)
Generowanie audiobooków wymaga FFmpeg:

Windows
bash
# Pobierz FFmpeg z https://ffmpeg.org/
# Dodaj do PATH
macOS
bash
brew install ffmpeg
Linux
bash
sudo apt-get install ffmpeg
🛠️ Technologie
Streamlit - interfejs użytkownika
OpenAI GPT-4 - generowanie tekstu
DALL-E / GPT-Image - tworzenie ilustracji
OpenAI TTS - synteza mowy
ReportLab - generowanie PDF
EbookLib - tworzenie EPUB
Pillow - przetwarzanie obrazów
PyDub - edycja audio
📋 Wymagania systemowe
Python 3.8+
2GB RAM (4GB zalecane)
Klucz API OpenAI
FFmpeg (tylko dla audiobooków)
🐛 Znane problemy
"Moderation blocked" przy generowaniu obrazów
OpenAI może blokować niektóre prompty. Aplikacja automatycznie próbuje alternatywnych promptów. Jeśli problem się powtarza, użyj bardziej ogólnych opisów.

Brak FFmpeg na Streamlit Cloud
Audiobooki nie działają na Streamlit Cloud. Uruchom aplikację lokalnie lub na serwerze z FFmpeg.

🤝 Wkład w projekt
Zgłaszaj błędy i sugestie przez Issues

📧 Kontakt
Anna Wilga
Email: awilga.ol@wp.pl

📄 Licencja
MIT License - możesz swobodnie używać i modyfikować kod.

⭐ Podziękowania
Dziękuję za korzystanie z Fabryki Opowiadań! ✨

Jeśli projekt Ci się podoba, zostaw gwiazdkę ⭐ na GitHubie!

