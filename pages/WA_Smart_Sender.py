"""
WA Smart Sender — Download + Buy Premium page (DK File Converter ka naya page)

Streamlit "pages/" folder ki har file apne aap sidebar me naya page ban jati hai.
Sirf neeche ka SETTINGS hissa apni details se badlo.
"""
import os
import io
from urllib.parse import quote

import streamlit as st

# ======================= SETTINGS (yahan apni details daalo) =======================
UPI_ID = "yourname@upi"            # apna UPI ID (GPay / PhonePe / Paytm)
PAYEE_NAME = "DK Tools"              # UPI me dikhne wala naam
WHATSAPP_NUMBER = "919999999999"     # apna WhatsApp number, 91 ke saath, bina + ke

PLANS = {                            # naam: (price ₹, din)  — 0 din = lifetime
    "1 Mahina": (199, 30),
    "1 Saal": (999, 365),
    "Lifetime": (1999, 0),
}
ZIP_FILE = "wa-smart-sender.zip"   # ye zip repo me upload karo (main folder ya downloads/ folder)
VERSION = "1.1.0"
# ===================================================================================

st.set_page_config(page_title="WA Smart Sender | DK Tools", page_icon="💬", layout="centered")

# ---------- Style (DK File Converter jaisa) ----------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border-right: 1px solid rgba(139, 92, 246, 0.2); }
h1, h2, h3, h4 { color: #ffffff !important; }
div, p, span, li { color: #e2e8f0; }
.wa-header {
    background: linear-gradient(135deg, #059669 0%, #8b5cf6 55%, #ec4899 100%);
    padding: 2.6rem 2rem; border-radius: 25px; text-align: center; margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(139, 92, 246, 0.35);
}
.wa-header h1 { margin: 0 0 .4rem 0; font-size: 2.6rem; font-weight: 900; }
.wa-header p { margin: 0; font-size: 1.15rem; color: #ffffff; opacity: .95; }
.wa-badge { display: inline-block; background: rgba(255,255,255,.18); color: #fff;
    padding: .25rem .8rem; border-radius: 99px; font-size: .85rem; margin-top: .8rem; }
.wa-card {
    background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
    padding: 1.4rem 1.5rem; border-radius: 18px; border-left: 6px solid #8b5cf6;
    margin-bottom: 1rem; box-shadow: 0 10px 35px rgba(0,0,0,.3); height: 100%;
}
.wa-card h4 { margin: 0 0 .4rem 0; font-size: 1.15rem; }
.wa-card p { margin: 0; font-size: .98rem; line-height: 1.5; }
.plan { text-align: center; border-left: none; border-top: 5px solid #8b5cf6; }
.plan.best { border-top-color: #f59e0b; box-shadow: 0 10px 40px rgba(245,158,11,.25); }
.plan .price { font-size: 2.1rem; font-weight: 900; color: #ffffff; margin: .3rem 0; }
.plan .sub { color: #94a3b8; font-size: .9rem; }
.wa-table { width: 100%; border-collapse: collapse; margin: .5rem 0 1rem 0; }
.wa-table th, .wa-table td { padding: .55rem .6rem; border-bottom: 1px solid rgba(139,92,246,.2);
    text-align: center; color: #e2e8f0; }
.wa-table th { color: #ffffff; font-weight: 800; }
.wa-table td:first-child, .wa-table th:first-child { text-align: left; }
.gold { color: #f59e0b !important; }
.pay-btn {
    display: block; text-align: center; padding: .85rem 1rem; border-radius: 50px;
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); color: #ffffff !important;
    font-weight: 800; text-decoration: none !important; margin: .4rem 0 .8rem 0;
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
}
.upi-box { background: rgba(139,92,246,.15); border: 1px dashed #a78bfa; border-radius: 12px;
    padding: .7rem 1rem; font-family: monospace; font-size: 1.15rem; color: #ffffff;
    text-align: center; margin: .3rem 0 .6rem 0; user-select: all; }
.wa-btn { background: linear-gradient(135deg, #059669 0%, #25d366 100%);
    box-shadow: 0 10px 30px rgba(37, 211, 102, 0.35); }
.footer { text-align: center; padding: 2rem; color: #64748b; margin-top: 2rem;
    border-top: 1px solid rgba(139, 92, 246, 0.2); }
.footer p { color: #64748b; }
.stDownloadButton>button {
    background: linear-gradient(135deg, #059669 0%, #25d366 100%); color: white; border: none;
    border-radius: 50px; padding: .8rem 2.5rem; font-weight: 800; font-size: 1.05rem; width: 100%;
    box-shadow: 0 10px 30px rgba(37, 211, 102, 0.35);
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown(f"""
<div class="wa-header">
  <h1>💬 WA Smart Sender</h1>
  <p>WhatsApp Web par custom messages, insaan jaise random time gap ke saath</p>
  <span class="wa-badge">Chrome Extension • v{VERSION} • Free + Premium ⭐</span>
</div>
""", unsafe_allow_html=True)

# ---------- Features ----------
st.markdown("### ✨ Features")
features = [
    ("⏱️ Human-like gap", "Har message ke baad alag random time, beech me batch breaks."),
    ("✍️ Custom message", "{{name}}, {{city}} jaise variables; Premium me {Hi|Hello} spintax."),
    ("📊 Live progress", "Sent / Failed count, countdown, aur CSV report."),
    ("🛡️ Safety limits", "Daily limit, working hours, opt-out line, do-not-send list."),
]
for i in range(0, len(features), 2):
    cols = st.columns(2)
    for col, (title, desc) in zip(cols, features[i:i + 2]):
        col.markdown(f'<div class="wa-card"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ---------- Download ----------
st.markdown("### 📥 Free Download")
ZIP_PATH = next((p for p in (ZIP_FILE, os.path.join("pages", ZIP_FILE), os.path.join("downloads", ZIP_FILE)) if os.path.exists(p)), None)
if ZIP_PATH:
    with open(ZIP_PATH, "rb") as f:
        st.download_button("⬇️ Download WA Smart Sender (.zip)", f.read(),
                           file_name="wa-smart-sender.zip", mime="application/zip")
    st.caption("Free plan download karte hi chalu. Premium ke liye neeche license key lein.")
else:
    st.warning("Download abhi taiyar nahi hai. (Owner: GitHub repo me `wa-smart-sender.zip` upload karein.)")

with st.expander("⚙️ Install kaise karein (5 minute)", expanded=True):
    st.markdown("""
1. Zip ko kisi **naye folder** me **Extract** karein.
2. Chrome me kholein: `chrome://extensions`
3. Upar right me **Developer mode** ON karein.
4. **Load unpacked** dabayein → woh folder chunein **jisme `manifest.json` seedha dikhe**.
   *(Agar folder ke andar ek aur folder ho, to andar wala chunein.)*
5. 🧩 puzzle icon se extension **pin** karein.
6. `web.whatsapp.com` kholein, QR scan karein → extension icon dabayein → shuru! ✅
""")

# ---------- Plans ----------
st.markdown("### ⭐ Free vs Premium")
st.markdown("""
<table class="wa-table">
<tr><th></th><th>Free</th><th class="gold">Premium ⭐</th></tr>
<tr><td>Messages / day</td><td>50</td><td>300</td></tr>
<tr><td>Contacts / campaign</td><td>100</td><td>5,000</td></tr>
<tr><td>Random gap & batch breaks</td><td>✔ Safe preset</td><td>✔ Custom</td></tr>
<tr><td>{{name}} variables</td><td>✔</td><td>✔</td></tr>
<tr><td>Spintax {Hi|Hello}</td><td>✖</td><td>✔</td></tr>
<tr><td>CSV import</td><td>✖</td><td>✔</td></tr>
<tr><td>Working hours</td><td>✖</td><td>✔</td></tr>
<tr><td>Typing simulation</td><td>✖</td><td>✔</td></tr>
<tr><td>Report export</td><td>✖</td><td>✔</td></tr>
</table>
""", unsafe_allow_html=True)

plan_names = list(PLANS.keys())
cols = st.columns(len(plan_names))
for idx, (col, name) in enumerate(zip(cols, plan_names)):
    price, days = PLANS[name]
    sub = "Lifetime ♾ • ek baar" if days == 0 else f"{days} din"
    best = " best" if idx == 1 else ""
    tag = "<div class='sub gold'>⭐ Sabse popular</div>" if best else "<div class='sub'>&nbsp;</div>"
    col.markdown(f"""<div class="wa-card plan{best}">{tag}<h4>{name}</h4>
        <div class="price">₹{price}</div><div class="sub">{sub}</div></div>""", unsafe_allow_html=True)

# ---------- Buy ----------
st.markdown("### 💳 Premium kaise lein")
choice = st.radio("Plan chunein:", plan_names, index=1, horizontal=True)
price, days = PLANS[choice]
note = f"WA Smart Sender {choice}"
upi_link = (f"upi://pay?pa={quote(UPI_ID)}&pn={quote(PAYEE_NAME)}"
            f"&am={price}&cu=INR&tn={quote(note)}")

left, right = st.columns([1, 1.3])
with left:
    try:
        import qrcode
        img = qrcode.make(upi_link)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption=f"Scan karke ₹{price} pay karein", use_container_width=True)
    except Exception:
        st.info("QR ke liye requirements.txt me `qrcode` jodein.")
with right:
    st.markdown(f"**Step 1:** ₹{price} pay karein (koi bhi UPI app)")
    st.markdown(f'<div class="upi-box">{UPI_ID}</div>', unsafe_allow_html=True)
    st.markdown(f'<a class="pay-btn" href="{upi_link}">📱 UPI App se Pay karein (mobile)</a>',
                unsafe_allow_html=True)
    st.markdown("**Step 2:** Payment ka screenshot WhatsApp par bhejein")
    wa_text = (f"Namaste! Maine WA Smart Sender Premium ({choice} - ₹{price}) ke liye "
               f"payment kar diya hai. Screenshot bhej raha/rahi hoon. Mera naam: ")
    wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(wa_text)}"
    st.markdown(f'<a class="pay-btn wa-btn" href="{wa_link}" target="_blank">💬 WhatsApp par screenshot bhejein</a>',
                unsafe_allow_html=True)
    st.markdown("**Step 3:** Aapko License Key mil jayegi → extension ke **Plan** tab me Activate karein ⭐")

# ---------- Honest note + FAQ ----------
st.markdown("### ❓ Aksar puchhe jaane wale sawal")
with st.expander("Kya mera number block nahi hoga?"):
    st.markdown("""
Extension insaan jaisa time gap, daily limit aur breaks rakhta hai, jo risk ko **kam** karta hai —
lekin **koi bhi tool 100% guarantee nahi de sakta**. WhatsApp sabse zyada tab block karta hai jab log
aapko **report/block** karte hain. Isliye sirf unhi logon ko message bhejein jo aapko jaante hain
(customers, enquiry wale), aur naye number se dheere-dheere shuru karein.
""")
with st.expander("Key kitne computer par chalegi?"):
    st.markdown("Ek key **1 computer** par chalti hai. Naya computer liya ho to WhatsApp par batayein, hum reset kar denge.")
with st.expander("Plan khatam hone par kya hoga?"):
    st.markdown("Extension apne aap **Free plan** par aa jayega — kuch delete nahi hota. Renew karte hi Premium wapas.")
with st.expander("Mobile par chalega?"):
    st.markdown("Nahi, ye **computer ke Chrome browser** ka extension hai (WhatsApp Web ke saath).")

st.markdown("""
<div class="footer"><p>Created with ❤️ by DK Tools • WA Smart Sender</p></div>
""", unsafe_allow_html=True)
