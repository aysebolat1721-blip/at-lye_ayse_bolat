import streamlit as st
import requests
import json

# Sayfa Ayarları
st.set_page_config(
    page_title="🥋 Sporcularda Öz Şefkat Oyun Alanı",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS Stilleri
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card-box {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #3B82F6;
    }
    .alert-box {
        background-color: #FEF2F2;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #EF4444;
        margin-bottom: 15px;
    }
    .success-box {
        background-color: #ECFDF5;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #10B981;
        margin-bottom: 15px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #1F2937;
        color: white;
        text-align: center;
        padding: 12px 0;
        font-size: 0.95rem;
        font-weight: 600;
        z-index: 1000;
    }
    .sidebar-footer {
        margin-top: auto;
        padding-top: 20px;
        font-size: 0.9rem;
        color: #4B5563;
        text-align: center;
        border-top: 1px solid #E5E7EB;
    }
    </style>
""", unsafe_allow_html=True)

# API Ayarları
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "gsk_" + "v58LoWEAqYd61eK5NkC6WGdyb3FYC4ygvwblvUAyeV5wK1ajk5bz"

def get_ai_scenario(dimension, age, gender, experience):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Sen uzman bir spor psikoloğusun. Kristin Neff'in (2003) Öz Şefkat Kuramı'na dayanarak, taekwondo sporu ile ilgilenen sporcular için bir atölye çalışması senaryosu oluşturacaksın.
    
    Sporcu Profili:
    - Yaş Grubu: {age}
    - Cinsiyet Dağılımı: {gender}
    - Deneyim Seviyesi: {experience}
    
    Seçilen Öz Şefkat Boyutu: {dimension}
    
    Lütfen şu formatta bir yanıt ver:
    1. **Müsabaka/Antrenman Senaryosu:** (Sporcunun zorlandığı, hata yaptığı veya stres yaşadığı gerçekçi bir taekwondo durumu)
    2. **Öz Şefkat Görev Kartı:** (Seçilen '{dimension}' boyutuna uygun olarak sporcunun bu durumda kendisine nasıl yaklaşması gerektiğini gösteren eyleme dönüştürülebilir bir görev veya düşünce pratiği)
    
    Yanıtın ilham verici, destekleyici ve Türkçe olmalıdır. Sporcuları cesaretlendirecek bir tonda yaz.
    """
    
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Sen Kristin Neff'in Öz Şefkat teorisini ve taekwondoyu çok iyi bilen bir spor psikoloğusun."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Yapay zeka bağlantısında bir hata oluştu: {str(e)}\n\nLütfen bağlantınızı kontrol edin veya biraz bekleyip tekrar deneyin."

# Oturum Durumu Başlatma
if 'self_talks' not in st.session_state:
    st.session_state.self_talks = []

# Sidebar
with st.sidebar:
    st.markdown("## 🥋 Ayarlar & Bilgi")
    
    st.markdown("### 👥 Atölye Grubu Özellikleri")
    participant_count = st.slider("Katılımcı Sayısı", min_value=8, max_value=15, value=10)
    age_group = st.selectbox("Yaş Grubu", ["Çocuk (8-12)", "Yıldız (12-14)", "Genç (15-17)", "Büyük (18+)"])
    gender_mix = st.selectbox("Cinsiyet Dağılımı", ["Karma", "Sadece Kadın", "Sadece Erkek"])
    exp_level = st.selectbox("Deneyim Seviyesi", ["Yeni Başlayan (Beyaz-Sarı Kuşak)", "Orta Seviye (Yeşil-Mavi Kuşak)", "İleri Seviye (Kırmızı-Siyah Kuşak)", "Milli Sporcu"])
    
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="sidebar-footer">
            <b>Tasarım ve Geliştirme:</b><br> Ayşe Bolat<br><br>
            <i>Neff (2003) Öz Şefkat Kuramı Temelli</i>
        </div>
    """, unsafe_allow_html=True)

# Ana Sayfa İçeriği
st.markdown("<h1 class='main-header'>🥋 Sporcularda Öz Şefkat Oyun Alanı</h1>", unsafe_allow_html=True)

# Sekmeler
tab1, tab2, tab3 = st.tabs(["🎯 Kart Çek ve Oyna", "📝 Sporcu İç Konuşma Formu", "ℹ️ Atölye Rehberi"])

with tab1:
    st.markdown("### 🎲 İnteraktif Senaryo ve Görev Kartları")
    st.write("Seçtiğiniz öz şefkat boyutuna ve yandaki panelden belirlediğiniz sporcu profiline göre yapay zeka destekli özel senaryolar oluşturulacaktır.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Boyut Seçimi")
        dimension = st.radio(
            "Kristin Neff'in 3 Temel Boyutu:",
            ["Kendine Nezaket (Öz Yargılamaya Karşı)", 
             "Ortak İnsanlık (İzolasyona Karşı)", 
             "Bilinçli Farkındalık (Aşırı Özdeşleşmeye Karşı)"]
        )
        
        generate_btn = st.button("✨ Senaryo ve Kart Üret", use_container_width=True, type="primary")
        
    with col2:
        if generate_btn:
            with st.spinner("AI Psikolog senaryoyu hazırlıyor..."):
                scenario_text = get_ai_scenario(dimension, age_group, gender_mix, exp_level)
                
            st.markdown(f"<div class='card-box'>{scenario_text}</div>", unsafe_allow_html=True)
            st.balloons()
        else:
            st.info("Senaryo oluşturmak için sol taraftaki butona tıklayın.")

with tab2:
    st.markdown("### 🗣️ İç Konuşmayı Dönüştürme")
    st.write("Sporcuların zihinlerindeki eleştirel sesi (Öz Yargılama) şefkatli ve destekleyici bir sese dönüştürme pratiği.")
    
    with st.form("self_talk_form", clear_on_submit=True):
        negative_talk = st.text_area("❌ Müsabaka veya antrenman anındaki olumsuz/eleştirel iç konuşman nedir?", placeholder="Örn: Yine aynı hatayı yaptım, benden hiçbir şey olmaz, maçı benim yüzümden kaybettik...")
        positive_talk = st.text_area("💚 Şefkatli, destekleyici ve yapıcı alternatif cümle nedir?", placeholder="Örn: Bu tekniği tam oturtamadım ama antrenmanlarda çalışıyorum. Herkes hata yapabilir, bir sonraki raunda odaklanacağım.")
        
        submit_btn = st.form_submit_button("Kaydet ve Dönüştür")
        
        if submit_btn and negative_talk and positive_talk:
            st.session_state.self_talks.append({
                "negative": negative_talk,
                "positive": positive_talk
            })
            st.success("İç konuşma başarıyla dönüştürüldü!")
            
    if st.session_state.self_talks:
        st.markdown("### Dönüşüm Panosu")
        for idx, talk in enumerate(reversed(st.session_state.self_talks)):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"<div class='alert-box'><b>Eski Ses:</b><br>{talk['negative']}</div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<div class='success-box'><b>Yeni Ses:</b><br>{talk['positive']}</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("### 📋 8-15 Kişilik Atölye Uygulama Rehberi")
    
    st.markdown(f"""
    <div class="card-box">
    <h4>Uygulama Amacı</h4>
    Bu atölye, taekwondo sporcularının performans kaygısı, başarısızlık korkusu ve yoğun antrenman stresiyle başa çıkabilmeleri için <b>Kristin Neff'in (2003) Öz Şefkat Kuramı</b> temel alınarak tasarlanmıştır.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🕒 Oturum Akışı (Tahmini 45-60 Dk)")
    st.markdown("""
    1. **Buz Kırıcı ve Isınma (10 Dk):**
       - Katılımcılar daire şeklinde oturur (8-15 kişi idealdir).
       - Antrenör/Psikolog "Öz Şefkat" kavramını kısaca taekwondo bağlamında açıklar.
       
    2. **Kart Çek ve Oyna - İnteraktif Senaryolar (20 Dk):**
       - Uygulamanın <b>🎯 Kart Çek ve Oyna</b> sekmesi açılır.
       - Sol panelden grubun yaş ve seviyesi seçilir.
       - Gönüllü sporcular sırayla bir boyut (Kendine Nezaket, Ortak İnsanlık, Bilinçli Farkındalık) seçer.
       - AI tarafından üretilen senaryo okunur ve sporcu bu durumda ne hissedeceğini/nasıl davranacağını grupla paylaşır.
       - Görev kartındaki pratik hep birlikte zihinsel olarak uygulanır.
       
    3. **İç Konuşmayı Dönüştürme Pratiği (15 Dk):**
       - <b>📝 Sporcu İç Konuşma Formu</b> sekmesine geçilir.
       - Sporculardan yakın zamanda yaşadıkları bir "hata" sonrası kendilerine ne söyledikleri istenir.
       - Bu cümleler isimsiz olarak forma "Eski Ses" olarak girilir.
       - Grupla beyin fırtınası yapılarak bu ses "Yeni Şefkatli Ses"e dönüştürülür ve kaydedilir.
       
    4. **Kapanış ve Değerlendirme (5-10 Dk):**
       - Dönüşüm panosu hep birlikte incelenir.
       - "Mindfulness (Bilinçli Farkındalık)" nefes egzersizi yapılarak atölye sonlandırılır.
    """)
    
    st.info("💡 **İpucu:** Uygulamayı büyük bir ekrana yansıtarak veya bir tablet üzerinden elden ele gezdirerek kullanabilirsiniz.")

# Sayfanın en altındaki Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        Tasarım ve Geliştirme: Ayşe Bolat | Neff (2003) Öz Şefkat Kuramı Temelli
    </div>
""", unsafe_allow_html=True)
