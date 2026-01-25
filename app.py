/////////////////////////// 1. Importy i Konfiguracja ///////////////////////////
import streamlit as st
import json
import os
import pandas as pd
from datetime import date

DB_FILE = 'baza_cukierni_v14.json'
IMG_FOLDER = 'zdjecia_tortow'
DEFAULT_IMG = 'default_cake.png'

os.makedirs(IMG_FOLDER, exist_ok=True)

/////////////////////////// 2. Funkcje pomocnicze ///////////////////////////
def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "skladniki": {
                "Mąka pszenna": {"cena": 3.50, "waga_opakowania": 1000, "kcal": 364},
                "Cukier": {"cena": 4.00, "waga_opakowania": 1000, "kcal": 387},
                "Masło": {"cena": 7.50, "waga_opakowania": 200, "kcal": 717},
                "Jajka (szt)": {"cena": 1.20, "waga_opakowania": 1, "kcal": 155}
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

Świetnie. Zgodnie z Twoją prośbą, oto uporządkowany podział Twojego kodu na sekcje. Możesz go teraz łatwo podmieniać lub edytować fragmentami.

Oto struktura Twojego pliku:
/////////////////////////// 1. Importy i Konfiguracja ///////////////////////////
Python

import streamlit as st
import json
import os
import pandas as pd
from datetime import date

DB_FILE = 'baza_cukierni_v14.json'
IMG_FOLDER = 'zdjecia_tortow'
DEFAULT_IMG = 'default_cake.png'

os.makedirs(IMG_FOLDER, exist_ok=True)

/////////////////////////// 2. Funkcje pomocnicze ///////////////////////////

(Ładowanie, zapisywanie, obliczenia, formatowanie)
Python

def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "skladniki": {
                "Mąka pszenna": {"cena": 3.50, "waga_opakowania": 1000, "kcal": 364},
                "Cukier": {"cena": 4.00, "waga_opakowania": 1000, "kcal": 387},
                "Masło": {"cena": 7.50, "waga_opakowania": 200, "kcal": 717},
                "Jajka (szt)": {"cena": 1.20, "waga_opakowania": 1, "kcal": 155}
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

/////////////////////////// 3. Wygląd i Inicjalizacja ///////////////////////////
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

# ... (Tutaj wstaw kod CSS z poprzedniej wiadomości) ...

if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'edit_order_index' not in st.session_state: st.session_state['edit_order_index'] = None
if 'edit_recipe_index' not in st.session_state: st.session_state['edit_recipe_index'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None
if 'edit_ing_key' not in st.session_state: st.session_state['edit_ing_key'] = None

data = load_data()

/////////////////////////// 4. Górne Menu ///////////////////////////
st.markdown('<div class="header-title">WK TORTY</div>', unsafe_allow_html=True)

menu_cols = st.columns(5)
with menu_cols[0]: 
    if st.button("📅 Kalendarz"): st.session_state['menu'] = "Kalendarz"
with menu_cols[1]: 
    if st.button("📖 Torty"): 
        st.session_state['menu'] = "Przepisy"
        st.session_state['fullscreen_recipe'] = None
        st.session_state['edit_recipe_index'] = None
with menu_cols[2]: 
    if st.button("➕ Dodaj"): st.session_state['menu'] = "Dodaj"
with menu_cols[3]: 
    if st.button("📦 Magazyn"): st.session_state['menu'] = "Magazyn"
with menu_cols[4]: 
    if st.button("🖼️ Galeria"): st.session_state['menu'] = "Galeria"

if 'menu' not in st.session_state: st.session_state['menu'] = "Kalendarz"
menu = st.session_state['menu']
st.write("---")

/////////////////////////// 5. Logika podstron ///////////////////////////
if menu == "Kalendarz":
    st.caption("PLANER ZAMÓWIEŃ")
    
    if st.button("➕ Dodaj / Zamknij", type="primary"):
        st.session_state['show_add_order'] = not st.session_state['show_add_order']
        st.session_state['edit_order_index'] = None

    idx_edit = st.session_state['edit_order_index']
    is_edit_mode = idx_edit is not None
    
    if st.session_state['show_add_order'] or is_edit_mode:
        with st.container(border=True):
            domyslne = data["kalendarz"][idx_edit] if is_edit_mode else {}
            with st.form("kalendarz_form"):
                d_val = date.fromisoformat(domyslne['data']) if 'data' in domyslne else date.today()
                data_zamowienia = st.date_input("Data", value=d_val)
                klient = st.text_input("Klient", value=domyslne.get('klient', ''))
                
                lista_nazw = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                wybrany_tort = st.selectbox("Tort", lista_nazw)
                srednica_zam = st.number_input("Fi (cm)", value=20)

                opis_val = domyslne.get('opis', '').split('[AUTO-WYCENA')[0] if is_edit_mode else ""
                opis_dodatkowy = st.text_area("Opis", value=opis_val)
                uploaded_order_imgs = st.file_uploader("Zdjęcia", type=['jpg','png'], accept_multiple_files=True)

                if st.form_submit_button("Zapisz"):
                    info_cenowe = ""
                    if wybrany_tort != "Własna kompozycja":
                        przepis = next((p for p in data["przepisy"] if p["nazwa"] == wybrany_tort), None)
                        if przepis:
                            cena_est = oblicz_cene_tortu(przepis, data["skladniki"], srednica_zam)
                            info_cenowe = f"\n[AUTO-WYCENA: {wybrany_tort} fi{srednica_zam}cm ~ {cena_est} zł]"

                    full_opis = f"{opis_dodatkowy}{info_cenowe}"
                    nowe_fotki = save_uploaded_files(uploaded_order_imgs)
                    stare_fotki = domyslne.get('zdjecia', []) if is_edit_mode else []
                    finalne_fotki = stare_fotki + nowe_fotki

                    wpis = {
                        "data": str(data_zamowienia), "klient": klient, 
                        "opis": full_opis, 
                        "wykonane": domyslne.get('wykonane', False) if is_edit_mode else False,
                        "zdjecia": finalne_fotki
                    }
                    if is_edit_mode:
                        data["kalendarz"][idx_edit] = wpis
                        st.session_state['edit_order_index'] = None
                    else:
                        data["kalendarz"].append(wpis)
                        st.session_state['show_add_order'] = False
                    data["kalendarz"] = sorted(data["kalendarz"], key=lambda x: x['data'])
                    save_data(data)
                    st.rerun()

    if not data["kalendarz"]:
        st.info("Brak zleceń.")
    else:
        for i, wpis in enumerate(data["kalendarz"]):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{wpis['klient']}**")
                c1.caption(f"{wpis['data']}")
                c2.markdown("✅" if wpis.get("wykonane") else "⏳", unsafe_allow_html=True)
                
                if wpis.get('opis'): st.write(wpis['opis'])
                
                if wpis.get('zdjecia'):
                    cols_img = st.columns(4)
                    for j, img_path in enumerate(wpis['zdjecia'][:4]):
                        if os.path.exists(img_path):
                            with cols_img[j]: st.image(img_path)
                
                st.write("")
                b1, b2, b3 = st.columns(3)
                if b1.button("Status", key=f"s_{i}"):
                    data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                    save_data(data)
                    st.rerun()
                if b2.button("Edytuj", key=f"e_{i}"):
                    st.session_state['edit_order_index'] = i
                    st.session_state['show_add_order'] = False 
                    st.rerun()
                if b3.button("Usuń", key=f"d_{i}"):
                    data["kalendarz"].pop(i)
                    save_data(data)
                    st.rerun()
