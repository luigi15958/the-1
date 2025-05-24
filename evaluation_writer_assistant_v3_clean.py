
import streamlit as st
import pandas as pd
from io import BytesIO
import openai
import os

st.set_page_config(page_title="כלי עזר לכתיבת הערכות – הדמוקרטי הוד השרון", layout="wide")
st.markdown(
    """
    <style>
    body, .main, .block-container {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("democratic_school_logo.jpg", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>כלי עזר לכתיבת הערכות סופשנה<br>הדמוקרטי הוד השרון</h1>", unsafe_allow_html=True)

api_key = os.environ.get("OPENAI_API_KEY")

if api_key:
    client = openai.OpenAI(api_key=api_key)

    def query_gpt(prompt, temperature=0.7):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "אתה מסייע למורים לנסח טקסטים חינוכיים בעברית תקנית תוך שמירה על קול אישי."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"שגיאה: {e}"

    st.header("שלב 1: פרטי הקורס")
    course_name = st.text_input("שם הקורס")
    teacher_name = st.text_input("שם המורה")

    st.header("שלב 2: מה למדנו?")
    raw_learning = st.text_area("רשימת נושאים ותכנים שנלמדו בקורס:")
    learning_paragraph = raw_learning
    if st.button("✨ שדרג את הניסוח של 'מה למדנו'"):
        prompt = f"""ערוך את כל הנושאים ברשימה לפסקה מנוסחת היטב שתסכם מה למדנו בקורס השנה.
הנה הרשימה:
{raw_learning}"""
        learning_paragraph = query_gpt(prompt)
    st.text_area("פסקת סיכום מוצעת:", value=learning_paragraph, height=150)

    st.header("שלב 3: רשימת תלמידים")
    names_input = st.text_area("הדבק כאן את שמות התלמידים (שם פרטי ואז שם משפחה, כל תלמיד בשורה נפרדת):")

    records = []
    if names_input.strip():
        lines = names_input.strip().split("\n")
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            first_name = " ".join(parts[:-1])
            last_name = parts[-1]
            full_name = f"{first_name} {last_name}"
            st.subheader(f"תלמיד.ה: {full_name}")

            q1 = st.text_area("1️⃣ נוכחות / מעורבות", key=f"q1_{i}")
            q2 = st.text_area("2️⃣ רמת ידע והבנה", key=f"q2_{i}")
            q3 = st.text_area("3️⃣ התמודדות עם משימות", key=f"q3_{i}")
            q4 = st.text_area("4️⃣ יחס ללמידה", key=f"q4_{i}")
            q5 = st.text_area("5️⃣ חוזקות ואתגרים", key=f"q5_{i}")
            q6 = st.text_area("6️⃣ טיפ אישי / המלצה", key=f"q6_{i}")

            all_info = f"נוכחות: {q1}\nידע: {q2}\nמשימות: {q3}\nיחס ללמידה: {q4}\nחוזקות ואתגרים: {q5}\nטיפ אישי: {q6}"
            insight_text = ""
            if st.button("📌 הפק תובנות השראתיות", key=f"insight_btn_{i}"):
                prompt = f"""הנה מידע שכתב מורה על תלמיד במספר קטגוריות:
נוכחות, ידע, התמודדות עם משימות, יחס ללמידה, חוזקות ואתגרים.
כתוב פסקת תובנות כללית ומקצועית בגוף שני שתוכל לשמש השראה לכתיבת הערכה.
{all_info}"""
                insight_text = query_gpt(prompt)
            insight_text = st.text_area("🔍 תובנות השראתיות", value=insight_text, key=f"insight_text_{i}")

            written = st.text_area("✍️ טיוטת ההערכה", key=f"written_{i}")
            final_text = written
            if st.button("🧠 הגהה ובקרת איכות", key=f"proof_{i}"):
                prompt = f"""בצע הגהה לשונית וניסוחית לטקסט הבא:
{written}
שמירה על סגנון אישי, תיקון תחביר, שגיאות כתיב ופיסוק בלבד."""
                final_text = query_gpt(prompt)
            final_text = st.text_area("🪄 גרסה לאחר הגהה", value=final_text, key=f"final_{i}")

            records.append({
                "שם פרטי": first_name,
                "שם משפחה": last_name,
                "תובנות השראה": insight_text,
                "טיוטה": written,
                "גרסה לאחר הגהה": final_text
            })

    if records and st.button("📥 הורד את קובץ ההערכות"):
        df = pd.DataFrame(records)
        df.insert(0, "שם המורה", teacher_name)
        df.insert(0, "שם הקורס", course_name)
        df.insert(2, "מה למדנו", learning_paragraph)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)

        st.download_button(
            label="📄 הורד את הקובץ",
            data=buffer.getvalue(),
            file_name="קובץ_הערכות_מסכם.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("🔒 אין גישה למפתח API. ודא שהוא הוגדר כ-OPENAI_API_KEY במשתני הסביבה.")
