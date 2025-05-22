
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
                    {"role": "system", "content": "אתה מסייע למורים לבצע הגהה וניסוח של טקסטים מקצועיים בעברית תקנית תוך שמירה על הסגנון המקורי."},
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
    learning_paragraph = ""
    if st.button("✨ שדרג את הניסוח של 'מה למדנו'"):
        prompt = f"ערוך את כל הנושאים וההיבטים ברשימה לפסקה מנוסחת היטב שתסכם מה למדנו בקורס השנה. הנה הרשימה:\n{raw_learning}"
        learning_paragraph = query_gpt(prompt)
        st.text_area("פסקת סיכום מוצעת:", value=learning_paragraph, height=150)
    else:
        learning_paragraph = raw_learning

    st.header("שלב 3: תובנות לפי קטגוריות")

    names_input = st.text_area("הדבק כאן את שמות התלמידים (שם פרטי ואז שם משפחה, כל תלמיד בשורה נפרדת):")
    students = []
    if names_input.strip():
        lines = names_input.strip().split("\n")
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                first_name = " ".join(parts[:-1])
                last_name = parts[-1]
                students.append({"שם פרטי": first_name, "שם משפחה": last_name})

    evaluations = []
    if students:
        df_students = pd.DataFrame(students)
        for index, row in df_students.iterrows():
            full_name = f"{row['שם פרטי']} {row['שם משפחה']}"
            st.subheader(f"תלמיד.ה: {full_name}")

            q1 = st.text_area("1️⃣ נוכחות / מעורבות", key=f"q1_{index}")
            q2 = st.text_area("2️⃣ רמת ידע והבנה", key=f"q2_{index}")
            q3 = st.text_area("3️⃣ התמודדות עם משימות", key=f"q3_{index}")
            q4 = st.text_area("4️⃣ יחס ללמידה", key=f"q4_{index}")
            q5 = st.text_area("5️⃣ חוזקות ואתגרים", key=f"q5_{index}")
            q6 = st.text_area("6️⃣ טיפ אישי / המלצה", key=f"q6_{index}")

            all_info = f"נוכחות: {q1}\nידע: {q2}\nמשימות: {q3}\nיחס ללמידה: {q4}\nחוזקות ואתגרים: {q5}\nטיפ אישי: {q6}"

            if st.button("📌 הפק תובנות השראתיות", key=f"insight_{index}"):
                insight_prompt = f"""הנה מידע שכתב מורה על תלמיד במספר קטגוריות:
נוכחות, ידע, התמודדות עם משימות, יחס ללמידה, חוזקות ואתגרים.
כתוב פסקת תובנות כללית ומקצועית בגוף שני, שמסכמת את העיקר –
אך תשמור על ניסוח פתוח ולא מחייב, כזה שיכול לשמש השראה למורה שיכתוב את ההערכה הסופית.
השתמש בשפה תקנית, רהוטה ומכבדת, והימנע מקלישאות.
{all_info}"""
                insight_text = query_gpt(insight_prompt)
                st.text_area("🔍 תובנות השראתיות:", value=insight_text, height=160, key=f"insight_text_{index}")
                evaluations.append(insight_text)
            else:
                evaluations.append("")

            written_eval = st.text_area("✍️ טיוטת ההערכה (ניסוח חופשי שלך)", key=f"written_{index}")
            if st.button("🧠 הגהה ובקרת איכות", key=f"proofread_{index}"):
                proof_prompt = f"""הטקסט הבא הוא טיוטה חופשית שכתב מורה כהערכה לתלמיד.
בצע הגהה לשונית בלבד: תקן שגיאות כתיב, טעויות תחביר, וסגנון ניסוח לא תקני.
אל תנסח מחדש את ההערכה — שמור על הסגנון, הטון והאופי המקורי של המורה ככל האפשר.
המטרה היא לשפר את הניסוח מבלי לשנות את התוכן או את רוח הדברים.
כתוב בעברית תקנית, בגוף שני, ובשפה ברורה ומכבדת המתאימה לבית ספר דמוקרטי.

הנה הטקסט:
{written_eval}"""
                proofed = query_gpt(proof_prompt)
                st.text_area("🪄 גרסה לאחר הגהה:", value=proofed, height=160, key=f"proofed_{index}")
                evaluations[index] = proofed

        if st.button("📥 הורד את קובץ ההערכות"):
            df_students.insert(0, "שם הקורס", course_name)
            df_students.insert(1, "מה למדנו", learning_paragraph)
            df_students["טיוטת / גרסה אחרונה"] = evaluations

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_students.to_excel(writer, index=False)

            st.download_button(
                label="📄 הורד את הקובץ",
                data=buffer.getvalue(),
                file_name="הערכות_סופשנה_השראה_והגהה.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.warning("🔒 אין גישה למפתח API. ודא שהוא הוגדר כ-OPENAI_API_KEY במשתני הסביבה.")
