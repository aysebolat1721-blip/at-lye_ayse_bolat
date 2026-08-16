import streamlit as st
import pandas as pd
import sqlite3
import datetime
import time
import random

# ---------------------------------------------------------
# 1. VERİ TABANI YÖNETİMİ (SQLite3)
# ---------------------------------------------------------
DB_NAME = "veri.db"

def init_db():
    """sqlite3 veri tabanını ve tabloyu otomatik olarak oluşturur."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS anchor_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                word TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Veri tabanı başlatma hatası: {e}")

def save_entry(name: str, word: str):
    """Sporcu adını ve odak kelimesini veri tabanına kaydeder."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO anchor_words (name, word, created_at)
            VALUES (?, ?, ?)
        ''', (name.strip(), word.strip().upper(), now_str))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Kayıt eklenirken hata oluştu: {e}")
        return False

def get_all_entries():
    """Tüm verileri Pandas DataFrame olarak çeker."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        df = pd.read_sql_query('''
            SELECT id AS 'ID', name AS 'Rumuz / Ad', word AS 'Odak Kelimesi', created_at AS 'Tarih / Saat'
            FROM anchor_words
            ORDER BY id DESC
        ''', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

def clear_db():
    """Veri tabanını sıfırlar (Sadece Uzman Paneli için)."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM anchor_words")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Veri tabanı silinirken hata: {e}")
        return False

# Veri tabanını başlat
init_db()

# ---------------------------------------------------------
# 2. SAYFA YAPILANDIRMASI VE CSS TASARIMI (DARK MODE & MOBİL)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bilişsel Odak Simülasyonu",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobil Odaklı Dev Boyutlu Dark Mode CSS Enjeksiyonu
st.markdown("""
    <style>
    /* Ana Sayfa Arka Planı ve Genişlik */
    .stApp {
        background-color: #090D16;
        color: #F8FAFC;
    }
    
    .block-container {
        max-width: 600px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Üst Başlık Stilleri */
    .hero-title {
        font-size: 2rem;
        font-weight: 900;
        text-align: center;
        color: #F8FAFC;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
        text-transform: uppercase;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        text-align: center;
        color: #94A3B8;
        margin-bottom: 1.8rem;
        font-weight: 600;
    }

    /* Mobil Uyumlu DEVASA Butonlar */
    div.stButton > button {
        width: 100% !important;
        height: 85px !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #F87171 !important;
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.4) !important;
        transition: transform 0.08s ease, box-shadow 0.08s ease !important;
        margin-top: 12px !important;
        margin-bottom: 12px !important;
        letter-spacing: 0.5px !important;
    }
    
    div.stButton > button:active {
        transform: scale(0.94) !important;
    }
    
    /* DEVASA Metin Giriş Kutusu (Text Input) */
    div.stTextInput > div > div > input {
        height: 75px !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        border-radius: 18px !important;
        background-color: #1E293B !important;
        color: #F3F4F6 !important;
        border: 3px solid #3B82F6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3) !important;
    }
    
    div.stTextInput > div > div > input:focus {
        border-color: #60A5FA !important;
        box-shadow: 0 0 25px rgba(96, 165, 250, 0.6) !important;
    }
    
    /* Bilişsel Gürültü (Page 2) Taktik Kartı */
    .tactic-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
        border-radius: 24px;
        padding: 35px 15px;
        text-align: center;
        min-height: 260px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 35px rgba(239, 68, 68, 0.4);
        border: 2px solid #EF4444;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    
    .tactic-text-red {
        color: #EF4444;
        font-size: 2.5rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 20px rgba(239, 68, 68, 0.8);
    }
    
    .tactic-text-yellow {
        color: #F59E0B;
        font-size: 2.5rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 20px rgba(245, 158, 11, 0.8);
    }
    
    .tactic-text-cyan {
        color: #06B6D4;
        font-size: 2.5rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 20px rgba(6, 182, 212, 0.8);
    }

    /* Talimat Kutusu (Page 3) */
    .instruction-card {
        background: #1E293B;
        border-left: 6px solid #3B82F6;
        border-radius: 16px;
        padding: 22px 18px;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .instruction-text {
        font-size: 1.35rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.45;
        margin: 0;
    }

    /* Teşekkür / Bitiş Kutusu */
    .finish-card {
        background: linear-gradient(135deg, #064E3B 0%, #022C22 100%);
        border: 2px solid #10B981;
        border-radius: 20px;
        padding: 35px 20px;
        text-align: center;
        margin-top: 20px;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);
    }

    /* Sidebar Gizleme Stili */
    [data-testid="collapsedControl"] { display: block; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. STATE YÖNETİMİ (SESSION STATE)
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = 1  # 1: Giriş, 2: Gürültü Simülasyonu, 3: Tek Çapa, 4: Uzman Dashboard

if "athlete_name" not in st.session_state:
    st.session_state.athlete_name = ""

if "submitted" not in st.session_state:
    st.session_state.submitted = False

def reset_to_start():
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
    st.caption("Eskrim Bilişsel Aşırı Yüklenme & Tek Çapa Veri Toplama Aracı v2.0")

# ---------------------------------------------------------
# SAYFA 1: GİRİŞ VE BEKLEME (SPORCULAR İÇİN)
# ---------------------------------------------------------
if st.session_state.page == 1:
    st.markdown("<div class='hero-title'>⚔️ PİSTE DÖNÜŞ ODAK TESTİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>1 Dakikalık Mola Bilişsel Yüklenme Simülasyonu</div>", unsafe_allow_html=True)
    
    with st.form("entry_form"):
        st.markdown("<p style='font-size: 1.2rem; font-weight: 800; color: #94A3B8; text-align: center; margin-bottom: 8px;'>SPORCU ADI VEYA RUMUZU</p>", unsafe_allow_html=True)
        name_input = st.text_input("Sporcu Adı/Rumuz", label_visibility="collapsed", placeholder="Örn: Şampiyon / Sporcu 1")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("PİSTE ÇIKMAYA HAZIRIM ⚔️", type="primary")
        
        if submit_btn:
            if name_input.strip():
                st.session_state.athlete_name = name_input.strip()
                st.session_state.submitted = False
                st.session_state.page = 2
                st.rerun()
            else:
                st.warning("Lütfen devam etmek için Adınızı veya Rumuzunuzu giriniz.")

# ---------------------------------------------------------
# SAYFA 2: BİLİŞSEL GÜRÜLTÜ SİMÜLASYONU (COGNITIVE OVERLOAD)
# ---------------------------------------------------------
elif st.session_state.page == 2:
    st.markdown("<div class='hero-title'>🧠 BİLİŞSEL AŞIRI YÜKLENME</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>10 Saniye Antrenör Taktik Gürültüsü Simüle Ediliyor...</div>", unsafe_allow_html=True)
    
    # 7 Taktik Listesi
    tactics = [
        "MESAFENİ KORU!",
        "KOLUNU DÜZ TUT!",
        "BLÖF YEME!",
        "İKİNCİ HATTAN GİR!",
        "GERİ ADIM AT!",
        "SİLAHINI DÜŞÜRME!",
        "DİZLERİNİ BÜK!"
    ]
    colors = ["tactic-text-red", "tactic-text-yellow", "tactic-text-cyan"]
    
    placeholder = st.empty()
    
    # 10 Saniyelik Görsel Gürültü Döngüsü
    for i in range(10):
        tactic = random.choice(tactics)
        color_cls = random.choice(colors)
        
        placeholder.markdown(f"""
            <div class='tactic-box'>
                <div>
                    <p class='{color_cls}'>{tactic}</p>
                    <p style='color: #64748B; font-weight: 800; font-size: 1.1rem; margin-top: 25px; letter-spacing: 1px;'>
                        GÖRSEL ZİHİNSEL GÜRÜLTÜ: {i + 1} / 10 SN
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1.0)
        
    # 10 Saniye dolunca otomatik Sayfa 3'e geç
    st.session_state.page = 3
    st.rerun()

# ---------------------------------------------------------
# SAYFA 3: PİSTE DÖNÜŞ (TEK ÇAPA / ANCHOR WORD)
# ---------------------------------------------------------
elif st.session_state.page == 3:
    st.markdown("<div class='hero-title'>🎯 TEK ODAK KELİMESİ</div>", unsafe_allow_html=True)
    
    if not st.session_state.submitted:
        st.markdown("""
            <div class='instruction-card'>
                <p class='instruction-text'>
                     Hakem "Allez" demek üzere. Kafandaki tüm o gürültüyü filtrele. Piste hangi TEK KELİME ile çıkıyorsun?
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("anchor_form"):
            word_input = st.text_input("Tek Odak Kelimeniz", label_visibility="collapsed", placeholder="TEK KELİME YAZIN")
            
            st.markdown("<br>", unsafe_allow_html=True)
            lock_btn = st.form_submit_button("KELİMEYİ KİLİTLE 🔒", type="primary")
            
            if lock_btn:
                word_clean = word_input.strip()
                if word_clean:
                    # Sadece 1 kelime kontrolü veya direkt kaydetme
                    success = save_entry(st.session_state.athlete_name, word_clean)
                    if success:
                        st.session_state.submitted = True
                        st.rerun()
                else:
                    st.warning("Lütfen piste çıkış için TEK KELİME yazınız.")
    else:
        st.markdown("""
            <div class='finish-card'>
                <h1 style='color: #34D399; font-size: 2.2rem; font-weight: 900; margin-bottom: 15px;'>🧘‍♂️ DERİN BİR NEFES AL VE PİSTE DÖN</h1>
                <p style='color: #E2E8F0; font-size: 1.3rem; font-weight: 700; line-height: 1.5;'>
                    Odak kelimen başarıyla sisteme kilitlendi.<br>
                    Başarılar Şampiyon! ⚔️
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("YENİDEN BAŞLA (YENİ MOLA) 🔄"):
            reset_to_start()
            st.rerun()

# ---------------------------------------------------------
# SAYFA 4: UZMAN DASHBOARD'U (YÖNETİCİ EKRANI)
# ---------------------------------------------------------
elif st.session_state.page == 4:
    st.markdown("<div class='hero-title'>📊 UZMAN DASHBOARD'U</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Canlı Sporcu Odak Kelimeleri & Frekans Analizi</div>", unsafe_allow_html=True)
    
    df_entries = get_all_entries()
    
    if not df_entries.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Toplam Girilen Kayıt", f"{len(df_entries)} Sporcu")
        with col2:
            unique_words = df_entries["Odak Kelimesi"].nunique()
            st.metric("Farklı Odak Kelimeleri", f"{unique_words} Adet")
            
        st.markdown("---")
        st.markdown("### 📋 Canlı Sporcu Odak Kelimeleri Listesi")
        st.dataframe(df_rounds := df_entries, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 📈 Odak Kelimeleri Frekans Dağılımı")
        
        # Frekans hesabı
        freq_df = df_entries["Odak Kelimesi"].value_counts().reset_index()
        freq_df.columns = ["Odak Kelimesi", "Kullanım Sayısı"]
        
        st.dataframe(freq_df, use_container_width=True, hide_index=True)
        st.bar_chart(freq_df.set_index("Odak Kelimesi"))
        
        st.markdown("---")
        # CSV İndirme Butonu
        csv_bytes = df_entries.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tüm Verileri İndir (CSV)",
            data=csv_bytes,
            file_name=f"eskrim_odak_kelimeleri_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
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
        st.info("Henüz kaydedilmiş sporcu odağı verisi bulunmuyor.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(" Sporcu Ana Sayfasına Dön 🏠", use_container_width=True):
        reset_to_start()
        st.rerun()
