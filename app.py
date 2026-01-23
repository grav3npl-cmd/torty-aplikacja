import streamlit as st
import json
import os
import pandas as pd
from datetime import date

# --- KONFIGURACJA ---
DB_FILE = 'baza_cukierni_v12.json'
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
    try: val = int(round(float(value)))
    except: val = 0
    return "⭐" * val + "☆" * (5 - val)

# --- WYGLĄD (CSS - ORYGINALNY PREMIUM) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .stApp { background-color: #121212; color: #ffffff; }
        section[data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }
        
        /* Styl Kafelków (Kolumn) */
        div[data-testid="column"] {
            background-color: #1e1e1e;
            border-radius: 15px;
            padding: 15px;
            border: 1px solid #333;
            transition: transform 0.2s;
        }
        div[data-testid="column"]:hover {
            border-color: #ff0aef;
        }

        /* Przyciski */
        .stButton > button { 
            background-color: transparent; 
            color: #ff0aef; 
            border: 2px solid #ff0aef; 
            border-radius: 25px; 
            font-weight: bold;
            width: 100%;
        }
        .stButton > button:hover { 
            background-color: #ff0aef; 
            color: white;
            box-shadow: 0 0 15px rgba(255, 10, 239, 0.5);
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
            text-align: center; padding: 20px; margin-bottom: 30px;
            border-bottom: 2px solid #ff0aef;
            background: linear-gradient(180deg, rgba(255,10,239,0.1) 0%, rgba(18,18,18,0) 100%);
        }
        .header-title {
            font-size: 2.5rem; font-weight: 900; color: #ff0aef;
            text-transform: uppercase; letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(255,10,239,0.6);
        }
        
        /* Karty Kalendarza */
        .task-card {
            background-color: #252525; padding: 15px; margin-bottom: 10px;
            border-left: 5px solid #ff0aef; border-radius: 8px;
        }
        .task-done { border-left: 5px solid #00ff00; opacity: 0.6; }
        
        img { border-radius: 10px; object-fit: cover; }
        .price-tag { font-size: 1.5em; font-weight: bold; color: #00ff00; text-align: center; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA ---
if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'edit_order_index' not in st.session_state: st.session_state['edit_order_index'] = None
if 'edit_recipe_index' not in st.session_state: st.session_state['edit_recipe_index'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None
if 'edit_ing_key' not in st.session_state: st.session_state['edit_ing_key'] = None

data = load_data()

# --- HEADER ---
st.markdown(f"""
    <div class="header-box">
        <div class="header-title">WK TORTY</div>
        <div style="color: #ccc;">System Cukierniczy</div>
    </div>
""", unsafe_allow_html=True)

# --- MENU ---
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1: 
    if st.button("📅 Kalendarz"): st.session_state['menu'] = "Kalendarz"
with col_m2: 
    if st.button("📖 Przepisy"): 
        st.session_state['menu'] = "Przepisy"
        st.session_state['fullscreen_recipe'] = None
with col_m3: 
    if st.button("➕ Nowy"): st.session_state['menu'] = "Dodaj"
with col_m4: 
    if st.button("📦 Magazyn"): st.session_state['menu'] = "Magazyn"
with col_m5: 
    if st.button("🖼️ Galeria"): st.session_state['menu'] = "Galeria"

if 'menu' not in st.session_state: st.session_state['menu'] = "Kalendarz"
menu = st.session_state['menu']
st.write("---")

# ==========================================
# 1. KALENDARZ (PO STAREMU - KAFELKI)
# ==========================================
if menu == "Kalendarz":
    st.subheader("📅 Planer Zamówień")
    
    if st.button("➕ Dodaj / Zamknij", type="primary"):
        st.session_state['show_add_order'] = not st.session_state['show_add_order']
        st.session_state['edit_order_index'] = None

    idx_edit = st.session_state['edit_order_index']
    is_edit_mode = idx_edit is not None
    
    if st.session_state['show_add_order'] or is_edit_mode:
        with st.container():
            st.info(f"✏️ Edycja #{idx_edit+1}" if is_edit_mode else "Nowe Zamówienie")
            domyslne = data["kalendarz"][idx_edit] if is_edit_mode else {}

            with st.form("kalendarz_form"):
                c1, c2 = st.columns(2)
                with c1: 
                    d_val = date.fromisoformat(domyslne['data']) if 'data' in domyslne else date.today()
                    data_zamowienia = st.date_input("Data", value=d_val)
                    klient = st.text_input("Klient", value=domyslne.get('klient', ''))
                with c2:
                    lista_nazw = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                    wybrany_tort = st.selectbox("Tort Bazowy", lista_nazw)
                    srednica_zam = st.number_input("Fi (cm)", value=20)

                opis_val = domyslne.get('opis', '').split('[AUTO-WYCENA')[0] if is_edit_mode else ""
                opis_dodatkowy = st.text_area("Szczegóły", value=opis_val)
                uploaded_order_imgs = st.file_uploader("Dodaj zdjęcia", type=['jpg','png'], accept_multiple_files=True)

                if st.form_submit_button("Zapisz Zlecenie"):
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
            styl_klasy = "task-card task-done" if wpis.get("wykonane") else "task-card"
            status_txt = "✅ GOTOWE" if wpis.get("wykonane") else "⏳ OCZEKUJE"
            
            st.markdown(f"""
            <div class="{styl_klasy}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:white;">{wpis['klient']}</h3>
                    <span style="background:#333; padding:5px 10px; border-radius:10px;">{wpis['data']}</span>
                </div>
                <p style="color:#bbb; margin-top:10px; white-space: pre-wrap;">{wpis['opis']}</p>
                <div style="font-weight:bold; color:#ff0aef; margin-top:10px;">{status_txt}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Miniaturki zdjęć
            if wpis.get('zdjecia'):
                cols_img = st.columns(6)
                for j, img_path in enumerate(wpis['zdjecia']):
                    if os.path.exists(img_path):
                        with cols_img[j % 6]:
                            st.image(img_path, use_container_width=True)

            c1, c2, c3 = st.columns([1, 1, 1])
            if c1.button("Zmień Status", key=f"status_{i}"):
                data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                save_data(data)
                st.rerun()
            if c2.button("Edytuj", key=f"edit_{i}"):
                st.session_state['edit_order_index'] = i
                st.session_state['show_add_order'] = False 
                st.rerun()
            if c3.button("Usuń", key=f"del_{i}"):
                data["kalendarz"].pop(i)
                save_data(data)
                st.rerun()

# ==========================================
# 2. MAGAZYN (PO STAREMU + EDYCJA)
# ==========================================
elif menu == "Magazyn":
    st.subheader("📦 Magazyn Składników")
    
    with st.expander("➕ Dodaj nowy produkt"):
        with st.form("magazyn_add"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: new_name = st.text_input("Nazwa")
            with c2: new_kcal = st.number_input("Kcal/100g", min_value=0)
            with c3: new_weight = st.number_input("Opak (g)", min_value=1)
            with c4: new_price = st.number_input("Cena", min_value=0.01)
            
            if st.form_submit_button("Zapisz"):
                if new_name:
                    data["skladniki"][new_name] = {
                        "cena": new_price, 
                        "waga_opakowania": new_weight,
                        "kcal": new_kcal
                    }
                    save_data(data)
                    st.rerun()
    
    st.write("---")
    
    # LISTA
    if data["skladniki"]:
        for k, v in list(data["skladniki"].items()):
            # TRYB EDYCJI
            if st.session_state['edit_ing_key'] == k:
                with st.container():
                    st.markdown(f"✏️ **{k}**")
                    with st.form(f"edit_{k}"):
                        ec1, ec2, ec3 = st.columns(3)
                        ek = ec1.number_input("Kcal", value=v['kcal'])
                        ew = ec2.number_input("Waga", value=v['waga_opakowania'])
                        ec = ec3.number_input("Cena", value=v['cena'])
                        if st.form_submit_button("Zapisz"):
                            data["skladniki"][k] = {"cena": ec, "waga_opakowania": ew, "kcal": ek}
                            save_data(data)
                            st.session_state['edit_ing_key'] = None
                            st.rerun()
            else:
                # TRYB PODGLĄDU - zwykłe kolumny jak dawniej
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
                c1.write(f"**{k}**")
                c2.write(f"{v['kcal']} kcal")
                c3.write(f"{v['waga_opakowania']} g")
                c4.write(f"{v['cena']} zł")
                
                with c5:
                    be, bd = st.columns(2)
                    if be.button("✏️", key=f"e_{k}"):
                        st.session_state['edit_ing_key'] = k
                        st.rerun()
                    if bd.button("❌", key=f"d_{k}"):
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

    st.subheader("🍰 Kreator Przepisu")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 1. Składniki")
        with st.container():
            wybran = st.selectbox("Produkt", list(data["skladniki"].keys()))
            ilo = st.number_input("Ilość (g/szt)", min_value=0, step=1, format="%d")
            if st.button("Dodaj"):
                if ilo > 0:
                    current_val = st.session_state['temp_skladniki'].get(wybran, 0)
                    st.session_state['temp_skladniki'][wybran] = current_val + ilo
                    st.rerun()
        
        if st.session_state['temp_skladniki']:
            st.write("---")
            for k, v in list(st.session_state['temp_skladniki'].items()):
                cc1, cc2 = st.columns([3,1])
                cc1.write(f"**{k}**: {v}")
                if cc2.button("X", key=f"del_t_{k}"):
                    del st.session_state['temp_skladniki'][k]
                    st.rerun()

    with col_right:
        st.markdown("### 2. Dane i Opis")
        with st.form("glowny_przepis_form"):
            nazwa_przepisu = st.text_input("Nazwa Tortu")
            opis = st.text_area("Instrukcja", height=200)
            uploaded_files = st.file_uploader("Zdjęcia", accept_multiple_files=True)
            
            c_d1, c_d2, c_d3, c_d4 = st.columns(4)
            srednica = c_d1.number_input("Fi (cm)", 15)
            marza = c_d2.number_input("Marża %", 10)
            czas = c_d3.number_input("Czas (min)", 180)
            stawka_h = c_d4.number_input("Stawka/h", 20)
            
            st.write("Oceny:")
            o1, o2, o3 = st.columns(3)
            s_look = o1.slider("Wygląd", 1, 5, 5)
            s_taste = o2.slider("Smak", 1, 5, 5)
            s_diff = o3.slider("Trudność", 1, 5, 3)
            
            if st.form_submit_button("ZAPISZ PRZEPIS"):
                if nazwa_przepisu and st.session_state['temp_skladniki']:
                    saved_imgs = save_uploaded_files(uploaded_files)
                    nowy = {
                        "nazwa": nazwa_przepisu, "opis": opis, "zdjecia": saved_imgs,
                        "srednica": srednica, "skladniki_przepisu": st.session_state['temp_skladniki'],
                        "oceny": {"wyglad": s_look, "smak": s_taste, "trudnosc": s_diff},
                        "marza": marza, "czas": czas, "stawka_h": stawka_h
                    }
                    data["przepisy"].append(nowy)
                    save_data(data)
                    st.session_state['temp_skladniki'] = {}
                    st.session_state['success_msg'] = f"Dodano: {nazwa_przepisu}"
                    st.rerun()

# ==========================================
# 4. PRZEPISY
# ==========================================
elif menu == "Przepisy":
    
    # --- EDYCJA (Zachowana funkcjonalność) ---
    if st.session_state['edit_recipe_index'] is not None:
        idx = st.session_state['edit_recipe_index']
        p_edit = data["przepisy"][idx]
        cur_oc = p_edit.get('oceny', {'wyglad':5,'smak':5,'trudnosc':3})
        
        st.subheader(f"✏️ Edycja: {p_edit['nazwa']}")
        if st.button("⬅️ Anuluj"):
            st.session_state['edit_recipe_index'] = None
            st.rerun()
            
        with st.form("edit_recipe_form"):
            e_nazwa = st.text_input("Nazwa", value=p_edit['nazwa'])
            e_opis = st.text_area("Instrukcja", value=p_edit['opis'], height=200)
            
            ec1, ec2, ec3, ec4 = st.columns(4)
            e_srednica = ec1.number_input("Fi", value=p_edit.get('srednica', 15))
            e_marza = ec2.number_input("Marża", value=p_edit.get('marza', 10))
            e_czas = ec3.number_input("Czas", value=p_edit.get('czas', 180))
            e_stawka = ec4.number_input("Stawka", value=p_edit.get('stawka_h', 20))
            
            st.write("Edycja Ocen:")
            eo1, eo2, eo3 = st.columns(3)
            el = eo1.slider("Wygląd", 1, 5, cur_oc.get('wyglad', 5))
            et = eo2.slider("Smak", 1, 5, cur_oc.get('smak', 5))
            ed = eo3.slider("Trudność", 1, 5, cur_oc.get('trudnosc', 3))

            st.write("Zdjęcia:")
            keep = []
            if p_edit.get('zdjecia'):
                cols_p = st.columns(4)
                for i, ph in enumerate(p_edit['zdjecia']):
                    with cols_p[i % 4]:
                        st.image(ph, use_container_width=True)
                        if not st.checkbox("Usuń", key=f"del_img_{i}"):
                            keep.append(ph)
            
            new_imgs = st.file_uploader("Dodaj nowe", accept_multiple_files=True)
            
            if st.form_submit_button("Zapisz Zmiany"):
                p_edit.update({
                    "nazwa": e_nazwa, "opis": e_opis, "srednica": e_srednica,
                    "marza": e_marza, "czas": e_czas, "stawka_h": e_stawka,
                    "oceny": {"wyglad": el, "smak": et, "trudnosc": ed},
                    "zdjecia": keep + save_uploaded_files(new_imgs)
                })
                data["przepisy"][idx] = p_edit
                save_data(data)
                st.session_state['edit_recipe_index'] = None
                st.rerun()

    # --- PEŁNY EKRAN ---
    elif st.session_state['fullscreen_recipe'] is not None:
        idx = st.session_state['fullscreen_recipe']
        przepis = data["przepisy"][idx]
        
        if st.button("⬅️ WRÓĆ DO LISTY", type="primary"):
            st.session_state['fullscreen_recipe'] = None
            st.rerun()
            
        st.title(przepis['nazwa'].upper())
        oceny = przepis.get('oceny', {})
        st.markdown(f"🎨 {render_stars(oceny.get('wyglad',0))} | 🤤 {render_stars(oceny.get('smak',0))} | 🤯 {render_stars(oceny.get('trudnosc',0))}")

        c_img, c_det = st.columns([1,1])
        with c_img:
            if przepis.get("zdjecia"): st.image(przepis["zdjecia"][0])
        
        with c_det:
            target_cm = st.number_input("Przelicz na średnicę (cm):", value=przepis.get('srednica', 20))
            cena = oblicz_cene_tortu(przepis, data["skladniki"], target_cm)
            st.markdown(f"<div class='price-tag'>{cena} PLN</div>", unsafe_allow_html=True)
            
            st.write("Składniki:")
            wsp = (target_cm / przepis.get('srednica', 20))**2
            for sk, il in przepis["skladniki_przepisu"].items():
                st.write(f"- {sk}: {il*wsp:.0f}")

        st.write("---")
        formatuj_instrukcje(przepis['opis'])
        
        if len(przepis.get('zdjecia', [])) > 1:
            st.write("Galeria:")
            gc = st.columns(4)
            for i, p in enumerate(przepis['zdjecia']):
                with gc[i%4]: st.image(p, use_container_width=True)

    # --- GRID (SIATKA - tak jak chciałeś) ---
    else:
        st.subheader("📖 Książka Kucharska")
        search = st.text_input("🔍 Szukaj...")
        
        lista = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        cols = st.columns(3) # SIATKA! 3 kolumny
        for index, przepis in enumerate(lista):
            with cols[index % 3]: # Układanie w kafelkach
                cena_est = oblicz_cene_tortu(przepis, data["skladniki"])
                oceny = przepis.get('oceny', {})
                avg = (oceny.get('wyglad',0) + oceny.get('smak',0))/2
                
                if przepis.get("zdjecia"):
                    st.image(przepis["zdjecia"][0], use_container_width=True)
                else:
                    st.write("Brak Foto")
                
                st.markdown(f"<h3 style='text-align:center; color:#ff0aef; margin:5px;'>{przepis['nazwa']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; color:#FFD700;'>{render_stars(avg)}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-weight:bold; color:#00ff00; margin-bottom:10px;'>{cena_est} PLN</div>", unsafe_allow_html=True)
                
                real_idx = data["przepisy"].index(przepis)
                b1, b2 = st.columns(2)
                if b1.button("👁️", key=f"open_{index}"):
                    st.session_state['fullscreen_recipe'] = real_idx
                    st.rerun()
                if b2.button("✏️", key=f"edit_p_{index}"):
                    st.session_state['edit_recipe_index'] = real_idx
                    st.rerun()

# ==========================================
# 5. GALERIA (2 Kolumny - bezpieczny wybór)
# ==========================================
elif menu == "Galeria":
    st.subheader("🖼️ Galeria Tortów")
    
    with st.expander("📷 Dodaj zdjęcie do przepisu"):
        c1, c2 = st.columns(2)
        wybor = c1.selectbox("Przepis", [p['nazwa'] for p in data['przepisy']])
        plik = c2.file_uploader("Foto", type=['jpg','png'])
        if st.button("Dodaj"):
            if wybor and plik:
                path = save_uploaded_files([plik])[0]
                for p in data['przepisy']:
                    if p['nazwa'] == wybor:
                        if 'zdjecia' not in p: p['zdjecia'] = []
                        p['zdjecia'].append(path)
                        save_data(data)
                        st.success("Dodano!")
                        st.rerun()
                        break

    imgs = []
    for idx, p in enumerate(data["przepisy"]):
        if p.get("zdjecia"):
            for i, f in enumerate(p["zdjecia"]):
                imgs.append({'src':f, 'name':p['nazwa'], 'rid':idx, 'iid':i, 'type':'recipe'})
    for i, f in enumerate(data["galeria_extra"]):
        imgs.append({'src':f, 'name':'Extra', 'rid':None, 'iid':i, 'type':'extra'})

    if imgs:
        gc = st.columns(2) # 2 kolumny wyglądają ok na mobile i desktop
        for i, item in enumerate(imgs):
            with gc[i % 2]:
                if os.path.exists(item['src']):
                    st.image(item['src'], use_container_width=True)
                    c1, c2 = st.columns(2)
                    if item['type'] == 'recipe':
                        if c1.button("➜", key=f"g_{i}"):
                            st.session_state['menu'] = "Przepisy"
                            st.session_state['fullscreen_recipe'] = item['rid']
                            st.rerun()
                        if c2.button("🗑️", key=f"gd_{i}"):
                            del data["przepisy"][item['rid']]["zdjecia"][item['iid']]
                            save_data(data)
                            st.rerun()
                    else:
                         if c2.button("🗑️", key=f"gd_{i}"):
                            del data["galeria_extra"][item['iid']]
                            save_data(data)
                            st.rerun()
