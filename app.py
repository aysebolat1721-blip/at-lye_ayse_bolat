import streamlit as st
import pandas as pd
import requests
import json

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

# Dinamik Grup Turnuvası Senaryoları (15 Farklı Katılımcı için)
GROUP_SCENARIOS = [
    {
        "q": "🥋 **Katılımcı Kartı #1:** Türkiye Şampiyonası elemelerinde ilk turda elendin. Antrenörün salondan ayrıldı.",
        "options": [
            ("A) 'Her şey bitti, ben yeteneksiz bir sporcuyum.'", 25, "Öz-Yargılama baskın."),
            ("B) 'Üzgünüm ama bu yenilgi eksiklerimi görmemi sağlayacak bir deneyim. Birçok şampiyon ilk turlarda elenmiştir.'", 100, "Mükemmel! Ortak İnsanlık ve Nezaket boyutları uygulandı."),
            ("C) 'Öfkeliyim, hakemler bilerek puanımı vermedi.'", 50, "Dışsal Yükleme baskın.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #2:** Antrenmanda en çok çalıştığın Dwit Chagi (Döner Tekme) hareketini yaparken yere düştün.",
        "options": [
            ("A) 'Düşmek sporun doğasında var. Tekniğimi düzeltip tekrar deneyeceğim.'", 100, "Harika! Bilinçli Farkındalık ve Öz-Nezaket yüksek."),
            ("B) 'Herkes bana gülüyor, bir daha bu tekniği denemeyeceğim.'", 25, "İzolasyon ve Yargılama baskın."),
            ("C) 'Önemli değil ama bir daha asla antrenman yapmayacağım.'", 30, "Bastırma tutumu.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #3:** Kuşak sınavında heyecandan Poomsae adımlarını şaşırdın.",
        "options": [
            ("A) 'Aptalım ben, bunca aylık emek çöp oldu.'", 20, "Aşırı Özdeşleşme."),
            ("B) 'Heyecanlanmam çok insani. Nefes alıp hatırladığım yerden devam edeceğim.'", 100, "Mükemmel! Farkındalık ve Kabul uygulandı."),
            ("C) 'Sınav sistemi zaten çok saçma.'", 45, "Savunma mekanizması.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #4:** Maçın son 10 saniyesinde ceza (kyongo) alarak yenildin.",
        "options": [
            ("A) 'Büyük bir hayal kırıklığı ama her sporcu son saniye stresi yaşayabilir. Bu tecrübe beni güçlendirecek.'", 100, "Harika! Ortak İnsanlık boyutu yüksek."),
            ("B) 'Dünyanın en şanssız insanı benim, tek talihsizlik ben mi yaşarım?'", 25, "İzolasyon tutumu."),
            ("C) 'Son saniyede maçı vermek tam benim gibi bir başarısızlığa yakışır.'", 20, "Öz-Yargılama.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #5:** Takım arkadaşın milli takıma seçildi ancak sen kıl payı kaçırdın.",
        "options": [
            ("A) 'Onun adına sevinirken kendi üzüntümü de kabul ediyorum. Çalışmaya devam edeceğim.'", 100, "Mükemmel! Duygusal denge ve Öz-Nezaket."),
            ("B) 'Ben hiç sevilmiyorum, torpil yapıldı.'", 30, "Dışsal Mağduriyet."),
            ("C) 'Artık sporu bırakıyorum, hiçbir anlamı kalmadı.'", 20, "Pes etme ve İzolasyon.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #6:** Antrenman maçında kendinden daha alt kuşaktaki birine nakavt oldun.",
        "options": [
            ("A) 'Gelişmek için bazen yenilmek gerekir. Alt kuşak arkadaşımı tebrik edip kendi savunmama odaklanacağım.'", 100, "Harika! Mütevazılık ve Farkındalık."),
            ("B) 'Rezil oldum, salondakilerin yüzüne bakamam.'", 25, "İzolasyon ve Utanç."),
            ("C) 'O şans eseri vurdu, normalde beni asla yenemez.'", 40, "İnkar.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #7:** Önemli bir maç öncesi tartıda kilon fazla çıktı ve strese girdin.",
        "options": [
            ("A) 'Stresli olmam normal. Şu an paniklemek yerine ter atma egzersizime odaklanıyorum.'", 100, "Mükemmel! Bilinçli Farkındalık."),
            ("B) 'Disiplinsizim, benden sporcu olmaz.'", 20, "Öz-Yargılama."),
            ("C) 'Aç kalarak kendime zarar vereceğim.'", 30, "Cezalandırıcı Tutum.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #8:** Maç esnasında sakatlandın ve doktor maça devam etmeni yasakladı.",
        "options": [
            ("A) 'Sağlığım her şeyden önemli. Birçok sporcu sakatlanır, iyileşme sürecime şefkatle yaklaşacağım.'", 100, "Harika! Nezaket ve Ortak İnsanlık."),
            ("B) 'Hayatım bitti, spor kariyerim buraya kadarmış.'", 25, "Felaketleştirme."),
            ("C) 'Doktor hiçbir şeyden anlamıyor.'", 40, "Öfke yansıtma.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #9:** Antrenörün sert eleştirisine maruz kaldın.",
        "options": [
            ("A) 'Eleştirideki yapıcı kısımları alıp kendime olan sevgimi koruyacağım.'", 100, "Mükemmel! İçsel Güven ve Nezaket."),
            ("B) 'Antrenörüm benden nefret ediyor.'", 30, "Kişiselleştirme."),
            ("C) 'Ben zaten hiçbir şeyi doğru yapamam.'", 20, "Öz-Yargılama.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #10:** Uzun bir sakatlıktan sonra ilk antrenmanına çıktın ve çok çabuk yoruldun.",
        "options": [
            ("A) 'Bedenime zaman tanımalıyım. Sakatlık sonrası performans düşüşü çok doğaldır.'", 100, "Harika! Sabır ve Beden Şefkati."),
            ("B) 'Eski halime asla dönemeyeceğim.'", 25, "Aşırı Özdeşleşme."),
            ("C) 'Kendimi zorlayıp sakatlığımı nüksettireceğim.'", 30, "Zorlayıcı Saldırganlık.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #11:** Müsabakada faul yaptığın için puanın silindi.",
        "options": [
            ("A) 'Anlık bir hataydı. Sakinleşip maça geri dönüyorum.'", 100, "Mükemmel! Anda Kalma ve Farkındalık."),
            ("B) 'Her şeyi batırdım.'", 25, "Genelleme."),
            ("C) 'Hakem bana taktı.'", 35, "Dışsal Yükleme.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #12:** Takım seçmelerinde yedek kaldın.",
        "options": [
            ("A) 'Yedek kalmak üzücü ama pes etmeden çalışmaya ve takımı desteklemeye devam edeceğim.'", 100, "Harika! Dayanıklılık ve Şefkat."),
            ("B) 'Beni hiç kimse önemsemiyor.'", 25, "İzolasyon."),
            ("C) 'Ben takımın en kötüsüyüm.'", 20, "Öz-Yargılama.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #13:** Yıllardır yendiğin rakibine bu sefer mağlup oldun.",
        "options": [
            ("A) 'Sporun doğasında yenilmek de var. Rakibimi tebrik edip kendi eksiklerime bakacağım.'", 100, "Mükemmel! Ortak İnsanlık ve Olgunluk."),
            ("B) 'Bitmişim ben, gururum kırıldı.'", 25, "Ego Zedelenmesi."),
            ("C) 'Zemin kaygandı yoksa yenilmezdim.'", 40, "Bahane Geliştirme.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #14:** Maç sırasında kondisyonunun tükendiğini hissettin.",
        "options": [
            ("A) 'Bedenimi dinliyorum, nefesimi ayarlayıp tempomu zekice yöneteceğim.'", 100, "Harika! Bilinçli Öz-Bakım."),
            ("B) 'Cılız biriyim, kondisyonum hiç yok.'", 25, "Öz-Yargılama."),
            ("C) 'Kendimi pürüzsüzce bitene kadar zorlayacağım.'", 40, "Aşırı Zorlama.")
        ]
    },
    {
        "q": "🥋 **Katılımcı Kartı #15:** Turnuvada madalya alamadan salondan ayrılıyorsun.",
        "options": [
            ("A) 'Madalya alamamak emeğimi değersiz kılmaz. Gösterdiğim çaba ile gurur duyuyorum.'", 100, "Mükemmel! Koşulsuz Öz-Kabul."),
            ("B) 'Boşuna antrenman yapmışım, her şey çöp.'", 20, "Hep ya da Hiç Düşüncesi."),
            ("C) 'Ailem ve arkadaşlarım bana çok kızacak.'", 30, "Dışsal Onay Bağımlılığı.")
        ]
    }
]

def calculate_score(answers):
    total = 0
    for i, q in enumerate(QUESTIONS):
        val = answers[i]
        if q["reverse"]:
            val = 6 - val
        total += val
    return round((total / (len(QUESTIONS) * 5)) * 100, 1)

def analyze_self_talk(negative, positive):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    Aşağıdaki metni nesnel olarak analiz et.
    Dönüşüm Metni: "{positive}"
    Eski Olumsuz Metin: "{negative}"
    
    Görev: 
    1. Duygu Dönüşümü (örn: Öfke -> Kabul)
    2. Kristin Neff, Paul Gilbert veya Tara Brach ilkelerinden hangisinin baskın olduğunu tespit et.
    Format:
    Duygu Değişimi: X -> Y
    Tespit Edilen Psikolojik Yaklaşım: Z
    """
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Sen sadece duygu ve psikolojik teknik analizi yapan nesnel bir veri asistanısın."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 150
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except:
        return "Duygu Değişimi: Analiz Edilemedi\nTespit Edilen Yaklaşım: Bilinmeyen (API Hatası)"

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

# Bireysel katılımcı geçici state'leri
if 'pre_answers' not in st.session_state:
    st.session_state.pre_answers = [3] * len(QUESTIONS)
if 'post_answers' not in st.session_state:
    st.session_state.post_answers = [3] * len(QUESTIONS)
if 'pre_score' not in st.session_state:
    st.session_state.pre_score = 0
if 'post_score' not in st.session_state:
    st.session_state.post_score = 0
if 'game_score' not in st.session_state:
    st.session_state.game_score = 100
if 'athlete_name' not in st.session_state:
    st.session_state.athlete_name = ""
if 'athlete_age' not in st.session_state:
    st.session_state.athlete_age = 15
if 'athlete_gender' not in st.session_state:
    st.session_state.athlete_gender = "Belirtmek İstemiyorum"

def next_stage():
    st.session_state.stage += 1

def reset_individual():
    st.session_state.pre_answers = [3] * len(QUESTIONS)
    st.session_state.post_answers = [3] * len(QUESTIONS)
    st.session_state.pre_score = 0
    st.session_state.post_score = 0
    st.session_state.game_score = 100
    st.session_state.athlete_name = ""
    st.session_state.game_played = False
    st.session_state.group_game_played = False
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
        st.markdown(f"**Mevcut Sporcu Aşaması:** {st.session_state.stage}/4")
        if st.session_state.athlete_name:
            st.markdown(f"👤 **Aktif Sporcu:** {st.session_state.athlete_name}")
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

# STAGE 0: ATÖLYE KURULUMU & KATILIMCI GİRİŞİ
if st.session_state.stage == 0:
    if not st.session_state.setup_complete:
        st.markdown("<div class='stage-title'>🏛️ Atölye Grubu Kurulumu (Psikolog / Eğitmen Paneli)</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box'>Lütfen bugün atölyeye katılacak **toplam sporcu sayısını** belirleyin (8-15 kişi). Tüm sporcular sırayla testi ve oyunları tamamladığında toplu veri tablosu ve grubu raporu otomatik oluşacaktır.</div>", unsafe_allow_html=True)
        
        with st.form("setup_form"):
            count = st.slider("Atölye Katılımcı Sayısı (Kişi):", min_value=1, max_value=15, value=8, step=1)
            if st.form_submit_button("Atölyeyi Başlat ve 1. Sporcuyu Çağır 🚀", type="primary"):
                st.session_state.target_participant_count = count
                st.session_state.setup_complete = True
                st.rerun()
    else:
        num = current_done + 1
        st.markdown(f"<div class='stage-title'>📌 Sporcu {num} / {st.session_state.target_participant_count} Giriş Ekranı</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-box'>Bu etkileşimli atölyede dünyaca ünlü psikologların yöntemleriyle zihinsel dayanıklılığını ve şefkat kaslarını güçlendireceğiz.</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown(f"#### Katılımcı #{num} Bilgileri")
            name = st.text_input("Rumuzun veya Adın:", placeholder="Şampiyon")
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Yaşın:", min_value=6, max_value=60, value=14, step=1)
            with col2:
                gender = st.selectbox("Cinsiyetin:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
                
            submitted = st.form_submit_button("Oyuna ve Teste Başla 🚀", type="primary")
            if submitted:
                if name:
                    st.session_state.athlete_name = name
                    st.session_state.athlete_age = age
                    st.session_state.athlete_gender = gender
                    next_stage()
                    st.rerun()
                else:
                    st.warning("Lütfen başlamadan önce bir rumuz veya isim giriniz.")

# STAGE 1: ÖN TEST
elif st.session_state.stage == 1:
    st.markdown(f"<div class='stage-title'>Aşama 1: Mevcut Durum Analizi (Ön Test) - {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    st.info("Lütfen aşağıdaki ifadelere ne kadar katıldığını dürüstçe işaretle. (1 = Hiç Katılmıyorum, 5 = Tamamen Katılıyorum)")
    
    with st.form("pre_test_form"):
        for i, q in enumerate(QUESTIONS):
            st.session_state.pre_answers[i] = st.slider(q["text"], 1, 5, st.session_state.pre_answers[i], key=f"pre_{i}")
        
        if st.form_submit_button("Testi Tamamla ve İlerle", type="primary"):
            st.session_state.pre_score = calculate_score(st.session_state.pre_answers)
            next_stage()
            st.rerun()

# STAGE 2: GELİŞİM OYUNU
elif st.session_state.stage == 2:
    st.markdown("<div class='stage-title'>Aşama 2: Dünyaca Ünlü Psikologların Yöntemleriyle Şefkat Atölyesi 🧠</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card-box'>
    Bu aşama zihinsel kaslarını güçlendirecek 5 bilimsel modülden oluşmaktadır. Özellikle 5. modüldeki Grup Turnuvası Oyununu tamamlamayı unutma!
    </div>
    """, unsafe_allow_html=True)
    
    game_tab1, game_tab2, game_tab3, game_tab4, game_tab5 = st.tabs([
        "🌧️ 1. Tara Brach - RAIN Metodu", 
        "🔴🔵🟢 2. Paul Gilbert - 3 Beyin Sistemi", 
        "🛡️ 3. Kristin Neff - Kriz Senaryoları", 
        "✉️ 4. Germer & Neff - Şefkatli Mektup",
        "🏆 5. MSC Grup Turnuvası (Şefkat Müttefiki Oyunu)"
    ])
    
    # MODÜL 1: TARA BRACH - RAIN METODU
    with game_tab1:
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

    # MODÜL 2: PAUL GILBERT - 3 BEYİN SİSTEMİ
    with game_tab2:
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

    # MODÜL 3: KRISTIN NEFF - KRIZ SENARYO BANKASI
    with game_tab3:
        st.markdown("### 🛡️ Kristin Neff'in 3 Boyutlu Kriz Simülatörü")
        senaryo_secim = st.selectbox("Bir Kriz Senaryosu Seç:", [
            "Senaryo 1: Kuşak sınavında hareketi unuttun.",
            "Senaryo 2: Favori tekmende rakip kontradan puan aldı.",
            "Senaryo 3: Sakatlık yüzünden turnuvadan çekilmek zorunda kaldın."
        ])
        
        if "Senaryo 1" in senaryo_secim:
            st.markdown("<div class='card-box'>🥋 <b>Kuşak sınavında poomsae çizerken adımı unuttun ve salondaki herkes sana bakıyor.</b></div>", unsafe_allow_html=True)
            ans = st.radio("Zihinsel Tepki Seçeneği:", [
                "A) 'Rezil oldum, benden hiçbir şey olmaz.' (Öz Yargılama)",
                "B) 'Derin bir nefes alıyorum. Heyecandan unutmak her sporcunun başına gelebilir, yalnız değilim.' (Öz Şefkat)"
            ])
            if st.button("Kuramsal Çerçeveyi İncele 1"):
                if ans.startswith("B)"):
                    st.success("Kuramsal Uygunluk: Kristin Neff'in (2003) Ortak İnsanlık boyutuna uygundur.")
                else:
                    st.info("Kuramsal Analiz: 'Öz-Yargılama' boyutuna örnektir.")
                    
        elif "Senaryo 2" in senaryo_secim:
            st.markdown("<div class='card-box'>🥋 <b>Dollyo Chagi tekmende puan alamadın ve kontradan kafana tekme yedin.</b></div>", unsafe_allow_html=True)
            ans = st.radio("Zihinsel Tepki Seçeneği:", [
                "A) 'Şu an canım yanıyor ama bu bir deneyim. Bir sonraki rauntta mesafemi ayarlayacağım.' (Öz Şefkat)",
                "B) 'Ben aptalım, bunu nasıl yerim!' (Aşırı Özdeşleşme)"
            ])
            if st.button("Kuramsal Çerçeveyi İncele 2"):
                if ans.startswith("A)"):
                    st.success("Kuramsal Uygunluk: Bilinçli Farkındalık ve Kendine Nezaket boyutuna örnektir.")
                else:
                    st.info("Kuramsal Analiz: 'Aşırı Özdeşleşme' boyutuna örnektir.")
                    
        else:
            st.markdown("<div class='card-box'>🥋 <b>Şampiyonaya 2 gün kala bileğin burkuldu ve turnuvadan çekilmen istendi.</b></div>", unsafe_allow_html=True)
            ans = st.radio("Zihinsel Tepki Seçeneği:", [
                "A) 'Bütün emeklerim çöp oldu, en şanssız insanım.' (İzolasyon)",
                "B) 'Sağlığım önemli. Birçok sporcu sakatlık yaşar, daha güçlü döneceğim.' (Öz Şefkat)"
            ])
            if st.button("Kuramsal Çerçeveyi İncele 3"):
                if ans.startswith("B)"):
                    st.success("Kuramsal Uygunluk: Ortak İnsanlık boyutuna örnektir.")
                else:
                    st.info("Kuramsal Analiz: 'İzolasyon' boyutuna örnektir.")

    # MODÜL 4: GERMER & NEFF - ŞEFKATLİ MEKTUP
    with game_tab4:
        st.markdown("### ✉️ Germer & Neff Şefkatli Mektup Egzersizi")
        with st.form("letter_form"):
            letter_text = st.text_area("Şefkatli Mektup Metni:", placeholder="Sevgili [Adın], antrenmanlardaki çabaların çok değerli...")
            if st.form_submit_button("Mektubu Analiz Et & Gönder ✉️", type="primary"):
                if letter_text:
                    with st.spinner("Yapay Zeka Veri Asistanı kategorize ediyor..."):
                        res = analyze_self_talk("Şefkatli Mektup Egzersizi", letter_text)
                    st.markdown(f"<div class='analysis-box'><b>🤖 Veri Analitiği Raporu:</b><br>{res}</div>", unsafe_allow_html=True)
                    st.success("Mektup metni başarıyla kaydedildi.")
                else:
                    st.warning("Lütfen mektup metnini doldurun.")

    # MODÜL 5: MSC GRUP ŞEFKAT MÜTTEFİKİ OYUNU (LİTERATÜR BAZLI DİNAMİK GRUP OYUNU)
    with game_tab5:
        st.markdown("### 🏆 Şefkat Müttefiki & Kriz Turnuvası Oyunu")
        st.markdown("""
        <div class='theory-box'>
        <b>Oyunun Literatür Dayanağı & Kuralları (Neff & Germer, 2018 MSC Group Challenge):</b><br>
        1. Bu oyun 8-15 kişilik atölyelerde her sporcuya özel dinamik bir kriz kartı atayarak grup etkileşimini sağlar.<br>
        2. Sana özel atanan aşağıdaki Taekwondo Kriz Kartı'nda 3 seçenek arasından <b>en yüksek Öz-Şefkat Puanına (100 Puan)</b> sahip Müttefik Yanıtı'nı seçmelisin.<br>
        3. Kazandığın Oyun Skoru, atölye sonundaki <b>Toplu Veri Raporu Tablosuna (Stage 5)</b> doğrudan eklenecektir!
        </div>
        """, unsafe_allow_html=True)
        
        # Dinamik Senaryo İndeksi (Sporcunun sırasına göre 15 senaryodan biri çekilir)
        scen_idx = current_done % len(GROUP_SCENARIOS)
        scen_data = GROUP_SCENARIOS[scen_idx]
        
        st.markdown(f"<div class='card-box'>{scen_data['q']}</div>", unsafe_allow_html=True)
        
        opts = [op[0] for op in scen_data['options']]
        chosen_opt = st.radio(f"Sıradaki Sporcu ({st.session_state.athlete_name}) için Müttefik Yanıtın Hangisi?", opts, key="group_game_radio")
        
        if st.button("Şefkat Müttefiki Yanıtını Onayla 🏆", type="primary"):
            # Seçilen opsiyonun puanını bul
            selected_tuple = next(item for item in scen_data['options'] if item[0] == chosen_opt)
            puan = selected_tuple[1]
            aciklama = selected_tuple[2]
            
            st.session_state.game_score = puan
            st.session_state.group_game_played = True
            
            if puan == 100:
                st.markdown(f"<div class='success-box'><b>🎉 TEBRİKLER! TAM PUAN (+100 Şefkat Skoru)</b><br>{aciklama}</div>", unsafe_allow_html=True)
                st.balloons()
            elif puan >= 50:
                st.markdown(f"<div class='card-box'><b>ORTA SEVİYE PUAN (+{puan} Puan)</b><br>{aciklama}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-box'><b>DÜŞÜK ŞEFKAT PUANI (+{puan} Puan)</b><br>{aciklama}</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Aşama 3'e Geç (Son Test) ➡️", type="primary"):
        next_stage()
        st.rerun()

# STAGE 3: SON TEST
elif st.session_state.stage == 1 or st.session_state.stage == 3:
    if st.session_state.stage == 3:
        st.markdown(f"<div class='stage-title'>Aşama 3: Gelişim Ölçümü (Son Test) - {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
        st.info("Psikolojik atölye egzersizlerinden SONRA, şu anki hissiyatına göre soruları tekrar yanıtla.")
        
        with st.form("post_test_form"):
            for i, q in enumerate(QUESTIONS):
                st.session_state.post_answers[i] = st.slider(q["text"], 1, 5, st.session_state.post_answers[i], key=f"post_{i}")
            
            if st.form_submit_button("Testi Tamamla ve Bireysel Raporu Gör 📊", type="primary"):
                st.session_state.post_score = calculate_score(st.session_state.post_answers)
                next_stage()
                st.rerun()

# STAGE 4: BİREYSEL SONUÇ & ATÖLYE GEÇİŞİ
elif st.session_state.stage == 4:
    pre = st.session_state.pre_score
    post = st.session_state.post_score
    diff = round(post - pre, 1)
    g_score = st.session_state.get('game_score', 100)
    
    st.markdown(f"<div class='stage-title'>Katılımcı Bireysel Raporu: {st.session_state.athlete_name}</div>", unsafe_allow_html=True)
    
    if diff > 0:
        st.markdown(f"<div class='success-box'>Harika! Öz şefkat seviyeniz oyundan sonra <b>+{diff:.1f}</b> puan arttı! (Grup Oyun Skoru: <b>{g_score}/100</b>)</div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<div class='card-box'>Öz şefkat skorunuz kaydedildi. (Grup Oyun Skoru: <b>{g_score}/100</b>)</div>", unsafe_allow_html=True)
    
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
            "Grup Oyun Skoru (100)": g_score
        })
    
    total_target = st.session_state.target_participant_count
    saved_count = len(st.session_state.workshop_data)
    
    st.markdown("---")
    if saved_count < total_target:
        st.info(f"Tamamlanan Sporcu: **{saved_count} / {total_target}**. Sıradaki sporcunun testi için aşağıdaki butona tıklayın.")
        if st.button(f"➡️ Sıradaki Sporcuya Geç (Sporcu #{saved_count + 1})", type="primary"):
            reset_individual()
    else:
        st.success(f"🎉 Tüm {total_target} sporcu testlerini ve antrenmanlarını tamamladı! Atölye sona erdi.")
        if st.button("📊 Atölye Grubu Toplu Veri Raporunu Gör", type="primary"):
            next_stage()
            st.rerun()

# STAGE 5: ATÖLYE TOPLU VERİ LİSTESİ VE RAPORU (PSİKOLOG / EĞİTMEN EKRANI)
elif st.session_state.stage == 5:
    st.markdown("<div class='stage-title'>📊 Atölye Grubu Toplu Sonuç Veri Raporu</div>", unsafe_allow_html=True)
    
    df_results = pd.DataFrame(st.session_state.workshop_data)
    
    avg_pre = round(df_results["Ön Test (%)"].mean(), 1)
    avg_post = round(df_results["Son Test (%)"].mean(), 1)
    avg_diff = round(df_results["Net Gelişim (%)"].mean(), 1)
    avg_game = round(df_results["Grup Oyun Skoru (100)"].mean(), 1)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Toplam Katılımcı", f"{len(df_results)} Sporcu")
    with col2:
        st.metric("Ön Test Ortalaması", f"{avg_pre}%")
    with col3:
        st.metric("Son Test Ortalaması", f"{avg_post}%")
    with col4:
        st.metric("Ortalama Gelişim", f"+{avg_diff}%" if avg_diff > 0 else f"{avg_diff}%")
    with col5:
        st.metric("Ort. Grup Oyun Skoru", f"{avg_game} / 100")
        
    st.markdown("### 📋 Katılımcı Veri Listesi (Detaylı Tablo)")
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
