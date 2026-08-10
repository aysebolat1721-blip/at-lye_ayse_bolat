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

# 1. Turda ön testi tamamlayıp korkusunu torbaya atan sporcuların verileri: {id: {name, age, gender, pre_score, fear}}
if 'pass1_athletes' not in st.session_state:
    st.session_state.pass1_athletes = {}

# Torbada Sporcu Numaralarına göre tutulan anonim korkular: {1: "korku 1", 2: "korku 2", ...}
if 'group_fears_dict' not in st.session_state:
    st.session_state.group_fears_dict = {}

# 2. Turda oyunda yazılan şefkatli mesajlar: {id: "şefkat mesajı"}
if 'pass2_responses' not in st.session_state:
    st.session_state.pass2_responses = {}

# 3. Turda Son Testini bitiren tüm katılımcıların final veri listesi
if 'workshop_data' not in st.session_state:
    st.session_state.workshop_data = []

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
    st.session_state.athlete_name = ""
    st.session_state.stage = 0

def reset_full_workshop():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# -----------------
# 4. ARAYÜZ (UI)
# -----------------
pass1_done_count = len(st.session_state.pass1_athletes)
pass2_done_count = len(st.session_state.pass2_responses)
pass3_done_count = len(st.session_state.workshop_data)

with st.sidebar:
    st.markdown("## 🥋 Atölye Grubu Paneli")
    if st.session_state.setup_complete:
        st.markdown(f"👥 **Atölye Hedef Mevcudu:** {st.session_state.target_participant_count} Sporcu")
        st.markdown(f"🪨 **1. Tur (Korkusunu Torbaya Atan):** {pass1_done_count} / {st.session_state.target_participant_count}")
        st.progress(min(pass1_done_count / st.session_state.target_participant_count, 1.0))
        st.markdown(f"🎮 **2. Tur (Oyunda Cevap Yazan):** {pass2_done_count} / {st.session_state.target_participant_count}")
        st.progress(min(pass2_done_count / st.session_state.target_participant_count, 1.0))
        st.markdown(f"📝 **3. Tur (Son Testini Bitiren):** {pass3_done_count} / {st.session_state.target_participant_count}")
        st.progress(min(pass3_done_count / st.session_state.target_participant_count, 1.0))
        st.markdown("---")
        if st.session_state.athlete_name and st.session_state.stage in [1, 2, 3, 4, 5]:
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
        st.markdown("<div class='card-box'>Lütfen bugün atölyeye katılacak **toplam sporcu sayısını** belirleyin (8-15 kişi). Tüm sporcular sırayla 1. turda testleri, modülleri ve anonim korkularını tamamladıktan sonra 2. Tur Oyunu ve 3. Tur Son Testi açılacaktır.</div>", unsafe_allow_html=True)
        
        with st.form("setup_form"):
            count = st.slider("Atölye Katılımcı Sayısı (Kişi):", min_value=1, max_value=15, value=8, step=1)
            if st.form_submit_button("Atölyeyi Başlat ve 1. Sporcuyu Çağır 🚀", type="primary"):
                st.session_state.target_participant_count = count
                st.session_state.setup_complete = True
                st.rerun()
    else:
        num = pass1_done_count + 1
        st.session_state.athlete_id = num
        st.markdown(f"<div class='stage-title'>📌 1. Tur: Sporcu #{num} / {st.session_state.target_participant_count} Giriş ve Onam Ekranı</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='theory-box'>
        <b>📋 SPOR PSİKOLOJİSİ ATÖLYESİ AYDINLATILMIŞ ONAM VE BİLGİLENDİRME FORMU</b><br><br>
        <b>1. Atölyenin Amacı:</b> Bu psikoeğitimsel çalışma, Taekwondo sporcularında zihinsel dayanıklılığı, öz-şefkat farkındalığını ve takım içi duygusal esneklik bağlarını geliştirmek amacıyla kurgulanmıştır.<br>
        <b>2. Gizlilik ve Gönüllülük İlkesi:</b> Katılım tamamen gönüllüdür. İlettiğiniz yanıtlar gizli tutulacak, 1. turda torbaya atacağınız iç sesler %100 anonim olarak işlenecek ve isim belirtilmeyecektir.<br>
        <b>3. Veri Güvenliği:</b> Elde edilen veriler sadece atölye gelişim takibi amacıyla saklanacaktır.
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
                
            submitted = st.form_submit_button("Onayla, Modüllere ve Ön Teste Başla 🚀", type="primary")
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
    Bu aşamada zihinsel kaslarını güçlendirecek 3 bilimsel modülü tamamlayacaksın. Tamamladıktan sonra bir sonraki aşamada <b>Anonim İç Ses / Korku Cümleni</b> torbaya atacaksın!
    </div>
    """, unsafe_allow_html=True)
    
    game_tab1, game_tab2, game_tab3 = st.tabs([
        "🔴🔵🟢 1. Paul Gilbert - 3 Beyin Sistemi",
        "🌧️ 2. Tara Brach - RAIN Metodu", 
        "🏆 3. Kristin Neff - Zihinsel Şampiyonluk Antrenmanı"
    ])
    
    # MODÜL 1: PAUL GILBERT - 3 BEYİN SİSTEMİ
    with game_tab1:
        st.markdown("### 🔴🔵🟢 Paul Gilbert'in 3 Beyin Sistemi")
        st.markdown("""
        <div class='theory-box'>
        Evrimsel Psikolog Prof. Paul Gilbert'e göre beynimizde 3 temel duygu düzenleme sistemi bulunur:
        <br>🔴 <b>Tehdit Sistemi:</b> Tehdit ve tehlike anlarında devreye girer.
        <br>🔵 <b>Güdü/Başarı Sistemi:</b> Hedef odaklılık ve arzuda devreye girer.
        <br>🟢 <b>Yatıştırıcı/Şefkat Sistemi:</b> Güven, rahatlama ve kabulde devreye girer.
        </div>
        """, unsafe_allow_html=True)
        
        q_gilbert = st.radio(
            "Seçme maçında rakibin senden 4 puan öne geçti. O an aklından geçen düşünce en çok hangisine benziyor?",
            [
                "🔴 'Eyvah bittim ben! Rezil olacağım, antrenörüm bana çok kızacak!'",
                "🔵 'Gözüm hiçbir şey görmüyor, şu an saldırıp ne pahasına olursa olsun puan almalıyım!'",
                "🟢 'Sakin ol, daha süre var. Heyecanlanmam normal, nefes alıp planıma odaklanıyorum.'"
            ]
        )
        if q_gilbert.startswith("🔴"):
            st.markdown("<div class='alert-box'>🔴 <b>Tehdit & Korunma Sistemi:</b> Bu düşünce tehdit anında beynin tehlike uyarısını temsil eder.</div>", unsafe_allow_html=True)
        elif q_gilbert.startswith("🔵"):
            st.markdown("<div class='card-box'>🔵 <b>Güdü & Başarı Sistemi:</b> Bu düşünce kazanma ve hırs güdüsüyle ilişkilidir.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='success-box'>🟢 <b>Yatıştırıcı & Şefkat Sistemi:</b> Bu düşünce zihinsel güvenlik ve öz-şefkat alanını temsil eder.</div>", unsafe_allow_html=True)

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

    # MODÜL 3: KRISTIN NEFF - ZİHİNSEL ŞAMPİYONLUK ANTRENMANI
    with game_tab3:
        st.markdown("### 🏆 Kristin Neff - Zihinsel Şampiyonluk Antrenmanı")
        st.markdown("""
        <div class='theory-box'>
        <b>🎯 Zihinsel Şampiyonluk Pratiği (Neff, 2003):</b> Spor psikolojisinde öz-şefkat zihinsel dayanıklılığı zirveye taşıyan bir güçtür. Aşağıdaki 3 adımdaki zihinsel antrenmanını tamamlayarak şampiyon zihniyetini oluştur!
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("mental_champion_form"):
            st.markdown("<div class='card-box'>🧘 <b>1. Anda Kalma & Odaklama Cümlen:</b> Müsabaka veya antrenmanda stres hissettiğinde kendini ana döndürecek odak cümlen:</div>", unsafe_allow_html=True)
            input_focus = st.text_input("Odak Cümlen:", placeholder="Örn: Nefes alıyorum, ana ve mesafemi korumaya odaklanıyorum.")
            
            st.markdown("<div class='card-box'>🤝 <b>2. Öğrenme & Büyüme Cümlen:</b> Hata yaptığında veya tekme kaçırdığında kendine söyleyeceğin öğrenme cümlen:</div>", unsafe_allow_html=True)
            input_growth = st.text_input("Öğrenme Cümlen:", placeholder="Örn: Hata yapmak sporda doğal, ben bu tecrübeden ders çıkarıp daha güçlü döneceğim.")
            
            st.markdown("<div class='card-box'>🛡️ <b>3. Güçlendirici Şampiyon Sesin:</b> Zorlu anlarda kendin için devreye sokacağın zihinsel koç sesin:</div>", unsafe_allow_html=True)
            input_strength = st.text_input("Şampiyon Koç Cümlen:", placeholder="Örn: Güvendesin. Çabana güveniyorum, ayağa kalk ve gücünü göster!")
            
            submitted_champion = st.form_submit_button("Zihinsel Şampiyonluk Antrenmanını Tamamla 🏆", type="primary")
            if submitted_champion:
                if input_focus and input_growth and input_strength:
                    st.markdown(f"""
                    <div class='success-box'>
                    🏆 <b>Zihinsel Şampiyonluk Antrenmanı Tamamlandı!</b><br>
                    <b>🧘 Odak Cümlen:</b> "{input_focus}"<br>
                    <b>🤝 Öğrenme Cümlen:</b> "{input_growth}"<br>
                    <b>🛡️ Şampiyon Koç Cümlen:</b> "{input_strength}"<br><br>
                    <i>Zihinsel dayanıklılığını ve şefkat gücünü başarıyla aktive ettin!</i>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Lütfen 3 adımı da tamamlayınız.")

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Aşama 3'e Geç (Anonim Korku Cümleni Torbaya At) ➡️", type="primary"):
        next_stage()
        st.rerun()

# STAGE 3: TUR 1 - KAYALARI BIRAKMAK (ANONİM İÇ SES & KORKU CÜMLESİ İŞLEME)
elif st.session_state.stage == 3:
    active_num = st.session_state.get('athlete_id', pass1_done_count + 1)
    
    st.markdown("<div class='stage-title'>Aşama 3: 🪨 Kayaları Bırakmak (Anonim Cümle Girdisi)</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='theory-box'>
    <b>🔒 %100 GİZLİ VE ANONİM TORBA GİRDİSİ (Sporcu #{active_num})</b><br><br>
    Antrenmanda veya maçta yaşamaktan en çok korktuğun başarısızlığı ya da aklından geçen o acımasız iç sesi birebir cümlenle yaz.<br>
    <i>📌 Cümleniz sisteme tamamen anonim olarak kaydedilecek ve tüm gruptaki sporcular ilk turu bitirdikten sonra 2. Tur Şefkatle Kurtarma Oyununda karışık olarak değerlendirilecektir. Hiç kimse hangi cümlenin kime ait olduğunu göremeyecektir!</i>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("fear_input_form"):
        fear_input = st.text_area(
            f"Sporcu #{active_num} - Antrenmanda/Maçta En Çok Korktuğun Başarısızlık veya Acımasız İç Ses (Birebir Cümlen):",
            placeholder="Örn: 'Seçme maçında çok kötü dövüşüp herkesi hayal kırıklığına uğratacağım' veya 'Antrenörüm benden ümidini kesti.'"
        )
        
        if st.form_submit_button("1. Tur Cümlemi Anonim Torbaya Kaydet 🪨 ve 1. Turunu Tamamla ➡️", type="primary"):
            if fear_input:
                st.session_state.my_fear = fear_input
                st.session_state.group_fears_dict[active_num] = fear_input
                
                # Sporcunun 1. Tur verisini kaydet
                st.session_state.pass1_athletes[active_num] = {
                    "id": active_num,
                    "name": st.session_state.athlete_name,
                    "age": st.session_state.athlete_age,
                    "gender": st.session_state.athlete_gender,
                    "pre_score": st.session_state.pre_score,
                    "fear": fear_input
                }
                
                st.success(f"Sporcu #{active_num} olarak birebir korku cümlen anonim torbaya atıldı!")
                st.session_state.stage = 35 # 1. Tur Bireysel Bekleme Ekranı
                st.rerun()
            else:
                st.warning("Lütfen bir korku veya iç ses yazın.")

# STAGE 35: 1. TUR SPORCU BEKLEME EKRANI
elif st.session_state.stage == 35:
    total_target = st.session_state.target_participant_count
    current_pass1 = len(st.session_state.pass1_athletes)
    
    st.markdown(f"<div class='stage-title'>1. Tur Tamamlandı: {st.session_state.athlete_name} (Sporcu #{st.session_state.athlete_id})</div>", unsafe_allow_html=True)
    st.markdown("<div class='success-box'><b>Tebrikler!</b> Ön testinizi, modülleri tamamladınız ve anonim korku cümlenizi torbaya attınız.</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    if current_pass1 < total_target:
        st.info(f"1. Turu Tamamlayan Sporcu: **{current_pass1} / {total_target}**. Sıradaki sporcunun girişi için aşağıdaki butona tıklayın.")
        if st.button(f"➡️ Sıradaki Sporcuya Geç (Sporcu #{current_pass1 + 1})", type="primary"):
            reset_individual()
    else:
        st.success(f"🎉 Tebrikler! Tüm {total_target} sporcu testlerini, modüllerini ve anonim korku cümlelerini tamamladı!")
        st.markdown("<div class='card-box'><b>🎮 ŞİMDİ 2. TUR ZAMANI:</b> Atölyedeki tüm anonim cümleler torbaya toplandı. Şimdi herkes sırayla adını/rumuzunu seçerek başkasının anonim cümlesini çekecek ve şefkatli kurtarma mesajını yazacaktır!</div>", unsafe_allow_html=True)
        if st.button("🎮 2. TUR: ŞEFKATLE YENİDEN İNŞA OYUNUNU BAŞLAT 🚀", type="primary"):
            st.session_state.stage = 7 # Stage 7: 2. Tur Oyunu
            st.rerun()

# STAGE 7: 2. TUR - ŞEFKATLE YENİDEN İNŞA KURTARMA OYUNU (ANONİM YAZILARI CEVAPLAMA)
elif st.session_state.stage == 7:
    st.markdown("<div class='stage-title'>🎮 2. Tur: Takım Şefkatle Yeniden İnşa Oyunu (Anonim Cevaplama)</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='theory-box'>
    <b>💌 2. TUR KURTARMA OYUNU İŞLEYİŞİ & ANONİMLİK GARANTİSİ</b><br><br>
    Tüm takım arkadaşlarının 1. Turda yazdığı cümleler şu an torbada tamamen karıştı.<br>
    Adınızı/Rumuzunuzu seçtiğinizde, sistem <b>KENDİ CÜM LENİZ HARİÇ</b> gruptaki diğer arkadaşlarınızın cümlelerinden birini rastgele ekrana getirecektir.<br>
    <i>🔒 Kimin hangi cümleyi yazdığı hiçbir ekranda ve raporda ASLA görünmez! Tüm sporcular cevabını tamamlayınca 3. Tur Son Test aşamasına geçilecektir.</i>
    </div>
    """, unsafe_allow_html=True)
    
    total_target = st.session_state.target_participant_count
    
    # 1. Turu bitirip henüz 2. tur oyunda cevap yazmamış veya tüm sporcuların listesi
    athlete_options = {info["id"]: f"Sporcu #{info['id']} - {info['name']}" for id_num, info in st.session_state.pass1_athletes.items()}
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        chosen_id = st.selectbox(
            "Lütfen Adınızı veya Rumuzunuzu Seçin:",
            options=list(athlete_options.keys()),
            format_func=lambda x: athlete_options[x],
            key="rescue_chosen_id"
        )
        
    # Süzme işlemi (Kendi cümlen çıkmasın)
    other_fears_dict = {id: fear for id, fear in st.session_state.group_fears_dict.items() if id != chosen_id}
    
    if other_fears_dict:
        if 'assigned_fear_for_id' not in st.session_state or st.session_state.get('last_chosen_id') != chosen_id:
            st.session_state.assigned_fear_for_id = random.choice(list(other_fears_dict.values()))
            st.session_state.last_chosen_id = chosen_id
            
        st.markdown(f"""
        <div class='fear-box'>
        <b>🪨 Ekrana Düşen Takım Arkadaşının Birebir Anonim Korku Cümlesi:</b><br>
        <i>"{st.session_state.assigned_fear_for_id}"</i>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("rescue_form_pass2"):
            resp = st.text_area(
                f"{athlete_options[chosen_id]} - Bu Takım Arkadaşını Ayağa Kaldıracak Şefkat Mesajın:",
                placeholder="Örn: Haklısın, bu korku hepimizin zihnine gelebilir ama senin ne kadar çabaladığını görüyoruz. Tek bir maç senin değerini belirlemez, yanındayız!"
            )
            
            if st.form_submit_button("Şefkatli Mesajı Torbaya Gönder 💌", type="primary"):
                if resp:
                    st.session_state.pass2_responses[chosen_id] = resp
                    # Panoya kaydet
                    st.session_state.group_board_entries.append({
                        "fear": st.session_state.assigned_fear_for_id,
                        "response": resp,
                        "responder_id": chosen_id
                    })
                    st.success(f"{athlete_options[chosen_id]} olarak şefkatli mesajın başarıyla kaydedildi!")
                    st.balloons()
                    if 'assigned_fear_for_id' in st.session_state:
                        del st.session_state['assigned_fear_for_id']
                    st.rerun()
                else:
                    st.warning("Lütfen şefkatli bir mesaj yazın.")
    else:
        st.warning("Henüz torbada yeterli anonim cümle bulunmuyor.")

    st.markdown("---")
    st.markdown("### 🤝 Ortak İnsanlık & Şefkat Panosu (Canlı Akış)")
    
    if st.session_state.group_board_entries:
        for idx, entry in enumerate(st.session_state.group_board_entries, 1):
            st.markdown(f"""
            <div class='compassion-board'>
            <b>🪨 Anonim Takım Arkadaşı Korku Cümlesi #{idx}:</b> <i>"{entry['fear']}"</i><br><br>
            <b>💌 Yazılan Şefkatli Yanıt (Sporcu #{entry['responder_id']}):</b> "{entry['response']}"
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    current_pass2 = len(st.session_state.pass2_responses)
    if current_pass2 < total_target:
        st.info(f"Oyunda Cevap Yazan Sporcu: **{current_pass2} / {total_target}**. Diğer sporcular da adını seçip şefkatli mesajını kaydetsin.")
    else:
        st.success(f"🎉 Harika! Tüm {total_target} sporcu anonim yazıları cevapladı ve Şefkat Oyununu tamamladı!")
        if st.button("📝 3. TUR: SON TEST (GELİŞİM ÖLÇÜMÜ) EKRANINA GEÇ 🚀", type="primary"):
            st.session_state.stage = 40 # 3. Tur Son Test Giriş Seçim Ekranı
            st.rerun()

# STAGE 40: 3. TUR SON TEST SPORCU SEÇİM EKRANI
elif st.session_state.stage == 40:
    st.markdown("<div class='stage-title'>📝 3. Tur: Gelişim Ölçümü (Son Test) Seçim Ekranı</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-box'>Tüm sporcular modülleri ve Şefkat Oyununu başarıyla tamamladı. Şimdi aşağıdaki seçeneklerden <b>adınızı veya rumuzunuzu seçerek</b> gelişim ölçümü için Son Testinizi tamamlayın!</div>", unsafe_allow_html=True)
    
    total_target = st.session_state.target_participant_count
    
    # 1. Turu geçen sporcuların listesi
    athlete_options = {info["id"]: f"Sporcu #{info['id']} - {info['name']}" for id_num, info in st.session_state.pass1_athletes.items()}
    
    # Henüz 3. Tur Son Testini bitirmemiş sporcular
    completed_post_ids = [row["Sporcu No"] for row in st.session_state.workshop_data]
    uncompleted_options = {k: v for k, v in athlete_options.items() if k not in completed_post_ids}
    
    if uncompleted_options:
        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            chosen_id_test = st.selectbox(
                "Lütfen Adınızı veya Rumuzunuzu Seçin:",
                options=list(uncompleted_options.keys()),
                format_func=lambda x: uncompleted_options[x],
                key="test_chosen_id"
            )
            
        athlete_info = st.session_state.pass1_athletes[chosen_id_test]
        st.session_state.athlete_id = chosen_id_test
        st.session_state.athlete_name = athlete_info["name"]
        st.session_state.athlete_age = athlete_info["age"]
        st.session_state.athlete_gender = athlete_info["gender"]
        st.session_state.pre_score = athlete_info["pre_score"]
        st.session_state.my_fear = athlete_info["fear"]
        st.session_state.my_compassion_response = st.session_state.pass2_responses.get(chosen_id_test, "Oyunda Cevap Yazıldı")
        
        if st.button(f"📝 {athlete_options[chosen_id_test]} Olarak Son Teste Başla ➡️", type="primary"):
            st.session_state.stage = 4 # Stage 4: Son Test Soruları
            st.rerun()
    else:
        st.success(f"🎉 Harika! Tüm {total_target} sporcu Son Testlerini tamamladı!")
        if st.button("📊 Atölye Grubu Toplu Veri Raporunu Gör 🚀", type="primary"):
            st.session_state.stage = 6
            st.rerun()

# STAGE 4: SON TEST SORULARI
elif st.session_state.stage == 4:
    st.markdown(f"<div class='stage-title'>Aşama 4: Gelişim Ölçümü (Son Test) - {st.session_state.athlete_name} (Sporcu #{st.session_state.athlete_id})</div>", unsafe_allow_html=True)
    st.info("Psikolojik atölye egzersizlerinden ve Takım Şefkat Oyunundan SONRA, şu anki hissiyatına göre soruları tekrar yanıtla.")
    
    with st.form("post_test_form"):
        for i, q in enumerate(QUESTIONS):
            st.session_state.post_answers[i] = st.slider(q["text"], 1, 5, st.session_state.post_answers[i], key=f"post_{i}")
        
        if st.form_submit_button("Testi Tamamla ve Bireysel Raporu Gör 📊", type="primary"):
            st.session_state.post_score = calculate_score(st.session_state.post_answers)
            st.session_state.stage = 5
            st.rerun()

# STAGE 5: BİREYSEL SONUÇ & 3. TUR SON TEST GEÇİŞ EKRANI
elif st.session_state.stage == 5:
    pre = st.session_state.pre_score
    post = st.session_state.post_score
    diff = round(post - pre, 1)
    fear_val = st.session_state.get('my_fear', 'Korku Girilmedi')
    resp_val = st.session_state.get('my_compassion_response', 'Yanıt Girilmedi')
    
    st.markdown(f"<div class='stage-title'>Katılımcı Bireysel Raporu: {st.session_state.athlete_name} (Sporcu #{st.session_state.athlete_id})</div>", unsafe_allow_html=True)
    
    if diff > 0:
        st.markdown(f"<div class='success-box'>Harika! Öz şefkat seviyeniz oyundan sonra <b>+{diff:.1f}</b> puan arttı!</div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<div class='card-box'>Öz şefkat skorunuz kaydedildi.</div>", unsafe_allow_html=True)
    
    # Veriyi listeye kaydet (Tekrarlanmaması için kontrol et)
    already_saved = any(row['Sporcu No'] == st.session_state.athlete_id for row in st.session_state.workshop_data)
    if not already_saved:
        st.session_state.workshop_data.append({
            "Sıra": len(st.session_state.workshop_data) + 1,
            "Sporcu No": st.session_state.athlete_id,
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
        st.info(f"Son Testi Tamamlayan Sporcu: **{saved_count} / {total_target}**. Sıradaki sporcunun Son Testi için aşağıdaki butona tıklayın.")
        if st.button("➡️ Sıradaki Sporcu Adını Seçsin ve Son Testini Çözsün", type="primary"):
            st.session_state.stage = 40 # 3. Tur Seçim Ekranına dön
            st.rerun()
    else:
        st.success(f"🎉 Tüm {total_target} sporcu testlerini, modüllerini, Şefkat Oyununu ve Son Testini başarıyla tamamladı!")
        if st.button("📊 Atölye Grubu Toplu Veri Raporunu Gör", type="primary"):
            st.session_state.stage = 6
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
    
    st.markdown("---")
    st.markdown("### 🤝 Ortak İnsanlık & Şefkat Panosu (Tam Döküm)")
    if st.session_state.group_board_entries:
        for idx, entry in enumerate(st.session_state.group_board_entries, 1):
            st.markdown(f"""
            <div class='compassion-board'>
            <b>🪨 Anonim Takım Arkadaşı Korku Cümlesi #{idx}:</b> <i>"{entry['fear']}"</i><br><br>
            <b>💌 Yazılan Şefkatli Yanıt (Sporcu #{entry['responder_id']}):</b> "{entry['response']}"
            </div>
            """, unsafe_allow_html=True)
            
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
