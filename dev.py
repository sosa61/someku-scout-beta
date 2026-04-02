import streamlit as st
from supabase import create_client, Client
import urllib.parse
import pandas as pd
import random
import json
import time
import re
import streamlit.components.v1 as components
import unicodedata
import datetime

# --- 1. SİSTEM VE SAYFA AYARLARI ---
st.set_page_config(page_title="SOMEKU ELITE PRO", layout="wide", page_icon="💎")

URL = "https://iwgowefraytdbcdgeqdz.supabase.co"
KEY = "sb_publishable_NHESQOd8-v3tYpVPcz88-w_vypIPQ8Z"

if 'supabase' not in st.session_state:
    st.session_state.supabase = create_client(URL, KEY)
supabase = st.session_state.supabase

# KRİTİK: Tüm değişkenleri sigortalıyoruz (Hata almamak için)
FOR_KEYS = {
    'authenticated': False, 
    'user': None, 
    'is_vip': False, 
    'menu': "🔍 Scout Merkezi", 
    'page': 0, 
    'fav_list': [],
    'rulet_winner': None,
    'animasyon_tamam': False
}
for key, val in FOR_KEYS.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. ELITE PREMİUM UI (CSS) ---
st.markdown("""
    <style>
    /* Ana Fon */
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #010409 !important; border-right: 1px solid #30363d; }
    
    /* Premium Butonlar */
    div.stButton > button {
        background: linear-gradient(90deg, #1f6feb 0%, #58a6ff 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important; 
        font-weight: 600 !important; transition: 0.3s !important;
        height: 50px !important;
    }
    div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(31, 111, 235, 0.4); }
    
    /* Video Alanı Kartı */
    .video-placeholder {
        width: 100%; height: 350px; background: #161b22; 
        border: 2px dashed #30363d; border-radius: 20px;
        display: flex; justify-content: center; align-items: center;
        text-align: center; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GİRİŞ VE KAYIT SİSTEMİ ---
if not st.session_state.authenticated:
    st.markdown('<h1 style="text-align:center; color:#58a6ff; font-size:45px; letter-spacing:3px; margin-top:50px;">🕵️ SOMEKU ELITE PRO</h1>', unsafe_allow_html=True)
    auth_tab = st.tabs(["🔐 SİSTEME GİRİŞ", "📝 YENİ KAYIT"])
    
    with auth_tab[0]:
        with st.form("login_form"):
            u_id = st.text_input("Kullanıcı Adı")
            u_pw = st.text_input("Şifre", type="password")
            if st.form_submit_button("ANALİZİ BAŞLAT", use_container_width=True):
                if u_id == "someku" and u_pw == "28616128Ok":
                    st.session_state.update({"authenticated": True, "user": u_id, "is_vip": True})
                    st.rerun()
                else:
                    try:
                        res = supabase.table("users").select("*").eq("username", u_id).eq("password", u_pw).execute()
                        if res.data:
                            st.session_state.update({"authenticated": True, "user": u_id, "is_vip": bool(res.data[0].get("is_vip", False))})
                            st.rerun()
                        else: st.error("❌ Hatalı Kimlik!")
                    except: st.error("⚠️ Veritabanı bağlantı hatası!")

    with auth_tab[1]:
        with st.form("reg_form"):
            n_user = st.text_input("Kullanıcı Adı")
            n_email = st.text_input("E-posta")
            n_pw = st.text_input("Şifre", type="password")
            if st.form_submit_button("HESAP OLUŞTUR"):
                if n_user and n_email and n_pw:
                    check = supabase.table("users").select("*").eq("username", n_user).execute()
                    if check.data: st.error("❌ Bu isim alınmış!")
                    else:
                        supabase.table("users").insert({"username": n_user, "email": n_email, "password": n_pw, "is_vip": False, "puan": 0}).execute()
                        st.success("✅ Kayıt başarılı! Girişe geçebilirsin.")
    st.stop()

# --- 4. ÜST VİDEO ALANI (SABİT) ---
st.markdown(f"""
    <div class="video-placeholder">
        <div>
            <h1 style="color:#58a6ff; margin:0;">[BURAYA VİDEO GELECEK]</h1>
            <p style="color:#8b949e;">Hoş geldin Master Scout, {st.session_state.user.upper()}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. HIZLI ERİŞİM BUTONLARI (ORTA PANEL) ---
st.markdown("### 🚀 HIZLI ERİŞİM MERKEZİ")
menu_list = ["🔍 Scout Merkezi", "🎰 Wonderkid Ruleti", "🏟️ Taktik Tahtası", "⭐ Favorilerim", "🎯 Avcı Modu", "🤵 Barrow AI", "🛡️ Yönetim"]
if st.session_state.user != "someku": menu_list = [m for m in menu_list if m != "🛡️ Yönetim"]

# 3'lü kolonlar halinde butonlar
cols = st.columns(len(menu_list))
for idx, item in enumerate(menu_list):
    if cols[idx].button(item, key=f"quick_{item}", use_container_width=True):
        st.session_state.menu = item
        st.rerun()

st.markdown("---")

# --- 6. SOL YAN BAR (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#58a6ff;'>ELITE NAV</h2>", unsafe_allow_html=True)
    st.markdown("---")
    for item in menu_list:
        # Seçili olan butonu vurgula
        is_active = st.session_state.menu == item
        if st.button(item, key=f"side_{item}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.menu = item
            st.rerun()
    
    st.markdown("---")
    if st.button("🚪 OTURUMU KAPAT", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# --- 7. İZOLASYON SİSTEMİ (900 SATIRLIK KODUN KÖPRÜSÜ) ---
class TabBridge:
    def __init__(self, label):
        self.label = label
    def __enter__(self):
        # Sadece seçilen menü içeriğini döndürür, diğerleri HTML olarak gizlenir (Hız sağlar)
        if st.session_state.menu == self.label:
            return st.container()
        else:
            st.write('<div style="display:none;">', unsafe_allow_html=True)
            return st.empty()
    def __exit__(self, *args):
        if st.session_state.menu != self.label:
            st.write('</div>', unsafe_allow_html=True)

# Senin 900 satırlık kodundaki tabs[0]...tabs[6] yapısını buraya bağlıyoruz
tabs = [TabBridge(m) for m in ["🔍 Scout Merkezi", "🎰 Wonderkid Ruleti", "🏟️ Taktik Tahtası", "⭐ Favorilerim", "🎯 Avcı Modu", "🤵 Barrow AI", "🛡️ Yönetim"]]

# --- 8. SAYFA İÇERİKLERİ (SENİN 900 SATIRLIK KODUN) ---
# Scout Merkezi (tabs[0])
with tabs[0]:
    if st.session_state.menu == "🔍 Scout Merkezi":
        st.subheader("🔍 Oyuncu Analiz ve Filtreleme")
        # Buradan aşağısı senin orijinal Scout kodların... (POS_TR, REG_TR, query, filtered_data vs.)
        # HİÇBİR ŞEYİ SİLMEDEN YAPIŞTIRABİLİRSİN.
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


# Wonderkid Ruleti (tabs[1])
with tabs[1]:
    if st.session_state.menu == "🎰 Wonderkid Ruleti":
        st.subheader("🎰 Wonderkid Ruleti")
        # Rulet kodların...

# Taktik Tahtası (tabs[2])
with tabs[2]:
    if st.session_state.menu == "🏟️ Taktik Tahtası":
        st.subheader("🏟️ Elite Arena")
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

# Favoriler (tabs[3])
with tabs[3]:
    if st.session_state.menu == "⭐ Favorilerim":
        st.subheader("⭐ Takip Listem")
        # Favori kodların...

# Avcı Modu (tabs[4])
with tabs[4]:
    if st.session_state.menu == "🎯 Avcı Modu":
        # Avcı oyunu kodların...
        pass

# Barrow AI (tabs[5])
with tabs[5]:
    if st.session_state.menu == "🤵 Barrow AI":
        # Barrow AI kodların...
        pass

# Yönetim (tabs[6])
with tabs[6]:
    if st.session_state.user == "someku" and st.session_state.menu == "🛡️ Yönetim":
        st.subheader("🛡️ Yönetim Paneli")
        # Admin kodların...
