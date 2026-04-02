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
    
    /* Neon Mavi Vurgular ve Kartlar */
    .elite-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363d;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* Premium Butonlar */
    div.stButton > button {
        background: linear-gradient(90deg, #1f6feb 0%, #58a6ff 100%) !important;
        color: white !important; border: none !important; border-radius: 8px !important; 
        font-weight: 600 !important; transition: 0.3s !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(31, 111, 235, 0.4); }
    
    /* Alt Sekmeler (Kayıt Ekranı İçin) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; background-color: #161b22; border-radius: 8px 8px 0 0; 
        color: #8b949e; border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] { background-color: #1f6feb !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GİRİŞ VE KAYIT SİSTEMİ ---
if not st.session_state.authenticated:
    st.markdown('<h1 style="text-align:center; color:#58a6ff; font-size:45px; letter-spacing:3px;">💎 SOMEKU ELITE PRO</h1>', unsafe_allow_html=True)
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
                    res = supabase.table("users").select("*").eq("username", u_id).eq("password", u_pw).execute()
                    if res.data:
                        st.session_state.update({"authenticated": True, "user": u_id, "is_vip": bool(res.data[0].get("is_vip", False))})
                        st.rerun()
                    else: st.error("❌ Yetkisiz Giriş!")

    with auth_tab[1]:
        with st.form("reg_form"):
            n_user = st.text_input("Kullanıcı Adı")
            n_email = st.text_input("E-posta")
            n_pw = st.text_input("Şifre", type="password")
            if st.form_submit_button("HESAP OLUŞTUR"):
                if n_user and n_email and n_pw:
                    check = supabase.table("users").select("*").eq("username", n_user).execute()
                    if check.data: st.error("Bu isim alınmış!")
                    else:
                        supabase.table("users").insert({"username": n_user, "email": n_email, "password": n_pw, "is_vip": False, "puan": 0}).execute()
                        st.success("Kayıt başarılı! Girişe geçebilirsin.")
    st.stop()

# --- 4. SABİT SİNEMATİK ÜST PANEL ---
# Bu video şifreden sonra hep en üstte kalır
intro_html = f"""
<div style="width:100%; height:350px; position:relative; overflow:hidden; border-radius:20px; margin-bottom:20px; border:2px solid #30363d;">
    <video autoplay muted loop playsinline style="width:100%; height:100%; object-fit:cover; opacity:0.5;">
        <source src="https://assets.mixkit.co/videos/preview/mixkit-business-analyst-working-with-data-on-a-tablet-41224-large.mp4" type="video/mp4">
    </video>
    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); text-align:center; width:100%;">
        <h1 style="color:#58a6ff; font-size:55px; font-family:'Segoe UI', sans-serif; text-shadow: 0 0 20px rgba(88,166,255,0.6); margin:0;">SOMEKU ELITE PRO</h1>
        <p style="color:#ffffff; font-size:20px; letter-spacing:2px; font-weight:300;">HOŞ GELDİN SCOUT MASTER, {st.session_state.user.upper()}</p>
    </div>
</div>
"""
st.components.v1.html(intro_html, height=360)

# --- 5. HIZLI ERİŞİM BUTONLARI (VİDEO ALTI NAVİGASYON) ---
st.markdown("### 🚀 HIZLI ERİŞİM")
nav_cols = st.columns(6)
menu_items = ["🔍 Scout Merkezi", "🎰 Wonderkid Ruleti", "🏟️ Taktik Tahtası", "⭐ Favorilerim", "🎯 Avcı Modu", "🛡️ Yönetim"]

for i, item in enumerate(menu_items):
    # Eğer admin değilse Yönetim butonunu gizle
    if item == "🛡️ Yönetim" and st.session_state.user != "someku":
        continue
    if nav_cols[i].button(item, key=f"quick_{i}", use_container_width=True):
        st.session_state.menu = item
        st.rerun()

st.markdown("---")

# --- 6. SOL YAN MENÜ ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#58a6ff; text-align:center;'>ELITE PANEL</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    display_menu = [m for m in menu_items if m != "🛡️ Yönetim"] if st.session_state.user != "someku" else menu_items

    for item in display_menu:
        if st.button(item, key=f"side_{item}", use_container_width=True, type="primary" if st.session_state.menu == item else "secondary"):
            st.session_state.menu = item
            st.rerun()

    st.markdown("---")
    if st.button("🚪 GÜVENLİ ÇIKIŞ", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# --- 7. İZOLASYON SİSTEMİ (HATALARI ÇÖZEN KÖPRÜ) ---
class TabBridge:
    def __init__(self, label):
        self.label = label
    def __enter__(self):
        # Sadece seçilen menü içeriğini döndürür
        if st.session_state.menu == self.label:
            return st.container()
        else:
            # Seçili olmayanlar için boş ama sistemin tanıyacağı alan bırak
            st.write('<div style="display:none;">', unsafe_allow_html=True)
            return st.empty()
    def __exit__(self, *args):
        if st.session_state.menu != self.label:
            st.write('</div>', unsafe_allow_html=True)

# 900 Satırlık kodundaki tabs[0]...tabs[6] yerleri sidebar ile mermi gibi bağladık
tabs = [TabBridge(m) for m in menu_items]

# --- 8. SAYFA İÇERİKLERİ (SENİN TÜM 900 SATIRLIK KODUN) ---
# Scout (tabs[0]), Rulet (tabs[1]), Taktik (tabs[2]), Favori (tabs[3]), Avcı (tabs[4]), Barrow (tabs[5]), Yönetim (tabs[6])

# BURADAN SONRA SENİN TÜM KODLARIN TIKIR TIKIR ÇALIŞACAK...
