import streamlit as st
import json
import os
import pandas as pd
from datetime import date
from PIL import Image

# --- KONFIGURACJA ---
DB_FILE = 'baza_cukierni_v5.json'
IMG_FOLDER = 'zdjecia_tortow'
# Jeśli nie wgrasz logo na GitHub, aplikacja zadziała bez niego (tekstowo)
LOGO_FILE = "logo_wk_torty.png" 
ILUSTRACJA_FILE = "ilustracja_ksiazka.png"

# Upewniamy się, że folder na zdjęcia istnieje
os.makedirs(IMG_FOLDER, exist_ok=True)

# --- FUNKCJE ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "skladniki": {
                "Mąka pszenna": {"cena": 3.50, "waga_opakowania": 1000},
                "Cukier": {"cena": 4.00, "waga_opakowania": 1000},
                "Masło": {"cena": 7.50, "waga_opakowania": 200},
                "Jajka (szt)": {"cena": 1.20, "waga_opakowania": 1}
            },
            "przepisy": [],
            "kalendarz": []
        }
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Naprawa starych wersji bazy danych (zgodność wsteczna)
        for p in data["przepisy"]:
            if "zdjecie" in p and isinstance(p["zdjecie"], str) and p["zdjecie"]:
                p["zdjecia"] = [p["zdjecie"]]
                del p["zdjecie"]
            elif "zdjecia" not in p:
                p["zdjecia"] = []
        return data

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_uploaded_files(uploaded_files):
    saved_paths = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Zapisujemy plik w folderze tymczasowym kontenera
            file_path = os.path.join(IMG_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(file_path)
    return saved_paths

# --- WYGLĄD (CSS) ---
st.set_page_config(page_title="WK Torty", page_icon="🧁", layout="wide")

st.markdown("""
    <style>
        /* Tło aplikacji - Ciemne */
        .stApp { background-color: #1e1e1e; color: #ffffff; }
        
        /* Pasek boczny - Trochę jaśniejszy */
        section[data-testid="stSidebar"] { background-color: #252525; border-right: 1px solid #333; }
        
        /* --- Twój Kolor: NEONOWY RÓŻ #ff0aef --- */
        .stButton > button { 
            background-color: #ff0aef; 
            color: white; 
            border-radius: 8px; 
            border: none; 
            font-weight: bold; 
            box-shadow: 0px 0px 10px rgba(255, 10, 239, 0.3); 
        }
        .stButton > button:hover { 
            background-color: #c900bc; 
            box-shadow: 0px 0px 15px rgba(255, 10, 239, 0.6);
        }
        
        /* Duży przycisk w Kalendarzu */
        .big-button { width: 100%; padding: 15px 0; border-radius: 50px !important; font-size: 1.2em !important; margin-bottom: 30px; }
        
        /* Kolory tekstu i nagłówków */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stRadio label { color: #ffffff !important; }
        .stCaption { color: #b0b0b0 !important; }
        
        /* Pola do pisania (Inputy) */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stNumberInput > div > div > input { 
            background-color: #333333; 
            color: #ffffff; 
            border: 1px solid #555555; 
        }
        
        /* Kalendarz systemowy */
        input[type="date"] { 
            background-color: #333333; 
            color: #ffffff; 
            border: 1px solid #555555; 
            min-height: 40px; 
            filter: invert(1); /* Triki żeby ikonka kalendarza była widoczna na ciemnym */
        }
        
        /* Karty zamówień */
        .order-card { 
            background-color: #2c2c2c; 
            padding: 15px; 
            border-radius: 15px; 
            margin-bottom: 15px; 
            border-left: 5px solid #ff0aef; 
        }
        
        /* Nagłówek z logo */
        .header-container { display: flex; align-items: center; justify-content: center; margin-bottom: 30px; }
        .logo-circle { width: 60px; height: 60px; border-radius: 50%; background-color: white; display: flex; align-items: center; justify-content: center; margin-right: 15px; overflow: hidden; }
        .header-title { font-size: 24px; font-weight: bold; text-shadow: 0px 0px 10px rgba(255, 10, 239, 0.5); color: #ff0aef !important; }
        
        .empty-state { text-align: center; margin-top: 50px; }
        .stCheckbox label { font-size: 1.1em; padding-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA ---
if 'temp_skladniki' not in st.session_state:
    st.session_state['temp_skladniki'] = {}
if 'show_add_order' not in st.session_state:
    st.session_state['show_add_order'] = False

data = load_data()

# --- SIDEBAR (MENU) ---
with st.sidebar:
    st.title("🧁 WK Torty")
    st.write("---")
    menu = st.radio("MENU", ["📅 Kalendarz", "📖 Książka Przepisów", "➕ Dodaj Przepis", "📦 Magazyn"])

# ==========================================
# 1. KALENDARZ
# ==========================================
if menu == "📅 Kalendarz":
    # Wyświetlenie nagłówka (z logo jeśli jest wgrane)
    if os.path.exists(LOGO_FILE):
        st.markdown(f"""
            <div class="header-container">
                <div class="logo-circle">
                    <img src="data:image/png;base64,{st.image(LOGO_FILE, output_format='PNG').data}" width="50">
                </div>
                <div class="header-title">WK Torty</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="header-container"><div class="header-title">WK Torty</div></div>""", unsafe_allow_html=True)
    
    # Przycisk dodawania
    if st.button("➕ Dodaj zamówienie", key="add_order_btn"):
        st.session_state['show_add_order'] = not st.session_state['show_add_order']
    st.markdown('<style>div.stButton > button:first-child { @extend .big-button; }</style>', unsafe_allow_html=True)

    if st.session_state['show_add_order']:
        with st.form("kalendarz_form"):
            st.subheader("Nowe zamówienie")
            col_k1, col_k2 = st.columns(2)
            with col_k1: data_zamowienia = st.date_input("Data odbioru", value=date.today())
            with col_k2: klient = st.text_input("Klient")
            opis_tortu = st.text_area("Szczegóły zamówienia")
            
            if st.form_submit_button("Zapisz"):
                nowy_wpis = {"data": str(data_zamowienia), "klient": klient, "opis": opis_tortu, "wykonane": False}
                data["kalendarz"].append(nowy_wpis)
                data["kalendarz"] = sorted(data["kalendarz"], key=lambda x: x['data'])
                save_data(data)
                st.session_state['show_add_order'] = False
                st.success("Dodano!")
                st.rerun()
        st.write("---")

    st.subheader("Nadchodzące zlecenia")
    if not data["kalendarz"]:
        st.markdown("""<div class="empty-state">""", unsafe_allow_html=True)
        # Placeholder jeśli brak ilustracji
        if os.path.exists(ILUSTRACJA_FILE):
             st.image(ILUSTRACJA_FILE, width=200)
        else:
             st.info("Brak aktywnych zamówień")
        st.markdown("""<h3>Kalendarz jest pusty</h3><p>Dodaj nowe zamówienie powyżej.</p></div>""", unsafe_allow_html=True)
    else:
        for i, wpis in enumerate(data["kalendarz"]):
            kolor = "✅" if wpis.get("wykonane") else "⏳"
            with st.container():
                st.markdown(f"""
                <div class="order-card">
                    <strong>{wpis['data']}</strong> | {kolor} <strong>{wpis['klient']}</strong><br>
                    <small style="color: #b0b0b0;">{wpis['opis']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 4])
                if not wpis.get("wykonane"):
                    if c1.button("Zrobione", key=f"done_{i}"):
                        data["kalendarz"][i]["wykonane"] = True
                        save_data(data)
                        st.rerun()
                if c1.button("Usuń", key=f"del_{i}"):
                    data["kalendarz"].pop(i)
                    save_data(data)
                    st.rerun()

# ==========================================
# 2. MAGAZYN
# ==========================================
elif menu == "📦 Magazyn":
    st.header("📦 Magazyn Składników")
    if data["skladniki"]:
        df = pd.DataFrame.from_dict(data["skladniki"], orient='index')
        df.reset_index(inplace=True)
        df.columns = ["Nazwa", "Cena (PLN)", "Waga (g/szt)"]
        st.dataframe(df, use_container_width=True)
    st.divider()
    with st.form("magazyn_add"):
        st.subheader("Dodaj składnik")
        c1, c2, c3 = st.columns(3)
        with c1: new_name = st.text_input("Nazwa")
        with c2: new_price = st.number_input("Cena", min_value=0.01)
        with c3: new_weight = st.number_input("Waga (g)", min_value=1)
        if st.form_submit_button("Zapisz Składnik"):
            if new_name:
                data["skladniki"][new_name] = {"cena": new_price, "waga_opakowania": new_weight}
                save_data(data)
                st.success(f"Dodano: {new_name}")
                st.rerun()

# ==========================================
# 3. DODAJ PRZEPIS
# ==========================================
elif menu == "➕ Dodaj Przepis":
    st.header("🍰 Nowy Przepis")
    st.info("KROK 1: Lista składników")
    with st.form("skladniki_form"):
        c_s1, c_s2, c_s3 = st.columns([3, 2, 2])
        with c_s1: wybran = st.selectbox("Składnik", list(data["skladniki"].keys()))
        with c_s2: ilo = st.number_input("Ilość", min_value=0.0)
        with c_s3: 
            st.write("")
            add_s = st.form_submit_button("Dodaj do listy")
        if add_s:
            st.session_state['temp_skladniki'][wybran] = ilo
            st.rerun()

    if st.session_state['temp_skladniki']:
        st.write("**Lista składników:**")
        temp_dict = st.session_state['temp_skladniki'].copy()
        for k, v in temp_dict.items():
            cols = st.columns([4, 1])
            cols[0].write(f"- {k}: {v}")
            if cols[1].button("❌", key=f"del_temp_{k}"):
                del st.session_state['temp_skladniki'][k]
                st.rerun()
    else:
        st.caption("Lista jest pusta.")

    st.write("---")
    st.info("KROK 2: Opis (Każda nowa linia w instrukcji będzie osobnym punktem do odhaczenia!)")
    with st.form("glowny_przepis_form"):
        nazwa_przepisu = st.text_input("Nazwa Tortu")
        opis = st.text_area("Instrukcja (Wpisz każdy krok w nowej linii)", height=200)
        uploaded_files = st.file_uploader("Dodaj zdjęcia", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
        srednica = st.number_input("Średnica (cm)", value=20)
        st.write("**Oceny:**")
        oc1, oc2, oc3 = st.columns(3)
        with oc1: s_look = st.slider("Wygląd", 1, 5, 5)
        with oc2: s_taste = st.slider("Smak", 1, 5, 5)
        with oc3: s_diff = st.slider("Trudność", 1, 5, 3)
        
        if st.form_submit_button("💾 ZAPISZ CAŁY PRZEPIS", type="primary"):
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
                    "oceny": {"wyglad": s_look, "smak": s_taste, "trudnosc": s_diff}
                }
                data["przepisy"].append(nowy)
                save_data(data)
                st.session_state['temp_skladniki'] = {}
                st.success("Zapisano!")
                st.rerun()

# ==========================================
# 4. KSIĄŻKA (TRYB LIVE)
# ==========================================
elif menu == "📖 Książka Przepisów":
    st.header("📖 Twoje Przepisy")
    search = st.text_input("🔍 Szukaj...")
    
    for idx, przepis in enumerate(data["przepisy"]):
        if search.lower() in przepis["nazwa"].lower():
            with st.expander(f"🍰 {przepis['nazwa']}"):
                
                # Oceny
                oceny = przepis.get("oceny", {"wyglad": 5, "smak": 5, "trudnosc": 3})
                st.caption(f"🎨 {oceny['wyglad']}/5 | 😋 {oceny['smak']}/5 | 🤯 {oceny['trudnosc']}/5")
                
                # Przełącznik LIVE
                mode_col1, mode_col2 = st.columns([3, 1])
                with mode_col2:
                    live_mode = st.toggle("👩‍🍳 Tryb Live", key=f"live_{idx}")
                
                # Galeria
                imgs = przepis.get("zdjecia", [])
                if imgs:
                    cols = st.columns(len(imgs)) if len(imgs) <= 3 else st.columns(3)
                    for i, img_path in enumerate(imgs):
                        if os.path.exists(img_path): 
                            cols[i%3].image(img_path, use_container_width=True)

                st.markdown("---")
                
                # Kalkulator
                col_calc_input, col_calc_res = st.columns(2)
                with col_calc_input:
                    baza_cm = przepis.get('srednica', 20)
                    target_cm = st.number_input(f"Pieczesz fi:", value=baza_cm, key=f"t_{idx}")
                    wsp = (target_cm / baza_cm) ** 2
                
                koszt_total = 0
                for sk, il in przepis["skladniki_przepisu"].items():
                    if sk in data["skladniki"]:
                        c = data["skladniki"][sk]["cena"] / data["skladniki"][sk]["waga_opakowania"]
                        koszt_total += (c * il * wsp)
                
                with col_calc_res:
                    if not live_mode:
                        st.metric("Koszt produktów", f"{koszt_total:.2f} zł")

                # --- TRYB LIVE ---
                if live_mode:
                    st.success("Tryb Pieczenia aktywny! Odhaczaj wykonane kroki.")
                    st.write("#### 🥣 Składniki (na twoją średnicę):")
                    for sk, il in przepis["skladniki_przepisu"].items():
                        il_skal = il * wsp
                        st.checkbox(f"**{sk}**: {il_skal:.1f}", key=f"chk_ing_{idx}_{sk}")
                    
                    st.write("---")
                    st.write("#### 📝 Etapy przygotowania:")
                    opis_linii = przepis['opis'].split('\n')
                    for line_i, linia in enumerate(opis_linii):
                        if linia.strip():
                            st.checkbox(linia, key=f"chk_step_{idx}_{line_i}")
                            
                # --- TRYB ZWYKŁY ---
                else:
                    with st.expander("Szczegóły wyceny (Robocizna)"):
                        h = st.number_input("Godziny pracy", 0.0, 100.0, 3.0, key=f"h_{idx}")
                        stawka = st.number_input("Stawka h", 0, 500, 50, key=f"s_{idx}")
                        narzut = st.number_input("Marża %", 0, 500, 30, key=f"m_{idx}")
                        cena_min = koszt_total + (koszt_total * narzut/100) + (h * stawka)
                        st.success(f"Cena dla klienta: {cena_min:.2f} zł")
                    
                    st.write(f"**Przepis:**")
                    st.write(przepis['opis'])