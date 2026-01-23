import streamlit as st
import json
import os
import pandas as pd
from datetime import date

# --- KONFIGURACJA ---
DB_FILE = 'baza_cukierni_v6.json'
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
            "kalendarz": []
        }
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Migracja danych (dodanie brakujących pól w starych rekordach)
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

# Funkcja do formatowania brzydkiego tekstu w ładny
def formatuj_instrukcje(tekst):
    linie = tekst.split('\n')
    for linia in linie:
        l = linia.strip()
        if not l: continue
        
        # Logika parsowania
        if l[0].isdigit() and (l[1] == '.' or l[1] == ')'):
            st.markdown(f"#### {l}") # Nagłówek kroku
        elif l.startswith('-') or l.startswith('*'):
            st.markdown(f"- {l[1:].strip()}") # Lista punktowana
        else:
            st.write(l) # Zwykły tekst

# --- WYGLĄD (CSS - STYL PREMIUM) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .stApp { background-color: #121212; color: #ffffff; }
        section[data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }
        
        /* Styl Kafelków */
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
        
        img { border-radius: 10px; object-fit: cover; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA ---
if 'temp_skladniki' not in st.session_state: st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state: st.session_state['show_add_order'] = False
if 'fullscreen_recipe' not in st.session_state: st.session_state['fullscreen_recipe'] = None

data = load_data()

# --- HEADER ---
st.markdown(f"""
    <div class="header-box">
        <div class="header-title">WK TORTY</div>
        <div style="color: #ccc; letter-spacing: 1px;">SYSTEM CUKIERNICZY 3.0</div>
    </div>
""", unsafe_allow_html=True)

# --- MENU NA GÓRZE ---
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1: 
    if st.button("📅 Kalendarz"): st.session_state['menu'] = "Kalendarz"
with col_m2: 
    if st.button("📖 Przepisy"): 
        st.session_state['menu'] = "Przepisy"
        st.session_state['fullscreen_recipe'] = None # Reset widoku
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
# 1. KALENDARZ (Z wyborem przepisu i ceną)
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
                    # Wybór przepisu z listy
                    lista_nazw = ["Własna kompozycja"] + [p["nazwa"] for p in data["przepisy"]]
                    wybrany_tort = st.selectbox("Wybierz Tort Bazowy", lista_nazw)
                    srednica_zam = st.number_input("Średnica (cm)", value=20)

                # Podgląd ceny (Symulacja wewnątrz forma jest trudna, więc robimy to po zapisie 
                # lub jako informacja dodatkowa w opisie)
                opis_dodatkowy = st.text_area("Szczegóły (Napis, dekoracja)")
                
                if st.form_submit_button("Zapisz Zlecenie"):
                    # Obliczenie wstępnej ceny jeśli wybrano tort
                    info_cenowe = ""
                    if wybrany_tort != "Własna kompozycja":
                        przepis = next((p for p in data["przepisy"] if p["nazwa"] == wybrany_tort), None)
                        if przepis:
                            baza_cm = przepis.get('srednica', 20)
                            wsp = (srednica_zam / baza_cm) ** 2
                            koszt_skladnikow = 0
                            for sk, il in przepis["skladniki_przepisu"].items():
                                if sk in data["skladniki"]:
                                    info = data["skladniki"][sk]
                                    cena_g = info["cena"] / info["waga_opakowania"]
                                    koszt_skladnikow += (cena_g * il * wsp)
                            
                            marza_proc = przepis.get('marza', 30)
                            czas = przepis.get('czas', 180) # minuty
                            stawka_h = 50 # Domyślna stawka
                            koszt_pracy = (czas/60) * stawka_h
                            cena_koncowa = koszt_skladnikow * (1 + marza_proc/100) + koszt_pracy
                            info_cenowe = f"\n[AUTO-WYCENA: {wybrany_tort} fi{srednica_zam}cm ~ {cena_koncowa:.2f} zł]"

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

            c1, c2, c3 = st.columns([1, 1, 3])
            
            # Przycisk Zmiany statusu (toggle)
            btn_label = "Cofnij" if wpis.get("wykonane") else "Oznacz Gotowe"
            if c1.button(btn_label, key=f"status_{i}"):
                data["kalendarz"][i]["wykonane"] = not data["kalendarz"][i]["wykonane"] # Negacja
                save_data(data)
                st.rerun()
                
            if c2.button("Usuń", key=f"del_{i}"):
                data["kalendarz"].pop(i)
                save_data(data)
                st.rerun()

# ==========================================
# 2. MAGAZYN (KCAL + INPUTY)
# ==========================================
elif menu == "Magazyn":
    st.subheader("📦 Magazyn i Kalorie")
    
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
                data["skladniki"][new_name] = {
                    "cena": new_price, 
                    "waga_opakowania": new_weight,
                    "kcal": new_kcal
                }
                save_data(data)
                st.success(f"Zapisano: {new_name}")
                st.rerun()

# ==========================================
# 3. DODAJ PRZEPIS (MARŻA, CZAS, SKOKI)
# ==========================================
elif menu == "Dodaj":
    st.subheader("🍰 Kreator Przepisu")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 1. Składniki")
        with st.form("skladniki_form"):
            wybran = st.selectbox("Wybierz", list(data["skladniki"].keys()))
            
            # Inteligentny krok (step)
            krok = 1.0
            if "szt" in wybran.lower() or "jaja" in wybran.lower():
                krok = 1.0 # Sztuki
            
            ilo = st.number_input("Ilość (g / szt)", min_value=0.0, step=krok)
            
            if st.form_submit_button("Dodaj"):
                st.session_state['temp_skladniki'][wybran] = ilo
                st.rerun()
        
        if st.session_state['temp_skladniki']:
            st.write("---")
            for k, v in st.session_state['temp_skladniki'].items():
                cc1, cc2 = st.columns([3,1])
                cc1.write(f"**{k}**: {v}")
                if cc2.button("X", key=f"del_{k}"):
                    del st.session_state['temp_skladniki'][k]
                    st.rerun()

    with col_right:
        st.markdown("### 2. Dane i Opis")
        with st.form("glowny_przepis_form"):
            nazwa_przepisu = st.text_input("Nazwa Tortu")
            
            # Instrukcja obsługi formatowania
            st.caption("Formatowanie: '1. Tekst' = Nagłówek | '- Tekst' = Składnik | Zwykły tekst = Opis")
            opis = st.text_area("Instrukcja", height=200)
            
            uploaded_files = st.file_uploader("Zdjęcia", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
            
            c_d1, c_d2, c_d3 = st.columns(3)
            with c_d1: srednica = st.number_input("Średnica (cm)", value=20)
            with c_d2: marza = st.number_input("Marża produktów (%)", value=30, step=5)
            with c_d3: czas = st.number_input("Czas pracy (min)", value=180, step=15)
            
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
                        "czas": czas
                    }
                    data["przepisy"].append(nowy)
                    save_data(data)
                    st.session_state['temp_skladniki'] = {}
                    st.success("Zapisano!")
                    st.rerun()

# ==========================================
# 4. PRZEPISY (GRID + PEŁNY EKRAN + CENA)
# ==========================================
elif menu == "Przepisy":
    
    # JEŚLI WYBRANO TRYB PEŁNOEKRANOWY
    if st.session_state['fullscreen_recipe'] is not None:
        idx = st.session_state['fullscreen_recipe']
        przepis = data["przepisy"][idx]
        
        # Przycisk powrotu
        if st.button("⬅️ WRÓĆ DO LISTY", type="primary"):
            st.session_state['fullscreen_recipe'] = None
            st.rerun()
            
        st.title(przepis['nazwa'].upper())
        
        col_img, col_det = st.columns([1, 1])
        with col_img:
            if przepis.get("zdjecia"):
                st.image(przepis["zdjecia"][0])
            else:
                st.markdown('<div style="height:300px; background:#333; display:flex; align-items:center; justify-content:center;">BRAK FOTO</div>', unsafe_allow_html=True)

        with col_det:
            # Kalkulacja na żywo
            baza_cm = przepis.get('srednica', 20)
            target_cm = st.number_input("Przelicz na średnicę (cm):", value=baza_cm)
            wsp = (target_cm / baza_cm) ** 2
            
            koszt_wsad = 0
            kcal_total = 0
            
            st.markdown("### 🥣 Składniki:")
            for sk, il in przepis["skladniki_przepisu"].items():
                il_skal = il * wsp
                
                # Cena i Kcal
                detale = ""
                if sk in data["skladniki"]:
                    info = data["skladniki"][sk]
                    c = info["cena"] / info["waga_opakowania"]
                    koszt_wsad += c * il_skal
                    
                    if "kcal" in info:
                        k = (info["kcal"] / 100) * il_skal
                        kcal_total += k
                        
                st.write(f"• {sk}: **{il_skal:.1f}**")

            marza_zl = koszt_wsad * (przepis.get('marza', 30)/100)
            st.metric("Koszt produktów", f"{koszt_wsad:.2f} zł", f"+ {marza_zl:.2f} zł marży")
            st.caption(f"Szacowane Kalorie całego tortu: {kcal_total:.0f} kcal")

        st.write("---")
        st.markdown("### 📝 Instrukcja:")
        # Użycie nowej funkcji formatowania
        formatuj_instrukcje(przepis['opis'])

    # JEŚLI WIDOK LISTY (GRID)
    else:
        st.subheader("📖 Książka Kucharska")
        search = st.text_input("🔍 Znajdź przepis...")
        
        przepisy_do_pokazania = [p for p in data["przepisy"] if search.lower() in p["nazwa"].lower()]
        
        cols = st.columns(3) 
        for index, przepis in enumerate(przepisy_do_pokazania):
            with cols[index % 3]:
                # Obliczenie wstępnej ceny (dla bazy)
                koszt_baza = 0
                for sk, il in przepis["skladniki_przepisu"].items():
                    if sk in data["skladniki"]:
                        info = data["skladniki"][sk]
                        koszt_baza += (info["cena"] / info["waga_opakowania"]) * il
                
                img_src = przepis["zdjecia"][0] if przepis.get("zdjecia") else None
                
                if img_src and os.path.exists(img_src):
                    st.image(img_src, use_container_width=True)
                
                st.markdown(f"<h3 style='text-align:center; color:#ff0aef; margin:0;'>{przepis['nazwa']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center; color:#aaa; font-size:0.9em;'>Koszt wsadu (fi{przepis.get('srednica',20)}): <b>{koszt_baza:.2f} zł</b></p>", unsafe_allow_html=True)
                
                # Przycisk otwierający pełny widok
                if st.button("OTWÓRZ PRZEPIS", key=f"open_{index}"):
                    # Znajdź prawdziwy indeks w głównej liście (bo filtrujemy)
                    real_idx = data["przepisy"].index(przepis)
                    st.session_state['fullscreen_recipe'] = real_idx
                    st.rerun()

# ==========================================
# 5. GALERIA (NOWOŚĆ)
# ==========================================
elif menu == "Galeria":
    st.subheader("🖼️ Galeria Tortów")
    
    # Zbieramy wszystkie zdjęcia ze wszystkich przepisów
    wszystkie_zdjecia = []
    for p in data["przepisy"]:
        if p.get("zdjecia"):
            for fotka in p["zdjecia"]:
                wszystkie_zdjecia.append({"src": fotka, "name": p["nazwa"]})
    
    if not wszystkie_zdjecia:
        st.info("Brak zdjęć w bazie.")
    else:
        # Wyświetlamy w siatce 4 kolumn
        g_cols = st.columns(4)
        for i, item in enumerate(wszystkie_zdjecia):
            with g_cols[i % 4]:
                if os.path.exists(item["src"]):
                    st.image(item["src"], use_container_width=True)
                    # Po kliknięciu w "Info" pokazuje nazwę (proste rozwiązanie)
                    if st.button(f"Info", key=f"gal_{i}"):
                        st.toast(f"To jest: {item['name']}")
                    st.caption(item["name"])
