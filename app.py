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
    stawka = przepis.get('stawka', 50)
    
    koszt_pracy = (czas_min / 60) * stawka
    cena_koncowa = koszt_skladnikow * (1 + marza_proc/100) + koszt_pracy
    return cena_koncowa

# --- CSS (STYL, KTÓRY CHCIAŁEŚ) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .stApp { background-color: #121212; color: #ffffff; }
        section[data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }
        
        /* KAFELKI */
        div[data-testid="column"] {
            background-color: #1e1e1e;
            border-radius: 15px;
            padding: 10px;
            border: 1px solid #333;
            transition: transform 0.2s;
        }
        div[data-testid="column"]:hover { border-color: #ff0aef; }

        /* PRZYCISKI - WERSJA PRZEZROCZYSTA (Outline) */
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

        /* OKRĄGŁY PRZYCISK X (USUWANIE) */
        button[kind="secondary"] {
            border-radius: 50% !important;
            width: 36px !important;
            height: 36px !important;
            aspect-ratio: 1 / 1 !important; /* Wymuszenie idealnego koła */
            padding: 0 !important;
            line-height: 1 !important;
            border: 1px solid red !important;
            color: red !important;
            background-color: transparent !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        button[kind="secondary"]:hover {
            background-color: red !important;
            color: white !important;
        }

        /* INPUTY */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div { 
            background-color: #2c2c2c !important; 
            color: white !important; 
            border: none !important; 
            border-radius: 8px;
        }

        /* NAGŁÓWEK */
        .header-box {
            text-align: center; padding: 15px; margin-bottom: 20px;
            border-bottom: 2px solid #ff0aef;
            background: linear-gradient(180deg, rgba(255,10,239,0.1) 0%, rgba(18,18,18,0) 100%);
        }
        .header-title {
            font-size: 2rem; font-weight: 900; color: #ff0aef;
            text-transform: uppercase; letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(255,10,239,0.6);
        }
        
        /* ZDJĘCIA W KAFELKACH */
        .recipe-img {
            width: 100%; height: 120px; object-fit: cover; border-radius: 10px; margin-bottom: 10px;
        }
        
        .big-price {
            font-size: 1.4rem; font-weight: bold; color: #00ff00; text-align: center; margin: 5px 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- STAN APLIKACJI ---
if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'edit_order_idx' not in st.session_state: st.session_state['edit_order_idx'] = None
if 'edit_recipe_idx' not in st.session_state: st.session_state['edit_recipe_idx'] = None
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None
if 'success_msg' not in st.session_state: st.session_state['success_msg'] = None

data = load_data()

# --- NAGŁÓWEK ---
st.markdown(f"""
    <div class="header-box">
        <div class="header-title">WK TORTY</div>
        <div style="color: #ccc; letter-spacing: 1px;">SYSTEM CUKIERNICZY 3.0</div>
    </div>
""", unsafe_allow_html=True)

if st.session_state['success_msg']:
    st.success(st.session_state['success_msg'])
    st.session_state['success_msg'] = None

# --- MENU ---
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1: 
    if st.button("📅 Kalendarz"): st.session_state['menu'] = "Kalendarz"
with col_m2: 
    if st.button("📖 Przepisy"): 
        st.session_state['menu'] = "Przepisy"
        st.session_state['fullscreen_recipe'] = None
with col_m3: 
    label_dodaj = "✏️ Edytuj" if st.session_state['edit_recipe_idx'] is not None else "➕ Nowy"
    if st.button(label_dodaj): st.session_state['menu'] = "Dodaj"
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

    if st.session_state['show_add_order']:
        with st.container():
            st.info("Kreator Zamówienia")
            with st.form("kalendarz_form"):
                c1, c2 = st.columns(2)
                with c1: 
                    data_zamowienia = st.date_input("Data odbioru", value=date.today())
                    klient = st.text_input("Klient")
                with c2:
                    lista_nazw = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                    wybrany_tort = st.selectbox("Wybierz Tort Bazowy", lista_nazw)
                    srednica_zam = st.number_input("Średnica (cm)", value=20)

                opis_dodatkowy = st.text_area("Szczegóły (Napis, dekoracja)")
                
                if st.form_submit_button("Zapisz Zlecenie"):
                    info_cenowe = ""
                    if wybrany_tort != "Własna kompozycja":
                        przepis = next((p for p in data["przepisy"] if p["nazwa"] == wybrany_tort), None)
                        if przepis:
                            cena = oblicz_cene_tortu(przepis, data, srednica_zam)
                            info_cenowe = f"\n[AUTO-WYCENA: {wybrany_tort} fi{srednica_zam}cm ~ {cena:.2f} zł]"

                    full_opis = f"{opis_dodatkowy}{info_cenowe}"
                    nowy_wpis = {"data": str(data_zamowienia), "klient": klient, "opis": full_opis, "wykonane": False}
                    data["kalendarz"].append(nowy_wpis)
                    data["kalendarz"] = sorted(data["kalendarz"], key=lambda x: x['data'])
                    save_data(data)
                    st.session_state['show_add_order'] = False
                    st.rerun()

    st.write("") 
    if not data["kalendarz"]:
        st.info("Brak zleceń.")
    else:
        for i, wpis in enumerate(data["kalendarz"]):
            # STYLE KARTY
            bg = "#252525"
            border = "#ff0aef"
            icon = "⏳ OCZEKUJE"
            if wpis.get("wykonane"):
                bg = "#1a3a1a"
                border = "#00ff00"
                icon = "✅ GOTOWE"

            st.markdown(f"""
            <div style="background-color:{bg}; padding:15px; margin-bottom:10px; border-left:5px solid {border}; border-radius:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:white;">{wpis['klient']}</h3>
                    <span style="background:#333; padding:5px 10px; border-radius:10px;">{wpis['data']}</span>
                </div>
                <p style="color:#bbb; margin-top:10px; white-space: pre-wrap;">{wpis['opis']}</p>
                <div style="font-weight:bold; color:{border}; margin-top:10px;">{icon}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns([1, 1, 3])
            
            btn_label = "Cofnij" if wpis.get("wykonane") else "Oznacz Gotowe"
            if c1.button(btn_label, key=f"status_{i}"):
                data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"]
                save_data(data)
                st.rerun()
                
            if c3.button("Usuń", key=f"del_{i}"):
                data["kalendarz"].pop(i)
                save_data(data)
                st.rerun()

# ==========================================
# 2. MAGAZYN
# ==========================================
elif menu == "Magazyn":
    st.subheader("📦 Magazyn Składników")
    
    if data["skladniki"]:
        df = pd.DataFrame.from_dict(data["skladniki"], orient='index')
        df.reset_index(inplace=True)
        df.columns = ["Składnik", "Cena (PLN)", "Waga (g/szt)", "Kcal/100g"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.write("---")
    with st.form("magazyn_add"):
        st.write("Dodaj/Edytuj produkt:")
        c1, c2, c3, c4 = st.columns(4)
        with c1: new_name = st.text_input("Nazwa")
        with c2: new_price = st.number_input("Cena (PLN)", min_value=0.01, step=0.5)
        with c3: new_weight = st.number_input("Waga op. (g)", min_value=1, step=1)
        with c4: new_kcal = st.number_input("Kcal (w 100g)", min_value=0, step=1)
        
        if st.form_submit_button("Zapisz w Magazynie"):
            if new_name:
                data["skladniki"][new_name] = {"cena": new_price, "waga_opakowania": new_weight, "kcal": new_kcal}
                save_data(data)
                st.success(f"Zapisano: {new_name}")
                st.rerun()

# ==========================================
# 3. DODAJ / EDYTUJ PRZEPIS
# ==========================================
elif menu == "Dodaj":
    edit_idx = st.session_state['edit_recipe_idx']
    is_edit_mode = edit_idx is not None
    naglowek = f"✏️ Edytuj Przepis" if is_edit_mode else "➕ Nowy Przepis"
    st.subheader(naglowek)
    
    if is_edit_mode and 'edit_loaded' not in st.session_state:
        p = data["przepisy"][edit_idx]
        st.session_state['form_nazwa'] = p['nazwa']
        st.session_state['form_opis'] = p['opis']
        st.session_state['form_srednica'] = p.get('srednica', 15)
        st.session_state['form_marza'] = p.get('marza', 10)
        st.session_state['form_czas'] = p.get('czas', 180)
        st.session_state['form_stawka'] = p.get('stawka', 50)
        st.session_state['form_oceny'] = p.get('oceny', {'wyglad':5, 'smak':5, 'trudnosc':3})
        st.session_state['temp_skladniki'] = p['skladniki_przepisu'].copy()
        st.session_state['edit_loaded'] = True
    
    if not is_edit_mode and 'form_nazwa' not in st.session_state:
        st.session_state['form_nazwa'] = ""
        st.session_state['form_opis'] = ""
        st.session_state['form_srednica'] = 15
        st.session_state['form_marza'] = 10
        st.session_state['form_czas'] = 180
        st.session_state['form_stawka'] = 50
        st.session_state['form_oceny'] = {'wyglad':5, 'smak':5, 'trudnosc':3}

    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 1. Składniki")
        with st.form("skladniki_form"):
            wybran = st.selectbox("Wybierz", list(data["skladniki"].keys()))
            krok = 1.0 if ("szt" in wybran.lower() or "jaja" in wybran.lower()) else 1.0
            ilo = st.number_input("Ilość (g / szt)", min_value=0.0, step=krok)
            
            if st.form_submit_button("Dodaj"):
                obecna = st.session_state['temp_skladniki'].get(wybran, 0)
                st.session_state['temp_skladniki'][wybran] = obecna + ilo
                st.rerun()
        
        if st.session_state['temp_skladniki']:
            st.write("---")
            for k, v in st.session_state['temp_skladniki'].items():
                cc1, cc2 = st.columns([3,1])
                cc1.write(f"**{k}**: {v}")
                if cc2.button("X", key=f"del_{k}", type="secondary"):
                    del st.session_state['temp_skladniki'][k]
                    st.rerun()

    with col_right:
        st.markdown("### 2. Dane i Opis")
        with st.form("glowny_przepis_form"):
            nazwa_przepisu = st.text_input("Nazwa Tortu", value=st.session_state.get('form_nazwa', ''))
            opis = st.text_area("Instrukcja", height=200, value=st.session_state.get('form_opis', ''))
            uploaded_files = st.file_uploader("Zdjęcia", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
            
            c_d1, c_d2 = st.columns(2)
            with c_d1: 
                srednica = st.number_input("Średnica (cm)", value=st.session_state.get('form_srednica', 15))
                marza = st.number_input("Marża (%)", value=st.session_state.get('form_marza', 10))
            with c_d2:
                czas = st.number_input("Czas (min)", value=st.session_state.get('form_czas', 180))
                stawka = st.number_input("Stawka (zł/h)", value=st.session_state.get('form_stawka', 50))
            
            st.write("Oceny:")
            oc = st.session_state.get('form_oceny', {})
            oc1, oc2, oc3 = st.columns(3)
            with oc1: s_look = st.slider("Wygląd", 1, 5, oc.get('wyglad', 5))
            with oc2: s_taste = st.slider("Smak", 1, 5, oc.get('smak', 5))
            with oc3: s_diff = st.slider("Trudność", 1, 5, oc.get('trudnosc', 3))
            
            btn_txt = "ZAPISZ ZMIANY" if is_edit_mode else "DODAJ TORT"
            if st.form_submit_button(btn_txt):
                if not nazwa_przepisu or not st.session_state['temp_skladniki']:
                    st.error("Uzupełnij nazwę i składniki!")
                else:
                    new_imgs = save_uploaded_files(uploaded_files)
                    final_imgs = new_imgs
                    if is_edit_mode:
                        old_imgs = data["przepisy"][edit_idx].get("zdjecia", [])
                        final_imgs = old_imgs + new_imgs

                    nowy = {
                        "nazwa": nazwa_przepisu,
                        "opis": opis,
                        "zdjecia": final_imgs,
                        "srednica": srednica,
                        "skladniki_przepisu": st.session_state['temp_skladniki'],
                        "oceny": {"wyglad": s_look, "smak": s_taste, "trudnosc": s_diff},
                        "marza": marza,
                        "czas": czas,
                        "stawka": stawka
                    }
                    
                    if is_edit_mode:
                        data["przepisy"][edit_idx] = nowy
                        st.session_state['edit_recipe_idx'] = None
                        st.session_state['success_msg'] = "Zaktualizowano!"
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
        if st.button("Anuluj edycję"):
            st.session_state['edit_recipe_idx'] = None
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
        
        c_back, c_edit = st.columns([4, 1])
        with c_back:
            if st.button("⬅️ WRÓĆ", type="primary"):
                st.session_state['fullscreen_recipe'] = None
                st.rerun()
        with c_edit:
            if st.button("✏️ Edytuj"):
                st.session_state['edit_recipe_idx'] = idx
                st.session_state['menu'] = "Dodaj"
                st.session_state['fullscreen_recipe'] = None
                st.rerun()
            
        st.title(przepis['nazwa'].upper())
        oc = przepis.get('oceny', {})
        st.markdown(f"**Oceny:** ⭐ Wygląd: {oc.get('wyglad')}/5 | 😋 Smak: {oc.get('smak')}/5 | 🤯 Trudność: {oc.get('trudnosc')}/5")
        
        col_img, col_det = st.columns([1, 1])
        with col_img:
            imgs = przepis.get("zdjecia", [])
            if imgs:
                st.image(imgs[0])
            else:
                st.markdown('<div style="height:300px; background:#333; display:flex; align-items:center; justify-content:center;">BRAK FOTO</div>', unsafe_allow_html=True)

        with col_det:
            cena = oblicz_cene_tortu(przepis, data)
            st.markdown(f'<div class="big-price">Sugerowana cena (fi{przepis.get("srednica")}cm): {cena:.2f} zł</div>', unsafe_allow_html=True)

            st.markdown("### 🥣 Składniki:")
            for sk, il in przepis["skladniki_przepisu"].items():
                st.write(f"• {sk}: **{il}**")

        st.write("---")
        st.markdown("### 📝 Instrukcja:")
        formatuj_instrukcje(przepis['opis'])
        
        if len(imgs) > 1:
            st.write("---")
            st.write("📸 Galeria:")
            cols_mini = st.columns(6)
            for i, pth in enumerate(imgs):
                cols_mini[i % 6].image(pth, use_container_width=True)

    else:
        st.subheader("📖 Książka Kucharska")
        search = st.text_input("🔍 Znajdź przepis...")
        
        przepisy_do_pokazania = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        cols = st.columns(3) 
        for index, przepis in enumerate(przepisy_do_pokazania):
            with cols[index % 3]:
                imgs = przepis.get("zdjecia", [])
                
                if imgs and os.path.exists(imgs[0]):
                    import base64
                    with open(imgs[0], "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                    st.markdown(f'<img src="data:image/png;base64,{encoded_string}" class="recipe-img">', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="recipe-img" style="background:#333; display:flex; align-items:center; justify-content:center;">BRAK</div>', unsafe_allow_html=True)
                
                st.markdown(f"<h4 style='text-align:center; color:#ff0aef; margin:5px 0;'>{przepis['nazwa']}</h4>", unsafe_allow_html=True)
                
                oc = przepis.get('oceny', {})
                st.markdown(f"<div style='text-align:center; color:gold; font-size:0.8em;'>{'★'*oc.get('wyglad',0)}</div>", unsafe_allow_html=True)
                
                cena = oblicz_cene_tortu(przepis, data)
                st.markdown(f"<div style='text-align:center; font-weight:bold; color:#00ff00; margin:5px 0;'>{cena:.2f} zł</div>", unsafe_allow_html=True)
                
                c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
                with c_btn2:
                    if st.button("OTWÓRZ", key=f"open_{index}"):
                        real_idx = data["przepisy"].index(przepis)
                        st.session_state['fullscreen_recipe'] = real_idx
                        st.rerun()

# ==========================================
# 5. GALERIA
# ==========================================
elif menu == "Galeria":
    st.subheader("🖼️ Galeria Tortów")
    
    wszystkie_zdjecia = []
    for idx, p in enumerate(data["przepisy"]):
        if p.get("zdjecia"):
            for fotka in p["zdjecia"]:
                wszystkie_zdjecia.append({
                    "src": fotka, "recipe_idx": idx, "name": p["nazwa"], "obj": p
                })
    
    if not wszystkie_zdjecia:
        st.info("Brak zdjęć w bazie.")
        if st.button("Dodaj nowy tort ze zdjęciem"):
            st.session_state['menu'] = "Dodaj"
            st.rerun()
    else:
        g_cols = st.columns(4)
        for i, item in enumerate(wszystkie_zdjecia):
            with g_cols[i % 4]:
                if os.path.exists(item["src"]):
                    st.image(item["src"], use_container_width=True)
                    
                    c_g1, c_g2 = st.columns(2)
                    with c_g1:
                        if st.button("Tort ➡️", key=f"g_go_{i}"):
                            st.session_state['fullscreen_recipe'] = item["recipe_idx"]
                            st.session_state['menu'] = "Przepisy"
                            st.rerun()
                    with c_g2:
                        if st.button("Info ℹ️", key=f"g_inf_{i}"):
                            p = item["obj"]
                            cena = oblicz_cene_tortu(p, data)
                            oc = p.get('oceny', {})
                            st.toast(f"🎂 {p['nazwa']}\n💰 Cena: {cena:.2f} zł\n⭐ Wygląd: {oc.get('wyglad')}/5")
    
    st.write("---")
    st.caption("Aby dodać więcej zdjęć, edytuj przepis.")
