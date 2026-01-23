import streamlit as st
import json
import os
import pandas as pd
from datetime import date
import time

# --- KONFIGURACJA ---
DB_FILE = 'baza_cukierni_v7.json'
IMG_FOLDER = 'zdjecia_tortow'
LOGO_FILE = "logo_wk_torty.png" 

# Upewniamy się, że folder na zdjęcia istnieje
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
            "galeria_extra": [] # Nowe pole na luźne zdjęcia
        }
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Migracja danych
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

# --- WYGLĄD (CSS) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .stApp { background-color: #121212; color: #ffffff; }
        section[data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }
        
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
        
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div { 
            background-color: #2c2c2c !important; 
            color: white !important; 
            border: none !important; 
            border-radius: 8px;
        }

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
        
        .task-card {
            background-color: #252525; padding: 15px; margin-bottom: 10px;
            border-left: 5px solid #ff0aef; border-radius: 8px;
        }
        .task-done { border-left: 5px solid #00ff00; opacity: 0.6; }
        
        img { border-radius: 10px; object-fit: cover; }
        
        .price-tag {
            font-size: 1.5em; font-weight: bold; color: #00ff00; text-align: center; display: block; margin: 10px 0;
        }
        .center-btn { display: flex; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA ---
if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'edit_order_index' not in st.session_state: st.session_state['edit_order_index'] = None
if 'edit_recipe_index' not in st.session_state: st.session_state['edit_recipe_index'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None

data = load_data()

# --- HEADER ---
st.markdown(f"""
    <div class="header-box">
        <div class="header-title">WK TORTY</div>
        <div style="color: #ccc; letter-spacing: 1px;">SYSTEM CUKIERNICZY 3.0</div>
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
# 1. KALENDARZ
# ==========================================
if menu == "Kalendarz":
    st.subheader("📅 Planer Zamówień")
    
    if st.button("➕ Dodaj nowe zamówienie", type="primary"):
        st.session_state['show_add_order'] = not st.session_state['show_add_order']
        st.session_state['edit_order_index'] = None # Reset edycji przy dodawaniu

    # Formularz dodawania / edycji
    idx_edit = st.session_state['edit_order_index']
    is_edit_mode = idx_edit is not None
    
    if st.session_state['show_add_order'] or is_edit_mode:
        with st.container():
            naglowek = f"✏️ Edycja Zamówienia #{idx_edit+1}" if is_edit_mode else "Kreator Zamówienia"
            st.info(naglowek)
            
            # Pobranie danych do edycji
            domyslne = {}
            if is_edit_mode:
                domyslne = data["kalendarz"][idx_edit]

            with st.form("kalendarz_form"):
                c1, c2 = st.columns(2)
                with c1: 
                    d_val = date.fromisoformat(domyslne['data']) if 'data' in domyslne else date.today()
                    data_zamowienia = st.date_input("Data odbioru", value=d_val)
                    klient = st.text_input("Klient", value=domyslne.get('klient', ''))
                with c2:
                    lista_nazw = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                    # Próba odnalezienia starego wyboru w opisie jest trudna, więc resetujemy do Własnej lub trzeba by parsować opis
                    wybrany_tort = st.selectbox("Wybierz Tort Bazowy", lista_nazw)
                    srednica_zam = st.number_input("Średnica (cm)", value=20)

                opis_val = domyslne.get('opis', '').split('[AUTO-WYCENA')[0] if is_edit_mode else ""
                opis_dodatkowy = st.text_area("Szczegóły (Napis, dekoracja)", value=opis_val)
                
                # Upload zdjęć do zamówienia
                uploaded_order_imgs = st.file_uploader("Dodaj zdjęcia/inspiracje", type=['jpg','png'], accept_multiple_files=True)

                if st.form_submit_button("Zapisz Zlecenie"):
                    info_cenowe = ""
                    # Logika wyceny (jak poprzednio)
                    if wybrany_tort != "Własna kompozycja":
                        przepis = next((p for p in data["przepisy"] if p["nazwa"] == wybrany_tort), None)
                        if przepis:
                            cena_est = oblicz_cene_tortu(przepis, data["skladniki"], srednica_zam)
                            info_cenowe = f"\n[AUTO-WYCENA: {wybrany_tort} fi{srednica_zam}cm ~ {cena_est} zł]"

                    full_opis = f"{opis_dodatkowy}{info_cenowe}"
                    
                    # Zapis zdjęć
                    nowe_fotki = save_uploaded_files(uploaded_order_imgs)
                    stare_fotki = domyslne.get('zdjecia', []) if is_edit_mode else []
                    finalne_fotki = stare_fotki + nowe_fotki

                    wpis = {
                        "data": str(data_zamowienia), 
                        "klient": klient, 
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

    st.write("") 
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
            </div>
            """, unsafe_allow_html=True)
            
            # Miniaturki zdjęć
            if wpis.get('zdjecia'):
                cols_img = st.columns(8)
                for j, img_path in enumerate(wpis['zdjecia']):
                    if os.path.exists(img_path):
                        with cols_img[j % 8]:
                            # Kliknięcie w obrazek w Streamlit automatycznie pozwala go powiększyć (hover -> fullscreen icon)
                            st.image(img_path, use_container_width=True)

            c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
            
            btn_label = "Cofnij" if wpis.get("wykonane") else "Gotowe"
            if c1.button(btn_label, key=f"status_{i}"):
                data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                save_data(data)
                st.rerun()
                
            if c2.button("Edytuj", key=f"edit_{i}"):
                st.session_state['edit_order_index'] = i
                st.session_state['show_add_order'] = False # Żeby nie kolidowało
                st.rerun()

            if c3.button("Usuń", key=f"del_{i}"):
                data["kalendarz"].pop(i)
                save_data(data)
                st.rerun()
            
            with c4:
                st.write(f"**STATUS:** {status_txt}")

# ==========================================
# 2. MAGAZYN
# ==========================================
elif menu == "Magazyn":
    st.subheader("📦 Magazyn Składników")
    
    if data["skladniki"]:
        # Konwersja do DF i zmiana kolejności
        df = pd.DataFrame.from_dict(data["skladniki"], orient='index')
        df.reset_index(inplace=True)
        # Oryginalne klucze w json to nazwy, tutaj robimy kolumny
        # JSON structure: {name: {cena, waga, kcal}}
        # DF structure: index=name, columns=[cena, waga, kcal]
        df.columns = ["Składnik", "Cena (PLN)", "Waga (g/szt)", "Kcal/100g"]
        # Zamiana kolejności Kcal i Cena
        df = df[["Składnik", "Kcal/100g", "Waga (g/szt)", "Cena (PLN)"]]
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.write("---")
    with st.form("magazyn_add"):
        st.write("Dodaj/Edytuj produkt:")
        c1, c2, c3, c4 = st.columns(4)
        with c1: new_name = st.text_input("Nazwa")
        with c2: new_kcal = st.number_input("Kcal (w 100g)", min_value=0, step=1)
        with c3: new_weight = st.number_input("Waga op. (g)", min_value=1, step=1)
        with c4: new_price = st.number_input("Cena (PLN)", min_value=0.01, step=0.5)
        
        if st.form_submit_button("Zapisz w Magazynie"):
            if new_name:
                data["skladniki"][new_name] = {
                    "cena": new_price, 
                    "waga_opakowania": new_weight,
                    "kcal": new_kcal
                }
                save_data(data)
                st.success(f"Zapisano: {new_name}")
                st.rerun()

# ==========================================
# 3. DODAJ PRZEPIS (NOWY)
# ==========================================
elif menu == "Dodaj":
    # Wyświetlenie komunikatu o sukcesie na samej górze
    if st.session_state['success_msg']:
        st.success(st.session_state['success_msg'])
        st.session_state['success_msg'] = None # Reset komunikatu

    st.subheader("🍰 Kreator Nowego Przepisu")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 1. Składniki")
        # Formularz dodawania składników - poza głównym formularzem, by działał dynamicznie
        with st.container():
            wybran = st.selectbox("Wybierz składnik", list(data["skladniki"].keys()))
            
            krok = 1 # Zawsze liczby całkowite
            ilo = st.number_input("Ilość (g / szt)", min_value=0, step=krok, format="%d")
            
            if st.button("Dodaj do listy"):
                if ilo > 0:
                    current_val = st.session_state['temp_skladniki'].get(wybran, 0)
                    st.session_state['temp_skladniki'][wybran] = current_val + ilo
                    st.rerun()
        
        if st.session_state['temp_skladniki']:
            st.write("---")
            st.write("##### Lista składników:")
            to_remove = []
            for k, v in st.session_state['temp_skladniki'].items():
                cc1, cc2 = st.columns([3,1])
                cc1.write(f"**{k}**: {v}")
                if cc2.button("X", key=f"del_{k}"):
                    to_remove.append(k)
            
            if to_remove:
                for k in to_remove:
                    del st.session_state['temp_skladniki'][k]
                st.rerun()

    with col_right:
        st.markdown("### 2. Dane i Opis")
        with st.form("glowny_przepis_form"):
            nazwa_przepisu = st.text_input("Nazwa Tortu")
            st.caption("Formatowanie: '1. Tekst' = Nagłówek | '- Tekst' = Składnik | Zwykły tekst = Opis")
            opis = st.text_area("Instrukcja", height=200)
            
            uploaded_files = st.file_uploader("Zdjęcia", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
            
            c_d1, c_d2 = st.columns(2)
            with c_d1: 
                srednica = st.number_input("Średnica (cm)", value=15, step=1)
                marza = st.number_input("Marża (%)", value=10, step=5)
            with c_d2: 
                czas = st.number_input("Czas pracy (min)", value=180, step=15)
                stawka_h = st.number_input("Stawka godzinowa (PLN)", value=20, step=5)
            
            st.write("Oceny:")
            oc1, oc2, oc3 = st.columns(3)
            with oc1: s_look = st.slider("Wygląd", 1, 5, 5)
            with oc2: s_taste = st.slider("Smak", 1, 5, 5)
            with oc3: s_diff = st.slider("Trudność", 1, 5, 3)
            
            if st.form_submit_button("ZAPISZ PRZEPIS"):
                if not nazwa_przepisu or not st.session_state['temp_skladniki']:
                    st.error("Uzupełnij nazwę i składniki!")
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
                    
                    # Reset
                    st.session_state['temp_skladniki'] = {}
                    st.session_state['success_msg'] = f"Tort '{nazwa_przepisu}' został dodany!"
                    st.rerun()

# ==========================================
# 4. PRZEPISY (EDYCJA, GRID, DETALE)
# ==========================================
elif menu == "Przepisy":
    
    # --- TRYB EDYCJI PRZEPISU ---
    if st.session_state['edit_recipe_index'] is not None:
        idx = st.session_state['edit_recipe_index']
        p_edit = data["przepisy"][idx]
        
        st.subheader(f"✏️ Edycja: {p_edit['nazwa']}")
        if st.button("⬅️ Anuluj edycję"):
            st.session_state['edit_recipe_index'] = None
            st.rerun()
            
        with st.form("edit_recipe_form"):
            e_nazwa = st.text_input("Nazwa", value=p_edit['nazwa'])
            e_opis = st.text_area("Instrukcja", value=p_edit['opis'], height=200)
            
            ec1, ec2, ec3, ec4 = st.columns(4)
            with ec1: e_srednica = st.number_input("Fi (cm)", value=p_edit.get('srednica', 15))
            with ec2: e_marza = st.number_input("Marża (%)", value=p_edit.get('marza', 10))
            with ec3: e_czas = st.number_input("Czas (min)", value=p_edit.get('czas', 180))
            with ec4: e_stawka = st.number_input("Stawka (PLN/h)", value=p_edit.get('stawka_h', 20))
            
            if st.form_submit_button("Zapisz Zmiany"):
                p_edit['nazwa'] = e_nazwa
                p_edit['opis'] = e_opis
                p_edit['srednica'] = e_srednica
                p_edit['marza'] = e_marza
                p_edit['czas'] = e_czas
                p_edit['stawka_h'] = e_stawka
                data["przepisy"][idx] = p_edit
                save_data(data)
                st.session_state['edit_recipe_index'] = None
                st.success("Zaktualizowano przepis!")
                st.rerun()

    # --- WIDOK SZCZEGÓŁOWY ---
    elif st.session_state['fullscreen_recipe'] is not None:
        idx = st.session_state['fullscreen_recipe']
        przepis = data["przepisy"][idx]
        
        if st.button("⬅️ WRÓĆ DO LISTY", type="primary"):
            st.session_state['fullscreen_recipe'] = None
            st.rerun()
            
        st.title(przepis['nazwa'].upper())
        
        # Oceny na górze
        oceny = przepis.get('oceny', {})
        st.markdown(f"""
        <div style="display:flex; gap: 20px; margin-bottom: 20px;">
            <span>🎨 Wygląd: <b>{oceny.get('wyglad','-')}/5</b></span>
            <span>🤤 Smak: <b>{oceny.get('smak','-')}/5</b></span>
            <span>🤯 Trudność: <b>{oceny.get('trudnosc','-')}/5</b></span>
        </div>
        """, unsafe_allow_html=True)

        col_img, col_det = st.columns([1, 1])
        with col_img:
            if przepis.get("zdjecia"):
                st.image(przepis["zdjecia"][0])
            else:
                st.markdown('<div style="height:300px; background:#333; display:flex; align-items:center; justify-content:center;">BRAK FOTO</div>', unsafe_allow_html=True)

        with col_det:
            baza_cm = przepis.get('srednica', 20)
            target_cm = st.number_input("Przelicz na średnicę (cm):", value=baza_cm)
            wsp = (target_cm / baza_cm) ** 2
            
            koszt_wsad = 0
            kcal_total = 0
            
            st.markdown("### 🥣 Składniki:")
            for sk, il in przepis["skladniki_przepisu"].items():
                il_skal = il * wsp
                
                detale = ""
                if sk in data["skladniki"]:
                    info = data["skladniki"][sk]
                    c = info["cena"] / info["waga_opakowania"]
                    koszt_wsad += c * il_skal
                    
                    if "kcal" in info:
                        k = (info["kcal"] / 100) * il_skal
                        kcal_total += k
                        
                st.write(f"• {sk}: **{il_skal:.0f}**") # bez przecinków dla ilości

            cena_koncowa = oblicz_cene_tortu(przepis, data["skladniki"], target_cm)
            
            st.write("---")
            st.markdown(f"<div class='price-tag'>CENA SUGEROWANA: {cena_koncowa} PLN</div>", unsafe_allow_html=True)
            st.caption(f"Szacowane Kalorie całego tortu: {kcal_total:.0f} kcal")

        st.write("---")
        st.markdown("### 📝 Instrukcja:")
        formatuj_instrukcje(przepis['opis'])
        
        # Galeria miniaturek wszystkich zdjęć
        if przepis.get("zdjecia") and len(przepis["zdjecia"]) > 0:
            st.write("---")
            st.write("📸 Galeria tego tortu:")
            g_cols = st.columns(6)
            for i, img in enumerate(przepis["zdjecia"]):
                with g_cols[i % 6]:
                    st.image(img, use_container_width=True)

    # --- WIDOK LISTY (GRID) ---
    else:
        st.subheader("📖 Książka Kucharska")
        search = st.text_input("🔍 Znajdź przepis...")
        
        przepisy_do_pokazania = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        cols = st.columns(3) 
        for index, przepis in enumerate(przepisy_do_pokazania):
            with cols[index % 3]:
                # Estymacja ceny dla domyślnej średnicy
                cena_est = oblicz_cene_tortu(przepis, data["skladniki"])
                oceny = przepis.get('oceny', {})
                
                # Zmniejszenie grafiki - używamy kolumn wewnątrz kafelka
                c_img1, c_img2, c_img3 = st.columns([1, 2, 1])
                with c_img2:
                    img_src = przepis["zdjecia"][0] if przepis.get("zdjecia") else None
                    if img_src and os.path.exists(img_src):
                        st.image(img_src, use_container_width=True)
                
                st.markdown(f"<h3 style='text-align:center; color:#ff0aef; margin:0;'>{przepis['nazwa']}</h3>", unsafe_allow_html=True)
                
                # Wyraźna cena
                st.markdown(f"<div style='text-align:center; font-size:1.2em; font-weight:bold; color:#00ff00; margin: 5px 0;'>{cena_est} PLN</div>", unsafe_allow_html=True)
                
                # Oceny w liście
                st.markdown(f"""
                <div style='text-align:center; font-size:0.8em; color:#ccc; margin-bottom:10px;'>
                   🎨{oceny.get('wyglad','-')} | 🤤{oceny.get('smak','-')} | 🤯{oceny.get('trudnosc','-')}
                </div>
                """, unsafe_allow_html=True)

                # Przyciski
                real_idx = data["przepisy"].index(przepis)
                
                b1, b2 = st.columns(2)
                if b1.button("OTWÓRZ", key=f"open_{index}"):
                    st.session_state['fullscreen_recipe'] = real_idx
                    st.rerun()
                
                if b2.button("EDYTUJ", key=f"edit_p_{index}"):
                    st.session_state['edit_recipe_index'] = real_idx
                    st.rerun()

# ==========================================
# 5. GALERIA
# ==========================================
elif menu == "Galeria":
    st.subheader("🖼️ Galeria Tortów")
    
    # Sekcja dodawania luźnych zdjęć
    with st.expander("Dodaj dodatkowe zdjęcia do galerii"):
        extra_imgs = st.file_uploader("Wybierz pliki", accept_multiple_files=True)
        if extra_imgs:
            if st.button("Wyślij zdjęcia"):
                paths = save_uploaded_files(extra_imgs)
                # Zapisujemy je w osobnej liście w jsonie, by nie zginęły
                data["galeria_extra"].extend(paths)
                save_data(data)
                st.success("Dodano!")
                st.rerun()
    
    # Zbieranie zdjęć: Z przepisów + Z extra galerii
    wszystkie_zdjecia = []
    
    # 1. Z przepisów
    for idx, p in enumerate(data["przepisy"]):
        if p.get("zdjecia"):
            for fotka in p["zdjecia"]:
                ocena = p.get('oceny', {})
                cena = oblicz_cene_tortu(p, data["skladniki"])
                wszystkie_zdjecia.append({
                    "src": fotka, 
                    "name": p["nazwa"], 
                    "recipe_idx": idx,
                    "info": f"🎨 {ocena.get('wyglad','-')} | 🤤 {ocena.get('smak','-')} | 🤯 {ocena.get('trudnosc','-')}",
                    "price": cena
                })
    
    # 2. Extra (bez przepisu)
    for fotka in data["galeria_extra"]:
        wszystkie_zdjecia.append({
            "src": fotka,
            "name": "Zdjęcie dodatkowe",
            "recipe_idx": None,
            "info": "Brak oceny",
            "price": "-"
        })

    if not wszystkie_zdjecia:
        st.info("Brak zdjęć w bazie.")
    else:
        g_cols = st.columns(4)
        for i, item in enumerate(wszystkie_zdjecia):
            with g_cols[i % 4]:
                if os.path.exists(item["src"]):
                    st.image(item["src"], use_container_width=True)
                    
                    c_btn1, c_btn2 = st.columns(2)
                    
                    # Przycisk Przejdź
                    if item["recipe_idx"] is not None:
                        if c_btn1.button("Przejdź", key=f"g_go_{i}"):
                            st.session_state['menu'] = "Przepisy"
                            st.session_state['fullscreen_recipe'] = item["recipe_idx"]
                            st.rerun()
                    else:
                        c_btn1.button("---", key=f"g_dis_{i}", disabled=True)
                        
                    # Przycisk Info
                    if c_btn2.button("Info", key=f"g_inf_{i}"):
                        info_msg = f"{item['name']}\n{item['info']}\nCena: {item['price']} PLN"
                        st.toast(info_msg, icon="🍰")
