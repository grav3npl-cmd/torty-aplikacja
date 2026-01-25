import streamlit as st
import json
import os
import pandas as pd
from datetime import date

# --- KONFIGURACJA ---
DB_FILE = 'baza_cukierni_v12.json'
IMG_FOLDER = 'zdjecia_tortow'
DEFAULT_IMG = 'default_cake.png'  # <--- TU ZAPISZ SWOJE ZDJĘCIE JAKO default_cake.png

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

# --- WYGLĄD (CSS - MOBILE FIX V2) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .stApp { background-color: #121212; color: #ffffff; }
        
        /* === MOBILE FIX: ZAPOBIEGANIE STACKOWANIU KOLUMN === */
        /* To wymusza, żeby kolumny na telefonie były obok siebie (flex), a nie jedna pod drugą (block) */
        div[data-testid="column"] {
            width: auto !important;
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
        
        /* Zdjęcia w kafelkach - stała wysokość */
        .element-container img {
            height: 150px !important; /* Mniejsza wysokość, żeby kafelki były zgrabniejsze */
            object-fit: cover;
            width: 100%;
            border-radius: 8px;
        }

        /* Przyciski Menu */
        .stButton > button { 
            background-color: transparent; 
            color: #ff0aef; 
            border: 2px solid #ff0aef; 
            border-radius: 10px; 
            font-weight: bold;
            padding: 0.2rem 0.1rem; /* Mniejszy padding na boki */
            font-size: 0.85rem;
            width: 100%;
            white-space: nowrap; /* Tekst nie zawija się */
        }
        .stButton > button:hover { 
            background-color: #ff0aef; 
            color: white;
            box-shadow: 0 0 10px rgba(255, 10, 239, 0.5);
        }

        /* Styl Kafelka */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 10px;
            margin-bottom: 10px;
        }

        /* Header */
        .header-title {
            font-size: 1.5rem; font-weight: 900; color: #ff0aef;
            text-align: center; margin-bottom: 5px; margin-top: -20px;
            text-transform: uppercase; letter-spacing: 2px;
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
if 'edit_ing_key' not in st.session_state: st.session_state['edit_ing_key'] = None

data = load_data()

# --- HEADER & MENU ---
st.markdown('<div class="header-title">WK TORTY</div>', unsafe_allow_html=True)

# Dzięki CSS powyżej, te kolumny powinny zostać w jednym rzędzie na telefonie
menu_cols = st.columns(5)
with menu_cols[0]: 
    if st.button("📅 Plan"): st.session_state['menu'] = "Kalendarz"
with menu_cols[1]: 
    if st.button("📖 Torty"): 
        st.session_state['menu'] = "Przepisy"
        st.session_state['fullscreen_recipe'] = None
with menu_cols[2]: 
    if st.button("➕ Nowy"): st.session_state['menu'] = "Dodaj"
with menu_cols[3]: 
    if st.button("📦 Mag"): st.session_state['menu'] = "Magazyn"
with menu_cols[4]: 
    if st.button("🖼️ Foto"): st.session_state['menu'] = "Galeria"

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
                
                if wpis.get('opis'):
                    st.write(wpis['opis'])
                
                if wpis.get('zdjecia'):
                    cols_img = st.columns(4)
                    for j, img_path in enumerate(wpis['zdjecia'][:4]):
                        if os.path.exists(img_path):
                            with cols_img[j]:
                                st.image(img_path) # CSS ustawi wysokość
                
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
            c1.text_input("Nazwa", key="mn")
            c2.number_input("Kcal", key="mk")
            c1.number_input("Waga", key="mw")
            c2.number_input("Cena", key="mp")
            if st.form_submit_button("Zapisz"):
                pass 

    st.write("---")
    
    if data["skladniki"]:
        for k, v in list(data["skladniki"].items()):
            # Edycja
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
                # Widok normalny
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
# 4. PRZEPISY (Z DOMYŚLNYM ZDJĘCIEM)
# ==========================================
elif menu == "Przepisy":
    
    # --- PEŁNY EKRAN ---
    if st.session_state['fullscreen_recipe'] is not None:
        idx = st.session_state['fullscreen_recipe']
        p = data["przepisy"][idx]
        if st.button("⬅️ Wróć"):
            st.session_state['fullscreen_recipe'] = None
            st.rerun()
            
        st.title(p['nazwa'])
        
        # LOGIKA DOMYŚLNEGO ZDJĘCIA
        img_to_show = None
        if p.get('zdjecia') and len(p['zdjecia']) > 0 and os.path.exists(p['zdjecia'][0]):
            img_to_show = p['zdjecia'][0]
        elif os.path.exists(DEFAULT_IMG):
            img_to_show = DEFAULT_IMG
        
        if img_to_show:
            st.image(img_to_show, use_container_width=True)
        
        st.write(f"Cena: **{oblicz_cene_tortu(p, data['skladniki'])} zł**")
        st.write("---")
        formatuj_instrukcje(p['opis'])

    # --- LISTA KAFELKÓW ---
    else:
        st.caption("LISTA PRZEPISÓW")
        search = st.text_input("Szukaj", label_visibility="collapsed", placeholder="Szukaj...")
        
        lista = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        for i, p in enumerate(lista):
            with st.container(border=True):
                # KOLUMNY: OBRAZ (po lewej) | TREŚĆ (po prawej)
                # Dzięki CSS width:auto, na mobile zostaną obok siebie
                c_img, c_info = st.columns([1, 2])
                
                with c_img:
                    # LOGIKA DOMYŚLNEGO ZDJĘCIA
                    if p.get("zdjecia") and os.path.exists(p["zdjecia"][0]):
                        st.image(p["zdjecia"][0])
                    elif os.path.exists(DEFAULT_IMG):
                        st.image(DEFAULT_IMG) # Użyje default_cake.png
                    else:
                        st.write("🍰") # Emoji jeśli nawet defaulta nie ma

                with c_info:
                    st.markdown(f"**{p['nazwa']}**")
                    oc = p.get('oceny', {})
                    avg = (oc.get('wyglad',0) + oc.get('smak',0))/2
                    st.caption(f"{render_stars(avg)}")
                    cena = oblicz_cene_tortu(p, data["skladniki"])
                    st.markdown(f"<span style='color:#00ff00; font-weight:bold'>{cena} zł</span>", unsafe_allow_html=True)
                
                # Przyciski
                st.write("")
                b1, b2 = st.columns(2)
                real_idx = data["przepisy"].index(p)
                
                if b1.button("👁️", key=f"op_{i}"):
                    st.session_state['fullscreen_recipe'] = real_idx
                    st.rerun()
                if b2.button("✏️", key=f"edp_{i}"):
                    st.session_state['edit_recipe_index'] = real_idx
                    st.rerun()

# ==========================================
# 5. GALERIA (BEZ DOMYŚLNEGO ZDJĘCIA)
# ==========================================
elif menu == "Galeria":
    st.caption("GALERIA ZDJĘĆ")
    
    # Tylko zdjęcia, które są FIZYCZNIE w JSON w przepisach lub extra
    # Domyślne zdjęcie (DEFAULT_IMG) nie jest dodawane do tej listy, więc się tu nie pokaże.
    imgs = []
    for p in data["przepisy"]:
        if p.get("zdjecia"): imgs.extend(p["zdjecia"])
    imgs.extend(data["galeria_extra"])
    
    if imgs:
        cols = st.columns(2)
        for i, path in enumerate(imgs):
            with cols[i % 2]:
                if os.path.exists(path):
                    st.image(path)
    else:
        st.info("Brak wgranych zdjęć.")
