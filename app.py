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
    st.markdown("<div class='card-box'>Bu etkileşimli atölyede dünyaca ünlü psikologların (Kristin Neff, Paul Gilbert, Tara Brach) yöntemleriyle zihinsel dayanıklılığını ve şefkat kaslarını güçlendireceğiz. Toplam 4 aşamadan oluşan bu oyunla kendi iç dünyanı keşfedeceksin.</div>", unsafe_allow_html=True)
    
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
    st.markdown("<div class='stage-title'>Aşama 2: Dünyaca Ünlü Psikologların Yöntemleriyle Şefkat Atölyesi 🧠</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card-box'>
    Bu aşama zihinsel kaslarını güçlendirecek 4 bilimsel modülden oluşmaktadır. İstediğin modülle başla ve tüm modülleri keşfet!
    </div>
    """, unsafe_allow_html=True)
    
    game_tab1, game_tab2, game_tab3, game_tab4 = st.tabs([
        "🌧️ 1. Tara Brach - RAIN Metodu", 
        "🔴🔵🟢 2. Paul Gilbert - 3 Beyin Sistemi", 
        "🛡️ 3. Kristin Neff - Kriz Senaryoları", 
        "✉️ 4. Germer & Neff - Şefkatli Mektup"
    ])
    
    # MODÜL 1: TARA BRACH - RAIN METODU
    with game_tab1:
        st.markdown("### 🌧️ Tara Brach'in RAIN Metodu (4 Adımlı Zihinsel Pratik)")
        st.markdown("""
        <div class='theory-box'>
        <b>RAIN Tekniği Nedir?</b> Dünyaca ünlü psikolog Tara Brach tarafından geliştirilen bu yöntem, zorlu duygularla (maç stresi, hata yapma korkusu) başa çıkmak için 4 adımdan oluşur:
        <br><b>R</b>ecognize (Tanı) | <b>A</b>llow (İzin Ver) | <b>I</b>nvestigate (İncele) | <b>N</b>urture (Şefkatle Besle)
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("rain_form"):
            rain_r = st.text_area("1. Recognize (Tanı): Zor bir maç veya antrenman anında zihninde hangi duygu var?", placeholder="Örn: Yenilme korkusu, başarısızlık stresi, hakeme öfke...")
            rain_a = st.text_area("2. Allow (İzin Ver): Bu duyguyla savaşmak yerine onun varlığına izin ver. 'Şu an bu hissi duyuyorum' yaz.", placeholder="Örn: Şu an korkuyorum ve bu hissin var olmasına izin veriyorum, bunu bastırmıyorum.")
            rain_i = st.text_area("3. Investigate (İncele): Bu duygu bedeninde nerede hissettiriyor?", placeholder="Örn: Göğsümde sıkışma var, karnıma ağrı giriyor, çenem kasılıyor...")
            rain_n = st.text_area("4. Nurture (Şefkatle Besle): İçindeki sporcuya ihtiyacı olan şefkat cümlesini söyle.", placeholder="Örn: Güvendesin. Elinden gelenin en iyisini yapıyorsun ve ben senin yanındayım.")
            
            if st.form_submit_button("RAIN Egzersizini Tamamla 🌧️", type="primary"):
                if rain_r and rain_a and rain_i and rain_n:
                    st.success("Tebrikler! Tara Brach'in RAIN Metodunu başarıyla uyguladın! Şefkat kasın güçlendi.")
                else:
                    st.warning("Lütfen 4 adımı da doldurun.")

    # MODÜL 2: PAUL GILBERT - 3 BEYİN SİSTEMİ
    with game_tab2:
        st.markdown("### 🔴🔵🟢 Paul Gilbert'in Şefkat Odaklı Terapi (CFT) 3 Beyin Sistemi")
        st.markdown("""
        <div class='theory-box'>
        Evrimsel Psikolog Prof. Paul Gilbert'e göre beynimizde 3 temel duygu düzenleme sistemi bulunur:
        <br>🔴 <b>Tehdit Sistemi:</b> Korku, panik, öz-eleştiri ("Mahvoldum, kesin kaybedeceğim")
        <br>🔵 <b>Güdü/Başarı Sistemi:</b> Hırs, kazanma odaklılık, sürüklenme ("Ne pahasına olursa olsun yenmeliyim")
        <br>🟢 <b>Yatıştırıcı/Şefkat Sistemi:</b> Güven, sakinlik, öz-şefkat ("Hata yapabilirim, ben güvendeyim")
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🎯 Taekwondo Durum Testi: Hangi Sistemdesin?")
        q_gilbert = st.radio(
            "Seçme maçında rakibin senden 4 puan öne geçti. O an içindeki ses en çok hangisine yakın?",
            [
                "🔴 Tehdit Sistemi: 'Eyvah bittim ben! Rezil olacağım, antrenörüm bana çok kızacak!'",
                "🔵 Güdü Sistemi: 'Gözüm hiçbir şey görmüyor, şu an saldırıp ne pahasına olursa olsun puan almalıyım!'",
                "🟢 Şefkat/Yatıştırma Sistemi: 'Sakin ol, daha süre var. Heyecanlanmam normal, nefes alıp planıma odaklanıyorum.'"
            ]
        )
        if st.button("Sistemini Analiz Et 🧠"):
            if q_gilbert.startswith("🔴"):
                st.markdown("<div class='alert-box'>🔴 <b>Tehdit Sistemindesin:</b> Beynin kortizol üretiyor. Kendini eleştirmek yerine 🟢 Yatıştırıcı sisteme geçmek için derin nefes al.</div>", unsafe_allow_html=True)
            elif q_gilbert.startswith("🔵"):
                st.markdown("<div class='card-box'>🔵 <b>Güdü/Başarı Sistemindesin:</b> Hırsın yüksek ama dikkat et! Kontrolsüz hırs hata yaptırabilir. Araya 🟢 Şefkat ekleyerek odağını koru.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='success-box'>🟢 <b>Harika! Yatıştırıcı Şefkat Sistemindesin:</b> Zihnin dengede, spor performansın için en verimli moddasın! (+100 Puan)</div>", unsafe_allow_html=True)
                st.balloons()

    # MODÜL 3: KRISTIN NEFF - KRIZ SENARYO BANKASI
    with game_tab3:
        st.markdown("### 🛡️ Kristin Neff'in 3 Boyutlu Kriz Simülatörü")
        st.write("Aşağıdaki taekwondo kriz durumlarında doğru zihinsel şefkat tepkisini ver.")
        
        senaryo_secim = st.selectbox("Bir Kriz Senaryosu Seç:", [
            "Senaryo 1: Kuşak sınavında hareketi unuttun.",
            "Senaryo 2: Favori tekmende rakip kontradan puan aldı.",
            "Senaryo 3: Sakatlık yüzünden turnuvadan çekilmek zorunda kaldın."
        ])
        
        if "Senaryo 1" in senaryo_secim:
            st.markdown("<div class='card-box'>🥋 <b>Kuşak sınavında poomsae çizerken adımı unuttun ve salondaki herkes sana bakıyor.</b></div>", unsafe_allow_html=True)
            ans = st.radio("Zihinsel Tepkin:", [
                "A) 'Rezil oldum, benden hiçbir şey olmaz.' (Öz Yargılama)",
                "B) 'Derin bir nefes alıyorum. Heyecandan unutmak her sporcunun başına gelebilir, yalnız değilim. Baştan devam ediyorum.' (Öz Şefkat)"
            ])
            if st.button("Tepkiyi Kontrol Et 1"):
                if ans.startswith("B)"):
                    st.success("Tebrikler! Ortak İnsanlık ve Farkındalık boyutunu mükemmel kullandın!")
                else:
                    st.error("Bu tepki Öz-Yargılama içeriyor. Kendine yüklenmek yerine nazik olmalısın.")
                    
        elif "Senaryo 2" in senaryo_secim:
            st.markdown("<div class='card-box'>🥋 <b>Çok güvendiğin Dollyo Chagi tekmende puan alamadın ve kontradan kafana tekme yedin.</b></div>", unsafe_allow_html=True)
            ans = st.radio("Zihinsel Tepkin:", [
                "A) 'Şu an canım yanıyor ve üzgünüm ama bu bir deneyim. Bir sonraki rauntta mesafemi ayarlayacağım.' (Öz Şefkat)",
                "B) 'Ben aptalım, bunu nasıl yerim!' (Aşırı Özdeşleşme)"
            ])
            if st.button("Tepkiyi Kontrol Et 2"):
                if ans.startswith("A)"):
                    st.success("Tebrikler! Farkındalık ve Kendine Nezaket boyutunu kullandın!")
                else:
                    st.error("Bu tepki Aşırı Özdeşleşme içeriyor.")
                    
        else:
            st.markdown("<div class='card-box'>🥋 <b>Şampiyonaya 2 gün kala bileğin burkuldu ve doktor turnuvadan çekilmeni söyledi.</b></div>", unsafe_allow_html=True)
            ans = st.radio("Zihinsel Tepkin:", [
                "A) 'Bütün emeklerim çöp oldu, dünya üzerimdeki en şanssız insanım.' (İzolasyon)",
                "B) 'Çok üzgünüm ama sağlığım her şeyden önemli. Birçok sporcu sakatlık yaşar, iyileşip daha güçlü döneceğim.' (Öz Şefkat)"
            ])
            if st.button("Tepkiyi Kontrol Et 3"):
                if ans.startswith("B)"):
                    st.success("Tebrikler! Ortak İnsanlık boyutunu harika uyguladın!")
                else:
                    st.error("Bu tepki İzolasyon içeriyor.")

    # MODÜL 4: GERMER & NEFF - ŞEFKATLİ MEKTUP
    with game_tab4:
        st.markdown("### ✉️ Germer & Neff Şefkatli Mektup Egzersizi")
        st.write("Kendine, seni koşulsuz seven ve anlayan bilge bir şampiyon antrenör gözüyle bir mektup yaz.")
        
        with st.form("letter_form"):
            letter_text = st.text_area("Kendine Şefkatli Mektubun:", placeholder="Sevgili [Adın], son maçta istediğin sonucu alamadığını biliyorum ama sen antrenmanlarda harika işler çıkardın...")
            if st.form_submit_button("Mektubu Analiz Et & Gönder ✉️", type="primary"):
                if letter_text:
                    with st.spinner("AI Veri Asistanı mektuptaki şefkat unsurlarını analiz ediyor..."):
                        res = analyze_self_talk("Şefkatli Mektup Egzersizi", letter_text)
                    st.markdown(f"<div class='analysis-box'><b>🤖 Mektup Analizi:</b><br>{res}</div>", unsafe_allow_html=True)
                    st.success("Mektubun kaydedildi! Şefkat kasın tavan yaptı!")
                else:
                    st.warning("Lütfen mektubunuzu yazın.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Bütün modülleri ve egzersizleri denediysen bir sonraki aşamaya geçebilirsin!")
    if st.button("Aşama 3'e Geç (Son Test) ➡️", type="primary"):
        next_stage()
        st.rerun()

# STAGE 3: SON TEST
elif st.session_state.stage == 3:
    st.markdown("<div class='stage-title'>Aşama 3: Gelişim Ölçümü (Son Test)</div>", unsafe_allow_html=True)
    st.info("Psikolojik atölye egzersizlerinden SONRA, şu anki hissiyatına göre soruları tekrar yanıtla.")
    
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
    
    st.markdown(f"""
        <div style="margin-bottom: 20px; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 600; color: #111827;">Ön Test (Aşama 1)</span>
                <span style="font-weight: 600; color: #111827;">{pre}%</span>
            </div>
            <div style="background-color: #E5E7EB; border-radius: 8px; width: 100%; height: 30px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                <div style="background-color: #3B82F6; width: {pre}%; height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: bold;">
                </div>
            </div>
        </div>
        <div style="margin-bottom: 30px; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 600; color: #111827;">Son Test (Aşama 3)</span>
                <span style="font-weight: 600; color: #111827;">{post}%</span>
            </div>
            <div style="background-color: #E5E7EB; border-radius: 8px; width: 100%; height: 30px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                <div style="background-color: #10B981; width: {post}%; height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: bold;">
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
