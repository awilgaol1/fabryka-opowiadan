import streamlit as st
import openai
from story_generator import StoryGenerator
from pdf_generator import PDFGenerator
from ebook_generator import EbookGenerator
import os

# Warunkowy import audiobooka (nie działa na Streamlit Cloud bez FFmpeg)
try:
    from audio_generator import AudioGenerator
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    st.warning("⚠️ Audiobook niedostępny na Streamlit Cloud (brak FFmpeg). Pobierz aplikację lokalnie aby używać tej funkcji.")

# Konfiguracja strony
st.set_page_config(
    page_title="Fabryka Opowiadań",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicjalizacja session_state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False
if 'story_text' not in st.session_state:
    st.session_state.story_text = ""
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'cover_image' not in st.session_state:
    st.session_state.cover_image = None
if 'cover_image_original' not in st.session_state:
    st.session_state.cover_image_original = None
if 'title_suggestions' not in st.session_state:
    st.session_state.title_suggestions = []
if 'selected_title' not in st.session_state:
    st.session_state.selected_title = ""
if 'author_name' not in st.session_state:
    st.session_state.author_name = "Anna Wilga"
if 'custom_title_input' not in st.session_state:
    st.session_state.custom_title_input = ""

# CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4ECDC4;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45B7AF;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
    }
    </style>
""", unsafe_allow_html=True)

# Nagłówek
st.markdown('<p class="main-header">📚 Fabryka Opowiadań 📚</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Ustawienia")
    
    # API Key
    st.subheader("🔑 OpenAI API")
    api_key_input = st.text_input("Klucz API", type="password", value=st.session_state.api_key)
    
    if st.button("🔗 Połącz z API"):
        if api_key_input:
            try:
                openai.api_key = api_key_input
                client = openai.OpenAI(api_key=api_key_input)
                client.models.list()
                st.session_state.api_key = api_key_input
                st.session_state.api_connected = True
                st.success("✅ Połączono z OpenAI API!")
            except Exception as e:
                st.error(f"❌ Błąd połączenia: {str(e)}")
                st.session_state.api_connected = False
        else:
            st.warning("⚠️ Wprowadź klucz API")
    
    if st.session_state.api_connected:
        st.markdown('<div class="success-box">✅ API Połączone</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Model GPT
    st.subheader("🤖 Model GPT")
    model = st.selectbox(
        "Wybierz model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0
    )
    
    # Długość opowiadania
    st.subheader("📏 Długość opowiadania")
    word_count = st.selectbox(
        "Liczba słów",
        [1500, 2000, 2500, 3000, 3500],
        index=1
    )
    
    st.divider()
    st.caption("💡 Wypełnij parametry i wygeneruj opowiadanie!")

# Zakładki
tab1, tab2, tab3 = st.tabs(["📝 Tworzenie", "🎨 Edycja i Export", "👤 O mnie"])

# -------------------------------
# TAB 1 — TWORZENIE OPOWIADANIA
# -------------------------------
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎭 Parametry opowiadania")
        
        age_group = st.selectbox("Grupa wiekowa", ["Dla dzieci", "Młodzieżowy", "Dla dorosłych"])
        genre = st.selectbox("Gatunek", ["Bajka/Baśń", "Fantasy", "Przygoda", "Komedia", "Horror", "Romans", "Sci-Fi", "Dramat"])
        location = st.radio("Miejsce akcji", ["Jedno miejsce", "Dwa miejsca", "Losowy wybór AI"])
        
        st.write("**Zakończenie:**")
        col_a, col_b = st.columns(2)
        with col_a:
            ending_type = st.selectbox("Typ", ["Z puentą", "Bez puenty"])
        with col_b:
            ending_mood = st.selectbox("Nastrój", ["Pozytywne", "Negatywne", "Otwarte"])
    
    with col2:
        st.subheader("👥 Bohaterowie")
        
        main_character = st.text_area(
            "Główny bohater (imię + krótki opis)",
            placeholder="np. Ania – odważna 10-letnia dziewczynka..."
        )
        
        num_characters = st.number_input("Liczba dodatkowych bohaterów", min_value=0, max_value=5, value=1)
        
        additional_characters = []
        for i in range(num_characters):
            st.write(f"**Bohater {i+1}:**")
            char_col1, char_col2 = st.columns([2, 1])
            with char_col1:
                char_name = st.text_input(f"Imię i opis", key=f"char_name_{i}")
            with char_col2:
                char_type = st.selectbox("Charakter", ["Pozytywny", "Negatywny"], key=f"char_type_{i}")
            if char_name:
                additional_characters.append({"name": char_name, "type": char_type})
    
    st.divider()

    # Ilustracje
    st.subheader("🎨 Ilustracje")
    col_ill1, col_ill2, col_ill3 = st.columns(3)
    
    with col_ill1:
        include_illustrations = st.checkbox("Dołącz ilustracje", value=True)
    
    with col_ill2:
        if include_illustrations:
            num_illustrations = st.number_input("Liczba ilustracji", min_value=1, max_value=10, value=3)
        else:
            num_illustrations = 0
    
    with col_ill3:
        if include_illustrations:
            illustration_style = st.selectbox("Styl ilustracji", ["Naturalne", "Komiks", "Akwarela", "Pixel Art"])
        else:
            illustration_style = "Naturalne"
    
    st.divider()

    # Okładka
    st.subheader("📖 Okładka książki")
    
    include_cover = st.checkbox("Generuj okładkę", value=True)
    
    if include_cover:
        col_cov1, col_cov2 = st.columns([2, 1])
        
        with col_cov1:
            cover_sketch = st.text_area("Szkic okładki", placeholder="np. Magiczny las...")
            cover_description = st.text_input("Krótki opis okładki", placeholder="np. Opowieść o odwadze...")
        
        with col_cov2:
            author_name = st.text_input("Autor", value=st.session_state.author_name)
            st.session_state.author_name = author_name
    else:
        cover_sketch = ""
        cover_description = ""
        author_name = st.text_input("Autor", value=st.session_state.author_name)
        st.session_state.author_name = author_name
    
    st.divider()

    # Przycisk generowania
    if st.button("🚀 Generuj opowiadanie", type="primary", use_container_width=True):
        if not st.session_state.api_connected:
            st.error("❌ Najpierw połącz się z API!")
        elif not main_character:
            st.error("❌ Podaj głównego bohatera!")
        else:
            with st.spinner("✨ Tworzę opowiadanie..."):
                try:
                    generator = StoryGenerator(st.session_state.api_key, model)
                    
                    params = {
                        "age_group": age_group,
                        "genre": genre,
                        "location": location,
                        "ending_type": ending_type,
                        "ending_mood": ending_mood,
                        "main_character": main_character,
                        "additional_characters": additional_characters,
                        "word_count": word_count,
                        "num_illustrations": num_illustrations,
                        "illustration_style": illustration_style,
                        "cover_sketch": cover_sketch,
                        "cover_description": cover_description,
                        "author_name": st.session_state.author_name
                    }
                    
                    story = generator.generate_story(params)
                    st.session_state.story_text = story
                    
                    st.info("📝 Generuję propozycje tytułów...")
                    titles = generator.generate_title_suggestions(story)
                    st.session_state.title_suggestions = titles
                    
                    if cover_sketch:
                        st.info("🎨 Tworzę okładkę...")
                        cover = generator.generate_cover(cover_sketch, cover_description, illustration_style)
                        if cover is None:
                            st.error("❌ Nie udało się wygenerować okładki. Spróbuj zmienić opis lub styl.")
                        else:
                            st.session_state.cover_image = cover
                            st.session_state.cover_image_original = cover.copy()
                    
                    st.success("✅ Opowiadanie wygenerowane!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Błąd: {str(e)}")

# -------------------------------
# TAB 2 — EDYCJA I EXPORT
# -------------------------------
with tab2:
    if st.session_state.story_text:

        # WYBÓR TYTUŁU - POPRAWIONA SEKCJA
        if st.session_state.title_suggestions:
            st.subheader("📖 Wybierz tytuł dla swojego opowiadania")
            
            col_t1, col_t2 = st.columns([3, 1])
            
            with col_t1:
                title_options = st.session_state.title_suggestions + ["Własny tytuł..."]

                # Radio button z zapamiętanym stanem
                selected = st.radio(
                    "Propozycje tytułów:",
                    title_options,
                    index=(
                        title_options.index(st.session_state.selected_title)
                        if st.session_state.selected_title in title_options
                        else 0
                    ),
                    key="title_radio"
                )

                # POPRAWIONA LOGIKA - używamy osobnego klucza dla własnego tytułu
                if selected == "Własny tytuł...":
                    custom_title = st.text_input(
                        "Wpisz własny tytuł:",
                        value=st.session_state.custom_title_input,
                        key="custom_title_field"
                    )
                    
                    # Zapisz do osobnego stanu
                    if custom_title != st.session_state.custom_title_input:
                        st.session_state.custom_title_input = custom_title
                    
                    # Ustaw jako selected_title tylko jeśli nie jest pusty
                    if custom_title.strip():
                        st.session_state.selected_title = custom_title.strip()
                    else:
                        st.session_state.selected_title = ""
                else:
                    # Wybrany jeden z sugerowanych tytułów
                    st.session_state.selected_title = selected
                    st.session_state.custom_title_input = ""  # Wyczyść pole własnego tytułu
            
            with col_t2:
                st.write(" ")
                st.write(" ")
                
                # Walidacja przed włączeniem przycisku
                can_apply = bool(st.session_state.selected_title and st.session_state.selected_title.strip())
                
                if st.button(
                    "✨ Nałóż tytuł na okładkę", 
                    use_container_width=True,
                    disabled=not can_apply
                ):
                    if st.session_state.cover_image_original is None:
                        st.error("⚠️ Najpierw wygeneruj okładkę w zakładce 'Tworzenie'!")
                    elif not st.session_state.selected_title:
                        st.error("⚠️ Wybierz lub wpisz tytuł!")
                    else:
                        with st.spinner("🎨 Nakładam tytuł..."):
                            try:
                                generator = StoryGenerator(st.session_state.api_key, model)

                                # KLUCZOWA POPRAWKA: ZAWSZE zaczynamy od czystej okładki
                                base_cover = st.session_state.cover_image_original.copy()

                                cover_with_title = generator.add_title_to_cover(
                                    base_cover,
                                    st.session_state.selected_title,
                                    st.session_state.author_name
                                )

                                st.session_state.cover_image = cover_with_title
                                st.success(f"✅ Tytuł '{st.session_state.selected_title}' dodany do okładki!")
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Błąd: {str(e)}")
                
                # Info jeśli tytuł pusty
                if not can_apply:
                    st.caption("⚠️ Wybierz lub wpisz tytuł")
            
            # Podgląd okładki
            st.divider()
            if st.session_state.cover_image is not None:
                st.image(st.session_state.cover_image, caption="Podgląd okładki", width=300)
            else:
                st.info("ℹ️ Okładka bez tytułu. Wygeneruj okładkę w zakładce 'Tworzenie'.")
            
            st.divider()

        # EDYCJA TEKSTU
        st.subheader("📝 Edycja opowiadania")
        
        edited_story = st.text_area(
            "Edytuj opowiadanie (możesz nanieść poprawki)",
            value=st.session_state.story_text,
            height=400
        )
        
        if st.button("💾 Zapisz zmiany"):
            st.session_state.story_text = edited_story
            st.success("✅ Zmiany zapisane!")
        
        st.divider()

        # MODYFIKACJA TEKSTU
        st.subheader("🔄 Modyfikuj opowiadanie")
        col_mod1, col_mod2 = st.columns(2)
        
        with col_mod1:
            new_style = st.text_input("Nowy styl (opcjonalnie)", placeholder="np. bardziej humorystyczny")
        
        with col_mod2:
            new_plot = st.text_input("Zmiana fabuły (opcjonalnie)", placeholder="np. dodaj zwrot akcji")
        
        if st.button("🎨 Zastosuj zmiany"):
            if new_style or new_plot:
                with st.spinner("🔄 Modyfikuję opowiadanie..."):
                    try:
                        generator = StoryGenerator(st.session_state.api_key, model)
                        modified_story = generator.modify_story(
                            st.session_state.story_text,
                            new_style,
                            new_plot
                        )
                        st.session_state.story_text = modified_story
                        st.success("✅ Opowiadanie zmodyfikowane!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Błąd: {str(e)}")
            else:
                st.warning("⚠️ Wprowadź przynajmniej jedną zmianę")
        
        st.divider()

        # GENEROWANIE ILUSTRACJI DO FRAGMENTU
        st.subheader("🖼️ Generuj ilustrację dla fragmentu")
        selected_fragment = st.text_area(
            "Zaznacz i wklej fragment opowiadania do zilustrowania",
            placeholder="Wklej tutaj fragment tekstu..."
        )
        
        fragment_style = st.selectbox(
            "Styl ilustracji dla fragmentu",
            ["Naturalne", "Komiks", "Akwarela", "Pixel Art"],
            key="fragment_style"
        )
        
        if st.button("🎨 Generuj ilustrację dla fragmentu"):
            if selected_fragment:
                with st.spinner("🎨 Tworzę ilustrację..."):
                    try:
                        generator = StoryGenerator(st.session_state.api_key, model)
                        image = generator.generate_illustration(selected_fragment, fragment_style)
                        if image is None:
                            st.error("❌ Nie udało się wygenerować ilustracji. Spróbuj zmienić fragment lub styl.")
                        else:
                            st.session_state.generated_images.append(image)
                            st.success("✅ Ilustracja wygenerowana!")
                            st.image(image, caption="Nowa ilustracja")
                    except Exception as e:
                        st.error(f"❌ Błąd: {str(e)}")
            else:
                st.warning("⚠️ Wklej fragment tekstu do zilustrowania")
        
        st.divider()

        # WYBÓR ILUSTRACJI DO PDF
        st.subheader("🖼️ Wybierz ilustracje do PDF")

        selected_illustrations = []
        if st.session_state.generated_images:
            cols = st.columns(3)

            for idx, img in enumerate(st.session_state.generated_images):
                with cols[idx % 3]:
                    if img is not None:
                        st.image(img, caption=f"Ilustracja {idx+1}", width=200)
                        use_it = st.checkbox(f"Użyj ilustracji {idx+1}", key=f"use_img_{idx}")
                        if use_it:
                            selected_illustrations.append(img)
                    else:
                        st.error(f"❌ Ilustracja {idx+1} nie została wygenerowana.")
        else:
            st.info("Brak ilustracji — wygeneruj je w zakładce Tworzenie lub powyżej.")

        st.divider()

        # EXPORT
        st.subheader("📥 Eksport")

        col_exp1, col_exp2, col_exp3 = st.columns(3)

        # --- PDF ---
        with col_exp1:
            if st.button("📄 Eksport do PDF", use_container_width=True):
                try:
                    pdf_gen = PDFGenerator()
                    pdf_file = pdf_gen.create_pdf(
                        st.session_state.story_text,
                        st.session_state.author_name,
                        st.session_state.cover_image,
                        selected_illustrations if selected_illustrations else None,
                        st.session_state.selected_title  # Przekazujemy tytuł
                    )
                    
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="⬇️ Pobierz PDF",
                            data=f,
                            file_name="opowiadanie.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"❌ Błąd: {str(e)}")

        # --- EBOOK ---
        with col_exp2:
            ebook_format = st.selectbox("Format eBook", ["EPUB", "MOBI"])
            if st.button(f"📚 Eksport do {ebook_format}", use_container_width=True):
                try:
                    ebook_gen = EbookGenerator()
                    ebook_file = ebook_gen.create_ebook(
                        st.session_state.story_text,
                        st.session_state.author_name,
                        ebook_format.lower(),
                        st.session_state.cover_image,
                        selected_illustrations if selected_illustrations else None
                    )
                    
                    with open(ebook_file, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Pobierz {ebook_format}",
                            data=f,
                            file_name=f"opowiadanie.{ebook_format.lower()}",
                            mime=f"application/{ebook_format.lower()}",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"❌ Błąd: {str(e)}")

        # --- AUDIOBOOK ---
        with col_exp3:
            if AUDIO_AVAILABLE:
                st.write("**Audiobook MP3**")
                voice = st.selectbox("Głos", ["alloy", "echo", "fable", "onyx", "nova"])
                speed = st.slider("Szybkość", 0.5, 2.0, 1.0, 0.1)
                audio_format = st.radio("Format", ["Jeden plik", "Rozdziały"])
                
                if st.button("🎧 Generuj audiobook", use_container_width=True):
                    with st.spinner("🎧 Tworzę audiobook..."):
                        try:
                            audio_gen = AudioGenerator(st.session_state.api_key)
                            audio_file = audio_gen.create_audiobook(
                                st.session_state.story_text,
                                voice,
                                speed,
                                audio_format == "Rozdziały"
                            )
                            
                            with open(audio_file, "rb") as f:
                                st.download_button(
                                    label="⬇️ Pobierz MP3",
                                    data=f,
                                    file_name="audiobook.mp3",
                                    mime="audio/mpeg",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"❌ Błąd: {str(e)}")
            else:
                st.info("🎧 Audiobook wymaga lokalnej instalacji FFmpeg.")

        # PODGLĄD WSZYSTKICH ILUSTRACJI
        if st.session_state.generated_images:
            st.divider()
            st.subheader("🖼️ Wszystkie wygenerowane ilustracje")
            cols = st.columns(3)
            for idx, img in enumerate(st.session_state.generated_images):
                with cols[idx % 3]:
                    if img is not None:
                        st.image(img, caption=f"Ilustracja {idx+1}")
                    else:
                        st.error(f"❌ Ilustracja {idx+1} nie została wygenerowana.")
    
    else:
        st.info("📝 Najpierw wygeneruj opowiadanie w zakładce 'Tworzenie'")

# -------------------------------
# TAB 3 — O AUTORCE
# -------------------------------
with tab3:
    st.subheader("👤 O autorce aplikacji")
    
    st.markdown("""
    ### Anna Wilga
    
    Tworzenie tej aplikacji to moja **pasja**!  
    Łączę technologię z kreatywnością, aby każdy mógł stworzyć własną, unikalną historię.
    
    Wierzę, że każdy ma w sobie opowieść wartą opowiedzenia,  
    a nowoczesne narzędzia AI mogą pomóc ją wypowiedzieć w sposób,  
    który wcześniej był niedostępny.
    
    ---
    
    ### 📧 Kontakt
    
    Jeśli zauważysz **błędy** lub masz **pomysły na usprawnienia**,  
    skontaktuj się ze mną!
    
    **Email:** awilga.ol@wp.pl
    
    ---
    
    *Dziękuję za korzystanie z Fabryki Opowiadań!* ✨
    """)
    
    st.divider()
    
    st.markdown("""
    ### 🛠️ Technologie użyte w projekcie:
    - **Streamlit** – interfejs użytkownika  
    - **OpenAI GPT-4** – generowanie treści  
    - **DALL·E / GPT-Image** – tworzenie ilustracji  
    - **OpenAI TTS** – synteza mowy  
    - **Python** – backend aplikacji  
    """)