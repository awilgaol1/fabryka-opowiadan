📚 Fabryka Opowiadań
Aplikacja do generowania opowiadań z wykorzystaniem sztucznej inteligencji (OpenAI GPT-4 i DALL-E).

🌟 Funkcje
✍️ Generowanie opowiadań w różnych gatunkach i stylach
🎨 Tworzenie ilustracji przez DALL-E
📖 Generowanie okładek książek
📝 Edytor z możliwością modyfikacji tekstu
📄 Eksport do PDF
📚 Eksport do eBook (EPUB/MOBI)
🎧 Generowanie audiobooka (MP3) z wyborem głosu
👥 Możliwość definiowania bohaterów i ich charakterów
🎭 Wybór gatunku, miejsca akcji i typu zakończenia
🚀 Instalacja i uruchomienie lokalne
1. Wymagania wstępne
Python 3.10 lub nowszy
Konto OpenAI z aktywnym API key
Conda lub venv
2. Klonowanie repozytorium
bash
git clone https://github.com/TWOJA_NAZWA/fabryka-opowiadan.git
cd fabryka-opowiadan
3. Tworzenie środowiska wirtualnego
Opcja A: Conda (zalecane)

bash
conda create -n fabryka-opowiadan python=3.11 -y
conda activate fabryka-opowiadan
Opcja B: venv

bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
4. Instalacja zależności
bash
pip install -r requirements.txt
5. Uruchomienie aplikacji
bash
streamlit run app.py
Aplikacja otworzy się w przeglądarce pod adresem http://localhost:8501

🌐 Deployment na Streamlit Cloud
Krok 1: Przygotowanie repozytorium GitHub
Stwórz nowe repozytorium na GitHub
Dodaj wszystkie pliki:
bash
git init
git add .
git commit -m "Initial commit - Fabryka Opowiadań"
git branch -M main
git remote add origin https://github.com/TWOJA_NAZWA/fabryka-opowiadan.git
git push -u origin main
Krok 2: Deployment na Streamlit Cloud
Wejdź na https://share.streamlit.io/
Zaloguj się przez GitHub
Kliknij "New app"
Wybierz:
Repository: fabryka-opowiadan
Branch: main
Main file path: app.py
Kliknij "Deploy"
Krok 3: Konfiguracja Secrets (OpenAI API Key)
Możesz dodać swój klucz API jako secret:

W Streamlit Cloud kliknij "Settings" → "Secrets"
Dodaj:
toml
OPENAI_API_KEY = "sk-twoj-klucz-api"
📖 Jak używać aplikacji
1. Połączenie z OpenAI API
W panelu bocznym wprowadź swój klucz API OpenAI
Kliknij "Połącz z API"
2. Wybór parametrów
Wybierz model GPT (GPT-4o-mini lub GPT-4o)
Ustaw długość opowiadania (1500-3500 słów)
Wybierz grupę wiekową i gatunek
Określ miejsce akcji i typ zakończenia
3. Dodaj bohaterów
Podaj głównego bohatera (imię + opis)
Dodaj dodatkowych bohaterów z określeniem charakteru
4. Ilustracje i okładka
Zaznacz czy chcesz ilustracje i ile
Wybierz styl ilustracji
Dodaj szkic okładki i opis
5. Generowanie
Kliknij "Generuj opowiadanie"
Poczekaj na wygenerowanie treści
6. Edycja i eksport
Edytuj tekst w zakładce "Edycja i Export"
Generuj ilustracje dla wybranych fragmentów
Eksportuj do PDF, EPUB/MOBI lub audiobooka MP3
🛠️ Technologie
Streamlit - framework do tworzenia aplikacji webowych
OpenAI GPT-4 - generowanie treści opowiadań
DALL-E 3 - tworzenie ilustracji
OpenAI TTS - synteza mowy (audiobook)
FPDF2 - generowanie PDF
ebooklib - tworzenie eBook
Pillow - przetwarzanie obrazów
Pydub - edycja audio
⚠️ Uwagi
Koszty OpenAI API
Korzystanie z aplikacji wiąże się z kosztami OpenAI API:

GPT-4o: ~$0.005 / 1K tokens
GPT-4o-mini: ~$0.00015 / 1K tokens
DALL-E 3: ~$0.040 / obraz (1024x1024)
TTS: ~$0.015 / 1K znaków
Limity
Długość opowiadania: maksymalnie 3500 słów (ze względu na limity API)
Ilustracje: maksymalnie 10 na opowiadanie
Audiobook: maksymalnie ~10,000 znaków na fragment
📝 Licencja
MIT License - możesz swobodnie używać i modyfikować kod.

👤 Autorka
Anna Wilga

Email: awilga.ol@wp.pl

Jeśli masz pytania, pomysły lub zauważysz błędy - skontaktuj się ze mną!

🤝 Wkład w projekt
Pull requesty są mile widziane! W przypadku większych zmian, najpierw otwórz issue, aby omówić zmiany.

📋 TODO / Przyszłe funkcje
 Dodanie więcej stylów ilustracji
 Eksport do innych formatów (DOCX, TXT)
 Możliwość zapisu i wczytywania projektów
 Historia wygenerowanych opowiadań
 Udostępnianie opowiadań (link publiczny)
 Wsparcie dla innych języków
Stworzone z ❤️ przez Anna Wilga

