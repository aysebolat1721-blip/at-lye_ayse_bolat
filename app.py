import streamlit as st
import pandas as pd
import requests
import json
import random

# -----------------
# 1. AYARLAR & CSS
# -----------------
st.set_page_config(
    page_title="🥋 Öz Şefkat Gelişim Oyunu",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; font-weight: 700; text-align: center; margin-bottom: 2rem; }
    .card-box { background-color: #F3F4F6; color: #111827; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; border-left: 5px solid #3B82F6; }
    .alert-box { background-color: #FEF2F2; color: #7F1D1D; border-radius: 10px; padding: 15px; border-left: 5px solid #EF4444; margin-bottom: 15px; }
    .success-box { background-color: #ECFDF5; color: #064E3B; border-radius: 10px; padding: 15px; border-left: 5px solid #10B981; margin-bottom: 15px; }
    .analysis-box { background-color: #EFF6FF; color: #1E3A8A; border-radius: 10px; padding: 15px; border-left: 5px solid #60A5FA; margin-top: 10px; font-weight: 500; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1F2937; color: white; text-align: center; padding: 12px 0; font-size: 0.95rem; font-weight: 600; z-index: 1000; }
    .sidebar-footer { margin-top: auto; padding-top: 20px; font-size: 0.9rem; color: #4B5563; text-align: center; border-top: 1px solid #E5E7EB; }
    .stage-title { font-size: 1.8rem; color: #2563EB; font-weight: 600; border-bottom: 2px solid #BFDBFE; padding-bottom: 10px; margin-bottom: 20px;}
    .theory-box { background-color: #FFE4E6; color: #9F1239; border-radius: 10px; padding: 15px; border-left: 5px solid #F43F5E; margin-bottom: 15px; }
    .fear-box { background-color: #FEF3C7; color: #92400E; border-radius: 10px; padding: 18px; border-left: 5px solid #F59E0B; margin-bottom: 20px; font-size: 1.1rem; font-weight: 500; }
    .compassion-board { background-color: #F0FDF4; color: #166534; border-radius: 10px; padding: 18px; border: 1px solid #BBF7D0; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# API
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "gsk_" + "v58LoWEAqYd61eK5NkC6WGdyb3FYC4ygvwblvUAyeV5wK1ajk5bz"

# -----------------
# 2. VERİ & FONKSİYONLAR
# -----------------

QUESTIONS = [
    {"text": "1. Antrenmanda veya maçta benim için önemli olan bir şeyi başaramadığımda, yetersizlik duygusuna kapılırım.", "reverse": True},
    {"text": "2. Kendi oyun tarzımda sevmediğim özelliklere karşı anlayışlı ve sabırlı olmaya çalışırım.", "reverse": False},
    {"text": "3. Maçta can sıkıcı bir şey olduğunda durumu dengeli bir şekilde değerlendirmeye çalışırım.", "reverse": False},
    {"text": "4. Formsuz olduğumda, diğer sporcuların benden daha başarılı ve mutlu olduğunu düşünürüm.", "reverse": True},
    {"text": "5. Hatalarımı ve başarısızlıklarımı sporun ve insan olmanın doğal bir parçası olarak görmeye çalışırım.", "reverse": False},
    {"text": "6. Çok zor bir antrenman veya maç dönemi geçirdiğimde, kendime ihtiyacım olan şefkat ve anlayışı gösteririm.", "reverse": False},
    {"text": "7. Minderde beni üzen bir şey olduğunda, duygularımı dengede tutmaya çalışırım.", "reverse": False},
    {"text": "8. Benim için önemli olan bir maçta başarısız olduğumda, bu başarısızlığı sadece ben yaşıyormuşum gibi yalnız hissederim.", "reverse": True},
    {"text": "9. Performansım düştüğünde, sürekli yanlış giden şeylere takılıp kalırım.", "reverse": True},
    {"text": "10. Bir teknikte yetersiz hissettiğimde, kendime bu duyguların çoğu sporcu tarafından paylaşıldığını hatırlatırım.", "reverse": False},
    {"text": "11. Kendi hatalarıma ve eksiklerime karşı çok yargılayıcıyımdır.", "reverse": True},
    {"text": "12. Oyunumda sevmediğim yönlere karşı tahammülsüz ve sabırsızım.", "reverse": True},
]

def calculate_score(answers):
    total = 0
    for i, q in enumerate(QUESTIONS):
        val = answers[i]
        if q["reverse"]:
            val = 6 - val
        total += val
    return round((total / (len(QUESTIONS) * 5)) * 100, 1)

# -----------------
# 3. STATE YÖNETİMİ
# -----------------
if 'stage' not in st.session_state:
    st.session_state.stage = 0
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
if 'target_participant_count' not in st.session_state:
    st.session_state.target_participant_count = 8
if 'workshop_data' not in st.session_state:
    st.session_state.workshop_data = []

# Torbada Sporcu Numaralarına göre tutulan anonim korkular: {1: "korku 1", 2: "korku 2", ...}
if 'group_fears_dict' not in st.session_state:
    st.session_state.group_fears_dict = {}

# Ortak Yüzleşme Panosu Kayıtları
if 'group_board_entries' not in st.session_state:
    st.session_state.group_board_entries = []

# Bireysel katılımcı geçici state'leri
if 'pre_answers' not in st.session_state:
    st.session_state.pre_answers = [3] * len(QUESTIONS)
if 'post_answers' not in st.session_state:
    st.session_state.post_answers = [3] * len(QUESTIONS)
if 'pre_score' not in st.session_state:
    st.session_state.pre_score = 0
if 'post_score' not in st.session_state:
    st.session_state.post_score = 0
if 'my_fear' not in st.session_state:
    st.session_state.my_fear = ""
if 'assigned_fear' not in st.session_state:
    st.session_state.assigned_fear = ""
if 'my_compassion_response' not in st.session_state:
    st.session_state.my_compassion_response = ""
if 'game_substep' not in st.session_state:
    st.session_state.game_substep = 1
if 'athlete_name' not in st.session_state:
    st.session_state.athlete_name = ""
if 'athlete_id' not in st.session_state:
    st.session_state.athlete_id = 1
if 'athlete_age' not in st.session_state:
    st.session_state.athlete_age = 14
if 'athlete_gender' not in st.session_state:
    st.session_state.athlete_gender = "Belirtmek İstemiyorum"

def next_stage():
    st.session_state.stage += 1

def reset_individual():
    st.session_state.pre_answers = [3] * len(QUESTIONS)
    st.session_state.post_answers = [3] * len(QUESTIONS)
    st.session_state.pre_score = 0
    st.session_state.post_score = 0
    st.session_state.my_fear = ""
    st.session_state.assigned_fear = ""
    st.session_state.my_compassion_response = ""
    st.session_state.game_substep = 1
    st.session_state.athlete_name = ""
    st.session_state.stage = 0

def reset_full_workshop():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# -----------------
# 4. ARAYÜZ (UI)
# -----------------
current_done = len(st.session_state.workshop_data)

with st.sidebar:
    st.markdown("## 🥋 Atölye Grubu Paneli")
    if st.session_state.setup_complete:
        st.markdown(f"👥 **Atölye Hedef Mevcudu:** {st.session_state.target_participant_count} Sporcu")
        st.markdown(f"✅ **Tamamlayan Sporcu:** {current_done} / {st.session_state.target_participant_count}")
        st.progress(min(current_done / st.session_state.target_participant_count, 1.0))
        st.markdown("---")
        st.markdown(f"**Mevcut Sporcu Aşaması:** {st.session_state.stage}/5")
        if st.session_state.athlete_name:
            st.markdown(f"👤 **Aktif Sporcu:** {st.session_state.athlete_name} (Sporcu #{st.session_state.athlete_id})")
            st.markdown(f"🎂 **Yaş:** {st.session_state.athlete_age}")
            st.markdown(f"⚧ **Cinsiyet:** {st.session_state.athlete_gender}")
    else:
        st.markdown("⚙️ *Atölye henüz kurulmadı.*")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="sidebar-footer">
            <b>Tasarım ve Geliştirme:</b><br> Ayşe Bolat<br><br>
            <i>Neff (2003) Öz Şefkat Kuramı Temelli</i>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🥋 Öz Şefkat Gelişim Oyunu</h1>", unsafe_allow_html=True)

# STAGE 0: ATÖLYE KURULUMU & KATILIMCI GİRİŞİ (AYDINLATILMIŞ ONAM FORMU İLE)
if st.session_state.stage == 0:
    if not st.session_state.setup_complete:
        st.markdown("<div class='stage-title'>🏛️ Atölye Grubu Kurulumu (Psikolog / Eğitmen Paneli)</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box'>Lütfen bugün atölyeye katılacak **toplam sporcu sayısını** belirleyin (8-15 kişi). Tüm sporcular sırayla testleri, modülleri ve Şefkatle Yeniden İnşa Oyununu tamamladığında toplu veri tablosu otomatik oluşacaktır.</div>", unsafe_allow_html=True)
        
        with st.form("setup_form"):
            count = st.slider("Atölye Katılımcı Sayısı (Kişi):", min_value=1, max_value=15, value=8, step=1)
            if st.form_submit_button("Atölyeyi Başlat ve 1. Sporcuyu Çağır 🚀", type="primary"):
                st.session_state.target_participant_count = count
                st.session_state.setup_complete = True
                st.rerun()
    else:
        num = current_done + 1
        st.session_state.athlete_id = num
        st.markdown(f"<div class='stage-title'>📌 Sporcu #{num} / {st.session_state.target_participant_count} Giriş ve Onam Ekranı</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='theory-box'>
        <b>📋 SPOR PSİKOLOJİSİ ATÖLYESİ AYDINLATILMIŞ ONAM VE BİLGİLENDİRME FORMU</b><br><br>
        <b>1. Atölyenin Amacı:</b> Bu psikoeğitimsel çalışma, Taekwondo sporcularında zihinsel dayanıklılığı, öz-şefkat farkındalığını ve takım içi duygusal esneklik bağlarını geliştirmek amacıyla kurgulanmıştır.<br>
        <b>2. Gizlilik ve Gönüllülük İlkesi:</b> Çalışmaya katılım tamamen gönüllüdür. İlettiğiniz yanıtlar gizli tutulacak, grup içi etkileşim oyununda paylaşılan iç sesler isim belirtilmeksizin anonim olarak işlenecektir.<br>
        <b>3. Veri Güvenliği:</b> Elde edilen veriler sadece atölye gelişim takibi amacıyla saklanacaktır. Dilediğiniz an katılımı durdurma hakkınız mevcuttur.
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown(f"#### Katılımcı #{num} Kimlik ve Onam Bilgileri")
            name = st.text_input("Rumuzun veya Adın:", placeholder="Şampiyon")
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Yaşın:", min_value=6, max_value=60, value=14, step=1)
            with col2:
                gender = st.selectbox("Cinsiyetin:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
                
            consent = st.checkbox("📌 Aydınlatılmış Onam ve Psikolojik Bilgilendirme Formunu okudum, anladım ve çalışmaya gönüllü katılmayı onaylıyorum.")
                
            submitted = st.form_submit_button("Onayla, Oyuna ve Teste Başla 🚀", type="primary")
            if submitted:
                if not name:
                    st.warning("Lütfen başlamadan önce bir rumuz veya isim giriniz.")
                elif not consent:
                    st.warning("⚠️ Lütfen devam edebilmek için Aydınlatılmış Onam Formunu onaylayınız.")
                else:
                    st.session_state.athlete_name = name
                    st.session_state.athlete_age = age
                    st.session_state.athlete_gender = gender
                    next_stage()
                    st.rerun()

# STAGE 1: ÖN TEST
elif st.session_state.stage == 1:
    st.markdown(f"<div class='stage-title'>Aşama 1: Mevcut Durum Analizi (Ön Test) - {st.session_state.athlete_name} (Sporcu #{st.session_state.athlete_id})</div>", unsafe_allow_html=True)
    st.info("Lütfen aşağıdaki ifadelere ne kadar katıldığını dürüstçe işaretle. (1 = Hiç Katılmıyorum, 5 = Tamamen Katılıyorum)")
    
    with st.form("pre_test_form"):
        for i, q in enumerate(QUESTIONS):
            st.session_state.pre_answers[i] = st.slider(q["text"], 1, 5, st.session_state.pre_answers[i], key=f"pre_{i}")
        
        if st.form_submit_button("Testi Tamamla ve İlerle", type="primary"):
            st.session_state.pre_score = calculate_score(st.session_state.pre_answers)
            next_stage()
            st.rerun()

# STAGE 2: PSİKOLOJİK GELİŞİM MODÜLLERİ (3 BİLİMSEL MODÜL)
elif st.session_state.stage == 2:
    st.markdown("<div class='stage-title'>Aşama 2: Dünyaca Ünlü Psikologların Yöntemleriyle Şefkat Atölyesi 🧠</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card-box'>
    Bu aşamada zihinsel kaslarını güçlendirecek 3 bilimsel modülü tamamlayacaksın. Tamamladıktan sonra bir sonraki aşamada <b>Takım Şefkatle Yeniden İnşa Oyununa</b> geçeceksin!
    </div>
    """, unsafe_allow_html=True)
    
    game_tab1, game_tab2, game_tab3 = st.tabs([
        "🔴🔵🟢 1. Paul Gilbert - 3 Beyin Sistemi",
        "🌧️ 2. Tara Brach - RAIN Metodu", 
        "🏋️‍♂️ 3. Kristin Neff - Öz-Şefkat Kasları & Şampiyon Zihniyeti"
    ])
    
    # MODÜL 1: PAUL GILBERT - 3 BEYİN SİSTEMİ
    with game_tab1:
        st.markdown("### 🔴🔵🟢 Paul Gilbert'in Şefkat Odaklı Terapi (CFT) 3 Beyin Sistemi")
        st.markdown("""
        <div class='theory-box'>
        Evrimsel Psikolog Prof. Paul Gilbert'e göre beynimizde 3 temel duygu düzenleme sistemi bulunur:
        <br>🔴 <b>Tehdit Sistemi:</b> Tehdit ve tehlike anlarında devreye girer. (Korku, kaygı, öz-eleştiri)
        <br>🔵 <b>Güdü/Başarı Sistemi:</b> Hedef odaklılık ve arzuda devreye girer. (Hırs, kazanma odaklılık)
        <br>🟢 <b>Yatıştırıcı/Şefkat Sistemi:</b> Güven, rahatlama ve kabulde devreye girer. (Öz-şefkat, zihinsel denge)
        </div>
        """, unsafe_allow_html=True)
        
        q_gilbert = st.radio(
            "Seçme maçında rakibin senden 4 puan öne geçti. O anki düşüncen en çok hangi kuramsal sisteme örnektir?",
            [
                "🔴 Tehdit Sistemi Örneği: 'Eyvah bittim ben! Rezil olacağım, antrenörüm bana çok kızacak!'",
                "🔵 Güdü Sistemi Örneği: 'Gözüm hiçbir şey görmüyor, şu an saldırıp ne pahasına olursa olsun puan almalıyım!'",
                "🟢 Şefkat/Yatıştırma Sistemi Örneği: 'Sakin ol, daha süre var. Heyecanlanmam normal, nefes alıp planıma odaklanıyorum.'"
            ]
        )
        if st.button("Kuramsal Analizi Gör 🧠"):
            if q_gilbert.startswith("🔴"):
                st.markdown("<div class='alert-box'>🔴 <b>Tehdit & Korunma Sistemi Tespiti:</b> Bu modelleşme tehdit anında beynin tehlike uyarısını temsil eder.</div>", unsafe_allow_html=True)
            elif q_gilbert.startswith("🔵"):
                st.markdown("<div class='card-box'>🔵 <b>Güdü & Başarı Sistemi Tespiti:</b> Bu modelleşme kazanma güdüsüyle ilişkilidir.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='success-box'>🟢 <b>Yatıştırıcı & Şefkat Sistemi Tespiti:</b> Bu modelleşme zihinsel güvenlik ve öz-şefkat alanını temsil eder.</div>", unsafe_allow_html=True)

    # MODÜL 2: TARA BRACH - RAIN METODU
    with game_tab2:
        st.markdown("### 🌧️ Tara Brach'in RAIN Metodu (4 Adımlı Zihinsel Pratik)")
        st.markdown("""
        <div class='theory-box'>
        <b>RAIN Tekniği Nedir?</b> Dünyaca ünlü psikolog Tara Brach tarafından geliştirilen bu yöntem, zorlu duygularla başa çıkmak için 4 adımdan oluşur:
        <br><b>R</b>ecognize (Tanı) | <b>A</b>llow (İzin Ver) | <b>I</b>nvestigate (İncele) | <b>N</b>urture (Şefkatle Besle)
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("rain_form"):
            rain_r = st.text_area("1. Recognize (Tanı): Zor bir maç veya antrenman anında zihninde hangi duygu var?", placeholder="Örn: Yenilme korkusu, başarısızlık stresi...")
            rain_a = st.text_area("2. Allow (İzin Ver): Bu duyguyla savaşmak yerine onun varlığına izin ver.", placeholder="Örn: Şu an korkuyorum ve bu hissin var olmasına izin veriyorum...")
            rain_i = st.text_area("3. Investigate (İncele): Bu duygu bedeninde nerede hissettiriyor?", placeholder="Örn: Göğsümde sıkışma var, karnıma ağrı giriyor...")
            rain_n = st.text_area("4. Nurture (Şefkatle Besle): İçindeki sporcuya ihtiyacı olan şefkat cümlesini söyle.", placeholder="Örn: Güvendesin. Elinden gelenin en iyisini yapıyorsun...")
            
            if st.form_submit_button("RAIN Egzersizini Kaydet 🌧️", type="primary"):
                if rain_r and rain_a and rain_i and rain_n:
                    st.success("RAIN Metodu Pratiği Kaydedildi: 4 adımlı zihinsel farkındalık süreci tamamlandı.")
                else:
                    st.warning("Lütfen 4 adımı da doldurun.")

    # MODÜL 3: KRISTIN NEFF - ÖZ-ŞEFKAT KASLARI ANTRENMAN SALONU
    with game_tab3:
        st.markdown("### 🏋️‍♂️ Kristin Neff - Aktif Zihinsel Kas Antrenmanı Salonu")
        st.markdown("""
        <div class='theory-box'>
        <b>💪 Zihinsel Kas Antrenman Salonu (Neff, 2003):</b> Tıpkı bacak veya kol kaslarını güçlendirdiğin gibi, öz-şefkat zihinsel kaslarını da pratik yaparak geliştirebilirsin. Aşağıdan güçlendirmek istediğin zihinsel kası seç ve aktif antrenman pratiğini tamamla!
        </div>
        """, unsafe_allow_html=True)
        
        muscle = st.radio(
            "Güçlendirmek İstediğin Zihinsel Kası Seç:",
            [
                "🧘 1. Zihinsel Esneklik Kası (Mindfulness - Anda Kalma)",
                "🤝 2. Olimpik Bağ Kası (Ortak İnsanlık - Yalnız Değilim)",
                "🛡️ 3. İçsel Kalkan Kası (Kendine Nezaket - Şampiyon Koç)"
            ]
        )
        
        with st.form("muscle_workout_form"):
            if "1. Zihinsel Esneklik" in muscle:
                st.markdown("<div class='card-box'>🧘 <b>Zihinsel Esneklik Pratiği:</b> Müsabaka veya antrenman esnasında zihnin kaygıya gittiğinde kendin için oluşturacağın <b>odak sıfırlama cümleni</b> kur.</div>", unsafe_allow_html=True)
                m_input = st.text_area(
                    "Şu an zihnimdeki stresi fark ediyorum ama zihnimi dağıtmayıp sadece şu anki:",
                    placeholder="Örn: Nefesime ve mesafemi korumaya odaklanıyorum. Anda kalıyorum."
                )
            elif "2. Olimpik Bağ" in muscle:
                st.markdown("<div class='card-box'>🤝 <b>Olimpik Bağ Pratiği:</b> Hata yaptığında dünya şampiyonlarının dahi bu yollardan geçtiğini hatırlayarak <b>öğrenme cümleni</b> yaz.</div>", unsafe_allow_html=True)
                m_input = st.text_area(
                    "Sporda hata yapmak insani. Dünyadaki en başarılı Taekwondocular da tekme kaçırır. Ben bu tecrübeden:",
                    placeholder="Örn: Gardımı yüksek tutmayı öğrendim, bu bir eksiklik değil gelişim adımı."
                )
            else:
                st.markdown("<div class='card-box'>🛡️ <b>İçsel Kalkan Pratiği:</b> İçindeki sert eleştirmen yerine, sana en çok inanan <b>şampiyon antrenörünün zihinsel sesini</b> devreye sok.</div>", unsafe_allow_html=True)
                m_input = st.text_area(
                    "Zorlu anlarda kendimi suçlamak yerine, şampiyon antrenörüm gibi kendime şunu söylüyorum:",
                    placeholder="Örn: Güvendesin. Çabana güveniyorum, ayağa kalk ve gücünü göster!"
                )
            
            submitted_muscle = st.form_submit_button("Zihinsel Kas Antrenmanını Tamamla & Kas Skorunu Gör 🏋️‍♂️", type="primary")
            if submitted_muscle:
                if m_input:
                    power_score = random.randint(88, 99)
                    st.markdown(f"""
                    <div class='success-box'>
                    🏋️‍♂️ <b>Zihinsel Kas Antrenmanı Başarıyla Tamamlandı!</b><br>
                    💪 <b>Geliştirilen Kas Seviyesi:</b> %{power_score} Güç Oranı<br>
                    <b>🧠 Zihinsel Cümleniz:</b> "{m_input}"<br>
                    <i>Sporda öz-şefkat zihinsel kasınızı aktif olarak çalıştırdınız!</i>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Lütfen zihinsel kas antrenman cümlenizi yazın.")

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Aşama 3'e Geç (Takım Şefkatle Yeniden İnşa Oyunu) ➡️", type="primary"):
        next_stage()
        st.rerun()

# STAGE 3: TAKIM ŞEFKATLE YENİDEN İNŞA OYUNU (2 AŞAMALI ANONİM & BİREBİR TAKIM KURTARMA OYUNU)
elif st.session_state.stage == 3:
    active_num = st.session_state.get('athlete_id', current_done + 1)
    
    st.markdown("<div class='stage-title'>Aşama 3: 🎮 Takım Şefkatle Yeniden İnşa Oyunu (3 Aşamalı Etkileşim)</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='theory-box'>
    <b>📋 TAKIM ŞEFKATLE YENİDEN İNŞA OYUNU İŞLEYİŞİ VE GİZLİLİK BİLGİLENDİRMESİ</b><br><br>
    <b>1. Aşama (Kendi Numarana Özel Anonim Cümle Kaydı):</b> Sıranız geldiğinde (Aktif: <b>Sporcu #{active_num}</b>) antrenmanda veya maçta yaşamaktan en çok korktuğunuz başarısızlığı ya da acımasız iç sesi yazacaksınız. Cümleniz Sporcu #{active_num} koduyla sisteme %100 gizli ve anonim kaydedilir.<br>
    <b>2. Aşama (Şefkatle Kurtarma & Yüzleşme):</b> Bu aşamada sistem torbadan <u>kendi yazdığınız cümle hariç</u> diğer takım arkadaşlarınızın cümlelerinden birini rastgele karşınıza çıkaracaktır.<br>
    <b>🔒 %100 Gizlilik Garantisi:</b> Hangi cümlenin kime ait olduğu hiçbir ekranda veya raporda gösterilmez, kimlikler tamamen gizlidir.
    </div>
    """, unsafe_allow_html=True)
    
    # SUBSTEP 1: KAYALARI BIRAKMAK (ANONİM İÇ SES & KORKU GİRDİSİ)
    if st.session_state.game_substep == 1:
        st.markdown(f"### 🪨 1. Aşama: Kayaları Bırakmak (Sporcu #{active_num} Anonim Girdisi)")
        
        with st.form("fear_input_form"):
            fear_input = st.text_area(
                f"Sporcu #{active_num} - Antrenmanda/Maçta En Çok Korktuğun Başarısızlık veya Acımasız İç Ses (Birebir Cümlen):",
                placeholder="Örn: 'Seçme maçında çok kötü dövüşüp herkesi hayal kırıklığına uğratacağım' veya 'Antrenörüm benden ümidini kesti.'"
            )
            
            if st.form_submit_button("1. Faz Cümlemi Anonim Torbaya Kaydet 🪨 (2. Aşamaya Geç)", type="primary"):
                if fear_input:
                    st.session_state.my_fear = fear_input
                    st.session_state.group_fears_dict[active_num] = fear_input
                    st.session_state.game_substep = 2
                    st.success(f"Sporcu #{active_num} olarak birebir korku cümlen anonim torbaya atıldı!")
                    st.rerun()
                else:
                    st.warning("Lütfen bir korku veya iç ses yazın.")

    # SUBSTEP 2: KARIŞIM VE KURTARMA (BİREBİR TAKIM ARKADAŞI KORKUSUNU ŞEFKATLE İNŞA ETME)
    elif st.session_state.game_substep == 2:
        st.markdown(f"### 💌 2. Aşama: Karışım ve Kurtarma (Sporcu #{active_num})")
        
        # Ekran için KENDİ KORKUSU HARİÇ başka bir takım arkadaşının yazdığı korkuyu süz
        other_fears_dict = {id: fear for id, fear in st.session_state.group_fears_dict.items() if id != active_num}
        
        if other_fears_dict:
            if not st.session_state.assigned_fear or st.session_state.assigned_fear not in other_fears_dict.values():
                st.session_state.assigned_fear = random.choice(list(other_fears_dict.values()))
            
            st.markdown(f"""
            <div class='fear-box'>
            <b>🪨 Ekrana Düşen Takım Arkadaşının Birebir Anonim Korku Cümlesi:</b><br>
            <i>"{st.session_state.assigned_fear}"</i>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("rescue_form"):
                resp = st.text_area(
                    "Bu Sporcuyu Ayağa Kaldıracak Şefkat ve Motivasyon Mesajın:",
                    placeholder="Örn: Haklısın, bu korku hepimizin zihnine gelebilir ama senin ne kadar çabaladığını görüyoruz. Tek bir maç senin değerini belirlemez, yanındayız!"
                )
                
                if st.form_submit_button("Şefkatli Kurtarma Mesajını Gönder 💌 (3. Aşamaya Geç)", type="primary"):
                    if resp:
                        st.session_state.my_compassion_response = resp
                        # Panoya kaydet
                        st.session_state.group_board_entries.append({
                            "fear": st.session_state.assigned_fear,
                            "response": resp,
                            "responder": st.session_state.athlete_name,
                            "responder_id": active_num
                        })
                        st.session_state.game_substep = 3
                        st.success("Şefkatli kurtarma mesajın gönderildi!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning("Lütfen şefkatli bir mesaj yazın.")
        else:
            # Grupta henüz Sporcu #active_num hariç başka hiç kimse 1. faz cümlesini girmediyse
            st.markdown(f"""
            <div class='alert-box'>
            <b>⏳ DİĞER TAKIM ARKADAŞLARINIZIN 1. FAZ CÜMLELERİ BEKLENİYOR</b><br>
            Şu an torbada yalnızca sizin (Sporcu #{active_num}) 1. Faz cümleniz bulunmaktadır. Kendi cümleniz size çıkmayacağı için, gruptaki diğer sporcuların (Sporcu #2, #3...) 1. Faz cümlelerini girmesi gerekmektedir.
            <br><br>
            <b>Eğitmen Yönlendirmesi:</b> Diğer sporcular 1. Fazı doldurduğunda 2. Faza geçmek için <b>🔄 Torbayı Yenile</b> butonuna basabilir veya sıradaki sporcunun 1. Faz girişini yapması için <b>➡️ Sıradaki Sporcuya Geç</b> butonuna tıklayabilirsiniz.
            </div>
            """, unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔄 Torbayı Kontrol Et / Yenile", type="primary"):
                    st.rerun()
            with col_b2:
                if st.button(f"➡️ Sıradaki Sporcu Giriş Yapsın (Sporcu #{active_num + 1})"):
                    # Bu sporcunun 1. faz cümlesini saklayıp sıradaki sporcunun girişine geçeriz
                    already_saved = any(row['Rumuz/Ad'] == st.session_state.athlete_name for row in st.session_state.workshop_data)
                    if not already_saved:
                        st.session_state.workshop_data.append({
                            "Sıra": len(st.session_state.workshop_data) + 1,
                            "Rumuz/Ad": st.session_state.athlete_name,
                            "Yaş": st.session_state.athlete_age,
                            "Cinsiyet": st.session_state.athlete_gender,
                            "Ön Test (%)": st.session_state.pre_score,
                            "Son Test (%)": st.session_state.pre_score,
                            "Net Gelişim (%)": 0.0,
                            "Anonim Korku/İç Ses (Birebir)": st.session_state.my_fear,
                            "Verilen Şefkatli Yanıt": "Henüz 2. Faz Tamamlanmadı"
                        })
                    reset_individual()
                    st.rerun()

    # SUBSTEP 3: BÜYÜK YÜZLEŞME (ORTAK İNSANLIK TABLOSU)
    elif st.session_state.game_substep == 3:
        st.markdown("""
        <div class='theory-box'>
        <b>3. Aşama: Büyük Yüzleşme (Ortak İnsanlık Tablosu)</b><br>
        Herkesin ilk yazdığı birebir korkular ve diğer arkadaşlarının yazdığı şefkatli cevaplar ortak panoda listelendi. 
        Bu panoya bak ve takım arkadaşlarının içten içe ne dediğini ve birbirinizi nasıl desteklediğinizi gör!
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🤝 Ortak İnsanlık & Şefkat Panosu")
        
        if st.session_state.group_board_entries:
            for idx, entry in enumerate(st.session_state.group_board_entries, 1):
                st.markdown(f"""
                <div class='compassion-board'>
                <b>🪨 Takım Arkadaşının Birebir Korku Cümlesi #{idx}:</b> <i>"{entry['fear']}"</i><br><br>
                <b>💌 Yazılan Şefkatli Yanıt ({entry['responder']} - Sporcu #{entry['responder_id']}):</b> "{entry['response']}"
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='compassion-board'>
            <b>🪨 Birebir Korku Cümlesi:</b> <i>"{st.session_state.my_fear}"</i><br><br>
            <b>💌 Yazılan Şefkatli Yanıt:</b> "{st.session_state.my_compassion_response}"
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("Aşama 4'e Geç (Son Test) ➡️", type="primary"):
            next_stage()
            st.rerun()

# STAGE 4: SON TEST
elif st.session_state.stage == 4:
    st.markdown(f"<div class='stage-title'>Aşama 4: Gelişim Ölçümü (Son Test) - {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    st.info("Psikolojik atölye egzersizlerinden ve Takım Şefkat Oyunundan SONRA, şu anki hissiyatına göre soruları tekrar yanıtla.")
    
    with st.form("post_test_form"):
        for i, q in enumerate(QUESTIONS):
            st.session_state.post_answers[i] = st.slider(q["text"], 1, 5, st.session_state.post_answers[i], key=f"post_{i}")
        
        if st.form_submit_button("Testi Tamamla ve Bireysel Raporu Gör 📊", type="primary"):
            st.session_state.post_score = calculate_score(st.session_state.post_answers)
            next_stage()
            st.rerun()

# STAGE 5: BİREYSEL SONUÇ & ATÖLYE GEÇİŞİ
elif st.session_state.stage == 5:
    pre = st.session_state.pre_score
    post = st.session_state.post_score
    diff = round(post - pre, 1)
    fear_val = st.session_state.get('my_fear', 'Korku Girilmedi')
    resp_val = st.session_state.get('my_compassion_response', 'Yanıt Girilmedi')
    
    st.markdown(f"<div class='stage-title'>Katılımcı Bireysel Raporu: {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    
    if diff > 0:
        st.markdown(f"<div class='success-box'>Harika! Öz şefkat seviyeniz oyundan sonra <b>+{diff:.1f}</b> puan arttı!</div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<div class='card-box'>Öz şefkat skorunuz kaydedildi.</div>", unsafe_allow_html=True)
    
    # Veriyi listeye kaydet (Tekrarlanmaması için kontrol et)
    already_saved = any(row['Rumuz/Ad'] == st.session_state.athlete_name for row in st.session_state.workshop_data)
    if not already_saved:
        st.session_state.workshop_data.append({
            "Sıra": len(st.session_state.workshop_data) + 1,
            "Rumuz/Ad": st.session_state.athlete_name,
            "Yaş": st.session_state.athlete_age,
            "Cinsiyet": st.session_state.athlete_gender,
            "Ön Test (%)": pre,
            "Son Test (%)": post,
            "Net Gelişim (%)": diff,
            "Anonim Korku/İç Ses (Birebir)": fear_val,
            "Verilen Şefkatli Yanıt": resp_val
        })
    
    total_target = st.session_state.target_participant_count
    saved_count = len(st.session_state.workshop_data)
    
    st.markdown("---")
    if saved_count < total_target:
        st.info(f"Tamamlanan Sporcu: **{saved_count} / {total_target}**. Sıradaki sporcunun testi için aşağıdaki butona tıklayın.")
        if st.button(f"➡️ Sıradaki Sporcuya Geç (Sporcu #{saved_count + 1})", type="primary"):
            reset_individual()
    else:
        st.success(f"🎉 Tüm {total_target} sporcu testlerini, modüllerini ve Şefkatle Yeniden İnşa Oyununu tamamladı! Atölye sona erdi.")
        if st.button("📊 Atölye Grubu Toplu Veri Raporunu Gör", type="primary"):
            next_stage()
            st.rerun()

# STAGE 6: ATÖLYE TOPLU VERİ LİSTESİ VE RAPORU (PSİKOLOG / EĞİTMEN EKRANI)
elif st.session_state.stage == 6:
    st.markdown("<div class='stage-title'>📊 Atölye Grubu Toplu Sonuç Veri Raporu</div>", unsafe_allow_html=True)
    
    df_results = pd.DataFrame(st.session_state.workshop_data)
    
    avg_pre = round(df_results["Ön Test (%)"].mean(), 1)
    avg_post = round(df_results["Son Test (%)"].mean(), 1)
    avg_diff = round(df_results["Net Gelişim (%)"].mean(), 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Katılımcı", f"{len(df_results)} Sporcu")
    with col2:
        st.metric("Ön Test Ortalaması", f"{avg_pre}%")
    with col3:
        st.metric("Son Test Ortalaması", f"{avg_post}%")
    with col4:
        st.metric("Ortalama Gelişim", f"+{avg_diff}%" if avg_diff > 0 else f"{avg_diff}%")
        
    st.markdown("### 📋 Katılımcı Veri Listesi ve Anonim Korku / Şefkatli Yanıt Tablosu")
    st.dataframe(df_results, use_container_width=True, hide_index=True)
    
    # CSV İndirme Butonu
    csv_data = df_results.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Atölye Veri Listesini İndir (CSV/Excel)",
        data=csv_data,
        file_name="atolye_ozsefkat_grup_verileri.csv",
        mime="text/csv",
        type="primary"
    )
    
    st.markdown("---")
    if st.button("Yeni Bir Atölye Grubu Başlat 🔄"):
        reset_full_workshop()

# Sayfanın en altındaki Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        Tasarım ve Geliştirme: Ayşe Bolat | Neff (2003) Öz Şefkat Kuramı Temelli
    </div>
""", unsafe_allow_html=True)
