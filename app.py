#/////////////////////////// 1. Importy i Konfiguracja ///////////////////////////
import streamlit as st
import json
import os
import pandas as pd
from datetime import date

DB_FILE = 'baza_cukierni_v14.json'
IMG_FOLDER = 'zdjecia_tortow'
DEFAULT_IMG = 'default_cake.png'

os.makedirs(IMG_FOLDER, exist_ok=True)

#/////////////////////////// 2. Funkcje pomocnicze ///////////////////////////
def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "skladniki": {
                # --- SKŁADNIKI (SPOŻYWCZE) ---
                "Jajko [szt]": {"cena": 1.20, "waga_opakowania": 1, "kcal": 155, "ikona": "🥚", "kategoria": "Składniki"},
                "Cukier drobny [g]": {"cena": 4.00, "waga_opakowania": 1000, "kcal": 387, "ikona": "🍬", "kategoria": "Składniki"},
                "Mąka pszenna [g]": {"cena": 3.50, "waga_opakowania": 1000, "kcal": 364, "ikona": "🌾", "kategoria": "Składniki"},
                "Mąka ziemniaczana [g]": {"cena": 5.00, "waga_opakowania": 500, "kcal": 348, "ikona": "🌾", "kategoria": "Składniki"},
                "Skrobia ziemniaczana [g]": {"cena": 4.50, "waga_opakowania": 500, "kcal": 348, "ikona": "🌾", "kategoria": "Składniki"},
                "Skrobia kukurydziana [g]": {"cena": 5.50, "waga_opakowania": 500, "kcal": 350, "ikona": "🌽", "kategoria": "Składniki"},
                "Kakao [g]": {"cena": 7.00, "waga_opakowania": 200, "kcal": 228, "ikona": "🍫", "kategoria": "Składniki"},
                "Masło [g]": {"cena": 7.50, "waga_opakowania": 200, "kcal": 717, "ikona": "🧈", "kategoria": "Składniki"},
                "Tłuszcz [g]": {"cena": 6.00, "waga_opakowania": 250, "kcal": 900, "ikona": "🧈", "kategoria": "Składniki"},
                "Olej [ml]": {"cena": 10.00, "waga_opakowania": 1000, "kcal": 884, "ikona": "🫗", "kategoria": "Składniki"},
                "Oliwa [ml]": {"cena": 30.00, "waga_opakowania": 500, "kcal": 884, "ikona": "🫒", "kategoria": "Składniki"},
                "Sól [g]": {"cena": 2.00, "waga_opakowania": 1000, "kcal": 0, "ikona": "🧂", "kategoria": "Składniki"},
                "Żelatyna [g]": {"cena": 5.00, "waga_opakowania": 50, "kcal": 338, "ikona": "🧬", "kategoria": "Składniki"},
                "Proszek do pieczenia [g]": {"cena": 1.50, "waga_opakowania": 30, "kcal": 100, "ikona": "🌬️", "kategoria": "Składniki"},
                "Śmietana 30% [ml]": {"cena": 8.50, "waga_opakowania": 500, "kcal": 292, "ikona": "🥛", "kategoria": "Składniki"},
                "Śmietana 36% [g]": {"cena": 9.50, "waga_opakowania": 500, "kcal": 340, "ikona": "🥛", "kategoria": "Składniki"},
                "Mascarpone [g]": {"cena": 11.00, "waga_opakowania": 250, "kcal": 394, "ikona": "🍦", "kategoria": "Składniki"},
                "Twaróg sernikowy [g]": {"cena": 15.00, "waga_opakowania": 1000, "kcal": 120, "ikona": "🍰", "kategoria": "Składniki"},
                "Mleko [ml]": {"cena": 4.00, "waga_opakowania": 1000, "kcal": 42, "ikona": "🥛", "kategoria": "Składniki"},
                "Czekolada biała [g]": {"cena": 6.00, "waga_opakowania": 100, "kcal": 539, "ikona": "⬜", "kategoria": "Składniki"},
                "Czekolada mleczna [g]": {"cena": 5.50, "waga_opakowania": 100, "kcal": 535, "ikona": "🟫", "kategoria": "Składniki"},
                "Czekolada gorzka 70% [g]": {"cena": 7.00, "waga_opakowania": 100, "kcal": 599, "ikona": "⬛", "kategoria": "Składniki"},
                "Pasta pistacjowa [g]": {"cena": 50.00, "waga_opakowania": 200, "kcal": 600, "ikona": "🟢", "kategoria": "Składniki"},
                "Pistacje obrane [g]": {"cena": 20.00, "waga_opakowania": 100, "kcal": 562, "ikona": "🥜", "kategoria": "Składniki"},
                "Prażynka francuska [g]": {"cena": 14.00, "waga_opakowania": 200, "kcal": 450, "ikona": "🥨", "kategoria": "Składniki"},
                "Ekstrakt z wanilii [ml]": {"cena": 25.00, "waga_opakowania": 50, "kcal": 288, "ikona": "🧪", "kategoria": "Składniki"},
                "Maliny świeże/mrożone [g]": {"cena": 15.00, "waga_opakowania": 250, "kcal": 52, "ikona": "🍓", "kategoria": "Składniki"},
                "Wiśnie mrożone [g]": {"cena": 12.00, "waga_opakowania": 500, "kcal": 50, "ikona": "🍒", "kategoria": "Składniki"},
                "Truskawki [g]": {"cena": 10.00, "waga_opakowania": 500, "kcal": 33, "ikona": "🍓", "kategoria": "Składniki"},
                "Mus z malin (frużelina) [g]": {"cena": 18.00, "waga_opakowania": 500, "kcal": 80, "ikona": "🍯", "kategoria": "Składniki"},
                "Cytryna [szt]": {"cena": 2.00, "waga_opakowania": 1, "kcal": 30, "ikona": "🍋", "kategoria": "Składniki"},
                "Orzechy laskowe [g]": {"cena": 12.00, "waga_opakowania": 100, "kcal": 628, "ikona": "🥜", "kategoria": "Składniki"},
                "Orzechy włoskie [g]": {"cena": 10.00, "waga_opakowania": 100, "kcal": 654, "ikona": "🥜", "kategoria": "Składniki"},

                # --- DODATKI ---
                "Barwnik spożywczy [szt]": {"cena": 12.00, "waga_opakowania": 1, "kcal": 0, "ikona": "🎨", "kategoria": "Dodatki"},
                "Podkład pod tort [szt]": {"cena": 5.00, "waga_opakowania": 1, "kcal": 0, "ikona": "💿", "kategoria": "Dodatki"},
                "Rum / Likier [ml]": {"cena": 40.00, "waga_opakowania": 500, "kcal": 230, "ikona": "🥃", "kategoria": "Dodatki"},

                # --- OPAKOWANIA ---
                "Pudełko na tort [szt]": {"cena": 6.00, "waga_opakowania": 1, "kcal": 0, "ikona": "📦", "kategoria": "Opakowania"}
            },
            "przepisy": [],
            "kalendarz": [],
            "galeria_extra": [] 
        }
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in data["skladniki"].items():
            if "kcal" not in v: v["kcal"] = 0
        if "galeria_extra" not in data: data["galeria_extra"] = []
        return data

# --- DODAJ TO W SEKCJI 2 ---

def dobierz_ikone(nazwa):
    """Automatycznie dobiera ikonę na podstawie nazwy produktu."""
    n = nazwa.lower()
    if "jaj" in n: return "🥚"
    if "mąk" in n or "skrob" in n: return "🌾"
    if "masł" in n or "tłuszcz" in n: return "🧈"
    if "olej" in n or "oliw" in n: return "🫗"
    if "cukier" in n: return "🍬"
    if "czekolada" in n: return "🍫"
    if "śmietan" in n or "mlek" in n: return "🥛"
    if "owoc" in n or "malin" in n or "trusk" in n or "wiśn" in n: return "🍓"
    if "pistac" in n or "orzech" in n: return "🥜"
    if "pudełk" in n or "karton" in n: return "📦"
    if "świecz" in n or "topper" in n: return "🕯️"
    if "sól" in n: return "🧂"
    if "kakao" in n: return "🍫"
    if "cytryn" in n: return "🍋"
    return "📦" # Ikona domyślna

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

def formatuj_instrukcje(tekst):
    if not tekst: return
    linie = tekst.split('\n')
    for linia in linie:
        l = linia.strip()
        if not l: continue
        if l[0].isdigit() and (l[1] == '.' or l[1] == ')'):
            st.markdown(f"#### {l}") 
        elif l.startswith('-') or l.startswith('*'):
            st.markdown(f"- {l[1:].strip()}") 
        else:
            st.write(l)

def oblicz_cene_tortu(przepis, data_skladnikow, srednica_docelowa=None):
    if not srednica_docelowa:
        srednica_docelowa = przepis.get('srednica', 20)
    baza_cm = przepis.get('srednica', 20)
    wsp = (srednica_docelowa / baza_cm) ** 2
    
    koszt_skladnikow = 0
    for sk, il in przepis["skladniki_przepisu"].items():
        if sk in data_skladnikow:
            info = data_skladnikow[sk]
            cena_g = info["cena"] / info["waga_opakowania"]
            koszt_skladnikow += (cena_g * il * wsp)
    
    marza_proc = przepis.get('marza', 10)
    czas = przepis.get('czas', 180)
    stawka_h = przepis.get('stawka_h', 20)
    
    koszt_pracy = (czas/60) * stawka_h
    cena_koncowa = koszt_skladnikow * (1 + marza_proc/100) + koszt_pracy
    return round(cena_koncowa, 2)

def render_stars(value):
    try: val = int(round(float(value)))
    except: val = 0
    return "⭐" * val + "☆" * (5 - val)

#/////////////////////////// 3. Wygląd i Inicjalizacja ///////////////////////////
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        
        /* 1. TŁO GŁÓWNE APLIKACJI I KONTENERÓW */
        .stApp, [data-testid="stForm"], [data-testid="stVerticalBlock"] { 
            background-color: #FDF5E6 !important; 
        }

        /* 2. TYLKO POLA WEJŚCIOWE MAJĄ BYĆ BIAŁE */
        /* Celujemy precyzyjnie w tła pól, a nie w ich kontenery */
        input, textarea, div[data-baseweb="select"] > div, 
        div[data-baseweb="input"] > div,
        section[data-testid="stFileUploaderDropzone"] {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 2px solid #f56cb3 !important;
            border-radius: 10px !important;
        }

        /* Naprawa list rozwijanych (popover) */
        div[data-baseweb="popover"] *, div[role="listbox"] * {
            background-color: #ffffff !important;
            color: #1A1A1A !important;
        }

        /* 3. TEKST - Zawsze ciemny grafit */
        input, textarea, select, span, label, p, h1, h2, h3, .stMarkdown {
            color: #1A1A1A !important;
            -webkit-text-fill-color: #1A1A1A !important;
        }

        /* 4. PRZYCISKI - Białe z różową ramką, na hover całe różowe */
        button[kind="secondaryFormSubmit"], button[kind="secondary"], .stButton > button {
            background-color: #ffffff !important;
            color: #ff0aef !important;
            border: 2px solid #ff0aef !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }

        button:hover {
            background-color: #ff0aef !important;
            color: #ffffff !important;
        }

        /* Naprawa białych "plam" wewnątrz przycisków */
        button * {
            background-color: transparent !important;
            color: inherit !important;
        }

        /* 5. KAFELKI (Magazyn, Kalendarz, Składniki) - Muszą pozostać białe */
        .order-card {
            background-color: #ffffff !important;
            border: 2px solid #f56cb3 !important;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .order-card b, .order-card small, .order-card div {
            color: #1A1A1A !important;
        }

        /* 6. SPOLSZCZENIE UPLOADERA */
        div[data-testid="stFileUploader"] section div::before { 
            content: "Przeciągnij zdjęcia tutaj"; 
            color: #1A1A1A !important; font-weight: bold;
        }
        div[data-testid="stFileUploader"] section div { font-size: 0px !important; }
        div[data-testid="stFileUploader"] section button span::after { 
            content: "Wybierz zdjęcia"; font-size: 14px; 
        }
        div[data-testid="stFileUploader"] section button span { font-size: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# Załadowanie danych
data = load_data()
st.session_state['data'] = data

if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'edit_order_index' not in st.session_state: st.session_state['edit_order_index'] = None
if 'edit_recipe_index' not in st.session_state: st.session_state['edit_recipe_index'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None
if 'edit_ing_key' not in st.session_state: st.session_state['edit_ing_key'] = None



#/////////////////////////// 4. Górne Menu ///////////////////////////
# Centrowanie i wyświetlanie logo (bez napisu pod spodem)
LOGO_PATH = "wktorty_logo.png"
if os.path.exists(LOGO_PATH):
    c1, c2, c3 = st.columns([1, 0.6, 1])
    with c2:
        st.image(LOGO_PATH, use_container_width=True)

# Usunięto: st.markdown('<div class="header-title">WK TORTY</div>', unsafe_allow_html=True)

# Elastyczne kolumny menu - rozciągają się do krawędzi strony
menu_cols = st.columns(5)

with menu_cols[0]: 
    if st.button("📅 Kalendarz", use_container_width=True): 
        st.session_state['menu'] = "Kalendarz"
with menu_cols[1]: 
    if st.button("📖 Przepisy", use_container_width=True): 
        st.session_state['menu'] = "Przepisy"
        st.session_state['fullscreen_recipe'] = None
        st.session_state['edit_recipe_index'] = None
with menu_cols[2]: 
    if st.button("➕ Dodaj", use_container_width=True): 
        st.session_state['menu'] = "Dodaj"
with menu_cols[3]: 
    if st.button("📦 Magazyn", use_container_width=True): 
        st.session_state['menu'] = "Magazyn"
with menu_cols[4]: 
    if st.button("🖼️ Galeria", use_container_width=True): 
        st.session_state['menu'] = "Galeria"

if 'menu' not in st.session_state: st.session_state['menu'] = "Kalendarz"
menu = st.session_state['menu']
st.write("---")

#/////////////////////////// 5. Logika podstron ///////////////////////////
#//--- 5.1. KALENDARZ ---//
if menu == "Kalendarz":
    st.caption("PLANER ZAMÓWIEŃ")
    
    # Odświeżenie danych
    data = load_data()
    
    if not st.session_state['show_add_order'] and st.session_state['edit_order_index'] is None:
        if st.button("➕ NOWE ZLECENIE", use_container_width=True):
            st.session_state['show_add_order'] = True
            st.rerun()

    idx_edit = st.session_state['edit_order_index']
    is_edit_mode = idx_edit is not None
    
    # FORMULARZ
    if st.session_state['show_add_order'] or is_edit_mode:
        with st.container(border=True):
            st.subheader("📝 " + ("Edytuj zlecenie" if is_edit_mode else "Nowe zlecenie"))
            domyslne = data["kalendarz"][idx_edit] if is_edit_mode else {}
            
            with st.form("kalendarz_form"):
                d_val = date.fromisoformat(domyslne['data']) if 'data' in domyslne else date.today()
                data_zamowienia = st.date_input("Termin odbioru", value=d_val)
                klient = st.text_input("Klient", value=domyslne.get('klient', ''))
                
                c1, c2 = st.columns(2)
                lista_przepisow = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                
                # POPRAWKA: Wyciąganie nazwy tortu z zapisanego opisu do edycji
                stary_opis_pelny = domyslne.get('opis', '')
                obecny_tort = "Własna kompozycja"
                if "[TORT:" in stary_opis_pelny:
                    obecny_tort = stary_opis_pelny.split("[TORT:")[1].split("]")[0].strip()
                
                # Ustawienie indeksu dla selectboxa, żeby nie wracał do "Własna kompozycja"
                idx_start = lista_przepisow.index(obecny_tort) if obecny_tort in lista_przepisow else 0
                
                wybrany_tort = c1.selectbox("Wybierz przepis", options=lista_przepisow, index=idx_start)
                srednica_zam = c2.number_input("Średnica Fi (cm)", value=20)

                # Obliczanie ceny sugerowanej
                cena_sugerowana = 0.0
                if wybrany_tort != "Własna kompozycja":
                    przepis_obj = next((p for p in data["przepisy"] if p["nazwa"] == wybrany_tort), None)
                    if przepis_obj:
                        cena_sugerowana = oblicz_cene_tortu(przepis_obj, data["skladniki"], srednica_zam)

                stara_cena = 0.0
                if is_edit_mode and "[CENA:" in stary_opis_pelny:
                    try: stara_cena = float(stary_opis_pelny.split("[CENA:")[1].split("]")[0].replace("zł", "").strip())
                    except: stara_cena = 0.0

                cena_finalna = st.number_input("Cena ostateczna (zł)", 
                                               value=stara_cena if is_edit_mode else float(cena_sugerowana))

                # Wyciąganie czystego opisu (bez tagów ceny i tortu)
                opis_czysty = stary_opis_pelny.split('[TORT:')[0].strip() if is_edit_mode else ""
                opis_dodatkowy = st.text_area("Uwagi", value=opis_czysty)
                uploaded_order_imgs = st.file_uploader("Dodaj zdjęcia", type=['jpg','png'], accept_multiple_files=True)

                b_col1, b_col2 = st.columns(2)
                with b_col1: save_btn = st.form_submit_button("ZAPISZ")
                with b_col2: cancel_btn = st.form_submit_button("ANULUJ")

                if cancel_btn:
                    st.session_state['show_add_order'] = False
                    st.session_state['edit_order_index'] = None
                    st.rerun()

                if save_btn:
                    nowe_fotki = save_uploaded_files(uploaded_order_imgs)
                    stare_fotki = domyslne.get('zdjecia', []) if is_edit_mode else []
                    
                    # Zapisujemy RODZAJ TORTU i CENĘ w opisie
                    wpis = {
                        "data": str(data_zamowienia), "klient": klient, 
                        "opis": f"{opis_dodatkowy} [TORT: {wybrany_tort}] [CENA: {cena_finalna:.2f} zł]", 
                        "wykonane": domyslne.get('wykonane', False) if is_edit_mode else False,
                        "zdjecia": stare_fotki + nowe_fotki
                    }
                    if is_edit_mode: data["kalendarz"][idx_edit] = wpis
                    else: data["kalendarz"].append(wpis)
                    
                    data["kalendarz"] = sorted(data["kalendarz"], key=lambda x: x['data'])
                    save_data(data)
                    st.session_state['show_add_order'] = False
                    st.session_state['edit_order_index'] = None
                    st.rerun()

    st.write("---")

    # LISTA KAFELKÓW
    if not data["kalendarz"]:
        st.info("Brak zaplanowanych zleceń.")
    else:
        for i, wpis in enumerate(data["kalendarz"]):
            # Wyciąganie ceny i rodzaju tortu do wyświetlenia
            opis_pelny = wpis.get('opis', '')
            cena_val = opis_pelny.split("[CENA:")[1].split("]")[0].strip() if "[CENA:" in opis_pelny else "0.00 zł"
            tort_val = opis_pelny.split("[TORT:")[1].split("]")[0].strip() if "[TORT:" in opis_pelny else "Własna kompozycja"
            czysty_opis_wyswietl = opis_pelny.split('[TORT:')[0].strip()
            
            st.markdown(f"""
                <div class="order-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-size: 1.1rem;">📅 <b>{wpis['data']}</b></span><br>
                            <span style="font-size: 1.3rem;">👤 <b>{wpis['klient']}</b></span><br>
                            <span style="font-size: 1.0rem; color: #ff0aef;">🎂 {tort_val}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: {'#00ff00' if wpis.get('wykonane') else '#f56cb3'}; font-weight: bold;">
                                {'✅ GOTOWE' if wpis.get('wykonane') else '⏳ W REALIZACJI'}
                            </span><br>
                            <span style="color: #00ff00; font-weight: bold; font-size: 1.2rem;">{cena_val}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Opcje i szczegóły"):
                st.write(f"**Uwagi:** {czysty_opis_wyswietl}")
                if wpis.get('zdjecia'):
                    c_img = st.columns(4)
                    for j, img in enumerate(wpis['zdjecia']):
                        if os.path.exists(img):
                            with c_img[j%4]: st.image(img)
                
                c_a, c_b, c_c = st.columns(3, gap="small")
                btn_txt = "Nadal w realizacji" if wpis.get('wykonane') else "Zakończ zlecenie"
                
                if c_a.button(btn_txt, key=f"s_{i}", use_container_width=True):
                    data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                    save_data(data); st.rerun()
                if c_b.button("Edytuj", key=f"e_{i}", use_container_width=True):
                    st.session_state['edit_order_index'] = i; st.rerun()
                if c_c.button("Usuń", key=f"d_{i}", use_container_width=True):
                    data["kalendarz"].pop(i); save_data(data); st.rerun()

#//--- 5.2. MAGAZYN ---//
elif menu == "Magazyn":
    st.caption("ZARZĄDZANIE ASORTYMENTEM")
    data = load_data()
    
    # 1. TRYB EDYCJI
    if st.session_state.get('edit_ing_key'):
        old_name = st.session_state['edit_ing_key']
        v = data["skladniki"][old_name]
        
        with st.container(border=True):
            st.subheader(f"✏️ Edycja: {old_name}")
            with st.form("edit_ing_form"):
                new_name = st.text_input("Nazwa produktu", value=old_name)
                new_kat = st.selectbox("Kategoria", ["Składniki", "Dodatki", "Opakowania"], 
                                      index=["Składniki", "Dodatki", "Opakowania"].index(v.get("kategoria", "Składniki")))
                
                c1, c2, c3 = st.columns(3)
                new_kcal = c1.number_input("Kcal/100g", value=v.get("kcal", 0))
                new_weight = c2.number_input("Waga/Ilość", value=v.get("waga_opakowania", 1))
                new_price = c3.number_input("Cena", value=float(v.get("cena", 0.01)))
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("ZAPISZ ZMIANY", use_container_width=True):
                    if new_name != old_name: del data["skladniki"][old_name]
                    
                    data["skladniki"][new_name] = {
                        "cena": new_price, "waga_opakowania": new_weight,
                        "kcal": new_kcal, "kategoria": new_kat,
                        "ikona": dobierz_ikone(new_name) # Automatyczna ikona
                    }
                    save_data(data); st.session_state['edit_ing_key'] = None; st.rerun()
                if b2.form_submit_button("ANULUJ", use_container_width=True):
                    st.session_state['edit_ing_key'] = None; st.rerun()

    # 2. DODAWANIE NOWEGO
    else:
        with st.expander("➕ DODAJ DO MAGAZYNU"):
            with st.form("magazyn_add_quick"):
                nn = st.text_input("Nazwa produktu (np. Olej słonecznikowy)")
                nk = st.selectbox("Kategoria", ["Składniki", "Dodatki", "Opakowania"])
                
                c1, c2, c3 = st.columns(3)
                kcal = c1.number_input("Kcal/100g", min_value=0)
                waga = c2.number_input("Waga/Szt", min_value=1)
                cena = c3.number_input("Cena (zł)", min_value=0.01)
                
                if st.form_submit_button("DODAJ PRODUKT", use_container_width=True) and nn:
                    data["skladniki"][nn] = {
                        "cena": cena, "waga_opakowania": waga, "kcal": kcal, 
                        "kategoria": nk, "ikona": dobierz_ikone(nn)
                    }
                    save_data(data); st.rerun()

    st.write("---")
    
    # 3. WYŚWIETLANIE TABS
    t1, t2, t3 = st.tabs(["🍎 Składniki", "🎀 Dodatki", "📦 Opakowania"])
    kat_list = [("Składniki", t1), ("Dodatki", t2), ("Opakowania", t3)]
    
    for kat_name, tab_obj in kat_list:
        with tab_obj:
            prods = {k: v for k, v in data["skladniki"].items() if v.get("kategoria", "Składniki") == kat_name}
            if not prods:
                st.info("Pusto w tej kategorii.")
            else:
                for k, v in prods.items():
                    st.markdown(f"""
                        <div class="order-card">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <div style="font-size: 28px; background: #fdf5e6; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; border: 1px solid #f56cb3;">
                                    {v.get('ikona', '📦')}
                                </div>
                                <div style="flex-grow: 1;">
                                    <b style="font-size: 1.1rem;">{k}</b><br>
                                    <small>{v.get('kcal',0)} kcal | {v.get('waga_opakowania',1)}g/szt</small>
                                </div>
                                <div style="text-align: right; color: #00ff00; font-weight: bold; font-size: 1.1rem;">
                                    {v.get('cena',0):.2f} zł
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    c_e, c_d = st.columns(2)
                    if c_e.button("Edytuj", key=f"e_{k}", use_container_width=True):
                        st.session_state['edit_ing_key'] = k; st.rerun()
                    if c_d.button("Usuń", key=f"d_{k}", use_container_width=True):
                        del data["skladniki"][k]; save_data(data); st.rerun()

#//--- 5.3. DODAJ PRZEPIS ---//
elif menu == "Dodaj":
    st.caption("KREATOR NOWEGO PRZEPISU")
    
    # Odświeżenie danych
    data = load_data()

    # 1. SEKCJA WYBORU SKŁADNIKÓW
    with st.container(border=True):
        st.subheader("1. Składniki przepisu")
        
        c1, c2, c3 = st.columns([2, 1, 1])
        lista_prod = sorted(list(data["skladniki"].keys()))
        wybrany_prod = c1.selectbox("Wybierz produkt", lista_prod, key="sel_prod_recipe")
        ilosc_prod = c2.number_input("Ilość (g/szt/ml)", min_value=0, key="num_prod_recipe")
        
        if c3.button("DODAJ DO LISTY", use_container_width=True):
            if ilosc_prod > 0:
                # Dodajemy lub sumujemy jeśli już jest
                st.session_state['temp_skladniki'][wybrany_prod] = st.session_state['temp_skladniki'].get(wybrany_prod, 0) + ilosc_prod
                st.rerun()

        st.write("---")
        
        # WYŚWIETLANIE SKŁADNIKÓW JAKO ODDZIELNE KAFELKI
        if st.session_state['temp_skladniki']:
            st.write("Składniki w tym przepisie (kliknij 'X' aby usunąć):")
            
            # Tworzymy pętlę generującą mały kafelek dla każdego składnika
            for nazwa_s, ilosc_s in list(st.session_state['temp_skladniki'].items()):
                # Kontener dla pojedynczego kafelka składnika
                with st.container(border=False):
                    # Kolumna lewa na dane, kolumna prawa na mały przycisk usuwania
                    ck1, ck2 = st.columns([4, 1])
                    
                    with ck1:
                        st.markdown(f"""
                            <div class="order-card" style="padding: 8px 15px; margin-bottom: 0px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: bold; color: #1A1A1A;">{nazwa_s}</span>
                                    <span style="color: #f56cb3; font-weight: bold;">{ilosc_s}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with ck2:
                        # Mały przycisk "X" do usuwania konkretnego kafelka
                        if st.button("✖", key=f"del_{nazwa_s}", help=f"Usuń {nazwa_s}"):
                            del st.session_state['temp_skladniki'][nazwa_s]
                            st.rerun()
            
            st.write("")
            if st.button("WYCZYŚĆ WSZYSTKO", type="secondary"):
                st.session_state['temp_skladniki'] = {}
                st.rerun()
        else:
            st.info("Dodaj składniki powyżej, aby stworzyć listę.")

    # 2. SEKCJA SZCZEGÓŁÓW PRZEPISU
    st.write("")
    with st.form("new_recipe_form"):
        st.subheader("2. Parametry i instrukcja")
        
        nazwa_r = st.text_input("Nazwa przepisu")
        instrukcja_r = st.text_area("Sposób przygotowania")
        zdjecia_r = st.file_uploader("Dodaj zdjęcia", accept_multiple_files=True)
        
        col1, col2, col3, col4 = st.columns(4)
        fi_r = col1.number_input("Średnica Fi (cm)", value=20)
        marza_r = col2.number_input("Marża (%)", value=10)
        czas_r = col3.number_input("Czas pracy (min)", value=120)
        zarobek_r = col4.number_input("Zarobek / h (zł)", value=30)
        
        if st.form_submit_button("ZAPISZ CAŁY PRZEPIS", use_container_width=True):
            if not nazwa_r:
                st.error("Podaj nazwę!")
            elif not st.session_state['temp_skladniki']:
                st.error("Lista składników nie może być pusta!")
            else:
                nowy_przepis = {
                    "nazwa": nazwa_r,
                    "opis": instrukcja_r,
                    "zdjecia": save_uploaded_files(zdjecia_r),
                    "srednica": fi_r,
                    "skladniki_przepisu": st.session_state['temp_skladniki'].copy(),
                    "marza": marza_r,
                    "czas": czas_r,
                    "stawka_h": zarobek_r
                }
                data["przepisy"].append(nowy_przepis)
                save_data(data)
                st.session_state['temp_skladniki'] = {} # czyścimy po zapisie
                st.success(f"Przepis {nazwa_r} zapisany pomyślnie!")
                st.rerun()

#//--- 5.4. PRZEPISY (TORTY) ---//
elif menu == "Przepisy":
    # 1. TRYB EDYCJI
    if st.session_state['edit_recipe_index'] is not None:
        idx = st.session_state['edit_recipe_index']
        p = data["przepisy"][idx]
        with st.form("edit_recipe"):
            st.subheader(f"✏️ Edytujesz: {p['nazwa']}")
            e_nazwa = st.text_input("Nazwa", value=p['nazwa'])
            e_opis = st.text_area("Instrukcja", value=p['opis'])
            c1, c2, c3, c4 = st.columns(4)
            e_fi = c1.number_input("Fi", value=p.get('srednica', 20))
            e_marza = c2.number_input("Marża", value=p.get('marza', 10))
            e_czas = c3.number_input("Czas", value=p.get('czas', 180))
            e_stawka = c4.number_input("Stawka", value=p.get('stawka_h', 20))
            if st.form_submit_button("ZAPISZ ZMIANY", use_container_width=True):
                p.update({"nazwa": e_nazwa, "opis": e_opis, "srednica": e_fi, "marza": e_marza, "czas": e_czas, "stawka_h": e_stawka})
                save_data(data); st.session_state['edit_recipe_index'] = None; st.rerun()
            if st.form_submit_button("ANULUJ", use_container_width=True):
                st.session_state['edit_recipe_index'] = None; st.rerun()

    # 2. TRYB SZCZEGÓŁÓW (FULLSCREEN)
    elif st.session_state['fullscreen_recipe'] is not None:
        p = data["przepisy"][st.session_state['fullscreen_recipe']]
        
        if st.button("⬅️ WRÓĆ DO LISTY", use_container_width=True): 
            st.session_state['fullscreen_recipe'] = None; st.rerun()
        
        st.markdown(f'<div class="order-card"><h1 style="margin:0;">{p["nazwa"]}</h1></div>', unsafe_allow_html=True)
        
        if p.get('zdjecia'): 
            st.image(p['zdjecia'][0], use_container_width=True)
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            cena_b = oblicz_cene_tortu(p, data['skladniki'])
            st.metric("Cena bazowa", f"{cena_b} zł")
        
        # OBLICZANIE SUMY KCAL
        suma_kcal = 0
        for sk_nazwa, ilosc in p["skladniki_przepisu"].items():
            if sk_nazwa in data["skladniki"]:
                sk_info = data["skladniki"][sk_nazwa]
                # kcal podajemy zazwyczaj na 100g/ml
                kcal_w_przepisie = (sk_info['kcal'] * ilosc) / 100
                suma_kcal += kcal_w_przepisie
        
        with col_info2:
            st.metric("Suma kalorii", f"{int(suma_kcal)} kcal")

        st.write("---")
        
        # WYŚWIETLANIE SKŁADNIKÓW Z IKONAMI
        st.subheader("🛒 Składniki")
        for sk_nazwa, ilosc in p["skladniki_przepisu"].items():
            ikona = data["skladniki"].get(sk_nazwa, {}).get("ikona", "📦")
            st.markdown(f"""
                <div style="background: white; border: 1px solid #f56cb3; border-radius: 10px; padding: 5px 15px; margin-bottom: 5px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 20px;">{ikona}</span>
                    <span style="flex-grow: 1;"><b>{sk_nazwa}</b></span>
                    <span style="color: #ff0aef;">{ilosc} g/szt/ml</span>
                </div>
            """, unsafe_allow_html=True)

        st.write("---")
        st.subheader("👩‍🍳 Instrukcja")
        formatuj_instrukcje(p['opis'])

    # 3. LISTA PRZEPISÓW
    else:
        search = st.text_input("🔍 Szukaj tortu...", placeholder="Wpisz nazwę...")
        st.write("")
        
        for i, p in enumerate(data["przepisy"]):
            if search.lower() in p["nazwa"].lower():
                cena_t = oblicz_cene_tortu(p, data["skladniki"])
                st.markdown(f"""
                    <div class="order-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <b style="font-size: 1.2rem;">{p["nazwa"]}</b><br>
                                <small>Średnica bazowa: {p.get("srednica", 20)}cm</small>
                            </div>
                            <div style="color: #00ff00; font-weight: bold; font-size: 1.2rem;">{cena_t} zł</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3, gap="small")
                if c1.button("👁️ Otwórz", key=f"v_{i}", use_container_width=True): 
                    st.session_state['fullscreen_recipe'] = i; st.rerun()
                if c2.button("✏️ Edytuj", key=f"re_{i}", use_container_width=True): 
                    st.session_state['edit_recipe_index'] = i; st.rerun()
                if c3.button("🗑️ Usuń", key=f"rd_{i}", use_container_width=True): 
                    data["przepisy"].pop(i); save_data(data); st.rerun()

#//--- 5.5. GALERIA ---//
elif menu == "Galeria":
    st.caption("GALERIA TWOICH DZIEŁ")
    wszystkie = []
    for idx, p in enumerate(data["przepisy"]):
        for f in p.get("zdjecia", []):
            if os.path.exists(f): wszystkie.append({"src": f, "name": p["nazwa"], "idx": idx})
    if not wszystkie: st.info("Brak zdjęć w galerii.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(wszystkie):
            with cols[i % 2]:
                st.markdown(f'<div class="order-card"><b>{item["name"]}</b></div>', unsafe_allow_html=True)
                st.image(item["src"], use_container_width=True)
                if st.button("👁️ Zobacz przepis", key=f"g_v_{i}", use_container_width=True):
                    st.session_state['menu'] = "Przepisy"; st.session_state['fullscreen_recipe'] = item["idx"]; st.rerun()





































