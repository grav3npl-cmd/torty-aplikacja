import streamlit as st
import json
import os
import pandas as pd
from datetime import date
import time

# --- KONFIGURACJA ---
DB_FILE = 'baza_cukierni_v10.json'
IMG_FOLDER = 'zdjecia_tortow'
LOGO_FILE = "logo_wk_torty.png" 

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
            "kalendarz": []
        }
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in data["skladniki"].items():
            if "kcal" not in v: v["kcal"] = 0
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

def oblicz_cene_tortu(przepis, data_db, srednica_docelowa=None):
    if srednica_docelowa is None:
        srednica_docelowa = przepis.get('srednica', 15)
    
    baza_cm = przepis.get('srednica', 15)
    wsp = (srednica_docelowa / baza_cm) ** 2
    
    koszt_skladnikow = 0
    for sk, il in przepis["skladniki_przepisu"].items():
        if sk in data_db["skladniki"]:
            info = data_db["skladniki"][sk]
            cena_g = info["cena"] / info["waga_opakowania"]
            koszt_skladnikow += (cena_g * il * wsp)
            
    marza_proc = przepis.get('marza', 10)
    czas_min = przepis.get('czas', 180)
    stawka = przepis.get('stawka', 20)
    
    koszt_pracy = (czas_min / 60) * stawka
    cena_koncowa = koszt_skladnikow * (1 + marza_proc/100) + koszt_pracy
    return cena_koncowa

# --- CSS (NAPRAWIONA NAWIGACJA) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .stApp { background-color: #121212; color: #ffffff; }
        
        /* --- NAWIGACJA (RADIO BUTTONS JAKO KAFELKI) --- */
        .stRadio > div {
            display: flex;
            justify-content: center;
            gap: 10px;
            width: 100%;
            overflow-x: auto; /* Przewijanie na małych ekranach */
            padding-bottom: 5px;
        }
        
        /* Wygląd pojedynczego przycisku menu */
        .stRadio > div > label {
            background-color: #1e1e1e !important;
            border: 1px solid #333 !important;
            padding: 10px 20px !important;
            border-radius: 20px !important;
            cursor: pointer;
            transition: all 0.3s;
            color: #ffffff !important;
            font-weight: bold !important;
            min-width: 100px;
            text-align: center;
        }
        
        /* Aktywny przycisk menu (Różowy) */
        .stRadio > div > label[data-checked="true"] {
            background-color: #ff0aef !important;
            color: white !important;
            border-color: #ff0aef !important;
            box-shadow: 0 0 15px rgba(255, 10, 239, 0.4);
        }
        
        /* Ukrycie kropki radio buttona */
        .stRadio div[role='radiogroup'] > label > div:first-child {
            display: none !important;
        }

        /* --- STYLIZACJA PRZYCISKÓW AKCJI --- */
        .stButton > button { 
            background-color: #ff0aef; 
            color: white; 
            border: none;
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
            padding: 0.5rem 1rem;
            margin-top: 5px;
        }
        .stButton > button:hover { 
            background-color: #c900bc; 
        }

        /* PRZYCISK USUWANIA (OKRĄGŁY X) */
        button[kind="secondary"] {
            background-color: transparent !important;
            border: 1px solid red !important;
            color: red !important;
            border-radius: 50% !important;
            width: 38px !important;
            height: 38px !important;
            min-width: 38px !important;
            padding: 0 !important;
            margin: 0 auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        /* INNE */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea, 
        .stNumberInput > div > div > input, .stSelectbox > div > div > div { 
            background-color: #2c2c2c !important; color: white !important; border-radius: 8px; border:none;
        }
        
        .header-box { text-align: center; margin-bottom: 10px; border-bottom: 2px solid #ff0aef; padding-bottom: 10px; }
        .header-title { font-size: 1.8rem; font-weight: 900; color: #ff0aef; letter-spacing: 2px; }
        
        .price-tag { font-size: 1.3rem; font-weight: 900; color: #00ff00; text-align: center; margin: 5px 0; }
        .recipe-img { width: 100%; height: 100px; object-fit: cover; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- STAN ---
if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'edit_order_idx' not in st.session_state: st.session_state['edit_order_idx'] = None
if 'edit_recipe_idx' not in st.session_state: st.session_state['edit_recipe_idx'] = None
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None
# Domyślne menu w session state
if 'current_view' not in st.session_state: st.session_state['current_view'] = "Kalendarz"

data = load_data()

# --- HEADER ---
st.markdown(f"""<div class="header-box"><div class="header-title">WK TORTY</div></div>""", unsafe_allow_html=True)

if st.session_state['success_msg']:
    st.info(f"✅ {st.session_state['success_msg']}")
    st.session_state['success_msg'] = None

# --- NAWIGACJA (POZIOMA) ---
# Używamy st.radio zamiast buttonów - to klucz do naprawy wyglądu na mobile
opcje_menu = ["Kalendarz", "Przepisy", "Dodaj", "Magazyn", "Galeria"]
ikony_menu = ["📅", "📖", "➕", "📦", "🖼️"]

# Mapowanie nazwy na ikonę (dla czytelności)
def format_func(option):
    idx = opcje_menu.index(option)
    # Jeśli jesteśmy w trybie edycji, zmień nazwę "Dodaj" na "Edytuj"
    if option == "Dodaj" and st.session_state['edit_recipe_idx'] is not None:
        return "✏️ Edytuj"
    return f"{ikony_menu[idx]} {option}"

wybrana_zakladka = st.radio(
    "", 
    opcje_menu, 
    index=opcje_menu.index(st.session_state['current_view']),
    format_func=format_func,
    horizontal=True,
    label_visibility="collapsed",
    key="nav_radio"
)

# Aktualizacja stanu widoku na podstawie radia
if wybrana_zakladka != st.session_state['current_view']:
    st.session_state['current_view'] = wybrana_zakladka
    # Jeśli zmieniamy zakładkę ręcznie, resetujemy fullscreen
    if wybrana_zakladka != "Dodaj": 
        st.session_state['fullscreen_recipe'] = None
    st.rerun()

menu = st.session_state['current_view']

# ==========================================
# 1. KALENDARZ
# ==========================================
if menu == "Kalendarz":
    st.subheader("📅 Planer Zamówień")
    
    is_editing = st.session_state['edit_order_idx'] is not None
    
    def_date = date.today()
    def_client = ""
    def_desc = ""
    def_imgs = []
    
    if is_editing:
        idx = st.session_state['edit_order_idx']
        order = data["kalendarz"][idx]
        st.info(f"Edytujesz: {order['klient']}")
        def_date = pd.to_datetime(order['data']).date()
        def_client = order['klient']
        def_desc = order['opis']
        def_imgs = order.get('zdjecia', [])
    
    with st.expander("📝 Formularz", expanded=is_editing):
        with st.form("kalendarz_form"):
            c1, c2 = st.columns(2)
            with c1: 
                data_zamowienia = st.date_input("Data", value=def_date)
                klient = st.text_input("Klient", value=def_client)
            with c2:
                lista_nazw = ["-"] + [p["nazwa"] for p in data["przepisy"]]
                wybrany_tort = st.selectbox("Tort (opcja)", lista_nazw)
                srednica_zam = st.number_input("Średnica", value=20)

            opis_tortu = st.text_area("Szczegóły", value=def_desc)
            new_imgs = st.file_uploader("Zdjęcia", accept_multiple_files=True)
            
            if is_editing and def_imgs:
                st.write("Obecne zdjęcia:")
                icols = st.columns(6)
                for i, p in enumerate(def_imgs):
                    if os.path.exists(p): icols[i%6].image(p, width=50)

            btn_txt = "Zapisz Zmiany" if is_editing else "Dodaj Zamówienie"
            
            if st.form_submit_button(btn_txt):
                info_cenowe = ""
                if wybrany_tort != "-":
                    przepis = next((p for p in data["przepisy"] if p["nazwa"] == wybrany_tort), None)
                    if przepis:
                        cena = oblicz_cene_tortu(przepis, data, srednica_zam)
                        info_cenowe = f"\n[Tort: {wybrany_tort} fi{srednica_zam}cm | ~{cena:.2f} zł]"

                full_opis = f"{opis_tortu}{info_cenowe}" if not is_editing else opis_tortu
                if wybrany_tort != "-" and is_editing: full_opis += info_cenowe

                saved_paths = save_uploaded_files(new_imgs)
                final_imgs = def_imgs + saved_paths
                
                wpis = {
                    "data": str(data_zamowienia), "klient": klient, 
                    "opis": full_opis, "wykonane": False, "zdjecia": final_imgs
                }
                
                if is_editing:
                    wpis["wykonane"] = data["kalendarz"][idx]["wykonane"]
                    data["kalendarz"][idx] = wpis
                    st.session_state['edit_order_idx'] = None
                    st.session_state['success_msg'] = "Zaktualizowano!"
                else:
                    data["kalendarz"].append(wpis)
                    st.session_state['success_msg'] = "Dodano!"
                
                data["kalendarz"] = sorted(data["kalendarz"], key=lambda x: x['data'])
                save_data(data)
                st.rerun()
                
        if is_editing:
            if st.button("Anuluj"):
                st.session_state['edit_order_idx'] = None
                st.rerun()

    if not data["kalendarz"]:
        st.info("Brak zleceń.")
    else:
        for i, wpis in enumerate(data["kalendarz"]):
            bg = "#1a3a1a" if wpis.get("wykonane") else "#252525"
            border = "#00ff00" if wpis.get("wykonane") else "#ff0aef"
            icon = "✅" if wpis.get("wykonane") else "⏳"

            with st.container():
                st.markdown(f"""
                <div style="background-color:{bg}; padding:10px; margin-bottom:10px; border-left:5px solid {border}; border-radius:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:white;">{icon} {wpis['klient']}</h4>
                        <span style="background:#333; padding:2px 8px; border-radius:5px; font-size:0.8em;">{wpis['data']}</span>
                    </div>
                    <p style="color:#ccc; margin-top:5px; font-size:0.9em; white-space: pre-wrap;">{wpis['opis']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                imgs = wpis.get("zdjecia", [])
                if imgs:
                    with st.expander(f"📷 Zdjęcia ({len(imgs)})"):
                        cols_p = st.columns(4)
                        for j, path in enumerate(imgs):
                            if os.path.exists(path):
                                cols_p[j % 4].image(path)

                c1, c2, c3 = st.columns([1, 1, 3])
                btn_label = "Cofnij" if wpis.get("wykonane") else "Gotowe"
                if c1.button(btn_label, key=f"s_{i}"):
                    data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                    save_data(data)
                    st.rerun()
                if c2.button("Edytuj", key=f"e_{i}"):
                    st.session_state['edit_order_idx'] = i
                    st.rerun()
                if c3.button("Usuń", key=f"d_{i}"):
                    data["kalendarz"].pop(i)
                    save_data(data)
                    st.rerun()

# ==========================================
# 2. MAGAZYN
# ==========================================
elif menu == "Magazyn":
    st.subheader("📦 Magazyn")
    
    if data["skladniki"]:
        tabela = []
        for nazwa, info in data["skladniki"].items():
            tabela.append({
                "Produkt": nazwa, "Waga (g)": info["waga_opakowania"],
                "Kcal": info["kcal"], "Cena": info["cena"]
            })
        st.dataframe(pd.DataFrame(tabela), use_container_width=True, hide_index=True)
    
    with st.form("magazyn_add"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: new_name = st.text_input("Nazwa")
        with c2: new_weight = st.number_input("Waga", min_value=1, step=1)
        with c3: new_kcal = st.number_input("Kcal", min_value=0, step=1)
        with c4: new_price = st.number_input("Cena", min_value=0.01, step=0.5)
        
        if st.form_submit_button("Zapisz"):
            if new_name:
                data["skladniki"][new_name] = {"cena": new_price, "waga_opakowania": new_weight, "kcal": new_kcal}
                save_data(data)
                st.session_state['success_msg'] = f"Zapisano: {new_name}"
                st.rerun()

# ==========================================
# 3. DODAJ / EDYTUJ
# ==========================================
elif menu == "Dodaj":
    edit_idx = st.session_state['edit_recipe_idx']
    is_edit_mode = edit_idx is not None
    naglowek = f"✏️ Edycja" if is_edit_mode else "➕ Nowy"
    st.subheader(naglowek)
    
    if is_edit_mode and 'edit_loaded' not in st.session_state:
        p = data["przepisy"][edit_idx]
        st.session_state['form_nazwa'] = p['nazwa']
        st.session_state['form_opis'] = p['opis']
        st.session_state['form_srednica'] = p.get('srednica', 15)
        st.session_state['form_marza'] = p.get('marza', 10)
        st.session_state['form_czas'] = p.get('czas', 180)
        st.session_state['form_stawka'] = p.get('stawka', 20)
        st.session_state['form_oceny'] = p.get('oceny', {'wyglad':5, 'smak':5, 'trudnosc':3})
        st.session_state['temp_skladniki'] = p['skladniki_przepisu'].copy()
        st.session_state['edit_loaded'] = True
    
    if not is_edit_mode and 'form_nazwa' not in st.session_state:
        st.session_state['form_nazwa'] = ""
        st.session_state['form_opis'] = ""
        st.session_state['form_srednica'] = 15
        st.session_state['form_marza'] = 10
        st.session_state['form_czas'] = 180
        st.session_state['form_stawka'] = 20
        st.session_state['form_oceny'] = {'wyglad':5, 'smak':5, 'trudnosc':3}

    c_left, c_right = st.columns([1, 1])
    
    with c_left:
        st.markdown("##### 1. Składniki")
        with st.form("skladniki_form"):
            wybran = st.selectbox("Wybierz", list(data["skladniki"].keys()))
            krok = 1.0 if ("szt" in wybran.lower() or "jaja" in wybran.lower()) else 1.0
            ilo = st.number_input("Ilość", min_value=0.0, step=krok)
            
            if st.form_submit_button("Dodaj"):
                obecna = st.session_state['temp_skladniki'].get(wybran, 0)
                st.session_state['temp_skladniki'][wybran] = obecna + ilo
                st.rerun()
        
        if st.session_state['temp_skladniki']:
            for k, v in st.session_state['temp_skladniki'].items():
                cc1, cc2 = st.columns([3,1])
                cc1.caption(f"{k}: {v}")
                if cc2.button("X", key=f"del_{k}", type="secondary"):
                    del st.session_state['temp_skladniki'][k]
                    st.rerun()

    with c_right:
        st.markdown("##### 2. Opis")
        with st.form("glowny_przepis_form"):
            nazwa_przepisu = st.text_input("Nazwa", value=st.session_state.get('form_nazwa', ''))
            opis = st.text_area("Instrukcja", height=100, value=st.session_state.get('form_opis', ''))
            uploaded_files = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
            
            c_d1, c_d2 = st.columns(2)
            with c_d1: 
                srednica = st.number_input("Średnica", value=st.session_state.get('form_srednica', 15))
                marza = st.number_input("Marża %", value=st.session_state.get('form_marza', 10))
            with c_d2:
                czas = st.number_input("Czas (min)", value=st.session_state.get('form_czas', 180))
                stawka = st.number_input("Stawka", value=st.session_state.get('form_stawka', 20))
            
            st.write("Oceny:")
            oc = st.session_state.get('form_oceny', {})
            oc1, oc2, oc3 = st.columns(3)
            with oc1: s_look = st.slider("Wygląd", 1, 5, oc.get('wyglad', 5))
            with oc2: s_taste = st.slider("Smak", 1, 5, oc.get('smak', 5))
            with oc3: s_diff = st.slider("Trudność", 1, 5, oc.get('trudnosc', 3))
            
            btn_txt = "ZAPISZ" if is_edit_mode else "DODAJ"
            if st.form_submit_button(btn_txt):
                if not nazwa_przepisu:
                    st.error("Brak nazwy!")
                else:
                    new_imgs = save_uploaded_files(uploaded_files)
                    final_imgs = new_imgs
                    if is_edit_mode:
                        old_imgs = data["przepisy"][edit_idx].get("zdjecia", [])
                        final_imgs = old_imgs + new_imgs

                    nowy = {
                        "nazwa": nazwa_przepisu, "opis": opis, "zdjecia": final_imgs,
                        "srednica": srednica, "skladniki_przepisu": st.session_state['temp_skladniki'],
                        "oceny": {"wyglad": s_look, "smak": s_taste, "trudnosc": s_diff},
                        "marza": marza, "czas": czas, "stawka": stawka
                    }
                    
                    if is_edit_mode:
                        data["przepisy"][edit_idx] = nowy
                        st.session_state['edit_recipe_idx'] = None
                        st.session_state['current_view'] = "Przepisy" # Powrót
                        st.session_state['success_msg'] = "Zapisano!"
                        if 'edit_loaded' in st.session_state: del st.session_state['edit_loaded']
                    else:
                        data["przepisy"].append(nowy)
                        st.session_state['success_msg'] = "Dodano!"
                    
                    save_data(data)
                    st.session_state['temp_skladniki'] = {}
                    st.session_state['form_nazwa'] = ""
                    st.session_state['form_opis'] = ""
                    st.rerun()
    
    if is_edit_mode:
        if st.button("Anuluj"):
            st.session_state['edit_recipe_idx'] = None
            st.session_state['current_view'] = "Przepisy"
            if 'edit_loaded' in st.session_state: del st.session_state['edit_loaded']
            st.session_state['temp_skladniki'] = {}
            st.rerun()

# ==========================================
# 4. PRZEPISY
# ==========================================
elif menu == "Przepisy":
    
    if st.session_state['fullscreen_recipe'] is not None:
        idx = st.session_state['fullscreen_recipe']
        przepis = data["przepisy"][idx]
        
        c_back, c_edit = st.columns([3, 1])
        with c_back:
            if st.button("⬅️ WRÓĆ"):
                st.session_state['fullscreen_recipe'] = None
                st.rerun()
        with c_edit:
            if st.button("✏️ Edytuj"):
                st.session_state['edit_recipe_idx'] = idx
                st.session_state['current_view'] = "Dodaj"
                st.session_state['fullscreen_recipe'] = None
                st.rerun()
            
        st.title(przepis['nazwa'])
        oc = przepis.get('oceny', {})
        st.markdown(f"🎨 {oc.get('wyglad')}/5 | 🤤 {oc.get('smak')}/5 | 🤯 {oc.get('trudnosc')}/5")
        
        col_img, col_det = st.columns([1, 1])
        with col_img:
            imgs = przepis.get("zdjecia", [])
            if imgs: st.image(imgs[0])
            else: st.info("Brak zdjęcia")

        with col_det:
            cena = oblicz_cene_tortu(przepis, data)
            st.markdown(f'<div class="price-tag">Cena (fi{przepis.get("srednica")}cm): {cena:.2f} zł</div>', unsafe_allow_html=True)
            st.markdown("#### Składniki:")
            for sk, il in przepis["skladniki_przepisu"].items():
                st.write(f"• {sk}: **{il}**")

        st.write("---")
        formatuj_instrukcje(przepis['opis'])
        
        if imgs:
            st.write("---")
            cols_mini = st.columns(6)
            for i, pth in enumerate(imgs):
                cols_mini[i % 6].image(pth)

    else:
        st.subheader("📖 Przepisy")
        search = st.text_input("🔍 Szukaj...")
        
        pokaz = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        cols = st.columns(4) 
        for index, przepis in enumerate(pokaz):
            with cols[index % 4]:
                imgs = przepis.get("zdjecia", [])
                if imgs and os.path.exists(imgs[0]):
                    import base64
                    with open(imgs[0], "rb") as f:
                        enc = base64.b64encode(f.read()).decode()
                    st.markdown(f'<img src="data:image/png;base64,{enc}" class="recipe-img">', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="recipe-img" style="background:#333; display:flex; align-items:center; justify-content:center;">BRAK</div>', unsafe_allow_html=True)
                
                st.markdown(f"<h5 style='text-align:center; color:#ff0aef; margin:5px 0;'>{przepis['nazwa']}</h5>", unsafe_allow_html=True)
                
                oc = przepis.get('oceny', {})
                cena = oblicz_cene_tortu(przepis, data)
                st.markdown(f"<div style='text-align:center; font-size:0.8em;'>🎨{oc.get('wyglad')} 🤤{oc.get('smak')} 💰{cena:.0f}zł</div>", unsafe_allow_html=True)
                
                if st.button("OTWÓRZ", key=f"open_{index}"):
                    real_idx = data["przepisy"].index(przepis)
                    st.session_state['fullscreen_recipe'] = real_idx
                    st.rerun()

# ==========================================
# 5. GALERIA
# ==========================================
elif menu == "Galeria":
    st.subheader("🖼️ Galeria")
    
    wszystkie = []
    for idx, p in enumerate(data["przepisy"]):
        if p.get("zdjecia"):
            for fotka in p["zdjecia"]:
                wszystkie.append({"src": fotka, "idx": idx, "name": p["nazwa"], "obj": p})
    
    if not wszystkie:
        st.info("Brak zdjęć.")
    else:
        g_cols = st.columns(4)
        for i, item in enumerate(wszystkie):
            with g_cols[i % 4]:
                if os.path.exists(item["src"]):
                    st.image(item["src"], use_container_width=True)
                    
                    c_g1, c_g2 = st.columns(2)
                    with c_g1:
                        if st.button("Idź", key=f"g_go_{i}"):
                            st.session_state['fullscreen_recipe'] = item["idx"]
                            st.session_state['current_view'] = "Przepisy"
                            st.rerun()
                    with c_g2:
                        if st.button("Info", key=f"g_inf_{i}"):
                            p = item["obj"]
                            c = oblicz_cene_tortu(p, data)
                            o = p.get('oceny', {})
                            st.info(f"**{p['nazwa']}**\n💰 {c:.0f} zł\n🎨 {o.get('wyglad')} 🤤 {o.get('smak')} 🤯 {o.get('trudnosc')}")
