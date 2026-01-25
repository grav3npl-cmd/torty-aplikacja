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

#/////////////////////////// 3. Wygląd i Inicjalizacja ///////////////////////////
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        
        /* TŁO KREMOWE CAŁOŚCI */
        .stApp { 
            background-color: #FDF5E6; 
            color: #1A1A1A; /* Bardzo ciemny grafit zamiast czarnego */
        }

        /* GŁÓWNY KONTENER */
        [data-testid="stMainViewContainer"] > section > div {
            max-width: 1100px;
            margin: 0 auto;
            padding: 5% !important;
        }

        /* TOTALNA BLOKADA CIEMNYCH TŁA DLA POLA WPISYWANIA I LIST */
        div[data-baseweb="input"], 
        div[data-baseweb="textarea"], 
        div[data-baseweb="select"], 
        div[role="combobox"],
        div[data-testid="stFileUploader"],
        .stSelectbox div,
        .stNumberInput div,
        .stDateInput div,
        .stTextInput div,
        .stTextArea div {
            background-color: #ffffff !important;
            color: #1A1A1A !important;
        }

        /* Wymuszenie grafitowego tekstu wewnątrz inputów */
        input, textarea, select, span {
            color: #1A1A1A !important;
            -webkit-text-fill-color: #1A1A1A !important;
        }

        /* SPOLSZCZENIE UPLOADERA */
        div[data-testid="stFileUploader"] section button span::after { content: "Wybierz pliki"; font-size: 14px; }
        div[data-testid="stFileUploader"] section button span { font-size: 0px; }
        div[data-testid="stFileUploader"] section div::before { content: "Przeciągnij zdjęcia tutaj"; color: #f56cb3; font-weight: bold; }
        div[data-testid="stFileUploader"] section div { font-size: 0px; }

        /* KAFELKI ZLECEŃ */
        .order-card {
            background-color: #ffffff;
            border: 2px solid #f56cb3 !important;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }

        /* PRZYCISKI MENU */
        .stButton > button { 
            background-color: #ffffff !important; 
            color: #ff0aef !important; 
            border: 2px solid #ff0aef !important; 
            border-radius: 10px; 
            font-weight: bold;
            width: 100%;
        }
        .stButton > button:hover { 
            background-color: #ff0aef !important; 
            color: white !important; 
        }

        .header-title {
            font-size: 1.6rem; font-weight: 900; color: #ff0aef;
            text-align: center; text-transform: uppercase; letter-spacing: 2px;
        }
        
        /* Kolor etykiet pól */
        label { color: #1A1A1A !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# Inicjalizacja danych na samym początku sekcji 3
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()
data = st.session_state['data']

if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'edit_order_index' not in st.session_state: st.session_state['edit_order_index'] = None
if 'edit_recipe_index' not in st.session_state: st.session_state['edit_recipe_index'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None
if 'edit_ing_key' not in st.session_state: st.session_state['edit_ing_key'] = None

#/////////////////////////// 4. Górne Menu ///////////////////////////
# Centrowanie i wyświetlanie logo
LOGO_PATH = "wktorty_logo.png"
if os.path.exists(LOGO_PATH):
    c1, c2, c3 = st.columns([1, 0.6, 1])
    with c2:
        st.image(LOGO_PATH, use_container_width=True)

st.markdown('<div class="header-title">WK TORTY</div>', unsafe_allow_html=True)

menu_cols = st.columns(5)
with menu_cols[0]: 
    if st.button("📅 Kalendarz"): st.session_state['menu'] = "Kalendarz"
with menu_cols[1]: 
    if st.button("📖 Przepisy"): 
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

#/////////////////////////// 5. Logika podstron ///////////////////////////
#//--- 5.1. KALENDARZ ---//
if menu == "Kalendarz":
    st.caption("PLANER ZAMÓWIEŃ")
    data = load_data()
    
    if not st.session_state['show_add_order'] and st.session_state['edit_order_index'] is None:
        if st.button("➕ NOWE ZLECENIE", use_container_width=True):
            st.session_state['show_add_order'] = True
            st.rerun()

    idx_edit = st.session_state['edit_order_index']
    is_edit_mode = idx_edit is not None
    
    if st.session_state['show_add_order'] or is_edit_mode:
        with st.container(border=True):
            st.subheader("📝 " + ("Edytuj" if is_edit_mode else "Nowe zlecenie"))
            domyslne = data["kalendarz"][idx_edit] if is_edit_mode else {}
            with st.form("kalendarz_form"):
                d_val = date.fromisoformat(domyslne['data']) if 'data' in domyslne else date.today()
                data_zamowienia = st.date_input("Termin odbioru", value=d_val)
                klient = st.text_input("Klient", value=domyslne.get('klient', ''))
                c1, c2 = st.columns(2)
                lista_przepisow = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                
                stary_opis_pelny = domyslne.get('opis', '')
                obecny_tort = "Własna kompozycja"
                if "[TORT:" in stary_opis_pelny:
                    obecny_tort = stary_opis_pelny.split("[TORT:")[1].split("]")[0].strip()
                
                idx_start = lista_przepisow.index(obecny_tort) if obecny_tort in lista_przepisow else 0
                wybrany_tort = c1.selectbox("Wybierz przepis", options=lista_przepisow, index=idx_start)
                srednica_zam = c2.number_input("Średnica Fi (cm)", value=20)

                cena_sugerowana = 0.0
                if wybrany_tort != "Własna kompozycja":
                    przepis_obj = next((p for p in data["przepisy"] if p["nazwa"] == wybrany_tort), None)
                    if przepis_obj:
                        cena_sugerowana = oblicz_cene_tortu(przepis_obj, data["skladniki"], srednica_zam)

                stara_cena = 0.0
                if is_edit_mode and "[CENA:" in stary_opis_pelny:
                    try: stara_cena = float(stary_opis_pelny.split("[CENA:")[1].split("]")[0].replace("zł", "").strip())
                    except: stara_cena = 0.0

                cena_finalna = st.number_input("Cena ostateczna (zł)", value=stara_cena if is_edit_mode else float(cena_sugerowana))
                opis_czysty = stary_opis_pelny.split('[TORT:')[0].strip() if is_edit_mode else ""
                opis_dodatkowy = st.text_area("Uwagi", value=opis_czysty)
                uploaded_order_imgs = st.file_uploader("Dodaj zdjęcia", type=['jpg','png'], accept_multiple_files=True)

                b_col1, b_col2 = st.columns(2)
                if b_col1.form_submit_button("ZAPISZ"):
                    nowe_fotki = save_uploaded_files(uploaded_order_imgs)
                    stare_fotki = domyslne.get('zdjecia', []) if is_edit_mode else []
                    wpis = {
                        "data": str(data_zamowienia), "klient": klient, 
                        "opis": f"{opis_dodatkowy} [TORT: {wybrany_tort}] [CENA: {cena_finalna:.2f} zł]", 
                        "wykonane": domyslne.get('wykonane', False) if is_edit_mode else False,
                        "zdjecia": stare_fotki + nowe_fotki
                    }
                    if is_edit_mode: data["kalendarz"][idx_edit] = wpis
                    else: data["kalendarz"].append(wpis)
                    data["kalendarz"] = sorted(data["kalendarz"], key=lambda x: x['data'])
                    save_data(data); st.session_state['show_add_order'] = False; st.session_state['edit_order_index'] = None; st.rerun()
                if b_col2.form_submit_button("ANULUJ"):
                    st.session_state['show_add_order'] = False; st.session_state['edit_order_index'] = None; st.rerun()

    st.write("---")
    if not data["kalendarz"]:
        st.info("Brak zleceń.")
    else:
        for i, wpis in enumerate(data["kalendarz"]):
            opis_pelny = wpis.get('opis', '')
            cena_val = opis_pelny.split("[CENA:")[1].split("]")[0].strip() if "[CENA:" in opis_pelny else "0.00 zł"
            tort_val = opis_pelny.split("[TORT:")[1].split("]")[0].strip() if "[TORT:" in opis_pelny else "Własna kompozycja"
            czysty_opis_wyswietl = opis_pelny.split('[TORT:')[0].strip()
            
            st.markdown(f'<div class="order-card"><div style="display: flex; justify-content: space-between; align-items: flex-start;"><div><span style="font-size: 1.1rem;">📅 <b>{wpis["data"]}</b></span><br><span style="font-size: 1.3rem;">👤 <b>{wpis["klient"]}</b></span><br><span style="font-size: 1.0rem; color: #ff0aef;">🎂 {tort_val}</span></div><div style="text-align: right;"><span style="color: {"#00ff00" if wpis.get("wykonane") else "#f56cb3"}; font-weight: bold;">{"✅ GOTOWE" if wpis.get("wykonane") else "⏳ W REALIZACJI"}</span><br><span style="color: #00ff00; font-weight: bold; font-size: 1.2rem;">{cena_val}</span></div></div></div>', unsafe_allow_html=True)
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
    st.caption("MAGAZYN SKŁADNIKÓW")
    with st.expander("➕ DODAJ NOWY PRODUKT"):
        with st.form("magazyn_add"):
            c1, c2 = st.columns(2)
            nn = c1.text_input("Nazwa produktu")
            nk = c2.number_input("Kcal na 100g/szt", min_value=0)
            nw = c1.number_input("Waga opakowania (g/szt)", min_value=1)
            np = c2.number_input("Cena opakowania", min_value=0.01)
            if st.form_submit_button("ZAPISZ W MAGAZYNIE", use_container_width=True) and nn:
                data["skladniki"][nn] = {"cena": np, "waga_opakowania": nw, "kcal": nk}
                save_data(data); st.rerun()

    st.write("---")
    if data["skladniki"]:
        for k, v in list(data["skladniki"].items()):
            if st.session_state['edit_ing_key'] == k:
                with st.container(border=True):
                    with st.form(f"ef_{k}"):
                        st.write(f"✏️ Edytujesz: **{k}**")
                        c1, c2, c3 = st.columns(3)
                        nk = c1.number_input("Kcal", value=v['kcal'])
                        nw = c2.number_input("Waga", value=v['waga_opakowania'])
                        np = c3.number_input("Cena", value=v['cena'])
                        c_b1, c_b2 = st.columns(2)
                        if c_b1.form_submit_button("ZAPISZ"):
                            data["skladniki"][k] = {"cena": np, "waga_opakowania": nw, "kcal": nk}
                            save_data(data); st.session_state['edit_ing_key'] = None; st.rerun()
                        if c_b2.form_submit_button("ANULUJ"):
                            st.session_state['edit_ing_key'] = None; st.rerun()
            else:
                st.markdown(f'<div class="order-card"><div style="display: flex; justify-content: space-between; align-items: center;"><div><b>{k}</b><br><small>{v["kcal"]} kcal | {v["waga_opakowania"]}g</small></div><div style="text-align: right; color: #00ff00; font-weight: bold;">{v["cena"]:.2f} zł</div></div></div>', unsafe_allow_html=True)
                c_e, c_d = st.columns(2, gap="small")
                if c_e.button("Edytuj", key=f"ed_{k}", use_container_width=True):
                    st.session_state['edit_ing_key'] = k; st.rerun()
                if c_d.button("Usuń", key=f"del_{k}", use_container_width=True):
                    del data["skladniki"][k]; save_data(data); st.rerun()

#//--- 5.3. DODAJ PRZEPIS ---//
elif menu == "Dodaj":
    st.caption("NOWY PRZEPIS")
    with st.container(border=True):
        st.subheader("1. Wybierz składniki")
        c1, c2, c3 = st.columns([2,1,1])
        wyb = c1.selectbox("Produkt", list(data["skladniki"].keys()))
        il = c2.number_input("Ilość (g/szt)", min_value=0)
        if c3.button("DODAJ", use_container_width=True):
            if il > 0:
                st.session_state['temp_skladniki'][wyb] = st.session_state['temp_skladniki'].get(wyb, 0) + il
                st.rerun()
        if st.session_state['temp_skladniki']:
            st.info(", ".join([f"{k}: {v}" for k,v in st.session_state['temp_skladniki'].items()]))
            if st.button("WYCZYŚĆ LISTĘ SKŁADNIKÓW"):
                st.session_state['temp_skladniki'] = {}; st.rerun()

    with st.form("new_recipe"):
        st.subheader("2. Szczegóły przepisu")
        nazwa = st.text_input("Nazwa tortu")
        opis = st.text_area("Instrukcja przygotowania")
        imgs = st.file_uploader("Zdjęcia", accept_multiple_files=True)
        c1, c2, c3, c4 = st.columns(4)
        fi = c1.number_input("Fi (cm)", 15)
        marza = c2.number_input("Marża %", 10)
        czas = c3.number_input("Czas (min)", 180)
        stawka = c4.number_input("Zarobek/h", 20)
        if st.form_submit_button("ZAPISZ PRZEPIS", use_container_width=True):
            if nazwa and st.session_state['temp_skladniki']:
                data["przepisy"].append({"nazwa": nazwa, "opis": opis, "zdjecia": save_uploaded_files(imgs), "srednica": fi, "skladniki_przepisu": st.session_state['temp_skladniki'], "marza": marza, "czas": czas, "stawka_h": stawka})
                save_data(data); st.session_state['temp_skladniki'] = {}; st.session_state['menu'] = "Przepisy"; st.rerun()

#//--- 5.4. PRZEPISY (TORTY) ---//
elif menu == "Przepisy":
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
            if st.form_submit_button("ZAPISZ ZMIANY"):
                p.update({"nazwa": e_nazwa, "opis": e_opis, "srednica": e_fi, "marza": e_marza, "czas": e_czas, "stawka_h": e_stawka})
                save_data(data); st.session_state['edit_recipe_index'] = None; st.rerun()
            if st.button("ANULUJ"):
                st.session_state['edit_recipe_index'] = None; st.rerun()
    elif st.session_state['fullscreen_recipe'] is not None:
        p = data["przepisy"][st.session_state['fullscreen_recipe']]
        if st.button("⬅️ WRÓĆ DO LISTY"): st.session_state['fullscreen_recipe'] = None; st.rerun()
        st.markdown(f'<div class="order-card"><h1>{p["nazwa"]}</h1></div>', unsafe_allow_html=True)
        if p.get('zdjecia'): st.image(p['zdjecia'][0], use_container_width=True)
        st.write(f"Cena bazowa: **{oblicz_cene_tortu(p, data['skladniki'])} zł**")
        formatuj_instrukcje(p['opis'])
    else:
        search = st.text_input("Szukaj tortu...", placeholder="Wpisz nazwę...")
        for i, p in enumerate(data["przepisy"]):
            if search.lower() in p["nazwa"].lower():
                st.markdown(f'<div class="order-card"><div style="display: flex; justify-content: space-between; align-items: center;"><div><b>{p["nazwa"]}</b><br><small>Fi: {p.get("srednica", 20)}cm</small></div><div style="color: #00ff00; font-weight: bold;">{oblicz_cene_tortu(p, data["skladniki"])} zł</div></div></div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3, gap="small")
                if c1.button("👁️ Otwórz", key=f"v_{i}", use_container_width=True): st.session_state['fullscreen_recipe'] = i; st.rerun()
                if c2.button("✏️ Edytuj", key=f"re_{i}", use_container_width=True): st.session_state['edit_recipe_index'] = i; st.rerun()
                if c3.button("🗑️ Usuń", key=f"rd_{i}", use_container_width=True): data["przepisy"].pop(i); save_data(data); st.rerun()

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
















