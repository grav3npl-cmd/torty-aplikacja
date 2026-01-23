import streamlit as st
import json
import os
import pandas as pd
from datetime import date
from PIL import Image

# --- KONFIGURACJA ---
DB_FILE = 'baza_cukierni_v5.json'
IMG_FOLDER = 'zdjecia_tortow'
LOGO_FILE = "logo_wk_torty.png" 
ILUSTRACJA_FILE = "ilustracja_ksiazka.png"

# Upewniamy się, że folder na zdjęcia istnieje
os.makedirs(IMG_FOLDER, exist_ok=True)

# --- FUNKCJE ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "skladniki": {
                "Mąka pszenna": {"cena": 3.50, "waga_opakowania": 1000},
                "Cukier": {"cena": 4.00, "waga_opakowania": 1000},
                "Masło": {"cena": 7.50, "waga_opakowania": 200},
                "Jajka (szt)": {"cena": 1.20, "waga_opakowania": 1}
            },
            "przepisy": [],
            "kalendarz": []
        }
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for p in data["przepisy"]:
            if "zdjecie" in p and isinstance(p["zdjecie"], str) and p["zdjecie"]:
                p["zdjecia"] = [p["zdjecie"]]
                del p["zdjecie"]
            elif "zdjecia" not in p:
                p["zdjecia"] = []
        return data

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_uploaded_files(uploaded_files):
    saved_paths = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(IMG_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(file_path)
    return saved_paths

# --- WYGLĄD (CSS - STYL PREMIUM) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* UKRYWANIE ELEMENTÓW SYSTEMOWYCH */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* KOLORYSTYKA GŁÓWNA */
        .stApp { background-color: #121212; color: #ffffff; }
        section[data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }
        
        /* KAFELKI (CONTAINERY) */
        div[data-testid="column"] {
            background-color: #1e1e1e;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid #333;
            transition: transform 0.2s;
        }
        div[data-testid="column"]:hover {
            border-color: #ff0aef;
            transform: translateY(-2px);
        }

        /* PRZYCISKI - NEON PINK */
        .stButton > button { 
            background-color: transparent; 
            color: #ff0aef; 
            border: 2px solid #ff0aef; 
            border-radius: 25px; 
            font-weight: bold;
            width: 100%;
            transition: 0.3s;
        }
        .stButton > button:hover { 
            background-color: #ff0aef; 
            color: white;
            box-shadow: 0 0 15px rgba(255, 10, 239, 0.5);
        }
        
        /* INPUTY */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stNumberInput > div > div > input { 
            background-color: #2c2c2c !important; 
            color: white !important; 
            border: none !important; 
            border-radius: 8px;
        }

        /* NAGŁÓWEK Z LOGO */
        .header-box {
            text-align: center;
            padding: 20px;
            margin-bottom: 30px;
            border-bottom: 2px solid #ff0aef;
            background: linear-gradient(180deg, rgba(255,10,239,0.1) 0%, rgba(18,18,18,0) 100%);
        }
        .header-title {
            font-size: 2.5rem;
            font-weight: 900;
            color: #ff0aef;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(255,10,239,0.6);
        }
        
        /* KALENDARZ - KARTY */
        .task-card {
            background-color: #252525;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 5px solid #ff0aef;
            border-radius: 8px;
        }
        .task-done { border-left: 5px solid #00ff00; opacity: 0.6; }
        
        /* Obrazki w kafelkach */
        img { border-radius: 10px; object-fit: cover; width: 100%; }

    </style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA ---
if 'temp_skladniki' not in st.session_state:
    st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state:
    st.session_state['show_add_order'] = False

data = load_data()

# --- HEADER (NA KAŻDEJ STRONIE) ---
st.markdown(f"""
    <div class="header-box">
        <div class="header-title">WK TORTY</div>
        <div style="color: #ccc; letter-spacing: 1px;">PROFESSIONAL BAKERY ASSISTANT</div>
    </div>
""", unsafe_allow_html=True)

# --- MENU (TOP BAR zamiast Sidebar dla wygody na mobile) ---
# Używamy kolumn jako menu na górze
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1: 
    if st.button("📅 Kalendarz"): st.session_state['menu'] = "Kalendarz"
with col_m2: 
    if st.button("📖 Przepisy"): st.session_state['menu'] = "Przepisy"
with col_m3: 
    if st.button("➕ Nowy"): st.session_state['menu'] = "Dodaj"
with col_m4: 
    if st.button("📦 Magazyn"): st.session_state['menu'] = "Magazyn"

# Domyślne menu
if 'menu' not in st.session_state:
    st.session_state['menu'] = "Kalendarz"

menu = st.session_state['menu']
st.write("---")

# ==========================================
# 1. KALENDARZ (DESIGN KART)
# ==========================================
if menu == "Kalendarz":
    st.subheader("📅 Twoje Zlecenia")
    
    # Przycisk dodawania
    if st.button("➕ Dodaj nowe zamówienie", type="primary"):
        st.session_state['show_add_order'] = not st.session_state['show_add_order']

    if st.session_state['show_add_order']:
        with st.container():
            st.info("Wypełnij szczegóły zamówienia")
            with st.form("kalendarz_form"):
                col_k1, col_k2 = st.columns(2)
                with col_k1: data_zamowienia = st.date_input("Data odbioru", value=date.today())
                with col_k2: klient = st.text_input("Klient")
                opis_tortu = st.text_area("Szczegóły (Smak, napis, dekoracja)")
                
                if st.form_submit_button("Zapisz Zlecenie"):
                    nowy_wpis = {"data": str(data_zamowienia), "klient": klient, "opis": opis_tortu, "wykonane": False}
                    data["kalendarz"].append(nowy_wpis)
                    data["kalendarz"] = sorted(data["kalendarz"], key=lambda x: x['data'])
                    save_data(data)
                    st.session_state['show_add_order'] = False
                    st.rerun()
    
    st.write("") # Odstęp

    if not data["kalendarz"]:
        st.info("Kalendarz jest pusty. Odpoczywaj! 🏖️")
    else:
        # Wyświetlanie jako karty
        for i, wpis in enumerate(data["kalendarz"]):
            styl_klasy = "task-card task-done" if wpis.get("wykonane") else "task-card"
            status_icon = "✅ WYKONANE" if wpis.get("wykonane") else "⏳ W TRAKCIE"
            
            # HTML Karty
            st.markdown(f"""
            <div class="{styl_klasy}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:white;">{wpis['klient']}</h3>
                    <span style="background:#333; padding:5px 10px; border-radius:10px; font-size:0.8em;">{wpis['data']}</span>
                </div>
                <p style="color:#bbb; margin-top:5px;">{wpis['opis']}</p>
                <div style="font-size:0.8em; font-weight:bold; color:#ff0aef; margin-top:10px;">{status_icon}</div>
            </div>
            """, unsafe_allow_html=True)

            # Przyciski akcji pod kartą
            c1, c2, c3 = st.columns([1, 1, 3])
            if not wpis.get("wykonane"):
                if c1.button("Gotowe", key=f"done_{i}"):
                    data["kalendarz"][i]["wykonane"] = True
                    save_data(data)
                    st.rerun()
            if c2.button("Usuń", key=f"del_{i}"):
                data["kalendarz"].pop(i)
                save_data(data)
                st.rerun()

# ==========================================
# 2. MAGAZYN
# ==========================================
elif menu == "Magazyn":
    st.subheader("📦 Stan Magazynu")
    
    if data["skladniki"]:
        # Tabela stylizowana
        df = pd.DataFrame.from_dict(data["skladniki"], orient='index')
        df.reset_index(inplace=True)
        df.columns = ["Składnik", "Cena", "Waga (g/szt)"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.write("---")
    st.caption("Dodaj nowy produkt do bazy")
    
    with st.form("magazyn_add"):
        c1, c2, c3 = st.columns(3)
        with c1: new_name = st.text_input("Nazwa")
        with c2: new_price = st.number_input("Cena (PLN)", min_value=0.01)
        with c3: new_weight = st.number_input("Waga (g/szt)", min_value=1)
        
        if st.form_submit_button("Dodaj do Magazynu"):
            if new_name:
                data["skladniki"][new_name] = {"cena": new_price, "waga_opakowania": new_weight}
                save_data(data)
                st.success(f"Dodano: {new_name}")
                st.rerun()

# ==========================================
# 3. DODAJ PRZEPIS
# ==========================================
elif menu == "Dodaj":
    st.subheader("🍰 Kreator Przepisu")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 1. Składniki")
        with st.form("skladniki_form"):
            wybran = st.selectbox("Wybierz", list(data["skladniki"].keys()))
            ilo = st.number_input("Ilość", min_value=0.0)
            if st.form_submit_button("Dodaj"):
                st.session_state['temp_skladniki'][wybran] = ilo
                st.rerun()
        
        # Lista dodanych
        if st.session_state['temp_skladniki']:
            st.write("---")
            for k, v in st.session_state['temp_skladniki'].items():
                cc1, cc2 = st.columns([3,1])
                cc1.write(f"**{k}**: {v}")
                if cc2.button("X", key=f"del_{k}"):
                    del st.session_state['temp_skladniki'][k]
                    st.rerun()

    with col_right:
        st.markdown("### 2. Szczegóły")
        with st.form("glowny_przepis_form"):
            nazwa_przepisu = st.text_input("Nazwa Tortu")
            opis = st.text_area("Instrukcja (Każdy krok w nowej linii)", height=150)
            uploaded_files = st.file_uploader("Zdjęcia", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
            srednica = st.number_input("Średnica bazy (cm)", value=20)
            
            st.write("Oceny:")
            oc1, oc2, oc3 = st.columns(3)
            with oc1: s_look = st.slider("Wygląd", 1, 5, 5)
            with oc2: s_taste = st.slider("Smak", 1, 5, 5)
            with oc3: s_diff = st.slider("Trudność", 1, 5, 3)
            
            if st.form_submit_button("ZAPISZ PRZEPIS"):
                if not nazwa_przepisu or not st.session_state['temp_skladniki']:
                    st.error("Brakuje nazwy lub składników!")
                else:
                    saved_imgs = save_uploaded_files(uploaded_files)
                    nowy = {
                        "nazwa": nazwa_przepisu,
                        "opis": opis,
                        "zdjecia": saved_imgs,
                        "srednica": srednica,
                        "skladniki_przepisu": st.session_state['temp_skladniki'],
                        "oceny": {"wyglad": s_look, "smak": s_taste, "trudnosc": s_diff}
                    }
                    data["przepisy"].append(nowy)
                    save_data(data)
                    st.session_state['temp_skladniki'] = {}
                    st.success("Gotowe!")
                    st.rerun()

# ==========================================
# 4. KSIĄŻKA PRZEPISÓW (GRID/KAFELKI)
# ==========================================
elif menu == "Przepisy":
    st.subheader("📖 Książka Kucharska")
    search = st.text_input("🔍 Znajdź przepis...", placeholder="Wpisz nazwę tortu...")
    st.write("") 

    # Filtrowanie
    przepisy_do_pokazania = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
    
    if not przepisy_do_pokazania:
        st.warning("Nie znaleziono przepisów.")
    else:
        # UKŁAD KAFELKOWY (GRID) - 3 Kolumny
        cols = st.columns(3) 
        
        for index, przepis in enumerate(przepisy_do_pokazania):
            # Wybieramy kolumnę (0, 1 lub 2)
            with cols[index % 3]:
                # --- POCZĄTEK KAFELKA ---
                
                # Zdjęcie na górze kafelka
                imgs = przepis.get("zdjecia", [])
                if imgs and os.path.exists(imgs[0]):
                    st.image(imgs[0], use_container_width=True)
                else:
                    st.markdown(f'<div style="height:150px; background:#333; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#555;">BRAK ZDJĘCIA</div>', unsafe_allow_html=True)
                
                # Tytuł i Oceny
                st.markdown(f"<h3 style='text-align:center; color:#ff0aef; margin-bottom:0;'>{przepis['nazwa']}</h3>", unsafe_allow_html=True)
                oceny = przepis.get("oceny", {"wyglad":5})
                st.caption(f"⭐ {oceny['wyglad']}/5 | Poziom: {oceny.get('trudnosc', 3)}/5")
                
                # Przycisk "Otwórz" (Expandery działają słabo w kolumnach, używamy toggle)
                if st.toggle("Pokaż szczegóły", key=f"tog_{index}"):
                    
                    # --- WNĘTRZE KAFELKA PO ROZWINIĘCIU ---
                    
                    # Tryb Live
                    live_mode = st.checkbox("Tryb Live 👩‍🍳", key=f"live_{index}")
                    
                    # Kalkulator
                    baza_cm = przepis.get('srednica', 20)
                    target_cm = st.number_input("Średnica (cm):", value=baza_cm, key=f"dim_{index}")
                    wsp = (target_cm / baza_cm) ** 2
                    
                    st.markdown("#### Składniki:")
                    koszt_total = 0
                    for sk, il in przepis["skladniki_przepisu"].items():
                        il_skal = il * wsp
                        
                        # Pobieranie ceny
                        cena_txt = ""
                        if sk in data["skladniki"]:
                            c = data["skladniki"][sk]["cena"] / data["skladniki"][sk]["waga_opakowania"]
                            koszt = c * il_skal
                            koszt_total += koszt
                            cena_txt = f"({koszt:.2f} zł)"
                        
                        if live_mode:
                            st.checkbox(f"{sk}: **{il_skal:.1f}** {cena_txt}", key=f"chk_{index}_{sk}")
                        else:
                            st.write(f"• {sk}: **{il_skal:.1f}** {cena_txt}")
                    
                    if not live_mode:
                        st.markdown(f"**Koszt wsadu: {koszt_total:.2f} zł**")
                        st.write("---")
                        st.markdown("**Instrukcja:**")
                        st.write(przepis['opis'])
                    else:
                        st.markdown("#### Kroki:")
                        kroki = przepis['opis'].split('\n')
                        for kid, krok in enumerate(kroki):
                            if krok.strip():
                                st.checkbox(krok, key=f"step_{index}_{kid}")
