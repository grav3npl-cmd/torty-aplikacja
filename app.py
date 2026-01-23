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
    if st.button("📅 Plan"): st.session_state['menu'] = "Kalendarz"
with menu_cols[1]: 
    if st.button("📖 Przep"): 
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
    st.subheader("📅 Planer Zamówień")
    
    if st.button("➕ Dodaj / Zamknij", type="primary"):
        st.session_state['show_add_order'] = not st.session_state['show_add_order']
        st.session_state['edit_order_index'] = None

    idx_edit = st.session_state['edit_order_index']
    is_edit_mode = idx_edit is not None
    
    if st.session_state['show_add_order'] or is_edit_mode:
        with st.container(border=True):
            st.info(f"✏️ Edycja #{idx_edit+1}" if is_edit_mode else "Nowe Zamówienie")
            domyslne = data["kalendarz"][idx_edit] if is_edit_mode else {}

            with st.form("kalendarz_form"):
                # Dzielimy na 2 kolumny, na mobile ładnie się zestackują
                d_val = date.fromisoformat(domyslne['data']) if 'data' in domyslne else date.today()
                data_zamowienia = st.date_input("Data", value=d_val)
                klient = st.text_input("Klient", value=domyslne.get('klient', ''))
                
                lista_nazw = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                wybrany_tort = st.selectbox("Tort Bazowy", lista_nazw)
                srednica_zam = st.number_input("Fi (cm)", value=20)

                opis_val = domyslne.get('opis', '').split('[AUTO-WYCENA')[0] if is_edit_mode else ""
                opis_dodatkowy = st.text_area("Szczegóły", value=opis_val)
                uploaded_order_imgs = st.file_uploader("Dodaj zdjęcia", type=['jpg','png'], accept_multiple_files=True)

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
                # Header kafelka
                col_head1, col_head2 = st.columns([3, 1])
                with col_head1:
                    st.markdown(f"### {wpis['klient']}")
                with col_head2:
                    status_icon = "✅" if wpis.get("wykonane") else "⏳"
                    st.markdown(f"<div style='text-align:right; font-size:1.2em;'>{status_icon}</div>", unsafe_allow_html=True)
                
                st.caption(f"Data: {wpis['data']}")
                st.write(wpis['opis'])
                
                if wpis.get('zdjecia'):
                    st.write("---")
                    # Na mobile 4 kolumny to za dużo, dajemy 4 ale Streamlit sam to przeskaluje
                    cols_img = st.columns(4)
                    for j, img_path in enumerate(wpis['zdjecia']):
                        if os.path.exists(img_path):
                            with cols_img[j % 4]:
                                st.image(img_path, use_container_width=True)
                
                st.write("---")
                b1, b2, b3 = st.columns(3)
                if b1.button("Status", key=f"status_{i}"):
                    data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                    save_data(data)
                    st.rerun()
                if b2.button("Edytuj", key=f"edit_{i}"):
                    st.session_state['edit_order_index'] = i
                    st.session_state['show_add_order'] = False 
                    st.rerun()
                if b3.button("Usuń", key=f"del_{i}"):
                    data["kalendarz"].pop(i)
                    save_data(data)
                    st.rerun()

# ==========================================
# 2. MAGAZYN
# ==========================================
elif menu == "Magazyn":
    st.subheader("📦 Magazyn Składników")
    
    with st.expander("➕ Dodaj nowy produkt"):
        with st.form("magazyn_add"):
            # Układ 2x2 lepszy na mobile
            r1c1, r1c2 = st.columns(2)
            with r1c1: new_name = st.text_input("Nazwa")
            with r1c2: new_kcal = st.number_input("Kcal/100g", min_value=0, step=1)
            
            r2c1, r2c2 = st.columns(2)
            with r2c1: new_weight = st.number_input("Opak (g)", min_value=1, step=1)
            with r2c2: new_price = st.number_input("Cena (PLN)", min_value=0.01, step=0.5)
            
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
    
    if data["skladniki"]:
        for k, v in list(data["skladniki"].items()):
            # TRYB EDYCJI DLA POJEDYNCZEGO SKŁADNIKA
            if st.session_state['edit_ing_key'] == k:
                with st.container(border=True):
                    st.markdown(f"✏️ Edytujesz: **{k}**")
                    with st.form(f"edit_ing_form_{k}"):
                        # 2 kolumny na inputy
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            # Nazwa (klucz) jest trudna do zmiany w prostej strukturze JSON bez nadpisywania,
                            # więc tutaj pozwalamy edytować tylko wartości. Zmiana nazwy to usunięcie i dodanie nowego.
                            # e_name = st.text_input("Nazwa", value=k) 
                            e_kcal = st.number_input("Kcal/100g", value=v['kcal'], step=1)
                            e_waga = st.number_input("Opak (g)", value=v['waga_opakowania'], step=1)
                        with ec2:
                            e_cena = st.number_input("Cena (PLN)", value=v['cena'], step=0.5)
                            st.write("") # odstęp
                            st.write("")
                        
                        b_save, b_cancel = st.columns(2)
                        if b_save.form_submit_button("Zapisz"):
                            data["skladniki"][k] = {
                                "cena": e_cena,
                                "waga_opakowania": e_waga,
                                "kcal": e_kcal
                            }
                            save_data(data)
                            st.session_state['edit_ing_key'] = None
                            st.rerun()
                        
                        if b_cancel.form_submit_button("Anuluj"):
                            st.session_state['edit_ing_key'] = None
                            st.rerun()

            # TRYB PODGLĄDU
            else:
                with st.container(border=True):
                    # Na mobile [4,1] jest OK
                    c_info, c_actions = st.columns([3, 1])
                    with c_info:
                        st.markdown(f"#### {k}")
                        # Używamy markdown zamiast caption dla lepszej czytelności na mobile
                        st.markdown(f"Kcal: **{v['kcal']}** | Waga: **{v['waga_opakowania']}g** | Cena: **{v['cena']:.2f} zł**")
                    
                    with c_actions:
                        if st.button("✏️", key=f"edit_btn_{k}"):
                            st.session_state['edit_ing_key'] = k
                            st.rerun()
                        if st.button("🗑️", key=f"del_skl_{k}"):
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

    st.subheader("🍰 Nowy Przepis")
    
    with st.expander("1. Składniki", expanded=True):
        col_list, col_add = st.columns([2, 1])
        with col_add:
            wybran = st.selectbox("Produkt", list(data["skladniki"].keys()))
            ilo = st.number_input("Ilość (g/szt)", min_value=0, step=1, format="%d")
            if st.button("Dodaj"):
                if ilo > 0:
                    current_val = st.session_state['temp_skladniki'].get(wybran, 0)
                    st.session_state['temp_skladniki'][wybran] = current_val + ilo
                    st.rerun()
        
        with col_list:
            if st.session_state['temp_skladniki']:
                st.write("**Lista:**")
                to_remove = []
                for k, v in st.session_state['temp_skladniki'].items():
                    cc1, cc2 = st.columns([3,1])
                    cc1.write(f"- {k}: {v}")
                    if cc2.button("Usuń", key=f"del_t_{k}"):
                        to_remove.append(k)
                if to_remove:
                    for k in to_remove: del st.session_state['temp_skladniki'][k]
                    st.rerun()
            else:
                st.caption("Brak składników")

    with st.form("glowny_przepis_form"):
        st.markdown("### 2. Szczegóły")
        nazwa_przepisu = st.text_input("Nazwa Tortu")
        opis = st.text_area("Instrukcja", height=150)
        uploaded_files = st.file_uploader("Zdjęcia", type=['jpg', 'png'], accept_multiple_files=True)
        
        # 2x2 na mobile
        c_d1, c_d2 = st.columns(2)
        with c_d1: srednica = st.number_input("Fi (cm)", value=15, step=1)
        with c_d2: marza = st.number_input("Marża (%)", value=10, step=5)
        
        c_d3, c_d4 = st.columns(2)
        with c_d3: czas = st.number_input("Czas (min)", value=180, step=15)
        with c_d4: stawka_h = st.number_input("Stawka/h", value=20, step=5)
        
        st.write("Oceny:")
        # Slider jest OK na mobile
        s_look = st.slider("Wygląd", 1, 5, 5)
        s_taste = st.slider("Smak", 1, 5, 5)
        s_diff = st.slider("Trudność", 1, 5, 3)
        
        if st.form_submit_button("ZAPISZ PRZEPIS"):
            if not nazwa_przepisu or not st.session_state['temp_skladniki']:
                st.error("Brak nazwy lub składników!")
            else:
                saved_imgs = save_uploaded_files(uploaded_files)
                nowy = {
                    "nazwa": nazwa_przepisu,
                    "opis": opis,
                    "zdjecia": saved_imgs,
                    "srednica": srednica,
                    "skladniki_przepisu": st.session_state['temp_skladniki'],
                    "oceny": {"wyglad": s_look, "smak": s_taste, "trudnosc": s_diff},
                    "marza": marza,
                    "czas": czas,
                    "stawka_h": stawka_h
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
    
    # --- EDYCJA ---
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
                e_opis = st.text_area("Instrukcja", value=p_edit['opis'], height=200)
                
                # Inputy w układzie 2x2
                ec1, ec2 = st.columns(2)
                with ec1: e_srednica = st.number_input("Fi", value=p_edit.get('srednica', 15))
                with ec2: e_marza = st.number_input("Marża", value=p_edit.get('marza', 10))
                
                ec3, ec4 = st.columns(2)
                with ec3: e_czas = st.number_input("Czas", value=p_edit.get('czas', 180))
                with ec4: e_stawka = st.number_input("Stawka", value=p_edit.get('stawka_h', 20))
                
                st.write("---")
                st.write("**Edycja Ocen:**")
                e_look = st.slider("Wygląd", 1, 5, current_oceny.get('wyglad', 5))
                e_taste = st.slider("Smak", 1, 5, current_oceny.get('smak', 5))
                e_diff = st.slider("Trudność", 1, 5, current_oceny.get('trudnosc', 3))

                st.write("---")
                st.write("📷 Zarządzanie zdjęciami:")
                
                imgs_to_keep = []
                if p_edit.get('zdjecia'):
                    cols_pics = st.columns(3)
                    for i, path in enumerate(p_edit['zdjecia']):
                        with cols_pics[i % 3]:
                            st.image(path, use_container_width=True)
                            if not st.checkbox("Usuń", key=f"del_img_e_{i}"):
                                imgs_to_keep.append(path)
                else:
                    imgs_to_keep = []
                    
                new_imgs_upload = st.file_uploader("Dodaj zdjęcia", type=['jpg', 'png'], accept_multiple_files=True)
                
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

    # --- WIDOK SZCZEGÓŁOWY ---
    elif st.session_state['fullscreen_recipe'] is not None:
        idx = st.session_state['fullscreen_recipe']
        przepis = data["przepisy"][idx]
        
        if st.button("⬅️ Lista", type="primary"):
            st.session_state['fullscreen_recipe'] = None
            st.rerun()
            
        st.title(przepis['nazwa'].upper())
        
        oceny = przepis.get('oceny', {})
        # Flexbox dla ocen na mobile
        st.markdown(f"""
        <div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom: 20px; font-size: 1em;">
            <div style="background:#333; padding:5px 10px; border-radius:10px;">🎨 {render_stars(oceny.get('wyglad',0))}</div>
            <div style="background:#333; padding:5px 10px; border-radius:10px;">🤤 {render_stars(oceny.get('smak',0))}</div>
            <div style="background:#333; padding:5px 10px; border-radius:10px;">🤯 {render_stars(oceny.get('trudnosc',0))}</div>
        </div>
        """, unsafe_allow_html=True)

        if przepis.get("zdjecia"):
            st.image(przepis["zdjecia"][0], use_container_width=True)

        baza_cm = przepis.get('srednica', 20)
        target_cm = st.number_input("Przelicz na średnicę (cm):", value=baza_cm)
        wsp = (target_cm / baza_cm) ** 2
        
        st.markdown("### 🥣 Składniki:")
        koszt_wsad = 0
        kcal_total = 0
        for sk, il in przepis["skladniki_przepisu"].items():
            il_skal = il * wsp
            if sk in data["skladniki"]:
                info = data["skladniki"][sk]
                c = info["cena"] / info["waga_opakowania"]
                koszt_wsad += c * il_skal
                if "kcal" in info:
                    k = (info["kcal"] / 100) * il_skal
                    kcal_total += k
            st.write(f"• {sk}: **{il_skal:.0f}**")

        cena_koncowa = oblicz_cene_tortu(przepis, data["skladniki"], target_cm)
        st.write("---")
        st.markdown(f"<div style='font-size:1.5em; font-weight:bold; color:#00ff00; text-align:center;'>CENA: {cena_koncowa} PLN</div>", unsafe_allow_html=True)
        st.caption(f"Kcal całości: {kcal_total:.0f}")

        st.write("---")
        st.markdown("### 📝 Instrukcja:")
        formatuj_instrukcje(przepis['opis'])
        
        if przepis.get("zdjecia") and len(przepis["zdjecia"]) > 1:
            st.write("---")
            st.write("📸 Galeria:")
            g_cols = st.columns(2)
            for i, img in enumerate(przepis["zdjecia"]):
                with g_cols[i % 2]:
                    st.image(img, use_container_width=True)

    # --- WIDOK LISTY (KAFELKI) ---
    else:
        st.subheader("📖 Książka Kucharska")
        search = st.text_input("🔍 Szukaj...")
        
        przepisy_do_pokazania = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        for index, przepis in enumerate(przepisy_do_pokazania):
            with st.container(border=True):
                # Na mobile obrazek na górze, tekst pod spodem lepiej wygląda niż ściśnięte obok siebie
                # Ale Streamlit columns stackują się, więc zostawiamy columns([1,2])
                c_img, c_info = st.columns([1, 2])
                
                with c_img:
                    if przepis.get("zdjecia") and os.path.exists(przepis["zdjecia"][0]):
                        st.image(przepis["zdjecia"][0], use_container_width=True)
                    else:
                        st.write("Brak Foto")

                with c_info:
                    st.markdown(f"<h3 style='margin:0; color:#ff0aef;'>{przepis['nazwa']}</h3>", unsafe_allow_html=True)
                    
                    oceny = przepis.get('oceny', {})
                    avg_rate = (oceny.get('wyglad',0) + oceny.get('smak',0)) / 2
                    st.write(f"Ocena: {render_stars(avg_rate)}")
                    
                    cena_est = oblicz_cene_tortu(przepis, data["skladniki"])
                    st.markdown(f"<div style='font-weight:bold; color:#00ff00; font-size:1.2em;'>{cena_est} PLN</div>", unsafe_allow_html=True)
                
                b1, b2 = st.columns(2)
                real_idx = data["przepisy"].index(przepis)
                
                if b1.button("👁️ Otwórz", key=f"open_{index}"):
                    st.session_state['fullscreen_recipe'] = real_idx
                    st.rerun()
                if b2.button("✏️ Edytuj", key=f"edit_p_{index}"):
                    st.session_state['edit_recipe_index'] = real_idx
                    st.rerun()

# ==========================================
# 5. GALERIA
# ==========================================
elif menu == "Galeria":
    st.subheader("🖼️ Galeria Tortów")
    
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
                        st.success(f"Dodano zdjęcie do: {target_recipe_name}")
                        st.rerun()
                        break

    wszystkie_zdjecia = []
    
    for idx, p in enumerate(data["przepisy"]):
        if p.get("zdjecia"):
            for img_idx, fotka in enumerate(p["zdjecia"]):
                ocena = p.get('oceny', {})
                cena = oblicz_cene_tortu(p, data["skladniki"])
                wszystkie_zdjecia.append({
                    "src": fotka, 
                    "name": p["nazwa"], 
                    "recipe_idx": idx,
                    "img_idx_in_recipe": img_idx,
                    "info": f"🎨 {ocena.get('wyglad','-')} | 🤤 {ocena.get('smak','-')}",
                    "price": cena,
                    "type": "recipe"
                })
    
    for i, fotka in enumerate(data["galeria_extra"]):
        wszystkie_zdjecia.append({
            "src": fotka,
            "name": "Luźne zdjęcie",
            "recipe_idx": None,
            "img_idx_in_recipe": i,
            "info": "Brak oceny",
            "price": "-",
            "type": "extra"
        })

    if not wszystkie_zdjecia:
        st.info("Brak zdjęć.")
    else:
        g_cols = st.columns(2)
        
        for i, item in enumerate(wszystkie_zdjecia):
            with g_cols[i % 2]:
                with st.container(border=True):
                    if os.path.exists(item["src"]):
                        st.image(item["src"], use_container_width=True)
                        
                        cb1, cb2, cb3 = st.columns([1, 1, 1])
                        
                        if item["type"] == "recipe":
                            if cb1.button("➜", key=f"g_go_{i}", help="Przejdź"):
                                st.session_state['menu'] = "Przepisy"
                                st.session_state['fullscreen_recipe'] = item["recipe_idx"]
                                st.rerun()
                        else:
                            cb1.button("➜", key=f"g_dis_{i}", disabled=True)
                            
                        if cb2.button("ℹ️", key=f"g_inf_{i}", help="Info"):
                            info_msg = f"{item['name']}\n{item['info']}\nCena: {item['price']} PLN"
                            st.toast(info_msg, icon="🍰")
                        
                        if cb3.button("🗑️", key=f"g_del_{i}", help="Usuń"):
                            if item["type"] == "recipe":
                                r_idx = item["recipe_idx"]
                                img_idx = item["img_idx_in_recipe"]
                                del data["przepisy"][r_idx]["zdjecia"][img_idx]
                            else:
                                img_idx = item["img_idx_in_recipe"]
                                del data["galeria_extra"][img_idx]
                            
                            save_data(data)
                            st.rerun()
