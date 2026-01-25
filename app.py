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
            color: #000000; 
        }

        /* GŁÓWNY KONTENER Z MARGINESAMI */
        [data-testid="stMainViewContainer"] > section > div {
            max-width: 1100px;
            margin-left: auto;
            margin-right: auto;
            padding-left: 5% !important;
            padding-right: 5% !important;
        }

        @media (max-width: 600px) {
            [data-testid="stMainViewContainer"] > section > div {
                padding-left: 10px !important;
                padding-right: 10px !important;
            }
            html { font-size: 14px; }
        }

        /* WYMUSZENIE UKŁADU KOLUMN W MENU */
        [data-testid="column"] {
            width: auto !important;
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
        
        /* KOMPLEKSOWE CZYSZCZENIE KOLORÓW WIDGETÓW (BIAŁE TŁO DLA WSZYSTKIEGO) */
        /* Naprawa dla: Input, Textarea, Select, FileUploader, Date, Number */
        div[data-baseweb="input"], 
        div[data-baseweb="textarea"], 
        div[data-baseweb="select"], 
        div[role="combobox"],
        div[data-testid="stFileUploader"],
        .stNumberInput div,
        .stDateInput div {
            background-color: #ffffff !important;
            border-radius: 8px !important;
            color: #000000 !important;
        }

        /* Wymuszenie koloru tekstu i wypełnienia dla przeglądarek */
        input, textarea, select, span[data-baseweb="select"], .stMarkdown p {
            background-color: #ffffff !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* Styl dla labeli (napisów nad polami) */
        label {
            color: #000000 !important;
            font-weight: bold !important;
        }

        /* KAFELKI ZLECEŃ Z TWOJĄ RAMKĄ #f56cb3 */
        .order-card {
            background-color: #ffffff;
            border: 2px solid #f56cb3 !important;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            color: #000000;
        }

        /* Styl dla expanderów */
        .stExpander {
            background-color: #ffffff !important;
            border: 1px solid #E0E0E0 !important;
            border-radius: 12px !important;
        }

        /* Przycisk Form Submit */
        div.stFormSubmitButton > button {
            background-color: #ff0aef !important;
            color: white !important;
            width: 100% !important;
            border: none !important;
            font-weight: bold;
        }

        /* Przyciski Menu - Neonowy róż */
        .stButton > button { 
            background-color: #ffffff !important; 
            color: #ff0aef !important; 
            border: 2px solid #ff0aef !important; 
            border-radius: 10px; 
            font-weight: bold;
            padding: 0.4rem 0.2rem !important;
            font-size: 0.8rem !important;
            width: 100%;
            white-space: nowrap;
            transition: 0.3s ease;
        }

        .stButton > button:hover { 
            background-color: #ff0aef !important; 
            color: white !important; 
            box-shadow: 0 0 15px rgba(255, 10, 239, 0.6);
        }

        /* Header Tytuł */
        .header-title {
            font-size: 1.6rem; 
            font-weight: 900; 
            color: #ff0aef;
            text-align: center; 
            margin-bottom: 10px;
            text-transform: uppercase; 
            letter-spacing: 2px;
        }

        /* Wszystkie teksty czarne */
        .stMarkdown, p, span, li, div {
            color: #000000;
        }
    </style>
""", unsafe_allow_html=True)

if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'edit_order_index' not in st.session_state: st.session_state['edit_order_index'] = None
if 'edit_recipe_index' not in st.session_state: st.session_state['edit_recipe_index'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None
if 'edit_ing_key' not in st.session_state: st.session_state['edit_ing_key'] = None

data = load_data()

#/////////////////////////// 4. Górne Menu ///////////////////////////
# Centrowanie i wyświetlanie logo z poprawionym skalowaniem
LOGO_PATH = "wktorty_logo.png"
if os.path.exists(LOGO_PATH):
    # Używamy kolumn, ale blokujemy ich rozjeżdżanie się
    c1, c2, c3 = st.columns([1, 0.8, 1])
    with c2:
        st.image(LOGO_PATH, use_container_width=True)

st.markdown('<div class="header-title">WK TORTY</div>', unsafe_allow_html=True)

# Główne przyciski menu - teraz 5 kolumn będzie zawsze obok siebie, nawet na małym ekranie
menu_cols = st.columns(5)
with menu_cols[0]: 
    if st.button("📅 Plan"): st.session_state['menu'] = "Kalendarz"
with menu_cols[1]: 
    if st.button("📖 Przepisy"): 
        st.session_state['menu'] = "Przepisy"
        st.session_state['fullscreen_recipe'] = None
        st.session_state['edit_recipe_index'] = None
with menu_cols[2]: 
    if st.button("➕ Nowy"): st.session_state['menu'] = "Dodaj"
with menu_cols[3]: 
    if st.button("📦 Stan"): st.session_state['menu'] = "Magazyn"
with menu_cols[4]: 
    if st.button("🖼️ Foto"): st.session_state['menu'] = "Galeria"

if 'menu' not in st.session_state: st.session_state['menu'] = "Kalendarz"
menu = st.session_state['menu']
st.write("---")

#/////////////////////////// 5. Logika podstron ///////////////////////////
#//--- 5.1. KALENDARZ ---//
if menu == "Kalendarz":
    st.caption("PLANER ZAMÓWIEŃ")
    
    # Przycisk dodawania
    if not st.session_state['show_add_order'] and st.session_state['edit_order_index'] is None:
        if st.button("➕ NOWE ZLECENIE", use_container_width=True):
            st.session_state['show_add_order'] = True
            st.rerun()

    idx_edit = st.session_state['edit_order_index']
    is_edit_mode = idx_edit is not None
    
    # FORMULARZ (Dodawanie/Edycja)
    if st.session_state['show_add_order'] or is_edit_mode:
        with st.container(border=True):
            st.subheader("📝 " + ("Edytuj zlecenie" if is_edit_mode else "Nowe zlecenie"))
            domyslne = data["kalendarz"][idx_edit] if is_edit_mode else {}
            
            with st.form("kalendarz_form"):
                d_val = date.fromisoformat(domyslne['data']) if 'data' in domyslne else date.today()
                data_zamowienia = st.date_input("Termin odbioru", value=d_val)
                klient = st.text_input("Klient", value=domyslne.get('klient', ''))
                
                c1, c2 = st.columns(2)
                lista_nazw = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                wybrany_tort = c1.selectbox("Rodzaj tortu", lista_nazw)
                srednica_zam = c2.number_input("Średnica Fi (cm)", value=20)

                # Wyciąganie opisu i ceny do edycji
                stary_opis_pelny = domyslne.get('opis', '')
                opis_czysty = stary_opis_pelny.split('[CENA:')[0].strip() if '[CENA:' in stary_opis_pelny else stary_opis_pelny
                
                opis_dodatkowy = st.text_area("Uwagi", value=opis_czysty)
                cena_manualna = st.number_input("Cena zlecenia (zł)", value=0.0, step=0.01)
                uploaded_order_imgs = st.file_uploader("Inspiracje / Zdjęcia", type=['jpg','png'], accept_multiple_files=True)

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    save_btn = st.form_submit_button("ZAPISZ")
                with col_btn2:
                    cancel_btn = st.form_submit_button("ANULUJ")

                if cancel_btn:
                    st.session_state['show_add_order'] = False
                    st.session_state['edit_order_index'] = None
                    st.rerun()

                if save_btn:
                    nowe_fotki = save_uploaded_files(uploaded_order_imgs)
                    stare_fotki = domyslne.get('zdjecia', []) if is_edit_mode else []
                    
                    # Zapisujemy cenę w opisie w specjalnym formacie do łatwego wyciągnięcia
                    finalny_opis = f"{opis_dodatkowy} [CENA: {cena_manualna:.2f} zł]"
                    
                    wpis = {
                        "data": str(data_zamowienia), "klient": klient, 
                        "opis": finalny_opis, 
                        "wykonane": domyslne.get('wykonane', False) if is_edit_mode else False,
                        "zdjecia": stare_fotki + nowe_fotki
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

    st.write("---")

    # LISTA ZLECEŃ
    if not data["kalendarz"]:
        st.info("Brak zleceń.")
    else:
        for i, wpis in enumerate(data["kalendarz"]):
            # Wyciąganie ceny z opisu
            cena_str = ""
            if "[CENA:" in wpis.get('opis', ''):
                cena_str = wpis['opis'].split("[CENA:")[1].split("]")[0].strip()
            
            st.markdown(f"""
                <div class="order-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-size: 1.1rem;">📅 <b>{wpis['data']}</b></span><br>
                            <span style="font-size: 1.3rem;">👤 <b>{wpis['klient']}</b></span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: {'#00ff00' if wpis.get('wykonane') else '#f56cb3'}; font-weight: bold; font-size: 1rem;">
                                {'✅ GOTOWE' if wpis.get('wykonane') else '⏳ W REALIZACJI'}
                            </span><br>
                            <span style="color: #00ff00; font-weight: bold; font-size: 1.2rem;">
                                {cena_str}
                            </span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Zarządzaj zleceniem"):
                # Wyświetlamy czysty opis bez tagu ceny
                wyswietlany_opis = wpis.get('opis', '').split('[CENA:')[0]
                st.write(f"**Uwagi:** {wyswietlany_opis}")
                
                if wpis.get('zdjecia'):
                    cols_img = st.columns(4)
                    for j, img_path in enumerate(wpis['zdjecia']):
                        if os.path.exists(img_path):
                            with cols_img[j % 4]: st.image(img_path)
                
                # Przyciski rozciągnięte (gap_small lub brak kolumn z dużymi odstępami)
                # Używamy st.columns z małym odstępem
                c_a, c_b, c_c = st.columns([1, 1, 1], gap="small")
                
                # Dynamiczna nazwa przycisku statusu
                txt_status = "Nadal w realizacji" if wpis.get('wykonane') else "Zakończ zlecenie"
                
                if c_a.button(txt_status, key=f"stat_{i}", use_container_width=True):
                    data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                    save_data(data)
                    st.rerun()
                if c_b.button("Edytuj", key=f"edit_{i}", use_container_width=True):
                    st.session_state['edit_order_index'] = i
                    st.rerun()
                if c_c.button("Usuń", key=f"del_{i}", use_container_width=True):
                    data["kalendarz"].pop(i)
                    save_data(data)
                    st.rerun()

#//--- 5.2. MAGAZYN ---//
elif menu == "Magazyn":
    st.caption("MAGAZYN SKŁADNIKÓW")
    
    with st.expander("➕ Dodaj produkt"):
        with st.form("magazyn_add"):
            c1, c2 = st.columns(2)
            nn = c1.text_input("Nazwa")
            nk = c2.number_input("Kcal", min_value=0)
            nw = c1.number_input("Waga (g/szt)", min_value=1)
            np = c2.number_input("Cena", min_value=0.01)
            if st.form_submit_button("Zapisz") and nn:
                data["skladniki"][nn] = {"cena": np, "waga_opakowania": nw, "kcal": nk}
                save_data(data)
                st.rerun()

    st.write("---")
    
    if data["skladniki"]:
        for k, v in list(data["skladniki"].items()):
            if st.session_state['edit_ing_key'] == k:
                with st.container(border=True):
                    st.write(f"✏️ **{k}**")
                    with st.form(f"ef_{k}"):
                        c1, c2, c3 = st.columns(3)
                        nk = c1.number_input("Kcal", value=v['kcal'])
                        nw = c2.number_input("Waga", value=v['waga_opakowania'])
                        np = c3.number_input("Cena", value=v['cena'])
                        if st.form_submit_button("Zapisz"):
                            data["skladniki"][k] = {"cena": np, "waga_opakowania": nw, "kcal": nk}
                            save_data(data)
                            st.session_state['edit_ing_key'] = None
                            st.rerun()
            else:
                with st.container(border=True):
                    col_txt, col_btn = st.columns([2, 1])
                    with col_txt:
                        st.markdown(f"**{k}**")
                        st.caption(f"{v['kcal']}kcal | {v['waga_opakowania']}g | {v['cena']:.2f}zł")
                    with col_btn:
                        b_e, b_d = st.columns(2)
                        if b_e.button("✏️", key=f"ed_{k}"):
                            st.session_state['edit_ing_key'] = k
                            st.rerun()
                        if b_d.button("🗑️", key=f"del_{k}"):
                            del data["skladniki"][k]
                            save_data(data)
                            st.rerun()
    else:
        st.info("Magazyn pusty.")

#//--- 5.3. DODAJ PRZEPIS ---//
elif menu == "Dodaj":
    if st.session_state['success_msg']:
        st.success(st.session_state['success_msg'])
        st.session_state['success_msg'] = None

    st.caption("NOWY PRZEPIS")
    
    with st.expander("1. Składniki", expanded=True):
        c1, c2, c3 = st.columns([2,1,1])
        wyb = c1.selectbox("Składnik", list(data["skladniki"].keys()), label_visibility="collapsed")
        il = c2.number_input("Ilość", min_value=0, label_visibility="collapsed")
        if c3.button("Dodaj"):
            if il > 0:
                cur = st.session_state['temp_skladniki'].get(wyb, 0)
                st.session_state['temp_skladniki'][wyb] = cur + il
                st.rerun()
        
        if st.session_state['temp_skladniki']:
            st.info(", ".join([f"{k}: {v}" for k,v in st.session_state['temp_skladniki'].items()]))
            if st.button("Wyczyść listę"):
                st.session_state['temp_skladniki'] = {}
                st.rerun()

    with st.form("new_recipe"):
        st.write("2. Dane")
        nazwa = st.text_input("Nazwa")
        opis = st.text_area("Instrukcja")
        imgs = st.file_uploader("Zdjęcia", accept_multiple_files=True)
        
        c1, c2 = st.columns(2)
        fi = c1.number_input("Fi", 15)
        marza = c2.number_input("Marża %", 10)
        czas = c1.number_input("Czas min", 180)
        stawka = c2.number_input("Stawka", 20)
        
        st.write("Oceny")
        s1 = st.slider("Wygląd", 1, 5, 5)
        s2 = st.slider("Smak", 1, 5, 5)
        s3 = st.slider("Trudność", 1, 5, 3)
        
        if st.form_submit_button("ZAPISZ"):
            if nazwa and st.session_state['temp_skladniki']:
                s_imgs = save_uploaded_files(imgs)
                nowy = {
                    "nazwa": nazwa, "opis": opis, "zdjecia": s_imgs,
                    "srednica": fi, "skladniki_przepisu": st.session_state['temp_skladniki'],
                    "oceny": {"wyglad": s1, "smak": s2, "trudnosc": s3},
                    "marza": marza, "czas": czas, "stawka_h": stawka
                }
                data["przepisy"].append(nowy)
                save_data(data)
                st.session_state['temp_skladniki'] = {}
                st.session_state['success_msg'] = "Dodano!"
                st.rerun()

#//--- 5.4. PRZEPISY (TORTY) ---//
elif menu == "Przepisy":
    if st.session_state['edit_recipe_index'] is not None:
        # --- Tryb Edycji ---
        idx = st.session_state['edit_recipe_index']
        p_edit = data["przepisy"][idx]
        current_oceny = p_edit.get('oceny', {'wyglad':5, 'smak':5, 'trudnosc':3})
        
        with st.container(border=True):
            st.subheader(f"✏️ Edycja: {p_edit['nazwa']}")
            if st.button("⬅️ Anuluj"):
                st.session_state['edit_recipe_index'] = None
                st.rerun()
                
            with st.form("edit_recipe_form"):
                e_nazwa = st.text_input("Nazwa", value=p_edit['nazwa'])
                e_opis = st.text_area("Instrukcja", value=p_edit['opis'])
                
                c1, c2 = st.columns(2)
                e_srednica = c1.number_input("Fi", value=p_edit.get('srednica', 15))
                e_marza = c2.number_input("Marża", value=p_edit.get('marza', 10))
                e_czas = c1.number_input("Czas", value=p_edit.get('czas', 180))
                e_stawka = c2.number_input("Stawka", value=p_edit.get('stawka_h', 20))
                
                st.write("**Oceny:**")
                e_look = st.slider("Wygląd", 1, 5, current_oceny.get('wyglad', 5))
                e_taste = st.slider("Smak", 1, 5, current_oceny.get('smak', 5))
                e_diff = st.slider("Trudność", 1, 5, current_oceny.get('trudnosc', 3))

                st.write("**Zdjęcia:**")
                imgs_to_keep = []
                if p_edit.get('zdjecia'):
                    cols_pics = st.columns(3)
                    for i, path in enumerate(p_edit['zdjecia']):
                        with cols_pics[i % 3]:
                            if os.path.exists(path):
                                st.image(path)
                                if not st.checkbox("Usuń", key=f"del_img_e_{i}"):
                                    imgs_to_keep.append(path)
                
                new_imgs_upload = st.file_uploader("Dodaj nowe", type=['jpg', 'png'], accept_multiple_files=True)
                
                if st.form_submit_button("Zapisz Zmiany"):
                    p_edit['nazwa'] = e_nazwa
                    p_edit['opis'] = e_opis
                    p_edit['srednica'] = e_srednica
                    p_edit['marza'] = e_marza
                    p_edit['czas'] = e_czas
                    p_edit['stawka_h'] = e_stawka
                    p_edit['oceny'] = {'wyglad': e_look, 'smak': e_taste, 'trudnosc': e_diff}
                    added_paths = save_uploaded_files(new_imgs_upload)
                    p_edit['zdjecia'] = imgs_to_keep + added_paths
                    
                    data["przepisy"][idx] = p_edit
                    save_data(data)
                    st.session_state['edit_recipe_index'] = None
                    st.rerun()

    elif st.session_state['fullscreen_recipe'] is not None:
        # --- Pełny ekran przepisu ---
        idx = st.session_state['fullscreen_recipe']
        p = data["przepisy"][idx]
        if st.button("⬅️ Wróć"):
            st.session_state['fullscreen_recipe'] = None
            st.rerun()
            
        st.title(p['nazwa'])
        if p.get('zdjecia') and len(p['zdjecia']) > 0 and os.path.exists(p['zdjecia'][0]):
            st.image(p['zdjecia'][0], use_container_width=True)
        elif os.path.exists(DEFAULT_IMG):
            st.image(DEFAULT_IMG, use_container_width=True)

        st.write(f"Cena: **{oblicz_cene_tortu(p, data['skladniki'])} zł**")
        st.write("---")
        formatuj_instrukcje(p['opis'])
        
        if p.get('zdjecia') and len(p['zdjecia']) > 1:
            st.write("Galeria:")
            g_cols = st.columns(2)
            for i, img in enumerate(p["zdjecia"]):
                if os.path.exists(img):
                    with g_cols[i % 2]: st.image(img)

    else:
        # --- Lista kafelków ---
        st.caption("LISTA PRZEPISÓW")
        search = st.text_input("Szukaj", label_visibility="collapsed", placeholder="Szukaj...")
        lista = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        for i, p in enumerate(lista):
            with st.container(border=True):
                c_img, c_info = st.columns([1, 2])
                with c_img:
                    if p.get("zdjecia") and os.path.exists(p["zdjecia"][0]):
                        st.image(p["zdjecia"][0])
                    elif os.path.exists(DEFAULT_IMG):
                        st.image(DEFAULT_IMG) 
                    else: st.write("🍰")

                with c_info:
                    st.markdown(f"**{p['nazwa']}**")
                    oc = p.get('oceny', {})
                    avg = (oc.get('wyglad',0) + oc.get('smak',0))/2
                    st.caption(f"{render_stars(avg)}")
                    cena = oblicz_cene_tortu(p, data["skladniki"])
                    st.markdown(f"<span style='color:#00ff00; font-weight:bold'>{cena} zł</span>", unsafe_allow_html=True)
                
                st.write("")
                b1, b2, b3 = st.columns(3)
                real_idx = data["przepisy"].index(p)
                if b1.button("👁️", key=f"op_{i}"):
                    st.session_state['fullscreen_recipe'] = real_idx
                    st.rerun()
                if b2.button("✏️", key=f"edp_{i}"):
                    st.session_state['edit_recipe_index'] = real_idx
                    st.rerun()
                if b3.button("🗑️", key=f"del_rec_{i}"):
                    data["przepisy"].pop(real_idx)
                    save_data(data)
                    st.rerun()

#//--- 5.5. GALERIA ---//
elif menu == "Galeria":
    st.caption("GALERIA ZDJĘĆ")
    
    with st.expander("📷 Dodaj zdjęcie do przepisu", expanded=False):
        c_add1, c_add2 = st.columns(2)
        with c_add1:
            target_recipe_name = st.selectbox("Wybierz przepis:", [p['nazwa'] for p in data['przepisy']])
        with c_add2:
            new_gal_img = st.file_uploader("Wybierz zdjęcie", type=['jpg','png'])
        
        if st.button("Dodaj do wybranego tortu"):
            if new_gal_img and target_recipe_name:
                path = save_uploaded_files([new_gal_img])[0]
                for p in data['przepisy']:
                    if p['nazwa'] == target_recipe_name:
                        if 'zdjecia' not in p: p['zdjecia'] = []
                        p['zdjecia'].append(path)
                        save_data(data)
                        st.success(f"Dodano do: {target_recipe_name}")
                        st.rerun()
                        break

    wszystkie_zdjecia = []
    for idx, p in enumerate(data["przepisy"]):
        if p.get("zdjecia"):
            for img_idx, fotka in enumerate(p["zdjecia"]):
                if not os.path.exists(fotka): continue
                wszystkie_zdjecia.append({
                    "src": fotka, "name": p["nazwa"], "recipe_idx": idx,
                    "img_idx_in_recipe": img_idx, "type": "recipe"
                })

    if not wszystkie_zdjecia:
        st.info("Brak wgranych zdjęć.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(wszystkie_zdjecia):
            with cols[i % 2]:
                with st.container(border=True):
                    st.image(item["src"])
                    cb1, cb2 = st.columns([1, 1])
                    if cb1.button("👁️", key=f"g_go_{i}"):
                        st.session_state['menu'] = "Przepisy"
                        st.session_state['fullscreen_recipe'] = item["recipe_idx"]
                        st.rerun()
                    if cb2.button("🗑️", key=f"g_del_{i}"):
                        del data["przepisy"][item["recipe_idx"]]["zdjecia"][item["img_idx_in_recipe"]]
                        save_data(data)
                        st.rerun()












