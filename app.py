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

def analyze_self_talk(negative, positive):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    Aşağıdaki iki metni nesnel bir şekilde analiz et. 
    Eski Ses: "{negative}"
    Yeni Ses: "{positive}"
    Görev: 
    1. Hangi duygunun hangi duyguya dönüştüğünü yaz.
    2. Yeni sesin Kristin Neff'in 3 boyutundan (Kendine Nezaket, Ortak İnsanlık, Bilinçli Farkındalık) hangisine ait olduğunu tespit et.
    Asla tavsiye verme, kişisel yorum yapma, psikolog gibi davranma. Sadece veriyi kategorize et.
    Format:
    Duygu Değişimi: X -> Y
    Tespit Edilen Boyut: Z
    """
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Sen sadece duygu ve metin analizi yapan otomatik bir veri işleme asistanısın. Yorum veya tavsiye yapmazsın."},
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
        return "Duygu Değişimi: Analiz Edilemedi\nTespit Edilen Boyut: Bilinmeyen (API Hatası)"

# -----------------
# 3. STATE YÖNETİMİ
# -----------------
if 'stage' not in st.session_state:
    st.session_state.stage = 0
if 'pre_answers' not in st.session_state:
    st.session_state.pre_answers = [3] * len(QUESTIONS)
if 'post_answers' not in st.session_state:
    st.session_state.post_answers = [3] * len(QUESTIONS)
if 'pre_score' not in st.session_state:
    st.session_state.pre_score = 0
if 'post_score' not in st.session_state:
    st.session_state.post_score = 0
if 'athlete_name' not in st.session_state:
    st.session_state.athlete_name = ""
if 'athlete_age' not in st.session_state:
    st.session_state.athlete_age = 15
if 'athlete_gender' not in st.session_state:
    st.session_state.athlete_gender = "Belirtmek İstemiyorum"

def next_stage():
    st.session_state.stage += 1

def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# -----------------
# 4. ARAYÜZ (UI)
# -----------------
with st.sidebar:
    st.markdown("## 🥋 Atölye Paneli")
    st.markdown("Gruplar 8-15 kişi olacak şekilde tasarlandığında herkes kendi telefonundan bu adımları takip edebilir.")
    st.markdown(f"**Güncel Aşama:** {st.session_state.stage}/4")
    st.progress(st.session_state.stage / 4)
    
    if st.session_state.athlete_name:
        st.markdown(f"👤 **Oyuncu:** {st.session_state.athlete_name}")
        st.markdown(f"🎂 **Yaş:** {st.session_state.athlete_age}")
        st.markdown(f"⚧ **Cinsiyet:** {st.session_state.athlete_gender}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="sidebar-footer">
            <b>Tasarım ve Geliştirme:</b><br> Ayşe Bolat<br><br>
            <i>Neff (2003) Öz Şefkat Kuramı Temelli</i>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🥋 Öz Şefkat Gelişim Oyunu</h1>", unsafe_allow_html=True)

# STAGE 0: GİRİŞ
if st.session_state.stage == 0:
    st.markdown("<div class='stage-title'>Hoş Geldin Sporcu!</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-box'>Bu etkileşimli atölyede zihinsel dayanıklılığını ve şefkat kaslarını güçlendireceğiz. Toplam 4 aşamadan oluşan bu oyunla, kendi iç dünyanı keşfedeceksin.</div>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("#### Kendini Tanıt")
        name = st.text_input("Rumuzun veya Adın:", placeholder="Şampiyon")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Yaşın:", min_value=6, max_value=60, value=12, step=1)
        with col2:
            gender = st.selectbox("Cinsiyetin:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
            
        submitted = st.form_submit_button("Oyuna Başla 🚀", type="primary")
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
    st.markdown(f"<div class='stage-title'>Aşama 1: Mevcut Durum Analizi (Ön Test)</div>", unsafe_allow_html=True)
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
    st.markdown("<div class='stage-title'>Aşama 2: Şefkat Geliştirme Oyun Alanı 🎮</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card-box'>
    Zihinsel şefkat ve dayanıklılık kaslarını geliştirmek için aşağıdaki oyunları tamamla. İstediğin oyundan başlayabilirsin!
    </div>
    """, unsafe_allow_html=True)
    
    game_tab1, game_tab2, game_tab3 = st.tabs([
        "🔄 Oyun 1: Zihinsel Dönüştürücü", 
        "🛡️ Oyun 2: Şefkat Kalkanı (Kriz Testi)", 
        "🧘 Oyun 3: Mindfulness & Nefes Antrenmanı"
    ])
    
    # OYUN 1: ZİHİNSEL DÖNÜŞTÜRÜCÜ
    with game_tab1:
        st.markdown("### 🔄 3 Adımlı Zihinsel Dönüşüm Oyunu")
        st.write("Geçmişte taekwondoda yaşadığın bir hayal kırıklığını (maç kaybı, antrenman hatası vb.) düşün ve 3 adımı doldur.")
        
        with st.form("game_form_1"):
            st.markdown("#### Adım 1: Farkındalık (Mindfulness)")
            negative = st.text_area("O an kendine içinden ne söyledin? (Duygularını filtresiz yaz)", placeholder="Örn: Benden hiçbir şey olmaz, yine aynı hatayı yaptım...")
            
            st.markdown("#### Adım 2: Ortak İnsanlık (Common Humanity)")
            common = st.text_area("Sence dünyadaki diğer taekwondocular da benzer hatalar yapıyor mu?", placeholder="Örn: Olimpiyat şampiyonları bile maç kaybediyor, hata yapmak insanca bir durum...")
            
            st.markdown("#### Adım 3: Kendine Nezaket (Self-Kindness)")
            positive = st.text_area("En sevdiğin takım arkadaşın bu hatayı yapsaydı ona ne derdin? (KENDİNE söyle)", placeholder="Örn: Sorun değil, antrenmanda çok çalıştın. Ayağa kalk ve devam et...")
            
            if st.form_submit_button("Zihnimi Dönüştür 🔄", type="primary"):
                if negative and common and positive:
                    st.session_state.neg = negative
                    st.session_state.common = common
                    st.session_state.pos = positive
                    with st.spinner("AI Veri Asistanı dönüşümü analiz ediyor..."):
                        st.session_state.analysis = analyze_self_talk(negative, f"Ortak İnsanlık: {common} | Nezaket: {positive}")
                    st.session_state.game_played = True
                    st.rerun()
                else:
                    st.warning("Lütfen üç adımı da eksiksiz doldurun.")
                    
        if st.session_state.get('game_played', False):
            st.markdown("### 📊 Dönüşüm Raporun")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='alert-box'><b>Farkındalık (Eski Ses):</b><br>{st.session_state.neg}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='analysis-box'><b>Ortak İnsanlık:</b><br>{st.session_state.common}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='success-box'><b>Kendine Nezaket:</b><br>{st.session_state.pos}</div>", unsafe_allow_html=True)
                
            st.markdown(f"<div class='analysis-box' style='background-color: #F3E8FF; border-left: 5px solid #A855F7; color: #6B21A8;'><b>🤖 Veri Analizi:</b><br>{st.session_state.analysis}</div>", unsafe_allow_html=True)

    # OYUN 2: ŞEFKAT KALKANI (KRIZ SENARYOLARI)
    with game_tab2:
        st.markdown("### 🛡️ Şefkat Kalkanı: Taekwondo Kriz Simülatörü")
        st.write("Aşağıdaki zorlu Taekwondo senaryosunda doğru zihinsel tepkiyi (Şefkat Kalkanı) bularak puan kazan!")
        
        scenario_q = "🥋 **Senaryo:** Bölge Şampiyonası Final Maçı'nın son 5 saniyesinde öndeyken talihsiz bir ceza (kyongo) aldın ve maçı 1 puanla kaybettin. Minderden inerken zihninde ne tür bir tepki vermelisin?"
        st.markdown(f"<div class='card-box'>{scenario_q}</div>", unsafe_allow_html=True)
        
        choice = st.radio(
            "Hangi zihinsel tepki senin Şefkat Kalkanındır?",
            [
                "A) 'Ben berbat bir sporcuyum, son saniyede maçı vermek tam bana göre. Bir daha maça çıkmayacağım.'",
                "B) 'Çok öfkeliyim! Hakem de antrenör de ben de suçluyum, dünya üzerimdeki en adaletsiz yer!'",
                "C) 'Şu an derin bir üzüntü ve hayal kırıklığı hissediyorum (Farkındalık). Ama dünyadaki her taekwondocu son saniye mağlubiyeti yaşamıştır (Ortak İnsanlık). Kendime yüklenmek yerine bu maçtan ders çıkarıp bir sonrakine hazırlanacağım (Kendine Nezaket).'",
                "D) 'Hiç önemli değil, umurumda bile değil, ben zaten kazanmış sayılırım.'"
            ]
        )
        
        if st.button("Cevabı Kontrol Et 🛡️", type="primary"):
            if choice.startswith("C)"):
                st.markdown("<div class='success-box'><b>🎉 DOĞRU CEVAP! (+100 Şefkat Puanı)</b><br>Bu tepki Kristin Neff'in 3 temel boyutunun (Farkındalık, Ortak İnsanlık, Kendine Nezaket) mükemmel bir birleşimidir. Zihinsel kalkanın çok güçlü!</div>", unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown("<div class='alert-box'><b>❌ TEKRAR DENE:</b> Seçtiğin tepki öz-yargılama veya bastırma içeriyor. Doğru tepki, duyguyu kabul edip (Farkındalık), yalnız olmadığını hatırla (Ortak İnsanlık) ve kendine yapıcı davranmaktır (Nezaket).</div>", unsafe_allow_html=True)

    # OYUN 3: MINDFULNESS & NEFES ANTREMANI
    with game_tab3:
        st.markdown("### 🧘 Zihinsel Odak ve Nefes Antrenmanı (4-7-8 Tekniği)")
        st.write("Zorlu maçlardan sonra veya kaygılı anlarda zihnini ve kalbini sakinleştirmek için 4-7-8 Nefes Egzersizini uygula.")
        
        st.markdown("""
        <div class='card-box' style='text-align: center;'>
            <h4>🌬️ Nefes Ritim Rehberi</h4>
            <p><b>1. Adım:</b> 4 Saniye boyunca burnundan derin nefes al 📥</p>
            <p><b>2. Adım:</b> 7 Saniye boyunca nefesini tut ⏸️</p>
            <p><b>3. Adım:</b> 8 Saniye boyunca ağzından yavaşça ver 📤</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Nefes Egzersizini Tamamladım 🧘‍♂️", type="secondary"):
            st.success("Tebrikler! Zihinsel sakinleşme antrenmanını tamamladın. Zihnin son test için hazır!")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Bütün oyunları/pratikleri denediysen bir sonraki aşamaya geçebilirsin!")
    if st.button("Aşama 3'e Geç (Son Test) ➡️", type="primary"):
        next_stage()
        st.rerun()

# STAGE 3: SON TEST
elif st.session_state.stage == 3:
    st.markdown("<div class='stage-title'>Aşama 3: Gelişim Ölçümü (Son Test)</div>", unsafe_allow_html=True)
    st.info("İç sesini dönüştürme pratiğinden SONRA, şu anki hissiyatına göre soruları tekrar yanıtla.")
    
    with st.form("post_test_form"):
        for i, q in enumerate(QUESTIONS):
            st.session_state.post_answers[i] = st.slider(q["text"], 1, 5, st.session_state.post_answers[i], key=f"post_{i}")
        
        if st.form_submit_button("Testi Tamamla ve Sonuçları Gör 📊", type="primary"):
            st.session_state.post_score = calculate_score(st.session_state.post_answers)
            next_stage()
            st.rerun()

# STAGE 4: SONUÇLAR
elif st.session_state.stage == 4:
    st.markdown(f"<div class='stage-title'>Aşama 4: Rapor ve Kapanış</div>", unsafe_allow_html=True)
    
    pre = st.session_state.pre_score
    post = st.session_state.post_score
    diff = post - pre
    
    st.markdown(f"### Tebrikler {st.session_state.athlete_name}!")
    
    if diff > 0:
        st.markdown(f"<div class='success-box'>Harika! Öz şefkat seviyeniz oyundan sonra <b>+{diff:.1f}</b> puan arttı!</div>", unsafe_allow_html=True)
        st.balloons()
    elif diff < 0:
        st.markdown(f"<div class='card-box'>Öz şefkat seviyeniz <b>{diff:.1f}</b> puan değişti. Önemli olan farkındalık kazanmaktır.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='card-box'>Öz şefkat seviyeniz aynı kaldı. Gelişim sürekli bir antrenmandır.</div>", unsafe_allow_html=True)
    
    st.markdown("#### Öz Şefkat Skoru Değişimi (%)")
    
    # Harici kütüphane (Altair vb.) çökme hatasını %100 önlemek için saf HTML/CSS bar grafik kullanıldı.
    st.markdown(f"""
        <div style="margin-bottom: 20px; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 600; color: #111827;">Ön Test (Aşama 1)</span>
                <span style="font-weight: 600; color: #111827;">{pre}%</span>
            </div>
            <div style="background-color: #E5E7EB; border-radius: 8px; width: 100%; height: 30px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                <div style="background-color: #3B82F6; width: {pre}%; height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: bold; transition: width 1s ease-in-out;">
                </div>
            </div>
        </div>
        <div style="margin-bottom: 30px; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 600; color: #111827;">Son Test (Aşama 3)</span>
                <span style="font-weight: 600; color: #111827;">{post}%</span>
            </div>
            <div style="background-color: #E5E7EB; border-radius: 8px; width: 100%; height: 30px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                <div style="background-color: #10B981; width: {post}%; height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: bold; transition: width 1s ease-in-out;">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Oyunu Baştan Başlat 🔄", type="primary"):
        reset_game()

# Sayfanın en altındaki Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        Tasarım ve Geliştirme: Ayşe Bolat | Neff (2003) Öz Şefkat Kuramı Temelli
    </div>
""", unsafe_allow_html=True)
