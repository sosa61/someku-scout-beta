import streamlit as st
from supabase import create_client, Client
import urllib.parse
import pandas as pd
import random
import time
import re
import json
import streamlit.components.v1 as components
import unicodedata

# --- 1. SİSTEM AYARLARI (EN ÜSTTE) ---
st.set_page_config(page_title="SOMEKU ELITE PRO", layout="wide", page_icon="💎")

# Kasa Anahtarları (Supabase)
URL = "https://iwgowefraytdbcdgeqdz.supabase.co"
KEY = "sb_publishable_NHESQOd8-v3tYpVPcz88-w_vypIPQ8Z"

if 'supabase' not in st.session_state:
    st.session_state.supabase = create_client(URL, KEY)
supabase = st.session_state.supabase

# Oturum kutularını tanımla (Hata Engelleyici)
FOR_KEYS = {
    'authenticated': False, 
    'user': None, 
    'is_vip': False, 
    'menu': "🔍 Scout", 
    'page': 0, 
    'fav_list': [],
    'show_intro': True # Giriş animasyonunu kontrol eder
}
for key, val in FOR_KEYS.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. ELITE BLUE UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #010409 !important; border-right: 1px solid #30363d; }
    
    /* Premium Butonlar */
    div.stButton > button {
        background: linear-gradient(90deg, #1f6feb 0%, #58a6ff 100%) !important;
        color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(31, 111, 235, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GİRİŞ VE KAYIT SİSTEMİ ---
if not st.session_state.authenticated:
    st.markdown('<h1 style="text-align:center; color:#58a6ff;">💎 SOMEKU ELITE PRO</h1>', unsafe_allow_html=True)
    
    auth_tab = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with auth_tab[0]: # GİRİŞ
        with st.form("login"):
            u_id = st.text_input("Kullanıcı Adı")
            u_pw = st.text_input("Şifre", type="password")
            if st.form_submit_button("SİSTEME BAĞLAN", use_container_width=True):
                if u_id == "someku" and u_pw == "28616128Ok":
                    st.session_state.update({"authenticated": True, "user": u_id, "is_vip": True, "show_intro": True})
                    st.rerun()
                else:
                    try:
                        res = supabase.table("users").select("*").eq("username", u_id).eq("password", u_pw).execute()
                        if res.data:
                            st.session_state.update({"authenticated": True, "user": u_id, "is_vip": bool(res.data[0].get("is_vip", False)), "show_intro": True})
                            st.rerun()
                        else: st.error("❌ Hatalı Kimlik!")
                    except: st.error("⚠️ Sunucu bağlantı hatası.")

    with auth_tab[1]: # KAYIT
        with st.form("register"):
            n_user = st.text_input("Yeni Kullanıcı Adı")
            n_email = st.text_input("E-posta")
            n_pw = st.text_input("Yeni Şifre", type="password")
            if st.form_submit_button("HESAP OLUŞTUR", use_container_width=True):
                if n_user and n_email and n_pw:
                    check = supabase.table("users").select("*").eq("username", n_user).execute()
                    if check.data: st.error("❌ Bu isim alınmış!")
                    else:
                        supabase.table("users").insert({"username": n_user, "email": n_email, "password": n_pw, "is_vip": False, "puan": 0}).execute()
                        st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
    st.stop()

# --- 4. GİRİŞ VİDEO ANİMASYONU (4 SANİYE) ---
if st.session_state.show_intro:
    intro_html = f"""
    <div id="intro" style="position:fixed; top:0; left:0; width:100%; height:100%; background:#0d1117; z-index:9999; display:flex; flex-direction:column; justify-content:center; align-items:center; color:white; font-family:'Inter', sans-serif;">
        <video autoplay muted playsinline style="width:200px; height:200px;">
            <source src="https://icons8.com/animated-icons/formats/mp4/detective/512" type="video/mp4">
        </video>
        <h1 style="color:#58a6ff; margin-top:20px; font-size:40px; text-shadow: 0 0 15px rgba(88,166,255,0.5);">SOMEKU ELITE PRO</h1>
        <p style="color:#8b949e; font-size:18px;">🕵️‍♂️ Hoş geldin, {st.session_state.user}. Sistem yükleniyor...</p>
    </div>
    <script>
        setTimeout(function(){{
            document.getElementById('intro').style.display = 'none';
        }}, 4000);
    </script>
    """
    components.html(intro_html, height=1000) # HTML2 canvas kullanmadan direkt video/mp4 ile yapıldı
    time.sleep(4.2) # Streamlit'in arkada beklemesi için
    st.session_state.show_intro = False # Bir daha gösterme
    st.rerun() # Gerçek Scout sayfasına geç

# --- 5. PROFESYONEL YAN MENÜ ---
with st.sidebar:
    st.markdown(f"<div style='text-align:center;'><h2 style='color:#58a6ff;'>ELITE PRO</h2><p style='color:#8b949e;'>Hoş geldin, {st.session_state.user}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Menü seçeneklerini senin 900 satırlık kodunla tam uyumlu yapıyoruz
    menu_options = {
        "🔍 Scout Merkezi": "tabs[0]",
        "🎰 Wonderkid Ruleti": "tabs[1]",
        "🏟️ Taktik Tahtası": "tabs[2]",
        "⭐ Favorilerim": "tabs[3]",
        "🎯 Avcı Modu": "tabs[4]",
        "🛡️ Yönetim": "tabs[6]"
    }
    
    # Eğer admin değilse Yönetim seçeneğini listeden çıkar
    if st.session_state.user != "someku":
        if "🛡️ Yönetim" in menu_options: del menu_options["🛡️ Yönetim"]

    for item, tab_key in menu_options.items():
        if st.button(item, use_container_width=True, type="primary" if st.session_state.menu == item else "secondary"):
            st.session_state.menu = item
            st.session_state.page = 0 # Sayfayı sıfırla
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Güvenli Çıkış", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.show_intro = True # Çıkınca animasyonu sıfırla
        st.rerun()

# --- 6. DİNAMİK İÇERİK (SADECE SEÇİLEN SAYFA) ---
m = st.session_state.menu

# Hata ve Donma Engelleyici: Sahte tabs nesneleri oluşturuyoruz
# Bu sayede alt taraftaki with tabs[0] kodların hata vermez ama sadece seçili menü çalışır.
class FakeTab:
    def __init__(self, is_active): self.is_active = is_active
    def __enter__(self):
        if not self.is_active:
            st.stop() # Seçili değilse kodun geri kalanını ASLA okuma (Donmayı engelleyen kısım)
        return st.container()
    def __exit__(self, *args): pass

# 900 satırlık kodun hata vermemesi için 'tabs' listesini kuruyoruz
# Sidebar'daki menu_options sırasıyla tabs[0], tabs[1] vb. eşleşir.
tabs = []
options_list = list(menu_options.keys())
for item in options_list:
    tabs.append(FakeTab(m == item))

# --- 7. SAYFA İÇERİKLERİ ---
# Buradan aşağıda senin 900 satırlık kodun başlıyor.
# 'with tabs[0]:' satırına geldiğinde, eğer '🔍 Scout Merkezi' seçili değilse 
# 'st.stop()' sayesinde o bloğun geri kalanı hiç okunmayacak ve site kasmayacak.

# --- 1. SCOUT ---
with tabs[0]:
    POS_TR = {"Hepsi": "Hepsi", "Kaleci": "GK", "Stoper": "D C", "Sol Bek": "D L", "Sağ Bek": "D R", "Ön Libero": "DM", "Merkez Orta Saha": "M C", "Sol Kanat": "AM L", "Sağ Kanat": "AM R", "Ofansif Orta Saha": "AM C", "Forvet": "ST"}
    REG_TR = {"Hepsi": [], "Avrupa": ["Türkiye", "Almanya", "Fransa", "İngiltere", "İtalya", "İspanya", "Hollanda", "Portekiz", "Belçika", "Avusturya", "İsviçre"], "Kuzey Avrupa": ["Norveç", "İsveç", "Danimarka", "Finlandiya", "İzlanda"], "Balkanlar": ["Hırvatistan", "Sırbistan", "Yunanistan", "Bulgaristan", "Slovenya", "Bosna Hersek", "Romanya"], "Güney Amerika": ["Brezilya", "Arjantin", "Uruguay", "Kolombiya", "Ekvador", "Şili", "Paraguay"], "Afrika": ["Nijerya", "Senegal", "Mısır", "Fildişi Sahili", "Fas", "Cezayir", "Gana", "Kamerun"], "Asya": ["Japonya", "Güney Kore", "Suudi Arabistan", "Katar", "Avustralya", "Çin"]}
    
    curr_user = st.session_state.user
    f1, f2, f3 = st.columns(3)
    with f1: 
        name_f = st.text_input("👤 Oyuncu Ara:")
        team_f = st.text_input("Takım Ara:")
    with f2: 
        reg_f = st.selectbox("🌍 Bölge Seç:", list(REG_TR.keys()))
        country_f = st.text_input("Uyruk (Direkt Ülke):")
    with f3: 
        sort_f = st.selectbox("🔃 Sıralama Ölçütü:", ["pa", "ca", "yas"]) 
        sort_dir = st.selectbox("↕️ Sıralama Yönü:", ["En Yüksek / En Büyük", "En Düşük / En Küçük"])
    
    v1, v2, v3 = st.columns(3)
    with v1: age_f = st.slider("🎂 Yaş Aralığı:", 14, 50, (14, 25))
    with v2: pa_f = st.slider("📊 PA Aralığı:", 100, 200, (135, 200))
    with v3: val_f = st.slider("💰 Bütçe (Milyon £):", 0, 300, (0, 300))
    
    is_descending = True if sort_dir == "En Yüksek / En Büyük" else False

    f_res = supabase.table("favoriler").select("oyuncu_adi").eq("kullanici_adi", curr_user).execute()
    st.session_state.fav_list = [x['oyuncu_adi'] for x in f_res.data] if f_res.data else []

    query = supabase.table("oyuncular").select("*")\
        .gte("yas", age_f[0]).lte("yas", age_f[1])\
        .gte("pa", pa_f[0]).lte("pa", pa_f[1])

    if name_f: query = query.ilike("oyuncu_adi", f"%{name_f}%")
    if team_f: query = query.ilike("kulup", f"%{team_f}%")
    if country_f: query = query.ilike("ulke", f"%{country_f}%")
    
    pos_f = st.selectbox("👟 Mevki Seç:", list(POS_TR.keys()))
    if pos_f != "Hepsi": query = query.ilike("mevki", f"%{POS_TR[pos_f]}%")
    if reg_f != "Hepsi": query = query.in_("ulke", REG_TR[reg_f])
    
    # Bütçe filtresi için daha geniş veri çekiyoruz (Filtreleme kod tarafında kesinleşecek)
    res = query.order(sort_f, desc=is_descending).limit(500).execute()
    
    if res.data:
        def get_numeric_value(val_str):
            try:
                # Sayıyı temizle ve float'a çevir
                s = str(val_str).lower().replace('£','').replace('€','').replace(',','').strip()
                match = re.search(r"(\d+\.?\d*)", s)
                if not match: return 0
                num = float(match.group(1))
                if 'm' in s: return num
                if 'k' in s: return num / 1000
                if num > 1000: return num / 1000000 # Eğer ham sayı gelirse
                return num
            except: return 0

        # --- KESİN FİLTRELEME ---
        filtered_data = [p for p in res.data if val_f[0] <= get_numeric_value(p.get('deger', 0)) <= val_f[1]]
        
        # Sayfalama mantığı (Geniş listeden seçilen sayfa)
        start_idx = st.session_state.page * 12
        display_data = filtered_data[start_idx : start_idx + 12]

        if not display_data and st.session_state.page > 0:
            st.session_state.page = 0
            st.rerun()

        cols = st.columns(2)
        user_is_vip = st.session_state.get('is_vip', False)
        for i, p in enumerate(display_data):
            is_fav = p['oyuncu_adi'] in st.session_state.fav_list
            tm_url = f"https://www.transfermarkt.com.tr/schnellsuche/ergebnis/schnellsuche?query={urllib.parse.quote(p['oyuncu_adi'])}"
            pa_val, ca_val = p.get("pa", 0), p.get("ca", "-")
            
            # --- 300M VE ÜSTÜNÜ SATILAMAZ YAP ---
            current_val_num = get_numeric_value(p.get('deger', 0))
            if current_val_num >= 300:
                display_val = "❌ Satılamaz"
            else:
                display_val = p.get('deger', 'Bilinmiyor')

            with cols[i%2]:
                if pa_val > 150 and not user_is_vip:
                    st.markdown(f'''<div style="padding:15px; border-radius:12px; margin-bottom:10px; border: 2px dashed #f2cc60; background: rgba(242, 204, 96, 0.05); text-align:center;"><span style="background:#f2cc60; color:black; padding:2px 8px; border-radius:5px; font-size:10px; font-weight:bold;">💎 ELİT YETENEK KİLİTLİ</span><h4 style="margin:10px 0; color:#8b949e;">🔒 Gizli Yıldız</h4><p style="font-size:12px; color:#8b949e;">PA: <b>{pa_val}</b> olan bu oyuncunun detayları için VIP üye olmalısın.</p><a href="https://www.shopier.com/fmscout/45690641" target="_blank" style="display:inline-block; background:#238636; color:white; padding:8px 15px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:13px;">KİLİDİ AÇ</a></div>''', unsafe_allow_html=True)
                else:
                    card_border = "#238636" if is_fav else "#30363d"
                    bg_effect = "rgba(35, 134, 54, 0.08)" if is_fav else "rgba(255, 255, 255, 0.02)"
                    st.markdown(f'''<div style="padding:15px; border-radius:15px; margin-bottom:10px; border: 2px solid {card_border}; background: {bg_effect}; position:relative;"><div style="display:flex; justify-content:space-between;"><div><h4 style="margin:0; font-size:16px;">{p["oyuncu_adi"]}</h4><p style="font-size:11px; color:#8b949e; margin:2px 0;">🌍 {p.get("ulke","Bilinmiyor")} | 🎂 {p["yas"]} Yaş</p></div><div style="text-align:right;"><span style="background:#238636; color:white; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:bold;">PA: {p["pa"]}</span><p style="font-size:10px; color:#58a6ff; margin-top:3px;">CA: {ca_val}</p></div></div><div style="border-top:1px solid #30363d; margin-top:10px; padding-top:10px; font-size:12px;"><p style="margin:0;">🏟️ <b>Kulüp:</b> {p.get("kulup","Serbest")}</p><p style="margin:0;">👟 <b>Mevki:</b> {p.get("mevki", "--")}</p><p style="margin:0; color:#00ff41;">💰 <b>Değer:</b> {display_val}</p></div><div style="margin-top:10px;"><a href="{tm_url}" target="_blank" style="color:#58a6ff; font-size:11px; text-decoration:none; font-weight:bold;">Transfermarkt Profili ➔</a></div></div>''', unsafe_allow_html=True)
                    btn_txt = "⭐ FAVORİDEN ÇIKAR" if is_fav else "☆ FAVORİLERE EKLE"
                    if st.button(btn_txt, key=f"scout_btn_{p['oyuncu_adi']}_{i}", use_container_width=True):
                        if is_fav: supabase.table("favoriler").delete().eq("oyuncu_adi", p['oyuncu_adi']).eq("kullanici_adi", curr_user).execute()
                        else: supabase.table("favoriler").insert({"oyuncu_adi": p['oyuncu_adi'], "kulup": p.get('kulup', 'Serbest'), "pa": p['pa'], "mevki": p['mevki'], "ca": p.get('ca', 0), "kullanici_adi": curr_user}).execute()
                        st.rerun()
        
        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("⬅️ Geri", use_container_width=True) and st.session_state.page > 0: st.session_state.page -= 1; st.rerun()
        with c2: st.markdown(f"<p style='text-align:center;'>Sayfa: {st.session_state.page + 1}</p>", unsafe_allow_html=True)
        if c3.button("İleri ➡️", use_container_width=True): st.session_state.page += 1; st.rerun()

# --- 2. RULET (V196 - ECONOMY MIX) ---
with tabs[1]:
    st.markdown('<div style="text-align:center;"><h2 style="color:#ef4444;">🎰 WONDERKID RULETİ</h2><p style="color:#8b949e;">Maksimum 21 Yaş | Maksimum 30M Değer</p></div>', unsafe_allow_html=True)
    
    import random
    import json
    import time
    import urllib.parse

    user_is_vip = st.session_state.get('is_vip', False)
    curr_user = st.session_state.get('user')

    # --- RULET AYARLARI ---
    if user_is_vip:
        st.markdown('<div style="text-align:center; padding:10px; background:#f2cc60; color:black; border-radius:15px; font-weight:bold; margin-bottom:15px;">🌟 ALTIN VIP RULET (PA 140-200)</div>', unsafe_allow_html=True)
        min_pa, max_pa = 140, 200
        slot_border = "#f2cc60"
    else:
        st.markdown('<div style="text-align:center; padding:10px; background:#30363d; color:white; border-radius:15px; margin-bottom:15px;">🎰 STANDART RULET (PA 125-150)</div>', unsafe_allow_html=True)
        min_pa, max_pa = 125, 150 
        slot_border = "#30363d"

    if 'rulet_winner' not in st.session_state: st.session_state.rulet_winner = None
    if 'animasyon_tamam' not in st.session_state: st.session_state.animasyon_tamam = False

    # --- TAM KARIŞIK VE GÜVENLİ VERİ ÇEKME ---
    player_pool = []
    try:
        def get_price_num(txt):
            try:
                s = str(txt).lower().replace('£','').replace('€','').strip()
                n = float(re.findall(r"(\d+\.?\d*)", s)[0])
                if 'm' in s: return n
                if 'k' in s: return n / 1000
                return n if n < 1000 else n / 1000000
            except: return 0

        # Rastgele bir sayfadan çekerek tam karışıklık sağlıyoruz
        random_offset = random.randint(0, 100)
        res = supabase.table("oyuncular").select("*").gte("pa", min_pa).lte("pa", max_pa).lte("yas", 21).range(random_offset, random_offset + 150).execute()
        
        if res.data:
            # Sadece değeri 30M ve altı olanları ayıkla
            player_pool = [p for p in res.data if get_price_num(p.get('deger', 0)) <= 30]
            random.shuffle(player_pool)
    except Exception as e:
        st.error("⚠️ Bağlantı hatası, lütfen tekrar dene patron!")

    if player_pool:
        btn_label = "🎰 ALTIN RULETİ ÇEVİR" if user_is_vip else "🎰 STANDART RULETİ ÇEVİR"
        if st.button(btn_label, key="rulet_spin_btn_v196", use_container_width=True):
            winner = random.choice(player_pool)
            strip_players = [random.choice(player_pool) for _ in range(30)]
            strip_players[25] = winner
            
            st.session_state.rulet_winner = winner
            st.session_state.animasyon_tamam = False
            
            players_json = json.dumps(strip_players)
            
            roulette_html = f"""
            <div style="position:relative; width:100%; height:160px; background:#0d1117; border:3px solid {slot_border}; border-radius:15px; overflow:hidden; display:flex; justify-content:center; align-items:center;">
                <div style="position:absolute; width:100%; height:60px; border-top:2px solid {slot_border}; border-bottom:2px solid {slot_border}; background:rgba(242, 204, 96, 0.05); z-index:10;"></div>
                <div id="slot-track" style="display:flex; flex-direction:column; position:absolute; top:0; transition: top 4s cubic-bezier(0.1, 0, 0.1, 1); width:100%;"></div>
            </div>
            <script>
                (function() {{
                    const players = {players_json};
                    const track = document.getElementById('slot-track');
                    const itemH = 60; const contH = 160; const winI = 25;
                    track.innerHTML = players.map(p => `<div style="height:${{itemH}}px; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;"><small style="color:#8b949e; font-size:10px;">${{p.kulup || 'Scout Agent'}}</small><b style="color:white; font-size:13px;">${{p.oyuncu_adi}}</b></div>`).join('');
                    setTimeout(() => {{ track.style.top = "-" + ((winI * itemH) - (contH / 2 - itemH / 2)) + "px"; }}, 100);
                }})();
            </script>
            """
            st.components.v1.html(roulette_html, height=180)
            time.sleep(4.5)
            st.session_state.animasyon_tamam = True
            st.rerun()

        # --- OYUNCU KARTI ---
        if st.session_state.rulet_winner and st.session_state.animasyon_tamam:
            p = st.session_state.rulet_winner
            f_check = supabase.table("favoriler").select("oyuncu_adi").eq("oyuncu_adi", p['oyuncu_adi']).eq("kullanici_adi", curr_user).execute()
            is_fav = len(f_check.data) > 0
            tm_url = f"https://www.transfermarkt.com.tr/schnellsuche/ergebnis/schnellsuche?query={urllib.parse.quote(p['oyuncu_adi'])}"
            card_color = "#22c55e" if is_fav else ("#f2cc60" if user_is_vip else "#ef4444")
            
            st.markdown(f"""
            <div style="background: #111; border: 2px solid {card_color}; border-radius: 20px; padding: 25px; margin-top:20px; position:relative; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                <div style="position:absolute; top:15px; right:15px; text-align:right;">
                    <span style="background:{card_color}; color:#000; padding:2px 8px; border-radius:5px; font-weight:bold; font-size:12px;">{"⭐ FAVORİNDE" if is_fav else "🎰 RULET SONUCU"}</span><br>
                    <span style="color:#fff; font-weight:bold; font-size:18px; display:block; margin-top:5px;">PA: {p['pa']}</span>
                </div>
                <h3 style="margin:0; font-size:22px; color:#fff;">{p['oyuncu_adi']}</h3>
                <hr style="border-top:1px solid #333; margin:15px 0;">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; color:#ccc; font-size:14px;">
                    <div>🌍 <b>Ülke:</b> {p.get('ulke','-')}</div>
                    <div>🏟️ <b>Kulüp:</b> {p.get('kulup','Serbest')}</div>
                    <div>👟 <b>Mevki:</b> {p.get('mevki','-')}</div>
                    <div>🎂 <b>Yaş:</b> {p.get('yas','-')}</div>
                    <div style="grid-column: span 2; color:#00ff41; font-weight:bold; font-size:16px; margin-top:5px;">💰 Değer: {p.get('deger','-')}</div>
                </div>
                <div style="margin-top:20px;">
                    <a href="{tm_url}" target="_blank" style="text-decoration:none; color:#58a6ff; font-weight:bold; font-size:13px;">Transfermarkt Profili ➔</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not is_fav:
                if st.button("⭐ FAVORİLERİME EKLE", key=f"fav_btn_rulet_{p['oyuncu_adi']}", use_container_width=True):
                    supabase.table("favoriler").insert({"oyuncu_adi": p['oyuncu_adi'], "kulup": p.get('kulup','Serbest'), "pa": p['pa'], "mevki": p['mevki'], "kullanici_adi": curr_user}).execute()
                    st.toast("Mermi listeye eklendi!")
                    st.rerun()
            else:
                st.info("✅ Bu oyuncu zaten favori listende patron.")
    else:
        st.warning("⚠️ Kriterlere uygun ucuz wonderkid bulunamadı. Tekrar dene!")

# --- 3. İLK 11 (V185 - CENTRAL SEARCH & TR POS) ---
with tabs[2]:
    st.markdown('<h2 style="text-align:center;">🏟️ ELITE ARENA - TAKTİK TAHTASI</h2>', unsafe_allow_html=True)
    
    curr_user = st.session_state.get('user')
    
    # --- MERKEZİ ARAMA MOTORU ---
    st.markdown("### 🔍 Oyuncu Bul ve Kadroya Kat")
    search_input = st.text_input("Transfer Etmek İstediğin Oyuncuyu Yaz:", placeholder="Örn: Uğurcan, Onana, Muslera...", key="global_search")
    
    # Favorileri çek
    fav_res = supabase.table("favoriler").select("oyuncu_adi, pa").eq("kullanici_adi", curr_user).execute()
    fav_list = [f"⭐ {p['oyuncu_adi']} ({p['pa']})" for p in fav_res.data] if fav_res.data else []
    
    # Arama sonuçlarını çek
    search_pool = ["Boş Slot"] + fav_list
    if search_input and len(search_input) > 1:
        search_res = supabase.table("oyuncular").select("oyuncu_adi, pa").ilike("oyuncu_adi", f"%{search_input}%").limit(50).execute()
        if search_res.data:
            search_pool += [f"{p['oyuncu_adi']} ({p['pa']})" for p in search_res.data]
    
    st.info("💡 Yukarıdaki kutuya ismi yazın, aşağıdaki mevkilerde o ismi seçin!")

    tactic = st.selectbox("🏟️ Ana Diziliş Seç:", 
                         ["4-3-3", "4-4-2", "4-2-3-1", "3-5-2", "5-3-2", "5-4-1", "3-4-3", "4-1-2-1-2"], key="tactic_sel")

    # Mevki Seçim Fonksiyonu (Merkezi havuzu kullanır)
    def pick_player(label, key):
        return st.selectbox(label, search_pool, key=f"tact_{key}")

    positions = []
    
    # --- DİZİLİŞ VE KOORDİNAT SİSTEMİ (TÜRKÇE MEVKİLER) ---
    if tactic == "4-4-2":
        c1, c2, c3, c4, c5 = st.columns(5)
        gk = pick_player("KL", "gk"); lb = pick_player("SLB", "lb"); cb1 = pick_player("STP1", "cb1"); cb2 = pick_player("STP2", "cb2"); rb = pick_player("SĞB", "rb")
        m1, m2, m3, m4 = st.columns(4)
        lm = pick_player("SLK", "lm"); cm1 = pick_player("MZS1", "cm1"); cm2 = pick_player("MZS2", "cm2"); rm = pick_player("SĞK", "rm")
        f1, f2 = st.columns(2)
        st1 = pick_player("FRV1", "st1"); st2 = pick_player("FRV2", "st2")
        positions = [("KL",gk,82,39), ("SLB",lb,65,2), ("STP",cb1,65,26), ("STP",cb2,65,51), ("SĞB",rb,65,75), ("SLK",lm,40,2), ("MZS",cm1,40,26), ("MZS",cm2,40,51), ("SĞK",rm,40,75), ("FRV",st1,13,26), ("FRV",st2,13,51)]

    elif tactic == "5-3-2":
        c1, c2, c3, c4, c5 = st.columns(5)
        gk = pick_player("KL", "gk"); lb = pick_player("SLB", "lb"); cb1 = pick_player("STP1", "cb1"); cb2 = pick_player("STP2", "cb2"); cb3 = pick_player("STP3", "cb3"); rb = pick_player("SĞB", "rb")
        m1, m2, m3 = st.columns(3)
        cm1 = pick_player("MZS1", "cm1"); cdm = pick_player("ÖNL", "cdm"); cm2 = pick_player("MZS2", "cm2")
        f1, f2 = st.columns(2)
        st1 = pick_player("FRV1", "st1"); st2 = pick_player("FRV2", "st2")
        positions = [("KL",gk,85,39), ("SLB",lb,68,2), ("STP",cb1,70,22), ("STP",cb2,70,39), ("STP",cb3,70,56), ("SĞB",rb,68,75), ("MZS",cm1,45,15), ("ÖNL",cdm,52,39), ("MZS",cm2,45,63), ("FRV",st1,15,26), ("FRV",st2,15,51)]

    elif tactic == "4-2-3-1":
        c1, c2, c3, c4, c5 = st.columns(5)
        gk = pick_player("KL", "gk"); lb = pick_player("SLB", "lb"); cb1 = pick_player("STP1", "cb1"); cb2 = pick_player("STP2", "cb2"); rb = pick_player("SĞB", "rb")
        m1, m2, m3, m4, m5 = st.columns(5)
        cdm1 = pick_player("ÖNL1", "dm1"); cdm2 = pick_player("ÖNL2", "dm2"); aml = pick_player("SLK", "aml"); amc = pick_player("OOS", "amc"); amr = pick_player("SĞK", "amr")
        st1 = st.selectbox("FRV", search_pool, key="tact_st1")
        positions = [("KL",gk,82,39), ("SLB",lb,65,2), ("STP",cb1,65,26), ("STP",cb2,65,51), ("SĞB",rb,65,75), ("ÖNL",cdm1,52,26), ("ÖNL",cdm2,52,51), ("SLK",aml,28,5), ("OOS",amc,25,39), ("SĞK",amr,28,72), ("FRV",st1,8,39)]

    else: # Default 4-3-3
        c1, c2, c3, c4, c5 = st.columns(5)
        gk = pick_player("KL", "gk"); lb = pick_player("SLB", "lb"); cb1 = pick_player("STP1", "cb1"); cb2 = pick_player("STP2", "cb2"); rb = pick_player("SĞB", "rb")
        m1, m2, m3 = st.columns(3)
        cm1 = pick_player("MZS1", "cm1"); cm2 = pick_player("MZS2", "cm2"); cm3 = pick_player("MZS3", "cm3")
        f1, f2, f3 = st.columns(3)
        lw = pick_player("SLK", "lw"); st1 = pick_player("FRV", "st1"); rw = pick_player("SĞK", "rw")
        positions = [("KL",gk,82,39), ("SLB",lb,65,2), ("STP",cb1,65,26), ("STP",cb2,65,51), ("SĞB",rb,65,75), ("MZS",cm1,43,10), ("MZS",cm2,43,38), ("MZS",cm3,43,66), ("SLK",lw,14,5), ("FRV",st1,11,38), ("SĞK",rw,14,71)]

    # --- HTML SÜRÜKLEME MOTORU ---
    players_divs = "".join([f'<div class="player draggable" style="top:{y}%; left:{x}%;" onmousedown="startDrag(event)" ontouchstart="startDrag(event)"><div class="pos">{p}</div><div class="name">{n.split(" (")[0].replace("⭐ ", "")}</div></div>' for p, n, y, x in positions])

    tahta_html = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <div id="capture" style="position:relative; background:#1e4620; border:4px solid #ffffff; border-radius:15px; width:360px; height:540px; margin:auto; overflow:hidden; background-image: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px); background-size: 20px 20px;">
        <div style="position:absolute; top:50%; left:0; width:100%; border-top:2px solid rgba(255,255,255,0.4);"></div>
        <div style="position:absolute; top:40%; left:30%; width:40%; height:20%; border:2px solid rgba(255,255,255,0.4); border-radius:50%;"></div>
        {players_divs}
        <div style="position:absolute; bottom:5px; right:10px; color:rgba(255,255,255,0.3); font-size:9px; font-weight:bold;">SOMEKU ELITE SCOUT</div>
    </div>
    
    <button onclick="downloadImage()" style="width:100%; padding:14px; background:#238636; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer; margin-top:15px;">📸 KADROYU PNG OLARAK KAYDET</button>

    <script>
        let activeEl = null;
        function startDrag(e) {{
            activeEl = e.target.closest('.draggable');
            document.onmousemove = drag;
            document.ontouchmove = drag;
            document.onmouseup = endDrag;
            document.ontouchend = endDrag;
        }}
        function drag(e) {{
            if (!activeEl) return;
            e.preventDefault();
            let clientX = e.clientX || e.touches[0].clientX;
            let clientY = e.clientY || e.touches[0].clientY;
            let rect = document.getElementById('capture').getBoundingClientRect();
            let x = ((clientX - rect.left - 39) / rect.width) * 100;
            let y = ((clientY - rect.top - 20) / rect.height) * 100;
            activeEl.style.left = Math.max(0, Math.min(x, 80)) + "%";
            activeEl.style.top = Math.max(0, Math.min(y, 90)) + "%";
        }}
        function endDrag() {{ activeEl = null; }}
        function downloadImage() {{
            html2canvas(document.querySelector("#capture")).then(canvas => {{
                let link = document.createElement('a');
                link.download = 'mermi-kadro.png';
                link.href = canvas.toDataURL();
                link.click();
            }});
        }}
    </script>
    <style>
        .player {{ position:absolute; background:rgba(13,17,23,0.95); border:1.5px solid #58a6ff; border-radius:6px; color:white; width:75px; padding:3px; text-align:center; cursor:grab; z-index:100; user-select:none; touch-action:none; }}
        .pos {{ font-size:8px; color:#58a6ff; font-weight:bold; pointer-events:none; }}
        .name {{ font-size:9px; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; pointer-events:none; }}
    </style>
    """
    st.components.v1.html(tahta_html, height=650)

# --- 4. FAVORİLER (KİŞİYE ÖZEL) ---
with tabs[3]:
    st.markdown('<h2 style="text-align:center;">⭐ SENİN FAVORİLERİN</h2>', unsafe_allow_html=True)
    
    # KRİTİK: Sadece giriş yapan kullanıcıya (st.session_state.user) ait olanları çek!
    res = supabase.table("favoriler")\
        .select("*")\
        .eq("kullanici_adi", st.session_state.user)\
        .order("created_at", desc=True)\
        .execute()
        
    if res.data:
        # Favorileri şık kartlar halinde gösterelim
        for p in res.data:
            with st.container():
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-left: 5px solid #238636; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin:0; color: white;">{p['oyuncu_adi']}</h4>
                            <small style="color: #8b949e;">🏟️ {p.get('kulup', 'Serbest')} | 📍 {p.get('mevki', '-')}</small>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: #238636; color: white; padding: 2px 8px; border-radius: 5px; font-size: 12px;">PA: {p['pa']}</span>
                            <span style="background: #1a3151; color: white; padding: 2px 8px; border-radius: 5px; font-size: 12px; margin-left: 5px;">CA: {p.get('ca', '-')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Silme Butonu (Her oyuncunun altına küçük bir buton)
                if st.button(f"🗑️ Sil: {p['oyuncu_adi']}", key=f"del_{p['id']}"):
                    supabase.table("favoriler").delete().eq("id", p['id']).execute()
                    st.success("Mermi listeden çıkarıldı!")
                    st.rerun()
    else:
        st.info("Henüz favori mermin yok. Rulet kısmından avlanmaya başla! 🕵️‍♂️")
        
# --- 5. GİZLİ YETENEK AVI (V540 - KESKİN KURALLAR & NET BÖLGELER) ---
with tabs[4]:
    import unicodedata
    import time
    import random
    st.markdown('<h2 style="text-align:center; color:#f2cc60;">🕵️ GİZLİ YETENEK AVI</h2>', unsafe_allow_html=True)
    
    # --- OYUN KURALLARI ---
    with st.expander("📖 Oyun Kuralları & Analiz Notları", expanded=True):
        st.markdown("""
        1. **Bölgesel Analiz:** Mevki karmaşasını bitirdik. Oyuncular 4 ana bölgede (Hücum, Orta Saha, Savunma, Kaleci) analiz edilir.
        2. **Bonservis Kuralı:** Oyuncu kiralıksa, kiralık gittiği yer değil **asıl ait olduğu kulüp** görünür.
        3. **İpucu Akışı:** Son 10s PA (Potansiyel), son 5s CA (Yetenek) verileri sistemden şak diye açılır.
        4. **Akıllı Tespit:** Harf yazdığın an elit adaylar aşağıya dizilir. Seçtiğin an sistem kutuyu temizler ve teşhisi koyar.
        5. **⚠️ Önemli:** Sistem yapay zeka destekli olduğu için nadiren veri sapmaları olabilir; gerçek bir scout her zaman tetiktedir!
        """)

    # --- YARDIMCI FONKSİYONLAR ---
    def metin_temizle(metin):
        if not metin: return ""
        metin = str(metin).lower().replace('ı', 'i').replace('İ', 'i').strip()
        nfkd_form = unicodedata.normalize('NFKD', metin)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def bolgesel_mevki_yap(m):
        m = str(m).upper()
        # 1. KALECİ
        if "GK" in m: return "🧤 KALECİ"
        
        # 2. HÜCUM BÖLGESİ (Forvetler ve Kanatlar)
        if any(x in m for x in ["ST", "CF", "AM R", "AM L", "MR", "ML", "LW", "RW"]): 
            return "🔥 HÜCUM BÖLGESİ"
        
        # 3. SAVUNMA BÖLGESİ (Stoperler, Bekler ve Liberolar)
        if any(x in m for x in ["D C", "DC", "D R", "DR", "D L", "DL", "SW", "WBR", "WBL"]): 
            return "🛡️ SAVUNMA BÖLGESİ"
        
        # 4. ORTA SAHA BÖLGESİ (Diğer tüm orta saha türevleri)
        return "🧠 ORTA SAHA BÖLGESİ"

    # --- DURUM YÖNETİMİ ---
    if 'game_active' not in st.session_state: st.session_state.game_active = False
    if 'target_p' not in st.session_state: st.session_state.target_p = None
    if 'last_result' not in st.session_state: st.session_state.last_result = None
    if 'input_key' not in st.session_state: st.session_state.input_key = 0

    def yeni_av_tetikle():
        st.session_state.last_result = None
        st.session_state.input_key += 1 # Kutuyu sıfırlamak için anahtarı değiştir
        res_g = supabase.table("oyuncular").select("*").not_.eq("kulup", "None").gte("pa", 165).execute()
        if res_g.data:
            st.session_state.all_player_names = sorted(list(set([r['oyuncu_adi'] for r in res_g.data])))
            st.session_state.target_p = random.choice(res_g.data)
            st.session_state.game_active = True
            st.session_state.game_start_time = time.time()

    # --- BAŞLATMA ---
    if not st.session_state.game_active and st.session_state.last_result is None:
        if st.button("🚀 ANALİZİ BAŞLAT", use_container_width=True):
            yeni_av_tetikle()
            st.rerun()

    # --- OYUN ALANI ---
    if st.session_state.game_active and st.session_state.target_p:
        p = st.session_state.target_p
        kalan = max(0, int(30 - (time.time() - st.session_state.game_start_time)))
        yuzde = (kalan / 30) * 100
        
        if kalan > 0:
            pa_hint = f"🔥 PA: {p['pa']}" if kalan <= 10 else "🔥 PA: ??"
            ca_hint = f"📊 CA: {p.get('ca','?')}" if kalan <= 5 else "📊 CA: ??"
            
            st.markdown(f"""
                <div style="background:#161b22; padding:20px; border-radius:15px; border:2px solid #30363d; text-align:center;">
                    <h2 style="color:#f2cc60; margin:0;">{bolgesel_mevki_yap(p['mevki'])}</h2>
                    <div style="width:100%; background:#333; height:10px; border-radius:10px; margin:10px 0;">
                        <div style="width:{yuzde}%; background:#3b82f6; height:100%; border-radius:10px;"></div>
                    </div>
                    <p style="font-size:20px;">🎂 <b>{p['yas']} Yaş</b> | 🏟️ <b>{p['kulup']}</b></p>
                    <div style="display:flex; justify-content:center; gap:20px; font-weight:bold; font-size:17px;">
                        <span style="color:#f2cc60;">{pa_hint}</span>
                        <span style="color:#58a6ff;">{ca_hint}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.write("")
            query = st.text_input("Hedef ismini yazmaya başla...", key=f"input_{st.session_state.input_key}").strip()
            
            if query:
                matches = [name for name in st.session_state.all_player_names if metin_temizle(query) in metin_temizle(name)][:5]
                
                if matches:
                    st.write("🎯 **Potansiyel Hedefler (Analiz Et):**")
                    for match in matches:
                        if st.button(f"📍 {match}", key=f"btn_{match}", use_container_width=True):
                            st.session_state.input_key += 1 # Kutuyu sıfırla
                            if metin_temizle(match) == metin_temizle(p['oyuncu_adi']):
                                st.session_state.last_result = "WIN"
                                st.session_state.game_active = False
                                try:
                                    c = supabase.table("users").select("puan").eq("username", st.session_state.user).execute()
                                    eski = c.data[0].get("puan", 0) if c.data else 0
                                    supabase.table("users").update({"puan": eski + 1}).eq("username", st.session_state.user).execute()
                                except: pass
                            else:
                                st.error("❌ Yanlış Teşhis! Hedef bu değil.")
                            st.rerun()

            time.sleep(0.5)
            st.rerun()
        else:
            st.session_state.last_result = "LOSE"
            st.session_state.game_active = False
            st.rerun()

    # --- SONUÇ VE GERİ SAYIM ---
    if st.session_state.last_result:
        p = st.session_state.target_p
        if st.session_state.last_result == "WIN":
            st.balloons()
            st.success(f"🎯 HEDEF TESPİT EDİLDİ: {p['oyuncu_adi']}")
        else:
            st.error(f"⌛ VERİ ANALİZİ BAŞARISIZ! Aranan Hedef: {p['oyuncu_adi']}")

        if st.button("🚫 Durdur / Vazgeç"):
            st.session_state.last_result = None
            st.session_state.input_key += 1
            st.rerun()

        placeholder = st.empty()
        for i in range(5, 0, -1):
            placeholder.info(f"🔄 {i} saniye içinde yeni hedef belirlenecek...")
            time.sleep(1)
        
        yeni_av_tetikle()
        st.rerun()




    # --- 5. LİDERLİK TABLOSU (SADE VE GÜVENLİ) ---
    st.subheader("🏆 TOP 10 ELITE SCOUTS")
    try:
        leaders = supabase.table("users").select("username, puan").order("puan", desc=True).limit(10).execute()
        if leaders.data:
            import pandas as pd
            df = pd.DataFrame(leaders.data)
            df.columns = ["SCOUT ADI", "PUAN"]
            df.index = df.index + 1
            st.table(df)
    except:
        st.write("Tablo yüklenemedi.")
        
        
# --- 5. BARROW AI (V730 - BAKIM MODU) ---
with tabs[5]:
    st.markdown('<div style="text-align:center; padding:100px 0;">', unsafe_allow_html=True)
    st.markdown('<h1 style="color:#ef4444; font-size:60px;">🤵</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#fff;">BARROW AI BAKIMDA</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8b949e; font-size:18px;">Patron sistemi bakıma aldı. Barrow çok yakında mermi gibi filtrelerle geri dönecek!</p>', unsafe_allow_html=True)
    st.markdown('<div style="background:#1a1a1a; color:#facc15; padding:10px; border-radius:10px; display:inline-block; border:1px solid #facc15;">⏳ ÇOK YAKINDA YAYINDA</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)



# --- 6. ADMIN (V135 - TAM YETKİLİ YÖNETİM MERKEZİ) ---
with tabs[6]: 
    if st.session_state.get('user') == "someku":
        st.markdown('<h1 style="color:#ff4b4b; text-align:center;">🛡️ YÖNETİM MERKEZİ</h1>', unsafe_allow_html=True)
        
        # --- GENEL İSTATİSTİKLER ---
        try:
            # Kullanıcıları çek
            u_res = supabase.table("users").select("*").execute()
            users_list = u_res.data if u_res.data else []
            
            # Oyuncu sayısını çek
            res_count = supabase.table("oyuncular").select("*", count="exact").limit(1).execute()
            total_players = res_count.count
            
            # VIP sayısını hesapla
            vip_count = len([u for u in users_list if u.get('is_vip')])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Toplam Oyuncu", f"{total_players:,}".replace(",", "."))
            c2.metric("Kayıtlı Kullanıcı", len(users_list))
            c3.metric("Aktif VIP", vip_count)
            c4.success("Sistem: Aktif")
        except Exception as e:
            st.error(f"Veri çekme hatası: {e}")
            users_list = []

        st.markdown("---")
        adm_tabs = st.tabs(["👥 Kullanıcı & VIP", "🔍 Oyuncu Denetimi", "🛠️ Sistem Bakımı"])

        # --- A. KULLANICI & VIP YÖNETİMİ ---
        with adm_tabs[0]:
            st.write("### 👥 Kullanıcı Listesi ve Yetkilendirme")
            
            # Arama filtresi (Kullanıcılar arasında)
            search_u = st.text_input("Kullanıcı Ara:", placeholder="Kullanıcı adı yazın...")
            
            for u in users_list:
                # Arama yapılıyorsa filtrele
                if search_u and search_u.lower() not in u['username'].lower():
                    continue
                    
                with st.expander(f"{'🌟' if u.get('is_vip') else '⚪'} {u['username']} - {u.get('email', 'E-posta Yok')}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Şifre:** `{u.get('password')}`")
                        st.write(f"**Puan:** `{u.get('puan', 0)}` SC")
                        st.write(f"**Barrow Hak:** `{u.get('barrow_count', 0)}/3`")
                    
                    with col2:
                        # VIP Tarih Ayarı
                        db_date = u.get('last_barrow_date')
                        try:
                            default_date = datetime.datetime.strptime(db_date, "%Y-%m-%d").date() if db_date else datetime.date.today()
                        except:
                            default_date = datetime.date.today()
                        
                        new_date = st.date_input(f"VIP Bitiş Tarihi:", value=default_date, key=f"date_{u['username']}")
                        is_vip_toggle = st.checkbox("VIP Yetkisi Ver", value=u.get('is_vip', False), key=f"check_{u['username']}")

                    with col3:
                        st.write(" İşlemler")
                        if st.button("💾 GÜNCELLE", key=f"upd_{u['username']}", use_container_width=True):
                            supabase.table("users").update({
                                "is_vip": is_vip_toggle,
                                "last_barrow_date": str(new_date)
                            }).eq("username", u['username']).execute()
                            st.success("Güncellendi!")
                            st.rerun()
                            
                        if u['username'] != "someku":
                            if st.button("🗑️ SİL", key=f"del_{u['username']}", use_container_width=True):
                                supabase.table("users").delete().eq("username", u['username']).execute()
                                st.warning("Kullanıcı silindi.")
                                st.rerun()

        # --- B. OYUNCU DENETİMİ ---
        with adm_tabs[1]:
            st.write("### ✏️ Oyuncu Bilgisi Güncelle")
            target_p_name = st.text_input("Düzenlenecek Oyuncu Adı (Tam Eşleşme):")
            if target_p_name:
                p_data = supabase.table("oyuncular").select("*").eq("oyuncu_adi", target_p_name).execute()
                if p_data.data:
                    p_edit = p_data.data[0]
                    e1, e2, e3 = st.columns(3)
                    new_pa = e1.number_input("PA:", value=int(p_edit['pa']))
                    new_ca = e2.number_input("CA:", value=int(p_edit.get('ca', 0)))
                    new_club = e3.text_input("Kulüp:", value=p_edit.get('kulup', ''))
                    
                    if st.button("DEĞİŞİKLİKLERİ KAYDET"):
                        supabase.table("oyuncular").update({
                            "pa": new_pa, 
                            "ca": new_ca, 
                            "kulup": new_club
                        }).eq("oyuncu_adi", target_p_name).execute()
                        st.success("Oyuncu mermi gibi güncellendi!")
                else:
                    st.error("Oyuncu bulunamadı.")

        # --- C. SİSTEM BAKIMI ---
        with adm_tabs[2]:
            st.write("### 🛠️ Kritik Sistem Araçları")
            
            c_sec1, c_sec2 = st.columns(2)
            
            with c_sec1:
                if st.button("🧹 ÖNBELLEĞİ TEMİZLE", use_container_width=True):
                    st.cache_data.clear()
                    st.success("Streamlit cache temizlendi.")
                
                st.info("Bu işlem sayfanın yavaşlamasını önler.")

            with c_sec2:
                # Toplu Puan Sıfırlama vb. eklenebilir
                if st.button("📉 TÜM BARROW HAKLARINI SIFIRLA", use_container_width=True):
                    supabase.table("users").update({"barrow_count": 0}).execute()
                    st.success("Tüm standart üyelerin günlük hakları sıfırlandı.")

    else:
        st.markdown("""
            <div style="text-align:center; padding:50px;">
                <h1 style="font-size:100px;">🚫</h1>
                <h2>YETKİSİZ ERİŞİM</h2>
                <p>Bu bölgeye sadece ana scout (someku) erişebilir.</p>
            </div>
        """, unsafe_allow_html=True)
        
