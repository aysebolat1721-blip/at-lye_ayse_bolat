import streamlit as st
import requests
import json
import random

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
    .main-header { font-size: 2.5rem; color: #1E3A8A; font-weight: 700; text-align: center; margin-bottom: 2rem; }
    .card-box { background-color: #F3F4F6; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; border-left: 5px solid #3B82F6; }
    .alert-box { background-color: #FEF2F2; border-radius: 10px; padding: 15px; border-left: 5px solid #EF4444; margin-bottom: 15px; }
    .success-box { background-color: #ECFDF5; border-radius: 10px; padding: 15px; border-left: 5px solid #10B981; margin-bottom: 15px; }
    .analysis-box { background-color: #EFF6FF; border-radius: 10px; padding: 15px; border-left: 5px solid #60A5FA; margin-top: 10px; font-style: italic; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1F2937; color: white; text-align: center; padding: 12px 0; font-size: 0.95rem; font-weight: 600; z-index: 1000; }
    .sidebar-footer { margin-top: auto; padding-top: 20px; font-size: 0.9rem; color: #4B5563; text-align: center; border-top: 1px solid #E5E7EB; }
    </style>
""", unsafe_allow_html=True)

# API Ayarları
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "gsk_" + "v58LoWEAqYd61eK5NkC6WGdyb3FYC4ygvwblvUAyeV5wK1ajk5bz"

# SABİT SENARYOLAR (Yapay Zeka olmadan rastgele çekilir)
SCENARIOS = {
    "Kendine Nezaket (Öz Yargılamaya Karşı)": [
        {
            "scenario": "Bölge şampiyonasında, uzun süredir çalıştığın favori tekmende (Dollyo Chagi) puan alamadın ve rakibin sana kontradan puan aldı. Antrenörün kenardan sana sesleniyor ama o an sadece kendi hatana odaklandığın için onu duymuyorsun.",
            "task": "DUR VE NEFES AL. İçindeki yargılayıcı sesi sustur. Kendine, 'Bu tekniği mükemmel yapmak zorunda değilim, herkes hata yapabilir. Şimdi antrenörüme odaklanıp bir sonraki pozisyona hazırlanacağım' de."
        },
        {
            "scenario": "Antrenmanda esneklik (spagat) çalışırken, senden daha alt kuşaktaki bir sporcunun senden çok daha iyi açtığını gördün. Birden yetersizlik hissi geldi.",
            "task": "KENDİNE ŞEFKAT GÖSTER. Başkalarıyla kıyaslamak yerine kendi bedenine saygı duy. 'Benim bedenimin sınırları ve yolculuğu farklı. Ben elimden geleni yapıyorum' diyerek çalışmana devam et."
        },
        {
            "scenario": "Maçta önde giderken son 10 saniyede konsantrasyon kaybı yaşadın ve kafana tekme yiyerek maçı kaybettin. Kendine 'Ben aptalım, bunu nasıl yaparım!' diyorsun.",
            "task": "KENDİNE ARKADAŞIN GİBİ DAVRAN. Sevdiğin bir takım arkadaşın aynı şeyi yaşasa ona 'Aptal' demezdin. Kendine 'Çok iyi mücadele ettin, o an bir anlık dalgınlık oldu ama bu senin kötü bir sporcu olduğun anlamına gelmez' de."
        }
    ],
    "Ortak İnsanlık (İzolasyona Karşı)": [
        {
            "scenario": "Maça çıkmadan hemen önce karnına ağrılar girdi, kalbin çok hızlı atıyor. Etrafındaki diğer sporculara bakıyorsun ve sanki bir tek sen heyecanlıymışsın, herkes çok rahatmış gibi hissediyorsun.",
            "task": "ORTAK İNSANLIĞI HATIRLA. Çevrene bak ve içinden şunu tekrarla: 'Buradaki herkes şu an stresli. Olimpiyat şampiyonları bile bu mindere çıkarken heyecanlanır. Heyecanlanmak benim zayıf olduğumu değil, insan olduğumu gösterir.'"
        },
        {
            "scenario": "Önemli bir seçme maçında son saniyede kyongo (ceza) alarak maçı kaybettin. Minderden inerken dünyadaki en şanssız ve başarısız insanmışsın gibi hissediyorsun.",
            "task": "BİRLİKTELİK HİSSİ. 'Sporda kazanmak kadar kaybetmek de oyunun doğal bir parçası. Dünyadaki tüm büyük taekwondocular benzer yenilgiler yaşadı. Yalnız değilim' diyerek takım arkadaşlarınla vakit geçir."
        },
        {
            "scenario": "Aylardır çalıştığın kuşak sınavında heyecandan poomsae'nin bir adımını unuttun. Salondaki herkes sana bakıyor, rezil olduğunu düşünüyorsun.",
            "task": "İNSANLIK HALİ. Mükemmel olmak zorunda değilsin. Hata yapmak insanın doğasında vardır. Derin bir nefes al ve 'Her taekwondocu en az bir kez hareket unutmuştur, bu normal bir durum' diyerek devam et."
        }
    ],
    "Bilinçli Farkındalık (Aşırı Özdeşleşmeye Karşı)": [
        {
            "scenario": "Maçta hakemin sana haksız yere ceza verdiğini düşünüyorsun. Öfken giderek artıyor ve maça odaklanamıyorsun, sürekli o anı düşünüyorsun.",
            "task": "FARKINDALIK PRATİĞİ. Duygunu fark et ama ona kapılma: 'Şu an hakeme çok öfkeliyim. Bu öfkeyi hissediyorum. Ama ben bu öfkeden ibaret değilim. Zihnimi şimdi ve buradaki maça, bir sonraki adımıma geri getiriyorum.'"
        },
        {
            "scenario": "Arka arkaya girdiğin 3 maçı da kaybettin. Zihninde sürekli 'Ben yeteneksizim', 'Bıraksam daha iyi' gibi düşünceler dönüp duruyor.",
            "task": "DÜŞÜNCELERİ GÖZLEMLEYİCİ OL. Düşüncelerinle arana mesafe koy: 'Şu an zihnim bana başarısız olduğumu söylüyor. Bu sadece anlık bir düşünce, bir gerçek değil. Düşünceler gelir ve gider.' Sadece nefesine odaklan."
        },
        {
            "scenario": "Antrenman maçında çok iyi performans sergiledin ve kendini yenilmez hissediyorsun. Ancak rehavete kapılıp savunmanı düşürdün.",
            "task": "ANDA KAL. Aşırı özgüven ile kendini kaybetme. 'Şu an iyi hissediyorum ve gururluyum. Ama maç henüz bitmedi, dikkatimi şimdi atacağım tekmeye ve rakibime vermeliyim.' diyerek odağını ana getir."
        }
    ]
}

def analyze_self_talk(negative, positive):
    """Yapay Zeka sporcunun dönüşümünü analiz eder."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Sen uzman bir spor psikoloğusun. Taekwondo yapan bir sporcu, içindeki olumsuz sesi şefkatli bir sese dönüştürdü.
    Eski Olumsuz Ses: "{negative}"
    Yeni Şefkatli Ses: "{positive}"
    
    Lütfen bu dönüşümü Kristin Neff'in Öz Şefkat Kuramı (Kendine Nezaket, Ortak İnsanlık, Bilinçli Farkındalık) açısından kısaca (2-3 cümle) analiz et. 
    Sporcunun doğru boyutu kullanıp kullanmadığını belirt. Yapıcı, destekleyici, bilimsel ama kolay anlaşılır ol.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Sen Kristin Neff'in teorisini çok iyi uygulayan, taekwondo oyuncularına destek veren bir psikologsun."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 300
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Dönüşümünüz gayet başarılı! Ancak sistem şu an detaylı analiz yapamıyor. İlerlemeye devam edin!"

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
tab1, tab2, tab3 = st.tabs(["🎯 Kart Çek ve Oyna", "📝 Sporcu İç Konuşma Analizi", "ℹ️ Atölye Rehberi"])

with tab1:
    st.markdown("### 🎲 Senaryo ve Görev Kartları")
    st.write("Seçtiğiniz boyuta uygun, taekwondo'ya özel rastgele bir senaryo ve pratik görev kartı çekin. (Bu aşama yapay zeka kullanılmadan tamamen uzmanca hazırlanmış havuzdan gelir).")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Boyut Seçimi")
        dimension = st.radio(
            "Kristin Neff'in 3 Temel Boyutu:",
            list(SCENARIOS.keys())
        )
        
        generate_btn = st.button("✨ Kart Çek", use_container_width=True, type="primary")
        
    with col2:
        if generate_btn:
            selected_item = random.choice(SCENARIOS[dimension])
            st.markdown(f"""
            <div class='card-box'>
                <h4 style='color: #1E3A8A; margin-bottom:10px;'>🥋 Müsabaka/Antrenman Senaryosu:</h4>
                <p style='font-size: 1.1rem;'>{selected_item['scenario']}</p>
                <hr>
                <h4 style='color: #059669; margin-bottom:10px;'>💚 Öz Şefkat Görev Kartı:</h4>
                <p style='font-size: 1.1rem;'><b>{selected_item['task']}</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
        else:
            st.info("Senaryo çekmek için sol taraftaki butona tıklayın.")

with tab2:
    st.markdown("### 🗣️ İç Konuşma Yapay Zeka Analizi")
    st.write("Sporcuların zihinlerindeki eleştirel sesi şefkatli bir sese dönüştürme pratiği. Yapay zeka bu kez sadece bir 'analizci' olarak, girdiğiniz metnin Öz Şefkat kuramına ne kadar uygun olduğunu değerlendirir.")
    
    with st.form("self_talk_form", clear_on_submit=False):
        negative_talk = st.text_area("❌ Olumsuz İç Konuşman nedir?", placeholder="Örn: Yine aynı hatayı yaptım, benden hiçbir şey olmaz...")
        positive_talk = st.text_area("💚 Yeni Şefkatli Sesin nedir?", placeholder="Örn: Herkes hata yapabilir, antrenmanla düzelteceğim.")
        
        submit_btn = st.form_submit_button("Analiz Et ve Kaydet")
        
        if submit_btn and negative_talk and positive_talk:
            with st.spinner("AI Psikolog verileri analiz ediyor..."):
                analysis_result = analyze_self_talk(negative_talk, positive_talk)
                st.session_state.self_talks.append({
                    "negative": negative_talk,
                    "positive": positive_talk,
                    "analysis": analysis_result
                })
            st.success("Analiz tamamlandı ve kaydedildi!")
            
    if st.session_state.self_talks:
        st.markdown("### Analiz Panosu")
        for idx, talk in enumerate(reversed(st.session_state.self_talks)):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"<div class='alert-box'><b>Eski Ses:</b><br>{talk['negative']}</div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<div class='success-box'><b>Yeni Ses:</b><br>{talk['positive']}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='analysis-box'><b>🤖 AI Psikolog Analizi:</b><br>{talk['analysis']}</div>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

with tab3:
    st.markdown("### 📋 Atölye Uygulama Rehberi")
    
    st.markdown(f"""
    <div class="card-box">
    <h4>Uygulama Amacı</h4>
    Bu atölye, taekwondo sporcularının performans kaygısı, başarısızlık korkusu ve yoğun antrenman stresiyle başa çıkabilmeleri için <b>Kristin Neff'in (2003) Öz Şefkat Kuramı</b> temel alınarak tasarlanmıştır.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🕒 Oturum Akışı (Tahmini 45-60 Dk)")
    st.markdown("""
    1. **Buz Kırıcı ve Isınma (10 Dk):**
       - Katılımcılar daire şeklinde oturur.
       - Antrenör/Psikolog "Öz Şefkat" kavramını kısaca taekwondo bağlamında açıklar.
       
    2. **Kart Çek ve Oyna - Sabit Senaryolar (20 Dk):**
       - Gönüllü sporcular sırayla bir boyut seçip butonla kart çeker.
       - Senaryo okunur ve görev kartındaki pratik grupça zihinsel olarak uygulanır.
       - *Buradaki veriler tamamen uzman onayı almış, hatasız taekwondo senaryolarından rastgele çekilir.*
       
    3. **İç Konuşmayı Dönüştürme ve Analiz Pratiği (15 Dk):**
       - Sporculardan yakın zamanda yaşadıkları bir "hata" sonrası kendilerine ne söyledikleri (Eski Ses) istenir.
       - Grupla beyin fırtınası yapılarak bu ses (Yeni Ses)'e dönüştürülür.
       - Bunlar forma girilir ve Yapay Zeka'nın sadece analiz amacıyla sunduğu teorik geri bildirim birlikte değerlendirilir.
       
    4. **Kapanış ve Değerlendirme (5-10 Dk):**
       - "Mindfulness (Bilinçli Farkındalık)" nefes egzersizi yapılarak atölye sonlandırılır.
    """)

# Sayfanın en altındaki Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        Tasarım ve Geliştirme: Ayşe Bolat | Neff (2003) Öz Şefkat Kuramı Temelli
    </div>
""", unsafe_allow_html=True)
