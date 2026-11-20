"""
WA Smart Sender — Download + Buy Premium page (English / हिंदी)

Streamlit "pages/" folder ki har file apne aap sidebar me naya page ban jati hai.
Sirf neeche ka SETTINGS hissa apni details se badlo.
Page ka saara text neeche TEXT dictionary me hai ("en" = English, "hi" = Hindi).
"""
import os
import io
from urllib.parse import quote

import streamlit as st

# ======================= SETTINGS (yahan apni details daalo) =======================
UPI_ID = "9250300240@ybl"            # apna UPI ID (GPay / PhonePe / Paytm)
PAYEE_NAME = "DK Tools"              # UPI me dikhne wala naam
WHATSAPP_NUMBER = "919250300240"     # apna WhatsApp number, 91 ke saath, bina + ke

PLANS = {                            # plan: (price ₹, din)  — 0 din = lifetime
    "month": (199, 30),
    "year": (999, 365),
    "lifetime": (1999, 0),
}
ZIP_FILE = "wa-smart-sender.zip"     # zip repo me (main folder / pages / downloads) kahin bhi
VERSION = "1.3.0"
# ===================================================================================

TEXT = {
    "en": {
        "tagline": "Send personalised WhatsApp Web messages with natural, human-like timing",
        "badge": "Chrome Extension • v{v} • Free + Premium ⭐",
        "features": "✨ Features",
        "feature_list": [
            ("⏱️ Human-like timing", "A different random gap after every message, with automatic breaks between batches."),
            ("✍️ Personalised messages", "Use variables such as {{name}} and {{city}}. Premium adds spintax: {Hi|Hello}."),
            ("📊 Live progress", "See sent and failed counts, a countdown to the next message, and a CSV report."),
            ("🛡️ Safety limits", "Daily limit, working hours, an opt-out line and a do-not-send list."),
            ("📝 Message templates", "Save your messages and reuse them. Add names, emojis, ready lines and links in one click."),
            ("📎 Images & PDFs (Premium)", "Send one poster to everyone, or a personal letter/PDF to each contact."),
        ],
        "download": "📥 Free Download",
        "download_btn": "⬇️ Download WA Smart Sender (.zip)",
        "download_note": "The Free plan works right after installation. For Premium, get a licence key below.",
        "download_missing": "The download is not available yet. Please check back soon.",
        "install_title": "⚙️ How to install (5 minutes)",
        "install_steps": """
1. **Extract** the zip into a **new folder**.
2. Open Chrome and go to `chrome://extensions`.
3. Turn on **Developer mode** (top-right corner).
4. Click **Load unpacked** and select the folder **that directly contains `manifest.json`**.
   *(If there is another folder inside, select the inner one.)*
5. Click the 🧩 puzzle icon and **pin** the extension.
6. Open `web.whatsapp.com`, scan the QR code, then click the extension icon to start. ✅
""",
        "compare": "⭐ Free vs Premium",
        "rows": [
            ("Messages per day", "50", "300"),
            ("Contacts per campaign", "100", "5,000"),
            ("Random gaps & batch breaks", "✔ Safe preset", "✔ Customisable"),
            ("{{name}} variables", "✔", "✔"),
            ("Spintax {Hi|Hello}", "✖", "✔"),
            ("CSV import", "✖", "✔"),
            ("Working hours", "✖", "✔"),
            ("Typing simulation", "✖", "✔"),
            ("Report export", "✖", "✔"),
            ("Message templates", "5", "50"),
            ("Image / PDF attachments", "✖", "✔"),
            ("Personal file for each contact", "✖", "✔"),
        ],
        "plan_names": {"month": "1 Month", "year": "1 Year", "lifetime": "Lifetime"},
        "days": "{d} days",
        "lifetime_sub": "Lifetime ♾ • one-time payment",
        "popular": "⭐ Most popular",
        "buy": "💳 How to get Premium",
        "choose_plan": "Choose a plan:",
        "qr_caption": "Scan to pay ₹{p}",
        "qr_missing": "Add `qrcode` to requirements.txt to show the QR code.",
        "step1": "**Step 1:** Pay ₹{p} using any UPI app.",
        "pay_btn": "📱 Pay with a UPI app (mobile)",
        "step2": "**Step 2:** Send the payment screenshot on WhatsApp.",
        "wa_btn": "💬 Send screenshot on WhatsApp",
        "wa_text": "Hello! I have paid for WA Smart Sender Premium ({plan} - ₹{p}). I am sending the payment screenshot. My name: ",
        "step3": "**Step 3:** You will receive a licence key. Open the extension's **Plan** tab and click **Activate**. ⭐",
        "faq": "❓ Frequently asked questions",
        "faq_list": [
            ("Will my number be safe from blocking?",
             "The extension uses human-like gaps, daily limits and breaks, which **reduce** the risk — "
             "but **no tool can guarantee** that a number will never be blocked. WhatsApp blocks numbers "
             "mostly when people **report or block** the sender. Message only people who know you "
             "(customers, enquiries), and start slowly with a new number."),
            ("On how many computers does one key work?",
             "One key works on **one computer**. If you change your computer, message us on WhatsApp and we will reset it."),
            ("What happens when my plan ends?",
             "The extension switches back to the **Free plan** automatically. Nothing is deleted. Renew to get Premium back."),
            ("Does it work on mobile?",
             "No. It is an extension for the **Chrome browser on a computer**, used with WhatsApp Web."),
        ],
        "footer": "Made with ❤️ by DK Tools • WA Smart Sender",
    },
    "hi": {
        "tagline": "व्हाट्सऐप वेब पर अपने संदेश भेजें — इंसान जैसे स्वाभाविक समय-अंतराल के साथ",
        "badge": "क्रोम एक्सटेंशन • v{v} • फ्री + प्रीमियम ⭐",
        "features": "✨ विशेषताएँ",
        "feature_list": [
            ("⏱️ इंसान जैसा समय-अंतराल", "हर संदेश के बाद अलग-अलग समय का अंतर, और कुछ संदेशों के बाद अपने-आप विराम।"),
            ("✍️ व्यक्तिगत संदेश", "{{name}}, {{city}} जैसे वेरिएबल लगाएँ। प्रीमियम में स्पिनटैक्स भी: {Hi|Hello}।"),
            ("📊 लाइव प्रगति", "भेजे गए और असफल संदेशों की गिनती, अगले संदेश की उलटी गिनती, और CSV रिपोर्ट।"),
            ("🛡️ सुरक्षा सीमाएँ", "दैनिक सीमा, कार्य-समय, ऑप्ट-आउट पंक्ति और ‘न भेजें’ सूची।"),
            ("📝 संदेश टेम्पलेट", "अपने संदेश सेव करें और दोबारा इस्तेमाल करें। नाम, इमोजी, तैयार पंक्तियाँ और लिंक एक क्लिक में जोड़ें।"),
            ("📎 इमेज और PDF (प्रीमियम)", "सभी को एक जैसा पोस्टर भेजें, या हर व्यक्ति को उसका अलग पत्र/PDF।"),
        ],
        "download": "📥 मुफ़्त डाउनलोड",
        "download_btn": "⬇️ WA Smart Sender डाउनलोड करें (.zip)",
        "download_note": "इंस्टॉल करते ही फ्री प्लान चालू हो जाता है। प्रीमियम के लिए नीचे से लाइसेंस कोड लें।",
        "download_missing": "डाउनलोड अभी उपलब्ध नहीं है। कृपया थोड़ी देर बाद देखें।",
        "install_title": "⚙️ इंस्टॉल कैसे करें (5 मिनट)",
        "install_steps": """
1. ज़िप फ़ाइल को एक **नए फ़ोल्डर** में **एक्सट्रैक्ट** करें।
2. क्रोम में `chrome://extensions` खोलें।
3. ऊपर दाईं ओर **Developer mode** चालू करें।
4. **Load unpacked** दबाएँ और वह फ़ोल्डर चुनें **जिसमें सीधे `manifest.json` दिखे**।
   *(अगर फ़ोल्डर के अंदर एक और फ़ोल्डर है, तो अंदर वाला चुनें।)*
5. 🧩 पज़ल आइकन से एक्सटेंशन को **पिन** करें।
6. `web.whatsapp.com` खोलें, QR कोड स्कैन करें, फिर एक्सटेंशन आइकन दबाकर शुरू करें। ✅
""",
        "compare": "⭐ फ्री बनाम प्रीमियम",
        "rows": [
            ("प्रतिदिन संदेश", "50", "300"),
            ("प्रति अभियान संपर्क", "100", "5,000"),
            ("रैंडम अंतराल और विराम", "✔ सुरक्षित तय सेटिंग", "✔ अपनी सेटिंग"),
            ("{{name}} वेरिएबल", "✔", "✔"),
            ("स्पिनटैक्स {Hi|Hello}", "✖", "✔"),
            ("CSV इम्पोर्ट", "✖", "✔"),
            ("कार्य-समय", "✖", "✔"),
            ("टाइपिंग सिमुलेशन", "✖", "✔"),
            ("रिपोर्ट एक्सपोर्ट", "✖", "✔"),
            ("संदेश टेम्पलेट", "5", "50"),
            ("इमेज / PDF भेजना", "✖", "✔"),
            ("हर व्यक्ति को उसकी अलग फ़ाइल", "✖", "✔"),
        ],
        "plan_names": {"month": "1 महीना", "year": "1 साल", "lifetime": "आजीवन"},
        "days": "{d} दिन",
        "lifetime_sub": "आजीवन ♾ • एक बार भुगतान",
        "popular": "⭐ सबसे लोकप्रिय",
        "buy": "💳 प्रीमियम कैसे लें",
        "choose_plan": "प्लान चुनें:",
        "qr_caption": "₹{p} भुगतान के लिए स्कैन करें",
        "qr_missing": "QR कोड दिखाने के लिए requirements.txt में `qrcode` जोड़ें।",
        "step1": "**चरण 1:** किसी भी UPI ऐप से ₹{p} का भुगतान करें।",
        "pay_btn": "📱 UPI ऐप से भुगतान करें (मोबाइल)",
        "step2": "**चरण 2:** भुगतान का स्क्रीनशॉट व्हाट्सऐप पर भेजें।",
        "wa_btn": "💬 व्हाट्सऐप पर स्क्रीनशॉट भेजें",
        "wa_text": "नमस्ते! मैंने WA Smart Sender प्रीमियम ({plan} - ₹{p}) का भुगतान कर दिया है। भुगतान का स्क्रीनशॉट भेज रहा/रही हूँ। मेरा नाम: ",
        "step3": "**चरण 3:** आपको एक लाइसेंस कोड मिलेगा। एक्सटेंशन के **Plan** टैब में उसे डालकर **Activate** दबाएँ। ⭐",
        "faq": "❓ अक्सर पूछे जाने वाले प्रश्न",
        "faq_list": [
            ("क्या मेरा नंबर ब्लॉक होने से सुरक्षित रहेगा?",
             "एक्सटेंशन इंसान जैसा अंतराल, दैनिक सीमा और विराम रखता है, जिससे जोखिम **कम** होता है — "
             "लेकिन **कोई भी टूल पूरी गारंटी नहीं दे सकता** कि नंबर कभी ब्लॉक नहीं होगा। व्हाट्सऐप ज़्यादातर तब "
             "ब्लॉक करता है जब लोग भेजने वाले की **रिपोर्ट या ब्लॉक** करते हैं। केवल उन्हीं लोगों को संदेश भेजें "
             "जो आपको जानते हैं (ग्राहक, पूछताछ करने वाले), और नए नंबर से धीरे-धीरे शुरुआत करें।"),
            ("एक लाइसेंस कोड कितने कंप्यूटर पर चलेगा?",
             "एक कोड **एक कंप्यूटर** पर चलता है। कंप्यूटर बदलने पर हमें व्हाट्सऐप करें, हम उसे रीसेट कर देंगे।"),
            ("प्लान ख़त्म होने पर क्या होगा?",
             "एक्सटेंशन अपने-आप **फ्री प्लान** पर आ जाएगा। कुछ भी डिलीट नहीं होता। रिन्यू करते ही प्रीमियम वापस मिल जाएगा।"),
            ("क्या यह मोबाइल पर चलता है?",
             "नहीं। यह **कंप्यूटर के क्रोम ब्राउज़र** का एक्सटेंशन है, जो व्हाट्सऐप वेब के साथ काम करता है।"),
        ],
        "footer": "DK Tools द्वारा ❤️ के साथ बनाया गया • WA Smart Sender",
    },
}

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

# ---------- Language switch ----------
_, lang_col = st.columns([3, 1.2])
with lang_col:
    lang_label = st.radio("Language / भाषा", ["English", "हिंदी"], horizontal=True,
                          key="wa_lang", label_visibility="collapsed")
L = TEXT["hi" if lang_label == "हिंदी" else "en"]

# ---------- Header ----------
st.markdown(f"""
<div class="wa-header">
  <h1>💬 WA Smart Sender</h1>
  <p>{L["tagline"]}</p>
  <span class="wa-badge">{L["badge"].format(v=VERSION)}</span>
</div>
""", unsafe_allow_html=True)

# ---------- Features ----------
st.markdown(f"### {L['features']}")
features = L["feature_list"]
for i in range(0, len(features), 2):
    cols = st.columns(2)
    for col, (title, desc) in zip(cols, features[i:i + 2]):
        col.markdown(f'<div class="wa-card"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ---------- Download ----------
st.markdown(f"### {L['download']}")
ZIP_PATH = next((p for p in (ZIP_FILE, os.path.join("pages", ZIP_FILE), os.path.join("downloads", ZIP_FILE))
                 if os.path.exists(p)), None)
if ZIP_PATH:
    with open(ZIP_PATH, "rb") as f:
        st.download_button(L["download_btn"], f.read(), file_name="wa-smart-sender.zip", mime="application/zip")
    st.caption(L["download_note"])
else:
    st.warning(L["download_missing"])

with st.expander(L["install_title"], expanded=True):
    st.markdown(L["install_steps"])

# ---------- Plans ----------
st.markdown(f"### {L['compare']}")
rows_html = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in L["rows"])
st.markdown(f"""
<table class="wa-table">
<tr><th></th><th>Free</th><th class="gold">Premium ⭐</th></tr>
{rows_html}
</table>
""", unsafe_allow_html=True)

plan_ids = list(PLANS.keys())
cols = st.columns(len(plan_ids))
for idx, (col, pid) in enumerate(zip(cols, plan_ids)):
    price, days = PLANS[pid]
    sub = L["lifetime_sub"] if days == 0 else L["days"].format(d=days)
    best = " best" if idx == 1 else ""
    tag = f"<div class='sub gold'>{L['popular']}</div>" if best else "<div class='sub'>&nbsp;</div>"
    col.markdown(f"""<div class="wa-card plan{best}">{tag}<h4>{L['plan_names'][pid]}</h4>
        <div class="price">₹{price}</div><div class="sub">{sub}</div></div>""", unsafe_allow_html=True)

# ---------- Buy ----------
st.markdown(f"### {L['buy']}")
choice = st.radio(L["choose_plan"], plan_ids, index=1, horizontal=True,
                  format_func=lambda pid: L["plan_names"][pid], key="wa_plan")
price, days = PLANS[choice]
plan_name = L["plan_names"][choice]
note = f"WA Smart Sender {TEXT['en']['plan_names'][choice]}"
upi_link = (f"upi://pay?pa={quote(UPI_ID)}&pn={quote(PAYEE_NAME)}"
            f"&am={price}&cu=INR&tn={quote(note)}")

left, right = st.columns([1, 1.3])
with left:
    try:
        import qrcode
        img = qrcode.make(upi_link)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption=L["qr_caption"].format(p=price), use_container_width=True)
    except Exception:
        st.info(L["qr_missing"])
with right:
    st.markdown(L["step1"].format(p=price))
    st.markdown(f'<div class="upi-box">{UPI_ID}</div>', unsafe_allow_html=True)
    st.markdown(f'<a class="pay-btn" href="{upi_link}">{L["pay_btn"]}</a>', unsafe_allow_html=True)
    st.markdown(L["step2"])
    wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(L['wa_text'].format(plan=plan_name, p=price))}"
    st.markdown(f'<a class="pay-btn wa-btn" href="{wa_link}" target="_blank">{L["wa_btn"]}</a>',
                unsafe_allow_html=True)
    st.markdown(L["step3"])

# ---------- FAQ ----------
st.markdown(f"### {L['faq']}")
for q, a in L["faq_list"]:
    with st.expander(q):
        st.markdown(a)

st.markdown(f'<div class="footer"><p>{L["footer"]}</p></div>', unsafe_allow_html=True)
