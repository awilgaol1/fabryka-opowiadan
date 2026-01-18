import re
from openai import OpenAI

# -----------------------------
# 1. WPROWADŹ KLUCZ API
# -----------------------------
API_KEY = input("Wklej swój klucz API: ").strip()

print("\n=== TEST 1: Sprawdzanie klucza API ===")

# Test 1A — czy klucz ma tylko ASCII?
if not all(ord(c) < 128 for c in API_KEY):
    print("❌ BŁĄD: Klucz API zawiera znak nie-ASCII!")
    print("To powoduje błąd UnicodeEncodeError przy generowaniu obrazów.")
    print("Wygeneruj NOWY klucz w panelu OpenAI.")
else:
    print("✅ Klucz API wygląda poprawnie (tylko ASCII).")

# Test 1B — czy klucz ma prawidłowy format?
if not re.match(r"^sk-[A-Za-z0-9\-_]{20,}$", API_KEY):
    print("⚠️ Ostrzeżenie: Klucz API wygląda nietypowo.")
else:
    print("✅ Format klucza API wygląda prawidłowo.")

# -----------------------------
# 2. TEST POŁĄCZENIA Z OPENAI
# -----------------------------
print("\n=== TEST 2: Połączenie z OpenAI ===")

try:
    client = OpenAI(api_key=API_KEY)
    models = client.models.list()
    print("✅ Połączenie z OpenAI działa.")
except Exception as e:
    print("❌ BŁĄD: Nie można połączyć się z OpenAI.")
    print(str(e))
    exit()

# -----------------------------
# 3. TEST GENEROWANIA TEKSTU
# -----------------------------
print("\n=== TEST 3: Generowanie tekstu ===")

try:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Napisz jedno zdanie testowe."}]
    )
    print("✅ Generowanie tekstu działa.")
    print("Odpowiedź:", resp.choices[0].message.content)
except Exception as e:
    print("❌ BŁĄD: Generowanie tekstu nie działa.")
    print(str(e))
    exit()

# -----------------------------
# 4. TEST GENEROWANIA OBRAZU
# -----------------------------
print("\n=== TEST 4: Generowanie obrazu (DALL·E 2) ===")

try:
    resp = client.images.generate(
        model="dall-e-2",
        prompt="A red apple",
        size="512x512"
    )

    if not resp or not resp.data or not resp.data[0].b64_json:
        print("❌ BŁĄD: Model nie zwrócił obrazu (b64_json = None).")
        print("➡️ To oznacza, że Twoje konto NIE MA dostępu do DALL·E 2.")
    else:
        print("✅ Generowanie obrazu działa (DALL·E 2).")

except Exception as e:
    print("❌ BŁĄD podczas generowania obrazu.")
    print(str(e))

print("\n=== DIAGNOSTYKA ZAKOŃCZONA ===")
