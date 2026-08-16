import streamlit as st
import pandas as pd
import sqlite3
import datetime
import time

# ---------------------------------------------------------
# 1. VERİ TABANI YÖNETİMİ (SQLite3 - dekodlama.db)
# ---------------------------------------------------------
DB_NAME = "dekodlama.db"

def init_db():
    """sqlite3 dekodlama.db veri tabanını ve tablosunu otomatik oluşturur."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS decoding_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                box1_body TEXT,
                box2_opponent TEXT,
                box3_distance TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Veri tabanı oluşturma hatası: {e}")

def save_decoding_entry(name: str, box1: str, box2: str, box3: str):
    """Sporcunun ayıklayıp dekode ettiği 3 kutu taktik verisini kaydeder."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO decoding_data (name, box1_body, box2_opponent, box3_distance, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name.strip(), box1.strip(), box2.strip(), box3.strip(), now_str))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Veri kaydetme hatası: {e}")
        return False

def get_all_decoding_entries():
    """Tüm dekodlama verilerini Pandas DataFrame olarak çeker."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        df = pd.read_sql_query('''
            SELECT 
                id AS 'ID',
                name AS 'Sporcu Rumuzu',
                box1_body AS 'Beden / Silah Kutusu',
                box2_opponent AS 'Rakip / Taktik Kutusu',
                box3_distance AS 'Pist / Mesafe Kutusu',
                created_at AS 'Tarih / Saat'
            FROM decoding_data
            ORDER BY id DESC
        ''', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

def clear_db():
    """Tüm veri tabanını sıfırlar (Sadece Uzman Paneli için)."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM decoding_data")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Sıfırlama hatası: {e}")
        return False

# Uygulama başladığında veri tabanını otomatik initialize et
init_db()

# ---------------------------------------------------------
# 2. SAYFA YAPILANDIRMASI VE CSS TASARIMI (DARK MODE & MOBİL)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Taktiksel Dekodlama Simülasyonu",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobil Uyumlu Dev Boyutlu Dark Mode CSS Enjeksiyonu
st.markdown("""
    <style>
    /* Arka Plan ve Ana Konteyner */
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    
    .block-container {
        max-width: 620px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Üst Başlıklar */
    .hero-title {
        font-size: 1.9rem;
        font-weight: 900;
        text-align: center;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
        text-transform: uppercase;
    }
    
    .hero-subtitle {
        font-size: 0.95rem;
        text-align: center;
        color: #94A3B8;
        margin-bottom: 1.6rem;
        font-weight: 600;
    }

    /* Geri Sayım Rozeti */
    .timer-badge {
        background: #DC2626;
        color: #FFFFFF;
        font-size: 1.3rem;
        font-weight: 900;
        padding: 8px 16px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(220, 38, 38, 0.6);
        animation: pulse-timer 1s infinite alternate;
    }

    @keyframes pulse-timer {
        from { transform: scale(1); }
        to { transform: scale(1.05); }
    }

    /* Antrenör Rant Kartı (SAYFA 2) */
    .coach-rant-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%);
        border: 2px solid #EF4444;
        border-radius: 20px;
        padding: 24px 18px;
        text-align: center;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.4);
        margin-bottom: 20px;
    }

    .rant-title {
        color: #F59E0B;
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }

    .rant-text {
        color: #FFFFFF;
        font-size: 1.25rem;
        font-weight: 700;
        line-height: 1.55;
        font-style: italic;
        margin-bottom: 15px;
    }

    .rant-hint {
        color: #94A3B8;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0;
    }

    /* Mobil Uyumlu DEVASA Butonlar */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        font-size: 1.45rem !important;
        font-weight: 900 !important;
        border-radius: 18px !important;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #60A5FA !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4) !important;
        transition: transform 0.08s ease !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }

    div.stButton > button:active {
        transform: scale(0.94) !important;
    }

    /* Kutu Başlıkları */
    .box-label {
        font-size: 1.1rem;
        font-weight: 800;
        color: #60A5FA;
        margin-top: 15px;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
    }

    /* DEVASA Metin Giriş Kutuları (Text Input) */
    div.stTextInput > div > div > input {
        height: 60px !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 2px solid #3B82F6 !important;
        padding-left: 14px !important;
    }

    div.stTextInput > div > div > input:focus {
        border-color: #93C5FD !important;
        box-shadow: 0 0 20px rgba(147, 197, 253, 0.5) !important;
    }

    /* Talimat Kartı */
    .instruction-card {
        background: #1E293B;
        border-left: 6px solid #F59E0B;
        border-radius: 14px;
        padding: 18px 16px;
        margin-bottom: 20px;
    }

    .instruction-text {
        font-size: 1.2rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.4;
        margin: 0;
    }

    /* Bitiş Ekranı Kartı */
    .finish-card {
        background: linear-gradient(135deg, #064E3B 0%, #022C22 100%);
        border: 2px solid #10B981;
        border-radius: 20px;
        padding: 35px 20px;
        text-align: center;
        margin-top: 20px;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. STATE YÖNETİMİ (SESSION STATE)
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = 1  # 1: Bekleme Odası, 2: Kaos & Gürültü, 3: Dekodlama, 4: Uzman Dashboard

if "athlete_name" not in st.session_state:
    st.session_state.athlete_name = ""

if "submitted" not in st.session_state:
    st.session_state.submitted = False

def reset_simulation():
    st.session_state.page = 1
    st.session_state.athlete_name = ""
    st.session_state.submitted = False

# ---------------------------------------------------------
# 4. GİZLİ UZMAN DASHBOARD ERİŞİM KONTROLÜ (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔒 Uzman Paneli Girişi")
    admin_password = st.text_input("Yönetici Şifresi:", type="password", placeholder="Şifreyi giriniz")
    
    if admin_password == "tohm2026":
        st.success("✅ Yetki Onaylandı!")
        if st.button("📊 Uzman Dashboard'una Git", use_container_width=True):
            st.session_state.page = 4
            st.rerun()
    elif admin_password:
        st.error("Hatalı Şifre!")
        
    st.markdown("---")
    st.caption("Eskrim Taktiksel Dekodlama & Zihinsel Dosyalama v2.0")

# ---------------------------------------------------------
# SAYFA 1: BEKLEME ODASI (SPORCULAR İÇİN)
# ---------------------------------------------------------
if st.session_state.page == 1:
    st.markdown("<div class='hero-title'>⚔️ TAKTİKSEL DEKODLAMA</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Mola Anı Bilişsel Dosyalama Simülasyonu</div>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("<p style='font-size: 1.15rem; font-weight: 800; color: #94A3B8; text-align: center; margin-bottom: 8px;'>SPORCU RUMUZU / ADI</p>", unsafe_allow_html=True)
        name_input = st.text_input("Sporcu Rumuzu", label_visibility="collapsed", placeholder="Örn: Şampiyon / Sporcu 1")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("MOLAYA GİR (SİMÜLASYONU BAŞLAT) 🚀", type="primary")
        
        if submit_btn:
            if name_input.strip():
                st.session_state.athlete_name = name_input.strip()
                st.session_state.submitted = False
                st.session_state.page = 2
                st.rerun()
            else:
                st.warning("Lütfen başlamadan önce bir Rumuz giriniz.")

# ---------------------------------------------------------
# SAYFA 2: KAOS VE GÜRÜLTÜ (ANTRENÖRÜN RANT'I)
# ---------------------------------------------------------
elif st.session_state.page == 2:
    st.markdown("<div class='hero-title'>🔥 MOLA ANI: KAOS & GÜRÜLTÜ</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Antrenörün Konuşmasını Dinle ve Zihninde Ayıkla!</div>", unsafe_allow_html=True)
    
    coach_rant = (
        "Ne yapıyorsun sen! Maçı veriyorsun uyan artık! Mesafeyi inanılmaz daralttın, adam seni içeri çekiyor! "
        "Silahını çok düşük tutuyorsun, elini kaldır! Hakeme bakıp durma! İkinci hatta geç, blöflerine cevap verme! "
        "Hadi aslanım yaparsın, topla kendini!"
    )
    
    placeholder = st.empty()
    
    # 15 Saniyelik Geri Sayım Döngüsü
    for remaining in range(15, 0, -1):
        placeholder.markdown(f"""
            <div class='coach-rant-card'>
                <div class='timer-badge'>⏱️ KALAN SÜRE: {remaining} SANİYE</div>
                <p class='rant-title'>📢 ANTRENÖRÜN MOLADAKİ SELEKTA KONUŞMASI:</p>
                <p class='rant-text'>"{coach_rant}"</p>
                <p class='rant-hint'>⚠️ Süre dolmadan duygusal gürültüyü ele ve gerçek taktikleri zihnine kaydet!</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1.0)
        
    # 15 saniye dolunca otomatik Sayfa 3'e geç
    st.session_state.page = 3
    st.rerun()

# ---------------------------------------------------------
# SAYFA 3: TAKTİKSEL DEKODLAMA (SOĞUKKANLI İŞLEME)
# ---------------------------------------------------------
elif st.session_state.page == 3:
    st.markdown("<div class='hero-title'>🧠 TAKTİKSEL DEKODLAMA</div>", unsafe_allow_html=True)
    
    if not st.session_state.submitted:
        st.markdown("""
            <div class='instruction-card'>
                <p class='instruction-text'>
                    💡 Antrenörün paniğini çöpe at. Duyduğun gerçek taktikleri zihnindeki 3 kutuya yerleştir:
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("decoding_form"):
            st.markdown("<p class='box-label'>1. KUTU: BENİM BEDENİM / SİLAHIM</p>", unsafe_allow_html=True)
            box1 = st.text_input("Beden/Silah Kutusu", label_visibility="collapsed", placeholder="Buraya ne dendi? (Örn: Elini/silahı kaldır)")
            
            st.markdown("<p class='box-label'>2. KUTU: RAKİP / TAKTİK</p>", unsafe_allow_html=True)
            box2 = st.text_input("Rakip/Taktik Kutusu", label_visibility="collapsed", placeholder="Buraya ne dendi? (Örn: İkinci hatta geç, blöfe cevap verme)")
            
            st.markdown("<p class='box-label'>3. KUTU: PİST / MESAFE</p>", unsafe_allow_html=True)
            box3 = st.text_input("Pist/Mesafe Kutusu", label_visibility="collapsed", placeholder="Buraya ne dendi? (Örn: Mesafeyi daraltma, içeri çekilme)")
            
            st.markdown("<br>", unsafe_allow_html=True)
            lock_btn = st.form_submit_button("VERİYİ İŞLE VE PİSTE DÖN 🔒", type="primary")
            
            if lock_btn:
                # Veriyi sqlite3 veri tabanına kaydet
                success = save_decoding_entry(
                    st.session_state.athlete_name,
                    box1,
                    box2,
                    box3
                )
                if success:
                    st.session_state.submitted = True
                    st.rerun()
    else:
        st.markdown("""
            <div class='finish-card'>
                <h1 style='color: #34D399; font-size: 2.2rem; font-weight: 900; margin-bottom: 15px;'>🧘‍♂️ DERİN BİR NEFES AL VE PİSTE DÖN</h1>
                <p style='color: #E2E8F0; font-size: 1.3rem; font-weight: 700; line-height: 1.5;'>
                    Gürültüyü eledin ve taktikleri zihinsel 3 kutuna dosyaladın.<br>
                    Başarılar Şampiyon! ⚔️
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("YENİDEN BAŞLA (YENİ MOLA) 🔄"):
            reset_simulation()
            st.rerun()

# ---------------------------------------------------------
# SAYFA 4: UZMAN DASHBOARD'U (YÖNETİCİ EKRANI)
# ---------------------------------------------------------
elif st.session_state.page == 4:
    st.markdown("<div class='hero-title'>📊 UZMAN DASHBOARD'U</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Canlı Sporcu Dekodlama & Zihinsel Dosyalama Tablosu</div>", unsafe_allow_html=True)
    
    df_entries = get_all_decoding_entries()
    
    if not df_entries.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Toplam Giriş Yapan Sporcu", f"{len(df_entries)}")
        with col2:
            # 3 kutuyu da tam dolduranlar
            full_count = len(df_entries[(df_entries["Beden / Silah Kutusu"] != "") & 
                                     (df_entries["Rakip / Taktik Kutusu"] != "") & 
                                     (df_entries["Pist / Mesafe Kutusu"] != "")])
            st.metric("Tam Dosyalayan Sporcu", f"{full_count}")
        with col3:
            empty_count = len(df_entries) - full_count
            st.metric("Eksik/Donan Hafıza", f"{empty_count}")
            
        st.markdown("---")
        st.markdown("### 📋 Canlı Sporcu Dekodlama Veri Tablosu")
        st.dataframe(df_entries, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        # CSV İndirme Butonu
        csv_bytes = df_entries.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tüm Verileri CSV Olarak İndir",
            data=csv_bytes,
            file_name=f"taktiksel_dekodlama_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚠️ Veri Tabanı Yönetimi"):
            if st.button("🗑️ Tüm Veri Tabanını Sıfırla / Sil", use_container_width=True):
                if clear_db():
                    st.success("Veri tabanı başarıyla temizlendi!")
                    st.rerun()
    else:
        st.info("Henüz kaydedilmiş taktiksel dekodlama verisi bulunmuyor.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(" Sporcu Ana Sayfasına Dön 🏠", use_container_width=True):
        reset_simulation()
        st.rerun()
