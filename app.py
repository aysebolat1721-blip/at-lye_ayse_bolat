import streamlit as st
import pandas as pd
import sqlite3
import datetime
import time
import random

# ---------------------------------------------------------
# 1. VERİ TABANI YÖNETİMİ (SQLite3 - sok_testi.db)
# ---------------------------------------------------------
DB_NAME = "sok_testi.db"

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
                event_type TEXT NOT NULL,
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
    except Exception:
        pass

def set_user_offline(username: str):
    """Sporcu testi bitirdiğinde veya çıkış yaptığında Online durumunu 0 yapar."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            UPDATE users SET is_online = 0, last_active = ? WHERE username = ?
        ''', (now_str, username.strip()))
        conn.commit()
        conn.close()
    except Exception:
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

def save_trial_log(username: str, round_num: int, event_type: str, reaction_ms: float, is_fault: int):
    """Her tur detayını klinik veri tabanına ekler."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO trial_logs (username, round_num, event_type, reaction_ms, is_fault, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username.strip(), round_num, event_type, reaction_ms, is_fault, now_str))
        conn.commit()
        conn.close()
    except Exception:
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
    Sıralama: Önce En Az Hata Yapanlar (fault_count ASC), sonra En Düşük MS Hızına Sahip Olanlar (avg_speed_ms ASC).
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
                event_type AS 'Olay Tipi',
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
# 2. MÜKEMMEL ORTALANMIŞ CSS ENJEKSİYONU & DARK MODE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Karanlık Oda: Reaksiyon ve Fren",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# TAM ORTALANMIŞ VE SİMETRİK CSS
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #030712;
        color: #F8FAFC;
    }
    
    /* Yan Panel (Sidebar) Görünürlüğü ve Stili */
    section[data-testid="stSidebar"] {
        background-color: #090D16 !important;
        border-right: 2px solid #1E293B !important;
    }

    /* Streamlit Üst Bar ve Yan Panel Butonunu Açık/Görünür Tut */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 99 !important;
    }

    [data-testid="collapsedControl"], button[data-testid="baseButton-headerNoPadding"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        color: #00FF66 !important;
    }
    
    /* MÜKEMMEL TAM MERKEZLEME CONTAINER'I (Mobil & Masaüstü Üst Boşluk) */
    .block-container {
        max-width: 520px !important;
        padding-top: 3.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    
    [data-testid="stVerticalBlock"] {
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
    }

    /* Mükemmel Ortalanmış Başlıklar */
    .centered-title {
        font-size: 2.1rem;
        font-weight: 900;
        text-align: center;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        text-shadow: 0 0 25px rgba(0, 255, 102, 0.8);
        margin-bottom: 0.3rem;
        width: 100%;
    }

    .centered-subtitle {
        font-size: 0.95rem;
        text-align: center;
        color: #94A3B8;
        font-weight: 700;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
        width: 100%;
    }

    /* ANİ FLAŞ VE ŞOK KARTLARI */
    .shock-card-black {
        background: #000000;
        border: 3px solid #1E293B;
        border-radius: 24px;
        padding: 45px 20px;
        width: 100%;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9);
        margin-bottom: 20px;
    }

    .shock-card-green {
        background: radial-gradient(circle, #00FF66 0%, #059669 100%);
        border: 5px solid #34D399;
        border-radius: 24px;
        padding: 45px 20px;
        width: 100%;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 0 60px #00FF66, 0 0 120px rgba(0, 255, 102, 0.8);
        margin-bottom: 20px;
        animation: flash-pop 0.12s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .shock-card-red {
        background: radial-gradient(circle, #FF0055 0%, #991B1B 100%);
        border: 5px solid #F87171;
        border-radius: 24px;
        padding: 45px 20px;
        width: 100%;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 0 60px #FF0055, 0 0 120px rgba(255, 0, 85, 0.8);
        margin-bottom: 20px;
        animation: flash-pop 0.12s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .shock-card-white {
        background: #FFFFFF;
        border: 5px solid #E2E8F0;
        border-radius: 24px;
        padding: 45px 20px;
        width: 100%;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 0 100px #FFFFFF;
        margin-bottom: 20px;
    }

    @keyframes flash-pop {
        0% { transform: scale(0.35); opacity: 0; }
        80% { transform: scale(1.06); opacity: 1; }
        100% { transform: scale(1); }
    }

    /* MÜKEMMEL DENGELİ DEVE BUTONLAR */
    div.stButton > button {
        width: 100% !important;
        height: 85px !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        border-radius: 20px !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        letter-spacing: 1px !important;
    }

    .btn-green button {
        background: linear-gradient(135deg, #00FF66 0%, #059669 100%) !important;
        color: #000000 !important;
        border: 3px solid #34D399 !important;
        box-shadow: 0 0 35px rgba(0, 255, 102, 0.7) !important;
    }

    .btn-blue button {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 3px solid #60A5FA !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.5) !important;
    }

    div.stButton > button:active {
        transform: scale(0.94) !important;
    }

    /* ORTALANMIŞ İNPUT */
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

    /* Geri Bildirim Metni */
    .feedback-banner {
        background: #1E293B;
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 15px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. STATE YÖNETİMİ (SESSION STATE)
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = 1  # 1: Giriş, 2: Oyun, 3: Bitiş, 4: Uzman Dashboard

if "athlete_name" not in st.session_state:
    st.session_state.athlete_name = ""

if "game_sequence" not in st.session_state:
    st.session_state.game_sequence = []

if "current_round" not in st.session_state:
    st.session_state.current_round = 0

if "round_phase" not in st.session_state:
    st.session_state.round_phase = "ready"  # "waiting", "flashing_white", "active"

if "stimulus_time" not in st.session_state:
    st.session_state.stimulus_time = None

if "game_results" not in st.session_state:
    st.session_state.game_results = []

if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = ""

def generate_shock_sequence():
    """10 turluk şok olasılık dizilimi üretir (50% Atak, 30% Blöf, 20% Ters Köşe Blöf)."""
    pool = ["NET_ATAK"] * 5 + ["NET_BLOF"] * 3 + ["TERS_KESE_BLOF"] * 2
    random.shuffle(pool)
    return pool

def start_new_game():
    st.session_state.game_sequence = generate_shock_sequence()
    st.session_state.current_round = 0
    st.session_state.round_phase = "waiting"
    st.session_state.game_results = []
    st.session_state.last_feedback = ""

# ---------------------------------------------------------
# 4. SİDEBAR: CANLI SALON VE LEADERBOARD (TÜM SAYFALARDA)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🟢 Salondakiler (Online)")
    online_list = get_online_users()
    if online_list:
        for u in online_list:
            st.markdown(f"🟢 **{u}**")
    else:
        st.caption("Henüz aktif sporcu yok.")
        
    st.markdown("---")
    st.markdown("### 🏆 CANLI SKOR (LEADERBOARD)")
    st.caption("🥇 Öncelik: En Az Blöf/Hata | 🥈 İkincil: En Düşük MS Hızı")
    
    df_lb = get_leaderboard_df()
    if not df_lb.empty:
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
        st.info("Henüz skor yok.")
        
    st.markdown("---")
    with st.expander("🔒 Admin Girişi"):
        admin_pass = st.text_input("Şifre:", type="password")
        if admin_pass == "tohm2026":
            if st.button("📊 Uzman Dashboard'una Git", use_container_width=True):
                st.session_state.page = 4
                st.rerun()

# ---------------------------------------------------------
# SAYFA 1: GİRİŞ VE BEKLEME LOBİSİ
# ---------------------------------------------------------
if st.session_state.page == 1:
    st.markdown("<div class='centered-title'>⚡ KARANLIK ODA ⚡</div>", unsafe_allow_html=True)
    st.markdown("<div class='centered-subtitle'>REAKSİYON VE FREN SİMÜLASYONU</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='shock-card-black' style='min-height: auto; padding: 25px;'>
            <p style='font-size: 1.15rem; font-weight: 800; color: #F8FAFC; line-height: 1.6; margin: 0;'>
                🟢 <b>NEON YEŞİL</b> = EN HIZLI ŞEKİLDE <b>VUR!</b><br>
                🔴 <b>NEON KIRMIZI / BEYAZ FLAŞ</b> = BLÖF! <b>EKRANA SAKIN DOKUNMA!</b><br><br>
                <i>Blöfte ekrana dokunmazsan 1.5 saniye sonra tur otomatik geçilir. Soğukkanlı ol, hazırsan piste çık!</i>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("<p style='font-size: 1.2rem; font-weight: 800; color: #00FF66; text-align: center;'>SPORCU RUMUZU</p>", unsafe_allow_html=True)
        name_in = st.text_input("Rumuz", label_visibility="collapsed", placeholder="Rumuzunuzu yazın")
        
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
# SAYFA 2: OYUN EKRANI (ANİ FLAŞ VE ŞOK MEKANİĞİ)
# ---------------------------------------------------------
elif st.session_state.page == 2:
    round_num = st.session_state.current_round + 1  # 1..10
    event_type = st.session_state.game_sequence[st.session_state.current_round]
    
    st.markdown(f"<div class='centered-title'>TUR {round_num} / 10</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='centered-subtitle'>Sporcu: {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    
    # 1. ZİFİRİ KARANLIK BEKLEME EVRESİ (1.5 - 5.0 sn Tahmin Edilemez)
    if st.session_state.round_phase == "waiting":
        st.markdown("""
            <div class='shock-card-black'>
                <h2 style='color: #64748B; font-weight: 900; letter-spacing: 2px;'>BEKLE... 🛑</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # 1.5 - 5.0 saniye arası tamamen belirsiz rastgele süre
        delay = random.uniform(1.5, 5.0)
        time.sleep(delay)
        
        # Eğer Ters Köşe Blöf ise önce 0.18s Beyaz Flaş yap
        if event_type == "TERS_KESE_BLOF":
            st.session_state.round_phase = "flashing_white"
        else:
            st.session_state.round_phase = "active"
            st.session_state.stimulus_time = time.time()
        st.rerun()

    # 1.5 BEYAZ FLAŞ EKRANI (Ters Köşe Blöf için 0.18 saniye şok parlaması)
    elif st.session_state.round_phase == "flashing_white":
        st.markdown("""
            <div class='shock-card-white'>
                <h1 style='color: #000000; font-size: 3rem; font-weight: 900;'>⚡ FLASH! ⚡</h1>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(0.18)
        st.session_state.round_phase = "active"
        st.session_state.stimulus_time = time.time()
        st.rerun()

    # 2. ANİDEN PATLAYAN ŞOK EKRANI (Yeşil veya Kırmızı) + CANLI AKAN MİLİSANİYE SAYACI
    elif st.session_state.round_phase == "active":
        if event_type == "NET_ATAK":
            st.markdown("""
                <div class='shock-card-green'>
                    <h1 style='color: #000000; font-size: 3.5rem; font-weight: 900; margin: 0;'>VUR! ⚔️</h1>
                    <div id='ms-counter' style='font-family: monospace; font-size: 2.2rem; font-weight: 900; color: #000000; margin-top: 10px; text-shadow: 0 0 10px rgba(0,0,0,0.3);'>0 ms</div>
                </div>
                <script>
                    (function() {
                        var start = performance.now();
                        function updateMs() {
                            var el = document.getElementById('ms-counter');
                            if (el) {
                                var currentMs = Math.floor(performance.now() - start);
                                el.innerText = currentMs + ' ms';
                                requestAnimationFrame(updateMs);
                            }
                        }
                        requestAnimationFrame(updateMs);
                    })();
                </script>
            """, unsafe_allow_html=True)
        elif event_type == "NET_BLOF":
            st.markdown("""
                <div class='shock-card-red'>
                    <h1 style='color: #FFFFFF; font-size: 3.2rem; font-weight: 900; margin: 0;'>DUR! 🛑</h1>
                    <p style='color: #FFD1D1; font-weight: 800; font-size: 1.2rem; margin-top: 5px;'>NET BLÖF!</p>
                    <div id='ms-counter' style='font-family: monospace; font-size: 2.2rem; font-weight: 900; color: #FFFFFF; margin-top: 10px; text-shadow: 0 0 15px rgba(255,255,255,0.6);'>0 ms</div>
                </div>
                <script>
                    (function() {
                        var start = performance.now();
                        function updateMs() {
                            var el = document.getElementById('ms-counter');
                            if (el) {
                                var currentMs = Math.floor(performance.now() - start);
                                el.innerText = currentMs + ' ms';
                                requestAnimationFrame(updateMs);
                            }
                        }
                        requestAnimationFrame(updateMs);
                    })();
                </script>
            """, unsafe_allow_html=True)
        elif event_type == "TERS_KESE_BLOF":
            st.markdown("""
                <div class='shock-card-red'>
                    <h1 style='color: #FFFFFF; font-size: 3.2rem; font-weight: 900; margin: 0;'>DUR! 🛑</h1>
                    <p style='color: #FFD1D1; font-weight: 800; font-size: 1.2rem; margin-top: 5px;'>⚡ TERS KÖŞE BLÖF!</p>
                    <div id='ms-counter' style='font-family: monospace; font-size: 2.2rem; font-weight: 900; color: #FFFFFF; margin-top: 10px; text-shadow: 0 0 15px rgba(255,255,255,0.6);'>0 ms</div>
                </div>
                <script>
                    (function() {
                        var start = performance.now();
                        function updateMs() {
                            var el = document.getElementById('ms-counter');
                            if (el) {
                                var currentMs = Math.floor(performance.now() - start);
                                el.innerText = currentMs + ' ms';
                                requestAnimationFrame(updateMs);
                            }
                        }
                        requestAnimationFrame(updateMs);
                    })();
                </script>
            """, unsafe_allow_html=True)
            
        # TEK DEVASA VUR! BUTONU (BLÖFTE EKRANA DOKUNULMAZ!)
        st.markdown("<div class='btn-green'>", unsafe_allow_html=True)
        vur_btn = st.button("VUR! ⚔️", key=f"vur_{round_num}")
        st.markdown("</div>", unsafe_allow_html=True)
            
        click_time = time.time()
        
        # 1. SPORCU VUR! BUTONUNA BASTIYSA
        if vur_btn:
            elapsed_ms = round((click_time - st.session_state.stimulus_time) * 1000, 1)
            
            if event_type == "NET_ATAK":
                is_fault = 0
                st.session_state.last_feedback = f"⚡ ŞİMŞEK GİBİ VURUŞ! Süre: {elapsed_ms} ms"
            else:
                is_fault = 1
                elapsed_ms = 999.0
                st.session_state.last_feedback = "🚨 BLÖFÜ YEDİN! (HATA ❌)"
                
            save_trial_log(st.session_state.athlete_name, round_num, event_type, elapsed_ms, is_fault)
            st.session_state.game_results.append({
                "round": round_num,
                "event": event_type,
                "ms": elapsed_ms,
                "is_fault": is_fault
            })
            
            st.session_state.current_round += 1
            if st.session_state.current_round >= 10:
                st.session_state.page = 3
            else:
                st.session_state.round_phase = "waiting"
            st.rerun()

        # 2. EĞER BLÖF İSE VE SPORCU 1.5 SN EKRANA DOKUNMADAN BEKLEDİYSE (BAŞARILI FRENLEME)
        elif event_type in ["NET_BLOF", "TERS_KESE_BLOF"]:
            # Blöfte 1.5 saniye ekrana dokunulmazsa otomatik başarılı geçiş yap
            if (click_time - st.session_state.stimulus_time) >= 1.5:
                is_fault = 0
                elapsed_ms = 0.0
                st.session_state.last_feedback = "🛡️ HARİKA SOĞUKKANLILIK! Blöfe Kanmadın!"
                
                save_trial_log(st.session_state.athlete_name, round_num, event_type, elapsed_ms, is_fault)
                st.session_state.game_results.append({
                    "round": round_num,
                    "event": event_type,
                    "ms": elapsed_ms,
                    "is_fault": is_fault
                })
                
                st.session_state.current_round += 1
                if st.session_state.current_round >= 10:
                    st.session_state.page = 3
                else:
                    st.session_state.round_phase = "waiting"
                st.rerun()
                
            save_trial_log(st.session_state.athlete_name, round_num, event_type, elapsed_ms, is_fault)
            st.session_state.game_results.append({
                "round": round_num,
                "event": event_type,
                "ms": elapsed_ms,
                "is_fault": is_fault
            })
            
            st.session_state.current_round += 1
            if st.session_state.current_round >= 10:
                st.session_state.page = 3
            else:
                st.session_state.round_phase = "waiting"
            st.rerun()

    if st.session_state.last_feedback:
        st.markdown(f"<div class='feedback-banner'>{st.session_state.last_feedback}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SAYFA 3: BİTİŞ EKRANI
# ---------------------------------------------------------
elif st.session_state.page == 3:
    st.markdown("<div class='centered-title'>🏆 TUR TAMAMLANDI!</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='centered-subtitle'>Sporcu: {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    
    valid_speeds = [r["ms"] for r in st.session_state.game_results if r["is_fault"] == 0 and r["event"] == "NET_ATAK"]
    avg_speed_ms = round(sum(valid_speeds) / len(valid_speeds), 1) if valid_speeds else 999.0
    
    total_faults = sum(r["is_fault"] for r in st.session_state.game_results)
    
    # Skor tablosuna yaz ve sporcunun testi bittiği için Online durumunu kapat
    save_score_summary(st.session_state.athlete_name, avg_speed_ms, total_faults, total_rounds=10)
    set_user_offline(st.session_state.athlete_name)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎯 Ortalama Hızın", f"{avg_speed_ms} ms")
    with col2:
        st.metric("🚨 Yediğin Blöf", f"{total_faults} Adet")
        
    st.markdown("""
        <div class='shock-card-black' style='border-color: #00FF66;'>
            <h2 style='color: #00FF66; margin-bottom: 10px;'>⚡ SKORUN CANLI TABLOYA YAZILDI!</h2>
            <p style='color: #CBD5E1; font-size: 1.1rem; font-weight: 700;'>
                Rakiplerinin durumunu sol menüdeki <b>CANLI SKOR TABLOSUNDAN</b> anlık takip et!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("TEKRAR DENE 🔄", type="primary"):
            set_user_online(st.session_state.athlete_name)
            start_new_game()
            st.session_state.page = 2
            st.rerun()
    with col_btn2:
        if st.button("ÇIKIŞ YAP 🛑"):
            set_user_offline(st.session_state.athlete_name)
            st.session_state.athlete_name = ""
            st.session_state.page = 1
            st.rerun()

# ---------------------------------------------------------
# SAYFA 4: UZMAN DASHBOARD'U (GİZLİ PANEL)
# ---------------------------------------------------------
elif st.session_state.page == 4:
    st.markdown("<div class='centered-title'>📊 UZMAN DASHBOARD'U</div>", unsafe_allow_html=True)
    st.markdown("<div class='centered-subtitle'>Klinik Şok & Dürtü Kontrolü Veri Analizi</div>", unsafe_allow_html=True)
    
    df_trials = get_all_trials_df()
    
    if not df_trials.empty:
        st.markdown("### 📋 Tüm Tur Detayları (Canlı Akış)")
        st.dataframe(df_trials, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        csv_bytes = df_trials.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tüm Verileri CSV Olarak İndir",
            data=csv_bytes,
            file_name=f"sok_testi_verileri_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
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
