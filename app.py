import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

#  تحميل مفتاح API
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# إعداد الصفحة
st.set_page_config(
    page_title="Dashboard Co-pilot Agent | Wajd",
    page_icon="📊",
    layout="wide"
)

# إدارة حالة الجلسة
if "lang" not in st.session_state:
    st.session_state.lang = "العربية"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar - Settings & Chatbot
with st.sidebar:
    st.header("Settings")
    st.session_state.lang = st.selectbox(
        "Select Language",
        ["العربية", "English"],
        index=0 if st.session_state.lang == "العربية" else 1
    )
    
    st.divider()
    
    st.header("مساعد الدوال والبيانات" if st.session_state.lang == "العربية" else "Formulas & Data Assistant")
    st.caption("اسألني عن دوال الإكسل أو صيغ Pandas!" if st.session_state.lang == "العربية" else "Ask me about Excel formulas or Pandas!")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    user_query = st.chat_input("اكتب سؤالك هنا..." if st.session_state.lang == "العربية" else "Ask your question...")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير..." if st.session_state.lang == "العربية" else "Thinking..."):
                q_lower = user_query.lower()
                if "متوسط" in q_lower or "average" in q_lower:
                    reply = "**لحساب المتوسط:**\n- **في إكسل:** `=AVERAGE(A1:A10)`\n- **في بايثون (Pandas):** `df['col'].mean()`"
                elif "مجموع" in q_lower or "sum" in q_lower:
                    reply = "**لحساب المجموع:**\n- **في إكسل:** `=SUM(A1:A10)`\n- **في بايثون (Pandas):** `df['col'].sum()`"
                else:
                    reply = "يمكنك استخدام دوال الإكسل القياسية أو تنفيذ أوامر Pandas مثل `df.describe()` لاستخراج المؤشرات."
                
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

is_ar = st.session_state.lang == "العربية"
direction = "rtl" if is_ar else "ltr"
text_align = "right" if is_ar else "left"

st.markdown(f"""
    <style>
    @keyframes slideUpFade {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .stApp {{
        direction: {direction};
        text-align: {text_align};
        animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    .kpi-card {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.3);
        animation: slideUpFade 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 15px;
        text-align: center;
    }}
    .kpi-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.4);
    }}
    .kpi-title {{
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        color: #38bdf8;
        font-size: 1.8rem;
        font-weight: bold;
    }}
    .color-box {{
        display: inline-block;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        margin-right: 8px;
        margin-left: 8px;
        vertical-align: middle;
        border: 2px solid rgba(255,255,255,0.2);
        cursor: pointer;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease;
    }}
    .color-box:hover {{
        transform: scale(1.25) rotate(5deg);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
    }}
    .footer-box {{
        margin-top: 60px;
        padding: 25px;
        text-align: center;
        border-top: 1px solid rgba(100, 116, 139, 0.3);
        font-size: 1rem;
        animation: slideUpFade 1.2s ease-out forwards;
    }}
    .footer-box a {{
        color: #3b82f6;
        text-decoration: none;
        font-weight: bold;
        transition: color 0.2s ease;
    }}
    .footer-box a:hover {{
        color: #60a5fa;
        text-decoration: underline;
    }}
    </style>
""", unsafe_allow_html=True)

title_text = "مساعد لوحات التحكم الذكية | Dashboard Co-pilot Agent" if is_ar else "Dashboard Co-pilot Agent"
subtitle_text = "منصة التحليل التفاعلي واقتراحات التصميم الذكية " if is_ar else "Interactive Analytics Suite & Smart Design Copilot"

st.title(title_text)
st.caption(subtitle_text)
st.divider()


upload_label = "قم بتجربة رفع ملف بيانات بصيغة CSV أو Excel" if is_ar else "Upload dataset (CSV or Excel)"
uploaded_file = st.file_uploader(upload_label, type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success("تم قراءة البيانات بنجاح!" if is_ar else "Dataset loaded successfully!")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()


        st.subheader("مؤشرات الأداء الرئيسية (KPI Cards)" if is_ar else "Key Performance Indicator Cards")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_rows = len(df)
        total_cols = len(df.columns)
        max_val = df[numeric_cols[0]].max() if numeric_cols else 0
        mean_val = round(df[numeric_cols[0]].mean(), 1) if numeric_cols else 0
        top_metric_name = numeric_cols[0] if numeric_cols else "Value"

        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">إجمالي السجلات</div>
                <div class="kpi-value">{total_rows}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">عدد الأعمدة</div>
                <div class="kpi-value">{total_cols}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">أعلى قيمة ({top_metric_name})</div>
                <div class="kpi-value">{max_val}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">متوسط ({top_metric_name})</div>
                <div class="kpi-value">{mean_val}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

     
        tab_preview, tab_stats = st.tabs([
            "معاينة البيانات" if is_ar else "Data Preview",
            "الإحصائيات المتقدمة" if is_ar else "Advanced Statistics"
        ])
        with tab_preview:
            st.dataframe(df, use_container_width=True)
        with tab_stats:
            st.dataframe(df.describe(), use_container_width=True)
            
        st.divider()
        
       
        st.subheader("استكشاف البيانات والرسومات التفاعلية" if is_ar else "Interactive Chart Builder")

        if categorical_cols and numeric_cols:
            c_x, c_y, c_type = st.columns(3)
            with c_x:
                x_axis = st.selectbox("المحور الأفقي (X):" if is_ar else "X-Axis:", categorical_cols, index=0)
            with c_y:
                y_axis = st.selectbox("المحور الرأسي (Y):" if is_ar else "Y-Axis:", numeric_cols, index=0)
            with c_type:
                chart_type = st.selectbox(
                    "نوع الرسم البياني:" if is_ar else "Chart Type:",
                    ["شريطي (Bar)", "خطي (Line)", "دائري (Pie)", "مبعثر (Scatter)"]
                )

            single_color = "#3B82F6"

            if "شريطي" in chart_type or "Bar" in chart_type:
                fig = px.bar(df, x=x_axis, y=y_axis)
                fig.update_traces(marker_color=single_color)
            elif "خطي" in chart_type or "Line" in chart_type:
                fig = px.line(df, x=x_axis, y=y_axis)
                fig.update_traces(line=dict(color=single_color, width=3))
            elif "دائري" in chart_type or "Pie" in chart_type:
                fig = px.pie(df, names=x_axis, values=y_axis)
            else:
                fig = px.scatter(df, x=x_axis, y=y_axis)
                fig.update_traces(marker=dict(color=single_color, size=10))
                
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        
        file_name_lower = uploaded_file.name.lower()
        columns_str = " ".join(df.columns.astype(str)).lower()
        combined_text = file_name_lower + " " + columns_str

        if any(k in combined_text for k in ["patient", "hospital", "doctor", "health", "مريض", "مستشفى", "صحي", "طب"]):
            theme_name = "قطاع الرعاية الصحية والطبية (Medical & Healthcare)"
            theme_desc = "تتطلب طابعاً يوحى بالثقة والنظافة والنظام."
            c1, c2, c3 = "#0284C7", "#38BDF8", "#E0F2FE"
        elif any(k in combined_text for k in ["finance", "sales", "revenue", "invoice", "price", "مبيعات", "إيرادات", "فاتورة", "مالية", "سعر"]):
            theme_name = "القطاع المالي والأعمال (Corporate & Finance)"
            theme_desc = "تتطلب درجات احترافية توحي بالاستقرار والثقة الرسمية."
            c1, c2, c3 = "#1E3A8A", "#3B82F6", "#93C5FD"
        elif any(k in combined_text for k in ["hr", "employee", "staff", "salary", "موظف", "رواتب", "ساعات", "ادارة"]):
            theme_name = "الموارد البشرية والإدارية (HR & Operations)"
            theme_desc = "ألوان هادئة ومريحة لبيئة العمل والإنتاجية."
            c1, c2, c3 = "#065F46", "#10B981", "#A7F3D0"
        else:
            theme_name = "لوحة التحليلات العامة (General Analytics)"
            theme_desc = "لوحة ألوان عصرية ومتوازنة تناسب مختلف أنواع البيانات."
            c1, c2, c3 = "#4C1D95", "#8B5CF6", "#DDD6FE"

        st.subheader("التوصيات واقتراحات التصميم الذكية حسب محتوى ملفك" if is_ar else "Smart Contextual Design Recommendations")
        
        r_tab1, r_tab2, r_tab3 = st.tabs([
            "لوحة الألوان المقترحة لبياناتك" if is_ar else "Contextual Color Palette",
            "البطاقات والمؤشرات" if is_ar else "KPI Cards",
            "أفضل المخططات" if is_ar else "Recommended Charts"
        ])

        with r_tab1:
            st.info(f"تم تحليل محتوى الملف واكتشاف المجال: {theme_name}\n\nالسبب: {theme_desc}")
            st.markdown("إليك لوحة الألوان المخصصة والمقترحة لتصميم هذا الداشبورد باحترافية (مرر الماوس أو انقر لرؤية كود HEX):")
            st.markdown(f"""
            * **باليتة الألوان الموصى بها لمجالك:** 
              <span class="color-box" style="background-color: {c1};" title="{c1}"></span>
              <span class="color-box" style="background-color: {c2};" title="{c2}"></span>
              <span class="color-box" style="background-color: {c3};" title="{c3}"></span>
            """, unsafe_allow_html=True)

        with r_tab2:
            st.markdown("""
            * **بطاقات الأرقام الكبيرة (Big Stat Cards):** يفضل وضعها في قمة الداشبورد بخلفية داكنة وموحدة لإبراز إجمالي السجلات والمتوسطات فوراً.
            * **التصميم الموحد:** الحفاظ على بساطة البطاقات وعدم حشوها بأكواد برمجية لتبقى مريحة للعين وقابلة للقراءة السريعة.
            """)

        with r_tab3:
            st.markdown("""
            * **Bar Chart:** مثالي للمقارنات المباشرة بين الفئات والأنشطة بلون موحد.
            * **Line Chart:** رائع لتتبع مسار القيم عبر الزمن بدون تشتت بصري.
            """)

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("بانتظار رفع ملف بيانات للبدء في صياغة التحليلات واللوحات." if is_ar else "Awaiting dataset upload.")

st.markdown("""
<div class="footer-box">
    Developed with by <b>Wajd Al-Luhaibi</b> | Dashboard Co-pilot Agent<br>
    🔗 Follow on X: <a href="https://x.com/wajd_cs" target="_blank">@wajd_cs</a>
</div>
""", unsafe_allow_html=True)