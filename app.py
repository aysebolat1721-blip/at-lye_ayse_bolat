import streamlit as st
import pandas as pd
import sqlite3
import datetime
import time
import random

# ---------------------------------------------------------
# 1. VERİ TABANI YÖNETİMİ (SQLite3 - gonogo.db)
# ---------------------------------------------------------
DB_NAME = "gonogo.db"

def init_db():
    """sqlite3 veri tabanı tablolarını otomatik oluşturur."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        
        # Kullanıcılar (Online durumları)
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                is_online INTEGER DEFAULT 1,
                last_active TEXT NOT NULL
            )
        ''')
        
        # Skor Özeti (Leaderboard için)
        c.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                username TEXT PRIMARY KEY,
                avg_speed_ms REAL NOT NULL,
                fault_count INTEGER NOT NULL,
                total_rounds INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Detaylı Tur Günlükleri (Uzman Analizi için)
        c.execute('''
            CREATE TABLE IF NOT EXISTS trial_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                round_num INTEGER NOT NULL,
                target_color TEXT NOT NULL,
                reaction_ms REAL,
                is_fault INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Veri tabanı başlatma hatası: {e}")

def set_user_online(username: str):
    """Kullanıcıyı Online olarak işaretler ve son aktiflik süresini günceller."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO users (username, is_online, last_active)
            VALUES (?, 1, ?)
            ON CONFLICT(username) DO UPDATE SET is_online=1, last_active=?
        ''', (username.strip(), now_str, now_str))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def save_score_summary(username: str, avg_speed: float, faults: int, total_rounds: int = 10):
    """Sporcunun genel oyun özetini skor tablosuna işler."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO scores (username, avg_speed_ms, fault_count, total_rounds, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                avg_speed_ms=?,
                fault_count=?,
                total_rounds=?,
                updated_at=?
        ''', (username.strip(), avg_speed, faults, total_rounds, now_str,
              avg_speed, faults, total_rounds, now_str))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Skor kaydetme hatası: {e}")

def save_trial_log(username: str, round_num: int, color: str, reaction_ms: float, is_fault: int):
    """Her tur detayını klinik veri tabanına ekler."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO trial_logs (username, round_num, target_color, reaction_ms, is_fault, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username.strip(), round_num, color, reaction_ms, is_fault, now_str))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def get_online_users():
    """Şu an aktif/online olan sporcuları getirir."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE is_online = 1 ORDER BY last_active DESC LIMIT 15")
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []

def get_leaderboard_df():
    """
    Canlı Skor Tablosu (Leaderboard):
    Sıralama: Önce En Az Kırmızıya Basanlar (fault_count ASC), sonra En Düşük Ortalama Milisaniye (avg_speed_ms ASC).
    """
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        df = pd.read_sql_query('''
            SELECT 
                username AS 'Sporcu',
                fault_count AS 'Blöf / Hata',
                ROUND(avg_speed_ms, 1) AS 'Ort. Hız (ms)'
            FROM scores
            ORDER BY fault_count ASC, avg_speed_ms ASC
        ''', conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def get_all_trials_df():
    """Uzman paneli için tüm tur loglarını getirir."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        df = pd.read_sql_query('''
            SELECT 
                id AS 'ID',
                username AS 'Sporcu',
                round_num AS 'Tur No',
                target_color AS 'Hedef Renk',
                ROUND(reaction_ms, 1) AS 'Reaksiyon (ms)',
                is_fault AS 'Hata Var Mı',
                timestamp AS 'Tarih / Saat'
            FROM trial_logs
            ORDER BY id DESC
        ''', conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def clear_db():
    """Tüm veri tabanını sıfırlar."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM users")
        c.execute("DELETE FROM scores")
        c.execute("DELETE FROM trial_logs")
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# Veri tabanını otomatik initialize et
init_db()

# ---------------------------------------------------------
# 2. SAYFA YAPILANDIRMASI VE NEON E-SPORTS CSS TASARIMI
# ---------------------------------------------------------
st.set_page_config(
    page_title="Go/No-Go Motor Frenleme Simülasyonu",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# E-Spor Dark Mode & Neon CSS Injection
st.markdown("""
    <style>
    /* Global E-Sports Dark Mode Background */
    .stApp {
        background-color: #080A10;
        color: #F8FAFC;
    }
    
    .block-container {
        max-width: 600px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* E-Sports Neon Başlık */
    .esports-title {
        font-size: 2.1rem;
        font-weight: 900;
        text-align: center;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 15px rgba(0, 255, 102, 0.6), 0 0 30px rgba(0, 255, 102, 0.3);
        margin-bottom: 0.2rem;
    }

    .esports-subtitle {
        font-size: 0.95rem;
        text-align: center;
        color: #94A3B8;
        font-weight: 700;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }

    /* KURAL KARTLARI */
    .rule-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
        border: 2px solid #00FF66;
        box-shadow: 0 0 25px rgba(0, 255, 102, 0.25);
        border-radius: 18px;
        padding: 22px 18px;
        margin-bottom: 24px;
    }

    .rule-text {
        font-size: 1.15rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.55;
        margin: 0;
    }

    /* NEON DAİRELER */
    .circle-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 25px 0;
    }

    .circle-gray {
        width: 210px;
        height: 210px;
        border-radius: 50%;
        background: radial-gradient(circle, #334155 0%, #0F172A 100%);
        border: 4px solid #64748B;
        box-shadow: 0 0 25px rgba(100, 116, 139, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94A3B8;
        font-size: 1.4rem;
        font-weight: 900;
    }

    .circle-green {
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, #00FF66 0%, #059669 100%);
        border: 5px solid #34D399;
        box-shadow: 0 0 50px #00FF66, 0 0 100px rgba(0, 255, 102, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000000;
        font-size: 2.2rem;
        font-weight: 900;
        animation: pulse-green 0.2s ease-in-out;
    }

    .circle-red {
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, #FF0055 0%, #991B1B 100%);
        border: 5px solid #F87171;
        box-shadow: 0 0 50px #FF0055, 0 0 100px rgba(255, 0, 85, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 2rem;
        font-weight: 900;
        animation: pulse-red 0.2s ease-in-out;
    }

    @keyframes pulse-green {
        0% { transform: scale(0.9); }
        100% { transform: scale(1); }
    }

    @keyframes pulse-red {
        0% { transform: scale(0.9); }
        100% { transform: scale(1); }
    }

    /* NEON VUR BUTONU */
    .btn-attack button {
        width: 100% !important;
        height: 90px !important;
        background: linear-gradient(135deg, #00FF66 0%, #059669 100%) !important;
        color: #000000 !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        border-radius: 20px !important;
        border: 3px solid #34D399 !important;
        box-shadow: 0 0 35px rgba(0, 255, 102, 0.7) !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        letter-spacing: 1px !important;
    }
    
    .btn-attack button:active {
        transform: scale(0.93) !important;
    }

    /* BEKLE / PAS BUTONU */
    .btn-wait button {
        width: 100% !important;
        height: 75px !important;
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        border-radius: 18px !important;
        border: 2px solid #60A5FA !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.5) !important;
        margin-top: 5px !important;
    }

    /* DEVASA INPUT */
    div.stTextInput > div > div > input {
        height: 70px !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        border-radius: 16px !important;
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 3px solid #00FF66 !important;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.3) !important;
    }

    /* BİTİŞ KARTI */
    .finish-card {
        background: linear-gradient(135deg, #0F172A 0%, #022C22 100%);
        border: 2px solid #00FF66;
        box-shadow: 0 0 35px rgba(0, 255, 102, 0.4);
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        margin-top: 15px;
    }

    /* HATA UYARI KARTI */
    .alert-fault-box {
        background: linear-gradient(90deg, #DC2626, #991B1B);
        border: 2px solid #F87171;
        box-shadow: 0 0 25px rgba(220, 38, 38, 0.8);
        border-radius: 14px;
        padding: 14px;
        text-align: center;
        color: #FFFFFF;
        font-size: 1.3rem;
        font-weight: 900;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. STATE YÖNETİMİ (SESSION STATE)
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = 1  # 1: Giriş, 2: Oyun Ekranı, 3: Bitiş Ekranı, 4: Uzman Dashboard

if "athlete_name" not in st.session_state:
    st.session_state.athlete_name = ""

if "game_sequence" not in st.session_state:
    st.session_state.game_sequence = []

if "current_round" not in st.session_state:
    st.session_state.current_round = 0

if "round_phase" not in st.session_state:
    st.session_state.round_phase = "ready"  # "ready", "waiting", "active", "evaluated"

if "stimulus_time" not in st.session_state:
    st.session_state.stimulus_time = None

if "game_results" not in st.session_state:
    st.session_state.game_results = []  # List of dicts per round

if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = ""

def start_new_game():
    """10 turluk yeni oyun dizilimi oluşturur (7 Yeşil, 3 Kırmızı)."""
    seq = ["YEŞİL"] * 7 + ["KIRMIZI"] * 3
    random.shuffle(seq)
    st.session_state.game_sequence = seq
    st.session_state.current_round = 0
    st.session_state.round_phase = "waiting"
    st.session_state.game_results = []
    st.session_state.last_feedback = ""

# ---------------------------------------------------------
# 4. SİDEBAR: CANLI SALON VE LEADERBOARD (TÜM SAYFALARDA)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🟢 Salonda Olanlar (Online)")
    online_list = get_online_users()
    if online_list:
        for u in online_list:
            st.markdown(f"🟢 **{u}**")
    else:
        st.caption("Henüz aktif sporcu yok.")
        
    st.markdown("---")
    st.markdown("### 🏆 CANLI SKOR TABLOSU")
    st.caption("🥇 Öncelik: En Az Blöf/Hata | 🥈 İkincil: En Düşük Ortalama (ms)")
    
    df_lb = get_leaderboard_df()
    if not df_lb.empty:
        # İkonlu derece ekleme
        df_lb_display = df_lb.copy()
        ranks = []
        for i in range(len(df_lb_display)):
            if i == 0: ranks.append("🥇 1.")
            elif i == 1: ranks.append("🥈 2.")
            elif i == 2: ranks.append("🥉 3.")
            else: ranks.append(f"#{i+1}")
        df_lb_display.insert(0, "Sıra", ranks)
        st.dataframe(df_lb_display, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz tamamlanan skor yok.")
        
    st.markdown("---")
    with st.expander("🔒 Uzman Girişi"):
        admin_pass = st.text_input("Şifre:", type="password")
        if admin_pass == "tohm2026":
            if st.button("📊 Uzman Dashboard'una Git", use_container_width=True):
                st.session_state.page = 4
                st.rerun()

# ---------------------------------------------------------
# SAYFA 1: GİRİŞ VE OYUN KURALLARI
# ---------------------------------------------------------
if st.session_state.page == 1:
    st.markdown("<div class='esports-title'>⚡ DÜRTÜ KONTROLÜ & MOTOR FRENLEME</div>", unsafe_allow_html=True)
    st.markdown("<div class='esports-subtitle'>CANLI REKABETÇİ VUR / BEKLE OYUNU</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='rule-card'>
            <p class='rule-text'>
                🔥 <b>KURAL BASİT:</b><br><br>
                🟢 Daire <b>YEŞİL</b> yanınca en hızlı şekilde <b>VUR!</b><br>
                🔴 Daire <b>KIRMIZI</b> yanarsa blöftür, <b>SAKIN BASMA!</b><br><br>
                ⚡ Erken basarsan yanarsın. Sadece hızlı olan değil, soğukkanlı olan kazanır. Hazırsan piste çık!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("<p style='font-size: 1.2rem; font-weight: 800; color: #00FF66; text-align: center; margin-bottom: 5px;'>SPORCU RUMUZU</p>", unsafe_allow_html=True)
        name_in = st.text_input("Sporcu Rumuzu", label_visibility="collapsed", placeholder="Rumuzunuzu yazın")
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_start = st.form_submit_button("PİSTE ÇIK ⚡", type="primary")
        
        if btn_start:
            if name_in.strip():
                st.session_state.athlete_name = name_in.strip()
                set_user_online(name_in.strip())
                start_new_game()
                st.session_state.page = 2
                st.rerun()
            else:
                st.warning("Lütfen bir rumuz giriniz.")

# ---------------------------------------------------------
# SAYFA 2: OYUN EKRANI (GO / NO-GO SİMÜLASYONU)
# ---------------------------------------------------------
elif st.session_state.page == 2:
    round_num = st.session_state.current_round + 1  # 1..10
    target_color = st.session_state.game_sequence[st.session_state.current_round]
    
    st.markdown(f"<div class='esports-title'>TUR {round_num} / 10</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='esports-subtitle'>Sporcu: {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    
    # 1. BEKLEME EVRESİ (Rastgele 1.0 - 2.5 sn Gri Daire)
    if st.session_state.round_phase == "waiting":
        st.markdown("""
            <div class='circle-container'>
                <div class='circle-gray'>
                    HAZIRLAN...
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Erken basış engelleme / bekleme süresi
        delay = random.uniform(1.0, 2.5)
        time.sleep(delay)
        
        # Aktif renge geç
        st.session_state.round_phase = "active"
        st.session_state.stimulus_time = time.time()
        st.rerun()
        
    # 2. AKTİF EVRE (Yeşil veya Kırmızı Daire Görünümü)
    elif st.session_state.round_phase == "active":
        if target_color == "YEŞİL":
            st.markdown("""
                <div class='circle-container'>
                    <div class='circle-green'>
                        VUR! ⚔️
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class='circle-container'>
                    <div class='circle-red'>
                        BLÖF! 🛑
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # Butonlar
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='btn-attack'>", unsafe_allow_html=True)
            vur_btn = st.button("VUR! ⚔️", key=f"vur_{round_num}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='btn-wait'>", unsafe_allow_html=True)
            bekle_btn = st.button("PAS / BEKLE 🛡️", key=f"bekle_{round_num}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        click_time = time.time()
        
        # BUTON ETKİLEŞİM HESAPLAMALARI
        if vur_btn:
            elapsed_ms = round((click_time - st.session_state.stimulus_time) * 1000, 1)
            
            if target_color == "YEŞİL":
                # Başarılı Vuruş!
                is_fault = 0
                st.session_state.last_feedback = f"⚡ Harika Vuruş! Süre: {elapsed_ms} ms"
            else:
                # Kırmızıya Basıldı -> Blöfü Yedi (HATA)
                is_fault = 1
                elapsed_ms = 999.0  # Cezalı süre
                st.session_state.last_feedback = "🚨 BLÖFÜ YEDİN! (HATA ❌)"
                
            # Log ve tur kaydı
            save_trial_log(st.session_state.athlete_name, round_num, target_color, elapsed_ms, is_fault)
            st.session_state.game_results.append({
                "round": round_num,
                "color": target_color,
                "ms": elapsed_ms,
                "is_fault": is_fault
            })
            
            st.session_state.current_round += 1
            if st.session_state.current_round >= 10:
                st.session_state.page = 3
            else:
                st.session_state.round_phase = "waiting"
            st.rerun()
            
        elif bekle_btn:
            if target_color == "KIRMIZI":
                # Başarılı Frenleme / Motor İnhibisyon!
                is_fault = 0
                elapsed_ms = 0.0
                st.session_state.last_feedback = "🛡️ Harika Soğukkanlılık! Blöfe Kanmadın!"
            else:
                # Yeşilde Basmadı -> Kaçırılan Fırsat (HATA)
                is_fault = 1
                elapsed_ms = 999.0
                st.session_state.last_feedback = "⚠️ Yeşili Kaçırdın! (HATA ❌)"
                
            save_trial_log(st.session_state.athlete_name, round_num, target_color, elapsed_ms, is_fault)
            st.session_state.game_results.append({
                "round": round_num,
                "color": target_color,
                "ms": elapsed_ms,
                "is_fault": is_fault
            })
            
            st.session_state.current_round += 1
            if st.session_state.current_round >= 10:
                st.session_state.page = 3
            else:
                st.session_state.round_phase = "waiting"
            st.rerun()

# ---------------------------------------------------------
# SAYFA 3: SPORCU BİTİŞ EKRANI
# ---------------------------------------------------------
elif st.session_state.page == 3:
    st.markdown("<div class='esports-title'>🏆 TUR TAMAMLANDI!</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='esports-subtitle'>Sporcu: {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    
    # Ortalama hız ve Hata hesabı
    valid_speeds = [r["ms"] for r in st.session_state.game_results if r["is_fault"] == 0 and r["color"] == "YEŞİL"]
    avg_speed_ms = round(sum(valid_speeds) / len(valid_speeds), 1) if valid_speeds else 999.0
    
    total_faults = sum(r["is_fault"] for r in st.session_state.game_results)
    
    # Skorları DB'ye yaz (Canlı Leaderboard anında güncellenir)
    save_score_summary(st.session_state.athlete_name, avg_speed_ms, total_faults, total_rounds=10)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎯 Ort. Reaksiyon Hızı", f"{avg_speed_ms} ms")
    with col2:
        st.metric("🚨 Yediğin Blöf / Hata", f"{total_faults} Adet")
        
    st.markdown("""
        <div class='finish-card'>
            <h2 style='color: #00FF66; margin-bottom: 10px;'>⚡ SKORUN CANLI TABLOYA YAZILDI!</h2>
            <p style='color: #CBD5E1; font-size: 1.15rem; font-weight: 700;'>
                Rakiplerini ve salondaki dereceni <b>sol menüdeki (Sidebar) CANLI SKOR TABLOSUNDAN</b> anlık takip et!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("YENİDEN PİSTE ÇIK (TEKRAR DENE) 🔄", type="primary"):
        start_new_game()
        st.session_state.page = 2
        st.rerun()

# ---------------------------------------------------------
# SAYFA 4: UZMAN DASHBOARD'U (YÖNETİCİ EKRANI)
# ---------------------------------------------------------
elif st.session_state.page == 4:
    st.markdown("<div class='esports-title'>📊 UZMAN DASHBOARD'U</div>", unsafe_allow_html=True)
    st.markdown("<div class='esports-subtitle'>Klinik Go/No-Go Dürtü Kontrolü Veri Analizi</div>", unsafe_allow_html=True)
    
    df_trials = get_all_trials_df()
    
    if not df_trials.empty:
        st.markdown("### 📋 Tüm Tur Detayları (Canlı Akış)")
        st.dataframe(df_trials, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        # CSV İndirme Butonu
        csv_bytes = df_trials.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tüm Verileri CSV Olarak İndir",
            data=csv_bytes,
            file_name=f"durtsel_kontrol_verileri_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚠️ Veri Tabanı Yönetimi"):
            if st.button("🗑️ Tüm Veri Tabanını Sıfırla / Sil", use_container_width=True):
                if clear_db():
                    st.success("Tüm veriler sıfırlandı!")
                    st.rerun()
    else:
        st.info("Henüz kaydedilmiş tur verisi bulunmuyor.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(" Sporcu Ana Sayfasına Dön 🏠", use_container_width=True):
        st.session_state.page = 1
        st.rerun()
