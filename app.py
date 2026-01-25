 import streamlit as st

import json

import os

import pandas as pd

from datetime import date


# --- KONFIGURACJA ---

DB_FILE = 'baza_cukierni_v10.json'

IMG_FOLDER = 'zdjecia_tortow'


os.makedirs(IMG_FOLDER, exist_ok=True)


# --- FUNKCJE ---

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

    try:

        val = int(round(float(value)))

    except:

        val = 0

    return "⭐" * val + "☆" * (5 - val)


# --- WYGLĄD (CSS) ---

st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")


st.markdown("""

    <style>

        #MainMenu, footer, header {visibility: hidden;}

        .stApp { background-color: #121212; color: #ffffff; }

        section[data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }

        

        /* Styl Kafelków */

        div[data-testid="stVerticalBlockBorderWrapper"] {

            background-color: #1e1e1e;

            border: 1px solid #333;

            border-radius: 12px;

            margin-bottom: 15px;

            padding: 10px;

        }


        /* Przyciski */

        .stButton > button { 

            background-color: transparent; 

            color: #ff0aef; 

            border: 2px solid #ff0aef; 

            border-radius: 15px; 

            font-weight: bold;

            width: 100%;

            padding: 0.5rem 1rem;

        }

        .stButton > button:hover { 

            background-color: #ff0aef; 

            color: white;

            box-shadow: 0 0 10px rgba(255, 10, 239, 0.5);

        }

        

        /* Inputy */

        .stTextInput > div > div > input, 

        .stTextArea > div > div > textarea, 

        .stNumberInput > div > div > input,

        .stSelectbox > div > div > div { 

            background-color: #2c2c2c !important; 

            color: white !important; 

            border: none !important; 

            border-radius: 8px;

        }


        /* Nagłówek */

        .header-box {

            text-align: center; padding: 10px; margin-bottom: 15px;

            border-bottom: 2px solid #ff0aef;

            background: linear-gradient(180deg, rgba(255,10,239,0.1) 0%, rgba(18,18,18,0) 100%);

        }

        .header-title {

            font-size: 1.8rem; font-weight: 900; color: #ff0aef;

            text-transform: uppercase; letter-spacing: 2px;

        }

        

        /* CSS dla Mobile - poprawki */

        @media (max-width: 640px) {

            .header-title { font-size: 1.4rem; }

            /* Zmniejszenie paddingu w kafelkach na mobile */

            div[data-testid="column"] { padding: 5px; }

        }

    </style>

""", unsafe_allow_html=True)


# --- INICJALIZACJA ---

if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}

if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False

if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None

if 'edit_order_index' not in st.session_state: st.session_state['edit_order_index'] = None

if 'edit_recipe_index' not in st.session_state: st.session_state['edit_recipe_index'] = None

if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None

if 'edit_ing_key' not in st.session_state: st.session_state['edit_ing_key'] = None # Do edycji składnika


data = load_data()


# --- HEADER ---

st.markdown(f"""

    <div class="header-box">

        <div class="header-title">WK TORTY</div>

    </div>

""", unsafe_allow_html=True)


# --- MENU ---

# Używamy columns, Streamlit na mobile sam je ułoży w stos lub ściśnie. 

# Aby wyglądało dobrze, używamy prostych etykiet.

menu_cols = st.columns(5)

with menu_cols[0]: 

    if st.button("📅 Kalendarz"): st.session_state['menu'] = "Kalendarz"

with menu_cols[1]: 

    if st.button("📖 Przepisy"): 

        st.session_state['menu'] = "Przepisy"

        st.session_state['fullscreen_recipe'] = None

with menu_cols[2]: 

    if st.button("➕ Dodaj"): st.session_state['menu'] = "Dodaj"

with menu_cols[3]: 

    if st.button("📦 Magazyn"): st.session_state['menu'] = "Magazyn"

with menu_cols[4]: 

    if st.button("🖼️ Galeria"): st.session_state['menu'] = "Galeria"


if 'menu' not in st.session_state: st.session_state['menu'] = "Kalendarz"

menu = st.session_state['menu']

st.write("---") 

# ==========================================
# 1. KALENDARZ
# ==========================================
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

# ==========================================
# 2. MAGAZYN
# ==========================================
elif menu == "Magazyn":
    st.caption("MAGAZYN SKŁADNIKÓW")
    
    with st.expander("➕ Dodaj produkt"):
        with st.form("magazyn_add"):
            c1, c2 = st.columns(2)
            nn = c1.text_input("Nazwa")
            nk = c2.number_input("Kcal", min_value=0)
            nw = c1.number_input("Waga", min_value=1)
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

# ==========================================
# 3. DODAJ PRZEPIS
# ==========================================
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

# ==========================================
# 4. PRZEPISY
# ==========================================
elif menu == "Przepisy":
    
    # --- A. TRYB EDYCJI ---
    if st.session_state['edit_recipe_index'] is not None:
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
                    st.success("Zapisano!")
                    st.rerun()

    # --- B. PEŁNY EKRAN ---
    elif st.session_state['fullscreen_recipe'] is not None:
        idx = st.session_state['fullscreen_recipe']
        p = data["przepisy"][idx]
        if st.button("⬅️ Wróć"):
            st.session_state['fullscreen_recipe'] = None
            st.rerun()
            
        st.title(p['nazwa'])
        
        # Obrazek (Priorytet: Własny -> Domyślny)
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
                with g_cols[i % 2]: st.image(img)

    # --- C. LISTA KAFELKÓW ---
    else:
        st.caption("LISTA PRZEPISÓW")
        search = st.text_input("Szukaj", label_visibility="collapsed", placeholder="Szukaj...")
        
        lista = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        for i, p in enumerate(lista):
            with st.container(border=True):
                # KOLUMNY: OBRAZ (po lewej) | TREŚĆ (po prawej)
                c_img, c_info = st.columns([1, 2])
                
                with c_img:
                    # LOGIKA DOMYŚLNEGO ZDJĘCIA
                    if p.get("zdjecia") and os.path.exists(p["zdjecia"][0]):
                        st.image(p["zdjecia"][0])
                    elif os.path.exists(DEFAULT_IMG):
                        st.image(DEFAULT_IMG) 
                    else:
                        st.write("🍰")

                with c_info:
                    st.markdown(f"**{p['nazwa']}**")
                    oc = p.get('oceny', {})
                    avg = (oc.get('wyglad',0) + oc.get('smak',0))/2
                    st.caption(f"{render_stars(avg)}")
                    cena = oblicz_cene_tortu(p, data["skladniki"])
                    st.markdown(f"<span style='color:#00ff00; font-weight:bold'>{cena} zł</span>", unsafe_allow_html=True)
                
                st.write("")
                # TRZY KOLUMNY NA BUTTONY (Open, Edit, Delete)
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

# ==========================================
# 5. GALERIA (BEZ DEFAULTA)
# ==========================================
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

    # Wyświetlanie (tylko istniejące w bazie)
    wszystkie_zdjecia = []
    
    for idx, p in enumerate(data["przepisy"]):
        if p.get("zdjecia"):
            for img_idx, fotka in enumerate(p["zdjecia"]):
                if not os.path.exists(fotka): continue
                ocena = p.get('oceny', {})
                cena = oblicz_cene_tortu(p, data["skladniki"])
                wszystkie_zdjecia.append({
                    "src": fotka, 
                    "name": p["nazwa"], 
                    "recipe_idx": idx,
                    "img_idx_in_recipe": img_idx,
                    "info": f"{render_stars((ocena.get('wyglad',0)+ocena.get('smak',0))/2)}",
                    "price": cena,
                    "type": "recipe"
                })
    
    for i, fotka in enumerate(data["galeria_extra"]):
        if os.path.exists(fotka):
            wszystkie_zdjecia.append({
                "src": fotka,
                "name": "Luźne",
                "recipe_idx": None,
                "img_idx_in_recipe": i,
                "info": "-",
                "price": "-",
                "type": "extra"
            })

    if not wszystkie_zdjecia:
        st.info("Brak wgranych zdjęć.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(wszystkie_zdjecia):
            with cols[i % 2]:
                with st.container(border=True):
                    st.image(item["src"])
                    
                    cb1, cb2, cb3 = st.columns([1, 1, 1])
                    
                    if item["type"] == "recipe":
                        if cb1.button("➜", key=f"g_go_{i}"):
                            st.session_state['menu'] = "Przepisy"
                            st.session_state['fullscreen_recipe'] = item["recipe_idx"]
                            st.rerun()
                    else:
                        cb1.button("➜", disabled=True, key=f"d1_{i}")
                    
                    if cb2.button("ℹ️", key=f"g_inf_{i}"):
                        st.toast(f"{item['name']} | Cena: {item['price']} zł")
                    
                    if cb3.button("🗑️", key=f"g_del_{i}"):
                        if item["type"] == "recipe":
                            del data["przepisy"][item["recipe_idx"]]["zdjecia"][item["img_idx_in_recipe"]]
                        else:
                            del data["galeria_extra"][item["img_idx_in_recipe"]]
                        save_data(data)
                        st.rerun()
