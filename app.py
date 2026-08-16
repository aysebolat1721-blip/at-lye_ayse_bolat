import streamlit as st
import pandas as pd
import requests
import json
import time
import random

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI VE CSS TASARIMI (MOBİL DOSTU)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bilişsel Reaksiyon Testi",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobil Odaklı Modern CSS Enjeksiyonu
st.markdown("""
    <style>
    /* Ana Konteyner Genişliği ve Dolguları */
    .block-container {
        max-width: 650px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Üst Başlık Stili */
    .app-title {
        font-size: 1.8rem;
        font-weight: 800;
        text-align: center;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    
    .app-subtitle {
        font-size: 0.95rem;
        text-align: center;
        color: #94A3B8;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Senaryo Kartı */
    .scenario-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #3B82F6;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 24px 18px;
        text-align: center;
        margin-bottom: 24px;
        min-height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .scenario-text {
        font-size: 1.35rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.45;
        margin: 0;
    }
    
    /* Yanıp Sönen Stres Bildirim Kartı */
    .stress-alert-box {
        background: linear-gradient(90deg, #DC2626, #991B1B);
        border: 2px solid #F87171;
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.6);
        border-radius: 14px;
        padding: 14px 10px;
        text-align: center;
        margin-bottom: 20px;
        animation: pulse-red 1.2s infinite;
    }
    
    .stress-alert-text {
        color: #FFFFFF;
        font-size: 1.05rem;
        font-weight: 900;
        letter-spacing: 0.5px;
        margin: 0;
    }
    
    @keyframes pulse-red {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
        50% { transform: scale(1.02); box-shadow: 0 0 20px 8px rgba(220, 38, 38, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    
    /* Mobil Uyumlu Büyük Buton Stilleri */
    div.stButton > button {
        width: 100% !important;
        height: 85px !important;
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        border-radius: 16px !important;
        cursor: pointer !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.08s ease, box-shadow 0.08s ease !important;
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }
    
    div.stButton > button:active {
        transform: scale(0.94) !important;
    }

    /* Sol Buton (PARAT) Stili */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #60A5FA !important;
    }

    /* Sağ Buton (KONTRA) Stili */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #A78BFA !important;
    }
    
    /* Birincil Başlat/İndir Butonları Stili */
    .primary-action-btn button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #34D399 !important;
        height: 65px !important;
        font-size: 1.2rem !important;
    }

    /* Metrik Kartları */
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    
    /* Sidebar Gizleme */
    [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. YEDEK SENARYO HAVUZU VE API ANAHTARI YÖNETİMİ
# ---------------------------------------------------------
FALLBACK_SCENARIOS = [
    "Rakip kılıcı buldu, hızlıca bir adım öne çıktı.",
    "Rakip 6. hattan flöre ile üst kolda atak başlattı.",
    "Rakip mesafeyi kapattı ve fante hamlesi yaptı.",
    "Rakip doğrudan göğüs hizasına dürtüş atağı yapıyor.",
    "Rakip sahte hamle yapıp alt hatta geçiş yaptı.",
    "Rakip yüksek tempolu adımlarla kışkırtma hamlesi yapıyor."
]

def get_api_key():
    """Streamlit secrets veya varsayılan tanımlı anahtar üzerinden API key getirir."""
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"], "groq"
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"], "gemini"
    except Exception:
        pass
    # Varsayılan Groq API Key
    key_part1 = "gsk_" + "v58LoWEAqYd61eK5"
    key_part2 = "NkC6WGdyb3FYC4ygvwblvUAyeV5wK1ajk5bz"
    return key_part1 + key_part2, "groq"

def fetch_ai_scenarios():
    """Yapay Zeka (LLM) kullanarak 6 adet kısa eskrim atak senaryosu üretir."""
    api_key, provider = get_api_key()
    
    if provider == "groq" and api_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            prompt = (
                "Sen bir eskrim antrenörüsün. Eskrim maçları için 6 adet birbirinden farklı, çok kısa (maksimum 1 cümle) "
                "atak ve hamle senaryosu üret. Sporcu bu senaryoya göre PARAT veya KONTRA butonuna basacak.\n"
                "Yanıtını SADECE JSON formatında String listesi olarak ver, başka hiçbir metin ekleme:\n"
                '["Senaryo 1", "Senaryo 2", "Senaryo 3", "Senaryo 4", "Senaryo 5", "Senaryo 6"]'
            )
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            response = requests.post(url, headers=headers, json=payload, timeout=6)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                # Markdown kod bloğu temizleme
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                scenarios = json.loads(content)
                if isinstance(scenarios, list) and len(scenarios) >= 6:
                    return scenarios[:6]
        except Exception:
            pass

    # Hata durumunda yedek senaryoları karıştırarak döndür
    shuffled = FALLBACK_SCENARIOS.copy()
    random.shuffle(shuffled)
    return shuffled

# ---------------------------------------------------------
# 3. SESSION STATE (DURUM YÖNETİMİ)
# ---------------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = 1  # 1: Giriş, 2: AI Yükleme, 3: Normal Test, 4: Stres Testi, 5: Sonuçlar

if "athlete_name" not in st.session_state:
    st.session_state.athlete_name = ""

if "scenarios" not in st.session_state:
    st.session_state.scenarios = []

if "current_round" not in st.session_state:
    st.session_state.current_round = 0

if "round_start_time" not in st.session_state:
    st.session_state.round_start_time = None

if "normal_results" not in st.session_state:
    st.session_state.normal_results = []

if "stress_results" not in st.session_state:
    st.session_state.stress_results = []

def reset_test():
    """Tüm test verilerini sıfırlar ve 1. aşamaya döner."""
    st.session_state.stage = 1
    st.session_state.athlete_name = ""
    st.session_state.scenarios = []
    st.session_state.current_round = 0
    st.session_state.round_start_time = None
    st.session_state.normal_results = []
    st.session_state.stress_results = []

# ---------------------------------------------------------
# 4. AŞAMA GÖRÜNÜMLERİ VE UYGULAMA AKIŞI
# ---------------------------------------------------------

# UYGULAMA BAŞLIĞI
st.markdown("<div class='app-title'>⚔️ Bilişsel Reaksiyon Testi</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Eskrim Karar Verme & Tepki Hızı Ölçümü</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# AŞAMA 1: GİRİŞ VE KURULUM
# ---------------------------------------------------------
if st.session_state.stage == 1:
    st.markdown("### 👤 Sporcu Girişi")
    
    with st.form("login_form"):
        name_input = st.text_input("Ad Soyad:", placeholder="Örn: Ayşe Bolat")
        submit_btn = st.form_submit_button("Testi Başlat 🚀", type="primary", use_container_width=True)
        
        if submit_btn:
            if name_input.strip():
                st.session_state.athlete_name = name_input.strip()
                st.session_state.stage = 2
                st.rerun()
            else:
                st.warning("Lütfen devam etmek için Ad Soyad giriniz.")

# ---------------------------------------------------------
# AŞAMA 2: DİNAMİK SENARYO ÜRETİMİ (AI ENTEGRASYONU)
# ---------------------------------------------------------
elif st.session_state.stage == 2:
    with st.spinner("🤖 Yapay Zeka Eskrim Atak Senaryoları Üretiliyor..."):
        try:
            scenarios = fetch_ai_scenarios()
            st.session_state.scenarios = scenarios
            st.session_state.current_round = 0
            st.session_state.stage = 3
            st.rerun()
        except Exception as e:
            st.error("Senaryolar yüklenirken bir hata oluştu. Varsayılan senaryolar ile başlatılıyor.")
            st.session_state.scenarios = FALLBACK_SCENARIOS
            st.session_state.current_round = 0
            st.session_state.stage = 3
            st.rerun()

# ---------------------------------------------------------
# AŞAMA 3: NORMAL TEST (3 TUR)
# ---------------------------------------------------------
elif st.session_state.stage == 3:
    round_idx = st.session_state.current_round  # 0, 1, 2
    scenario_text = st.session_state.scenarios[round_idx]
    
    st.markdown(f"#### 🎯 Normal Test — Tur {round_idx + 1} / 3")
    
    # Süre başlangıcını kaydet
    if st.session_state.round_start_time is None:
        st.session_state.round_start_time = time.time()
        
    # Senaryo Metni Ekranı
    st.markdown(f"""
        <div class='scenario-card'>
            <p class='scenario-text'>{scenario_text}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # İki Büyük Buton (PARAT / KONTRA)
    col1, col2 = st.columns(2)
    
    with col1:
        parat_clicked = st.button("PARAT 🛡️", key=f"btn_norm_parat_{round_idx}")
    with col2:
        kontra_clicked = st.button("KONTRA ⚡", key=f"btn_norm_kontra_{round_idx}")
        
    if parat_clicked or kontra_clicked:
        click_time = time.time()
        elapsed_ms = round((click_time - st.session_state.round_start_time) * 1000, 1)
        choice = "PARAT" if parat_clicked else "KONTRA"
        
        st.session_state.normal_results.append({
            "Tur": round_idx + 1,
            "Aşama": "Normal",
            "Senaryo": scenario_text,
            "Karar": choice,
            "Tepki Süresi (ms)": elapsed_ms
        })
        
        st.session_state.round_start_time = None
        st.session_state.current_round += 1
        
        if st.session_state.current_round >= 3:
            st.session_state.current_round = 0
            st.session_state.stage = 4
        st.rerun()

# ---------------------------------------------------------
# AŞAMA 4: STRES TESTİ (3 TUR)
# ---------------------------------------------------------
elif st.session_state.stage == 4:
    round_idx = st.session_state.current_round  # 0, 1, 2
    scenario_text = st.session_state.scenarios[round_idx + 3]
    
    # Dikkat Dağıtıcı Yanıp Sönen Kırmızı Stres Bildirimi
    st.markdown("""
        <div class='stress-alert-box'>
            <p class='stress-alert-text'>🚨 SKOR 14-14 | SON 5 SANİYE | SARI KARTIN VAR 🚨</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"#### 🔥 Stres Testi — Tur {round_idx + 1} / 3")
    
    # Süre başlangıcını kaydet
    if st.session_state.round_start_time is None:
        st.session_state.round_start_time = time.time()
        
    # Senaryo Metni Ekranı
    st.markdown(f"""
        <div class='scenario-card' style='border-color: #EF4444;'>
            <p class='scenario-text'>{scenario_text}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # İki Büyük Buton (PARAT / KONTRA)
    col1, col2 = st.columns(2)
    
    with col1:
        parat_clicked = st.button("PARAT 🛡️", key=f"btn_stress_parat_{round_idx}")
    with col2:
        kontra_clicked = st.button("KONTRA ⚡", key=f"btn_stress_kontra_{round_idx}")
        
    if parat_clicked or kontra_clicked:
        click_time = time.time()
        elapsed_ms = round((click_time - st.session_state.round_start_time) * 1000, 1)
        choice = "PARAT" if parat_clicked else "KONTRA"
        
        st.session_state.stress_results.append({
            "Tur": round_idx + 1,
            "Aşama": "Stres",
            "Senaryo": scenario_text,
            "Karar": choice,
            "Tepki Süresi (ms)": elapsed_ms
        })
        
        st.session_state.round_start_time = None
        st.session_state.current_round += 1
        
        if st.session_state.current_round >= 3:
            st.session_state.stage = 5
        st.rerun()

# ---------------------------------------------------------
# AŞAMA 5: SONUÇLAR VE VERİ İNDİRME (PANDAS & CSV)
# ---------------------------------------------------------
elif st.session_state.stage == 5:
    st.markdown("### 📊 Test Sonuçları")
    st.markdown(f"**Sporcu:** {st.session_state.athlete_name}")
    
    # Süre hesaplamaları (Ortalamalar)
    normal_times = [r["Tepki Süresi (ms)"] for r in st.session_state.normal_results]
    stress_times = [r["Tepki Süresi (ms)"] for r in st.session_state.stress_results]
    
    avg_normal_ms = round(sum(normal_times) / len(normal_times), 1) if normal_times else 0.0
    avg_stress_ms = round(sum(stress_times) / len(stress_times), 1) if stress_times else 0.0
    
    delta_ms = round(avg_stress_ms - avg_normal_ms, 1)
    
    # Metrik Gösterimi (Yavaşlama -> Kırmızı / Hızlanma -> Yeşil)
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="🎯 Normal Test Ortalaması",
            value=f"{avg_normal_ms} ms",
            delta=f"{(avg_normal_ms / 1000):.3f} sn",
            delta_color="off"
        )
        
    with col2:
        # Reaksiyon süresi arttıysa yavaşlamıştır (Kırmızı / inverse), azaldıysa hızlanmıştır (Yeşil)
        delta_label = f"+{delta_ms} ms (Yavaşlama 🔴)" if delta_ms > 0 else (f"{delta_ms} ms (Hızlanma 🟢)" if delta_ms < 0 else "0 ms (Değişim Yok)")
        st.metric(
            label="🔥 Stres Testi Ortalaması",
            value=f"{avg_stress_ms} ms",
            delta=delta_label,
            delta_color="inverse" if delta_ms > 0 else "normal"
        )
    
    st.markdown("---")
    st.markdown("#### 📋 Tur Detay Verileri")
    
    # Tüm turların veri birleşimi
    all_rounds = st.session_state.normal_results + st.session_state.stress_results
    df_rounds = pd.DataFrame(all_rounds)
    df_rounds.insert(0, "Sporcu Adı", st.session_state.athlete_name)
    
    st.dataframe(df_rounds, use_container_width=True, hide_index=True)
    
    # Özet DataFrame
    status_text = "Stres Altında Yavaşlama" if delta_ms > 0 else ("Stres Altında Hızlanma" if delta_ms < 0 else "Değişim Yok")
    df_summary = pd.DataFrame([{
        "Sporcu Adı": st.session_state.athlete_name,
        "Normal Ortalama (ms)": avg_normal_ms,
        "Stres Ortalama (ms)": avg_stress_ms,
        "Fark Delta (ms)": delta_ms,
        "Stres Durum Etkisi": status_text
    }])
    
    # CSV İndirme Hazırlığı
    csv_buffer = df_rounds.to_csv(index=False).encode('utf-8-sig')
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Sonuçları İndir (CSV)",
        data=csv_buffer,
        file_name=f"bilissel_reaksiyon_{st.session_state.athlete_name.replace(' ', '_')}.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Yeni Test Başlat 🔄", use_container_width=True):
        reset_test()
        st.rerun()
