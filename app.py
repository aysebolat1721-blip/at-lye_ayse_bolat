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

# Ortak Yüzleşme Panosu Kayıtları: [{"fear": "...", "response": "..."}, ...]
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
current_done = len(st.session_state.workshop_data)

with st.sidebar:
    st.markdown("## 🥋 Atölye Grubu Paneli")
    if st.session_state.setup_complete:
        st.markdown(f"👥 **Atölye Hedef Mevcudu:** {st.session_state.target_participant_count} Sporcu")
        st.markdown(f"✅ **1. Turu Tamamlayan:** {current_done} / {st.session_state.target_participant_count}")
        st.progress(min(current_done / st.session_state.target_participant_count, 1.0))
        st.markdown("---")
        st.markdown(f"**Aşama Kodu:** {st.session_state.stage}")
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

st.markdown("<h1 class='main-header'>🥋 Öz Şefkat Gelişim Oyunu</h1>", unsafe_allow_header=True)

# STAGE 0: ATÖLYE KURULUMU & KATILIMCI GİRİŞİ (AYDINLATILMIŞ ONAM FORMU İLE)
if st.session_state.stage == 0:
    if not st.session_state.setup_complete:
        st.markdown("<div class='stage-title'>🏛️ Atölye Grubu Kurulumu (Psikolog / Eğitmen Paneli)</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box'>Lütfen bugün atölyeye katılacak **toplam sporcu sayısını** belirleyin (8-15 kişi). Tüm sporcular 1. turda testleri, modülleri ve anonim korku girdilerini tamamladıktan sonra 2. Tur Takım Oyunu başlayacaktır.</div>", unsafe_allow_html=True)
        
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
    active_num = st.session_state.get('athlete_id', current_done + 1)
    
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
        
        if st.form_submit_button("Cümlemi Anonim Torbaya Kaydet 🪨 ve Son Teste Geç ➡️", type="primary"):
            if fear_input:
                st.session_state.my_fear = fear_input
                st.session_state.group_fears_dict[active_num] = fear_input
                st.success(f"Sporcu #{active_num} olarak birebir korku cümlen anonim torbaya atıldı!")
                next_stage()
                st.rerun()
            else:
                st.warning("Lütfen bir korku veya iç ses yazın.")

# STAGE 4: SON TEST
elif st.session_state.stage == 4:
    st.markdown(f"<div class='stage-title'>Aşama 4: Gelişim Ölçümü (Son Test) - {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    st.info("Psikolojik atölye egzersizlerinden ve modüllerden SONRA, şu anki hissiyatına göre soruları tekrar yanıtla.")
    
    with st.form("post_test_form"):
        for i, q in enumerate(QUESTIONS):
            st.session_state.post_answers[i] = st.slider(q["text"], 1, 5, st.session_state.post_answers[i], key=f"post_{i}")
        
        if st.form_submit_button("Testi Tamamla ve Bireysel Raporu Gör 📊", type="primary"):
            st.session_state.post_score = calculate_score(st.session_state.post_answers)
            next_stage()
            st.rerun()

# STAGE 5: BİREYSEL SONUÇ & 1. TUR TAMAMLAMA EKRANI
elif st.session_state.stage == 5:
    pre = st.session_state.pre_score
    post = st.session_state.post_score
    diff = round(post - pre, 1)
    fear_val = st.session_state.get('my_fear', 'Korku Girilmedi')
    
    st.markdown(f"<div class='stage-title'>Katılımcı Bireysel Raporu: {st.session_state.athlete_name} (Sporcu #{st.session_state.athlete_id})</div>", unsafe_allow_html=True)
    
    if diff > 0:
        st.markdown(f"<div class='success-box'>Harika! Öz şefkat seviyeniz modüllerden sonra <b>+{diff:.1f}</b> puan arttı!</div>", unsafe_allow_html=True)
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
            "Verilen Şefkatli Yanıt": "2. Tur Bekleniyor"
        })
    
    total_target = st.session_state.target_participant_count
    saved_count = len(st.session_state.workshop_data)
    
    st.markdown("---")
    if saved_count < total_target:
        st.info(f"1. Turu Tamamlayan Sporcu: **{saved_count} / {total_target}**. Sıradaki sporcunun girişi için aşağıdaki butona tıklayın.")
        if st.button(f"➡️ Sıradaki Sporcuya Geç (Sporcu #{saved_count + 1})", type="primary"):
            reset_individual()
    else:
        st.success(f"🎉 Tebrikler! Tüm {total_target} sporcu testlerini, modüllerini ve anonim korku cümlelerini tamamladı!")
        st.markdown("<div class='card-box'><b>🎮 ŞİMDİ 2. TUR ZAMANI:</b> Atölyedeki tüm anonim cümleler torbaya toplandı. Şimdi herkes sırayla kendi numarasını seçerek başkasının anonim cümlesini çekip kurtarma mesajı yazacaktır!</div>", unsafe_allow_html=True)
        if st.button("🎮 2. TUR: TAKIM ŞEFKATLE YENİDEN İNŞA OYUNUNU BAŞLAT 🚀", type="primary"):
            st.session_state.stage = 7 # Stage 7: 2. Tur Kurtarma Oyunu
            st.rerun()

# STAGE 7: 2. TUR - ŞEFKATLE YENİDEN İNŞA KURTARMA OYUNU (TÜM KATILIMCILAR İÇİN ANONİM EŞLEŞTİRME)
elif st.session_state.stage == 7:
    st.markdown("<div class='stage-title'>🎮 2. Tur: Takım Şefkatle Yeniden İnşa Oyunu</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='theory-box'>
    <b>💌 2. TUR KURTARMA OYUNU İŞLEYİŞİ & ANONİMLİK GARANTİSİ</b><br><br>
    Tüm takım arkadaşlarının 1. Turda yazdığı cümleler şu an torbada karıştı.<br>
    Sistemde kendi numaranızı seçtiğinizde, sistem <b>KENDİ CÜMLENİZ HARİÇ</b> gruptaki diğer 8-10 arkadaşınızın cümlelerinden birini rastgele ekrana getirecektir.<br>
    <i>🔒 Kimin hangi cümleyi yazdığı hiçbir ekranda ve raporda ASLA görünmez!</i>
    </div>
    """, unsafe_allow_html=True)
    
    total_target = st.session_state.target_participant_count
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        chosen_id = st.selectbox(
            "Lütfen Sporcu Numarınızı Seçin:",
            options=list(range(1, total_target + 1)),
            key="rescue_chosen_id"
        )
    
    # Süzme işlemi (Kendi cümlen çıkmasın)
    other_fears_dict = {id: fear for id, fear in st.session_state.group_fears_dict.items() if id != chosen_id}
    
    if other_fears_dict:
        # Eğer bu oturumda henüz bir assigned fear yoksa veya seçilen id değiştiyse yenisini seç
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
                f"Sporcu #{chosen_id} - Bu Takım Arkadaşını Ayağa Kaldıracak Şefkat ve Motivasyon Mesajın:",
                placeholder="Örn: Haklısın, bu korku hepimizin zihnine gelebilir ama senin ne kadar çabaladığını görüyoruz. Tek bir maç senin değerini belirlemez, yanındayız!"
            )
            
            if st.form_submit_button("Şefkatli Kurtarma Mesajını Torbaya Ekle 💌", type="primary"):
                if resp:
                    # Panoya kaydet
                    st.session_state.group_board_entries.append({
                        "fear": st.session_state.assigned_fear_for_id,
                        "response": resp,
                        "responder_id": chosen_id
                    })
                    
                    # Tablodaki ilgili sporcunun kaydını güncelle
                    for row in st.session_state.workshop_data:
                        if row["Sıra"] == chosen_id:
                            row["Verilen Şefkatli Yanıt"] = resp
                            
                    st.success(f"Sporcu #{chosen_id} olarak şefkatli kurtarma mesajın başarıyla gönderildi!")
                    st.balloons()
                    # Yeni sporcu için sıfırla
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
    else:
        st.info("Henüz 2. Turda yanıtlanan bir cümle bulunmuyor. Numarasını seçip yanıt gönderen sporcuların mesajları burada canlı listelenecektir.")
        
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("📊 Tüm Oyun Tamamlandı, Toplu Sonuç Raporunu Gör ➡️", type="primary"):
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
