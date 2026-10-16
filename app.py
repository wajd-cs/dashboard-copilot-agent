import html
import io
import itertools
import os
import re
import warnings
import zlib
 
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
 
load_dotenv()
 
st.set_page_config(
    page_title="Dashboard Co-pilot Agent | Wajd",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]
 
TEXT = {
    "ar": {
        "title": "مساعد لوحات التحكم الذكية",
        "subtitle": "منصة التحليل التفاعلي واقتراحات التصميم الذكية",
        "upload": "ارفع ملف بيانات بصيغة CSV أو Excel",
        "loaded": "تم قراءة البيانات بنجاح: {rows} صف و {cols} عمود",
        "read_error": "تعذّرت قراءة الملف:",
        "empty": "الملف فارغ، لا توجد بيانات لعرضها.",
        "awaiting": "ارفع ملف بيانات للبدء في التحليل وصياغة اللوحات.",
        "filters": "الفلاتر",
        "all": "الكل",
        "date_range": "الفترة الزمنية",
        "num_filter": "فلترة حسب عمود رقمي",
        "none": "بدون",
        "active_filters": "الفلاتر النشطة:",
        "chart_filter": "تحديد من الرسم:",
        "reset_all": "مسح كل الفلاتر",
        "clear_chart": "إلغاء تحديد الرسم",
        "no_rows": "لا توجد بيانات تطابق الفلاتر الحالية. جرّب تخفيفها.",
        "kpi_header": "مؤشرات الأداء الرئيسية",
        "kpi_metric": "العمود الرقمي للمؤشرات",
        "compare_by": "المقارنة حسب",
        "period_M": "شهر",
        "period_Q": "ربع سنة",
        "period_Y": "سنة",
        "rows": "إجمالي السجلات",
        "total": "المجموع",
        "mean": "المتوسط",
        "max": "أعلى قيمة",
        "missing": "القيم المفقودة",
        "duplicates": "الصفوف المكررة",
        "cols_sub": "{n} عمود",
        "of_total": "{p}٪ من الإجمالي",
        "vs_overall": "عن المتوسط العام",
        "min_sub": "أقل قيمة: {v}",
        "period_card": "{m} في {p}",
        "vs_prev": "عن نفس الفترة من {p}",
        "no_prev": "لا توجد فترة سابقة للمقارنة",
        "missing_sub": "من أصل {n} خلية",
        "dup_sub": "من أصل {n} صف",
        "preview": "معاينة البيانات",
        "stats": "الإحصائيات",
        "no_numeric": "لا توجد أعمدة رقمية في هذا الملف.",
        "download_csv": "تحميل CSV",
        "download_xlsx": "تحميل Excel",
        "chart_header": "منشئ الرسوم التفاعلية",
        "click_hint": "اضغط على عمود أو شريحة في الرسم لفلترة الداشبورد كاملاً.",
        "scatter_hint": "الفلترة بالضغط متاحة في الرسوم الشريطية والخطية والدائرية.",
        "chart_type": "نوع الرسم",
        "x": "المحور الأفقي (X)",
        "y": "المحور الرأسي (Y)",
        "agg": "طريقة التجميع",
        "sum": "المجموع",
        "avg": "المتوسط",
        "count": "العدد",
        "bar": "شريطي (Bar)",
        "line": "خطي (Line)",
        "pie": "دائري (Pie)",
        "scatter": "مبعثر (Scatter)",
        "need_cat": "هذا الرسم يحتاج عموداً نصياً أو تاريخاً، وعموداً رقمياً.",
        "need_two_num": "الرسم المبعثر يحتاج عمودين رقميين على الأقل.",
        "top_note": "يعرض الرسم أعلى {n} فئة فقط.",
        "pie_note": "يعرض الرسم أعلى {n} فئات، والباقي مجمّع تحت «أخرى».",
        "other": "أخرى",
        "rec_header": "توصيات التصميم حسب محتوى ملفك",
        "tab_palette": "لوحة الألوان",
        "tab_kpi": "البطاقات والمؤشرات",
        "tab_charts": "أفضل المخططات",
        "detected": "المجال المكتشف:",
        "reason": "السبب:",
        "palette_intro": "الألوان المقترحة لهذا الداشبورد (وهي نفس ألوان الرسم أعلاه):",
        "kpi_suggest": "أعمدة مرشّحة لتكون مؤشرات رئيسية:",
        "kpi_tips": (
            "- ضع بطاقات الأرقام الكبيرة في أعلى الداشبورد بخلفية موحدة.\n"
            "- لا تزد عن 4–5 بطاقات حتى تبقى اللوحة سهلة القراءة.\n"
            "- اكتب الوحدة بجانب الرقم (ريال، ٪، يوم) لتوضيح المعنى."
        ),
        "rec_line": "**Line Chart** على `{col}` لتتبع التغيّر عبر الزمن.",
        "rec_pie": "**Donut Chart** على `{col}` لأن عدد فئاته قليل ({n}).",
        "rec_bar": "**Bar Chart** لمقارنة `{y}` بين فئات `{x}`.",
        "rec_scatter": "**Scatter** بين `{a}` و `{b}` لاكتشاف العلاقة بينهما.",
        "rec_none": "لا توجد أعمدة كافية لاقتراح مخططات.",
        "chat_header": "مساعد الدوال والبيانات",
        "chat_caption": "اسألني عن دوال الإكسل أو أكواد Pandas — أعرف أعمدة ملفك والفلاتر المطبّقة.",
        "chat_placeholder": "اكتب سؤالك هنا...",
        "thinking": "جاري التفكير...",
        "no_key": "لم يتم ضبط مفتاح GEMINI_API_KEY، لذلك المساعد غير مفعّل حالياً.",
        "ai_error": "تعذّر الحصول على رد من المساعد. حاول مرة ثانية.",
        "ai_busy": "المساعد عليه ضغط كبير الحين. حاول مرة ثانية بعد دقيقة.",
        "ai_quota": "وصل المساعد للحد المسموح مؤقتاً. حاول مرة ثانية بعد شوي.",
        "clear_chat": "مسح المحادثة",
        "clear_short": "مسح",
        "welcome_title": "أهلاً بك",
        "welcome_desc": "Dashboard Co-pilot يحوّل ملف بياناتك إلى لوحة تحكم تفاعلية خلال ثوانٍ، بدون أي برمجة.",
        "welcome_points": [
            "ارفع ملف CSV أو Excel وشوف أهم الأرقام فوراً.",
            "فلتر بياناتك واضغط على الرسوم لاستكشافها، مثل Power BI.",
            "احصل على اقتراحات للألوان والمؤشرات والرسوم المناسبة لبياناتك.",
            "اسأل المساعد الذكي عن دوال الإكسل وأكواد Pandas.",
            "حمّل بياناتك بعد الفلترة كملف CSV أو Excel.",
        ],
        "start": "ابدأ",
        "lang_switched": "تم التبديل إلى العربية",
        "chat_button": "المساعد الذكي",
        "send": "إرسال",
        "chat_welcome": "أهلاً! أنا مساعدك في تحليل البيانات. اسألني عن دوال الإكسل أو أكواد Pandas، أو اختر سؤالاً جاهزاً من تحت.",
    },
    "en": {
        "title": "Dashboard Co-pilot Agent",
        "subtitle": "Interactive Analytics Suite & Smart Design Copilot",
        "upload": "Upload a dataset (CSV or Excel)",
        "loaded": "Dataset loaded: {rows} rows and {cols} columns",
        "read_error": "Could not read the file:",
        "empty": "The file is empty — nothing to show.",
        "awaiting": "Upload a dataset to start building insights and dashboards.",
        "filters": "Filters",
        "all": "All",
        "date_range": "Date range",
        "num_filter": "Filter by a numeric column",
        "none": "None",
        "active_filters": "Active filters:",
        "chart_filter": "Selected on chart:",
        "reset_all": "Clear all filters",
        "clear_chart": "Clear chart selection",
        "no_rows": "No rows match the current filters. Try loosening them.",
        "kpi_header": "Key Performance Indicators",
        "kpi_metric": "Numeric column for KPIs",
        "compare_by": "Compare by",
        "period_M": "Month",
        "period_Q": "Quarter",
        "period_Y": "Year",
        "rows": "Total Records",
        "total": "Total",
        "mean": "Average",
        "max": "Max",
        "missing": "Missing Values",
        "duplicates": "Duplicate Rows",
        "cols_sub": "{n} columns",
        "of_total": "{p}% of total",
        "vs_overall": "vs overall average",
        "min_sub": "Min: {v}",
        "period_card": "{m} in {p}",
        "vs_prev": "vs same point in {p}",
        "no_prev": "No previous period to compare",
        "missing_sub": "out of {n} cells",
        "dup_sub": "out of {n} rows",
        "preview": "Data Preview",
        "stats": "Statistics",
        "no_numeric": "This file has no numeric columns.",
        "download_csv": "Download CSV",
        "download_xlsx": "Download Excel",
        "chart_header": "Interactive Chart Builder",
        "click_hint": "Tap a bar, point or slice to filter the whole dashboard.",
        "scatter_hint": "Click-to-filter works on bar, line and pie charts.",
        "chart_type": "Chart type",
        "x": "X-Axis",
        "y": "Y-Axis",
        "agg": "Aggregation",
        "sum": "Sum",
        "avg": "Average",
        "count": "Count",
        "bar": "Bar",
        "line": "Line",
        "pie": "Pie",
        "scatter": "Scatter",
        "need_cat": "This chart needs a text or date column and a numeric column.",
        "need_two_num": "A scatter chart needs at least two numeric columns.",
        "top_note": "Showing the top {n} categories only.",
        "pie_note": "Showing the top {n} categories; the rest are grouped as “Other”.",
        "other": "Other",
        "rec_header": "Smart Design Recommendations for Your File",
        "tab_palette": "Color Palette",
        "tab_kpi": "KPI Cards",
        "tab_charts": "Recommended Charts",
        "detected": "Detected domain:",
        "reason": "Why:",
        "palette_intro": "Suggested colors for this dashboard (the same ones used in the chart above):",
        "kpi_suggest": "Columns that make good headline KPIs:",
        "kpi_tips": (
            "- Put big-number cards at the top of the dashboard with a consistent background.\n"
            "- Keep it to 4–5 cards so the dashboard stays easy to scan.\n"
            "- Show the unit next to the number (SAR, %, days) so it's clear."
        ),
        "rec_line": "**Line Chart** on `{col}` to track change over time.",
        "rec_pie": "**Donut Chart** on `{col}` because it has few categories ({n}).",
        "rec_bar": "**Bar Chart** comparing `{y}` across `{x}`.",
        "rec_scatter": "**Scatter** of `{a}` vs `{b}` to spot a relationship.",
        "rec_none": "Not enough columns to recommend charts.",
        "chat_header": "Formulas & Data Assistant",
        "chat_caption": "Ask me about Excel formulas or Pandas code — I know your file's columns and active filters.",
        "chat_placeholder": "Ask your question...",
        "thinking": "Thinking...",
        "no_key": "GEMINI_API_KEY is not set, so the assistant is currently disabled.",
        "ai_error": "Couldn't get a reply from the assistant. Please try again.",
        "ai_busy": "The assistant is very busy right now. Please try again in a minute.",
        "ai_quota": "The assistant has reached its usage limit for now. Please try again shortly.",
        "clear_chat": "Clear chat",
        "clear_short": "Clear",
        "welcome_title": "Welcome",
        "welcome_desc": "Dashboard Co-pilot turns your data file into an interactive dashboard in seconds, with no coding needed.",
        "welcome_points": [
            "Upload a CSV or Excel file and see the key numbers instantly.",
            "Filter your data and click charts to explore it, like Power BI.",
            "Get color, KPI and chart suggestions that fit your data.",
            "Ask the AI assistant about Excel formulas and Pandas code.",
            "Download your filtered data as CSV or Excel.",
        ],
        "start": "Start",
        "lang_switched": "Switched to English",
        "chat_button": "Ask the assistant",
        "send": "Send",
        "chat_welcome": "Hi! I'm your data-analysis assistant. Ask me about Excel formulas or Pandas code, or pick a ready-made question below.",
    },
}
 
OTHER_LABELS = {TEXT["ar"]["other"], TEXT["en"]["other"]}
 
DOMAINS = [
    {
        "keys": ["patient", "hospital", "doctor", "health", "clinic", "medical",
                 "diagnosis", "مريض", "مستشفى", "صحي", "طبيب", "عيادة", "تشخيص"],
        "name": {"ar": "الرعاية الصحية والطبية", "en": "Medical & Healthcare"},
        "desc": {"ar": "تتطلب طابعاً يوحي بالثقة والنظافة والنظام.",
                 "en": "Calls for a look that feels trustworthy, clean and orderly."},
        "colors": ("#0284C7", "#38BDF8", "#E0F2FE"),
    },
    {
        "keys": ["finance", "sales", "revenue", "invoice", "price", "profit", "cost",
                 "مبيعات", "إيرادات", "فاتورة", "مالية", "سعر", "السعر", "ربح", "تكلفة"],
        "name": {"ar": "القطاع المالي والأعمال", "en": "Corporate & Finance"},
        "desc": {"ar": "تتطلب درجات احترافية توحي بالاستقرار والثقة الرسمية.",
                 "en": "Calls for professional tones that signal stability and trust."},
        "colors": ("#1E3A8A", "#3B82F6", "#93C5FD"),
    },
    {
        "keys": ["hr", "employee", "staff", "salary", "department", "attendance",
                 "موظف", "رواتب", "راتب", "ساعات", "ادارة", "قسم", "حضور"],
        "name": {"ar": "الموارد البشرية والإدارية", "en": "HR & Operations"},
        "desc": {"ar": "ألوان هادئة ومريحة لبيئة العمل والإنتاجية.",
                 "en": "Calm, comfortable colors suited to workplace and productivity data."},
        "colors": ("#065F46", "#10B981", "#A7F3D0"),
    },
]
 
GENERAL_DOMAIN = {
    "name": {"ar": "لوحة التحليلات العامة", "en": "General Analytics"},
    "desc": {"ar": "لوحة ألوان عصرية ومتوازنة تناسب مختلف أنواع البيانات.",
             "en": "A modern, balanced palette that suits most kinds of data."},
    "colors": ("#4C1D95", "#8B5CF6", "#DDD6FE"),
}
 
DATE_HINTS = ("date", "time", "month", "year", "day", "تاريخ", "شهر", "سنة", "يوم", "وقت")
MAX_FILTER_CATEGORIES = 50
MAX_CATEGORY_FILTERS = 4
 
st.session_state.setdefault("lang", "en")
st.session_state.setdefault("messages", [])
st.session_state.setdefault("filter_ver", 0)
st.session_state.setdefault("chart_ver", 0)
 
 
def t(key):
    return TEXT[st.session_state.lang][key]
 
 
@st.cache_data(show_spinner=False)
def load_data(file_bytes, name):
    buffer = io.BytesIO(file_bytes)
    if name.lower().endswith(".csv"):
        try:
            return pd.read_csv(buffer)
        except UnicodeDecodeError:
            buffer.seek(0)
            return pd.read_csv(buffer, encoding="cp1256")
    return pd.read_excel(buffer)
 
 
def detect_date_columns(df):
    found = list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if any(hint in str(col).lower() for hint in DATE_HINTS):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() >= 0.8:
                df[col] = parsed
                found.append(col)
    return found
 
 
def detect_domain(df, file_name):
    text = (file_name + " " + " ".join(map(str, df.columns))).lower()
    tokens = {tok for tok in re.split(r"[\W_]+", text) if tok}
    for domain in DOMAINS:
        for key in domain["keys"]:
            if key in tokens or (len(key) >= 4 and key in text):
                return domain
    return GENERAL_DOMAIN
 
 
def is_id_column(col):
    return "id" in re.split(r"[\W_]+", str(col).lower())
 
 
def fmt(value):
    if value is None or pd.isna(value):
        return "—"
    value = float(value)
    if value.is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"
 
 
def pct_change(current, previous):
    if previous is None or pd.isna(previous) or previous == 0 or pd.isna(current):
        return None
    return (current - previous) / abs(previous) * 100
 
 
def to_excel_bytes(df):
    out = df.copy()
    for col in out.select_dtypes(include=["datetimetz"]).columns:
        out[col] = out[col].dt.tz_localize(None)
    buffer = io.BytesIO()
    out.to_excel(buffer, index=False)
    return buffer.getvalue()
 
 
def render_filters(df, category_cols, date_cols, numeric_cols, file_key):
    ver = st.session_state.filter_ver
    mask = pd.Series(True, index=df.index)
    active = []
 
    filter_cats = [
        c for c in category_cols
        if c not in date_cols and 1 < df[c].nunique() <= MAX_FILTER_CATEGORIES
    ][:MAX_CATEGORY_FILTERS]
 
    with st.expander(t("filters"), expanded=False):
        grid = st.columns(2)
        slot = 0
 
        if date_cols:
            dcol = date_cols[0]
            dates = df[dcol].dropna()
            if not dates.empty:
                lo, hi = dates.min().date(), dates.max().date()
                with grid[slot % 2]:
                    picked = st.date_input(
                        f"{t('date_range')} ({dcol})",
                        value=(lo, hi), min_value=lo, max_value=hi,
                        key=f"f_{file_key}_{ver}_date",
                    )
                slot += 1
                if isinstance(picked, (list, tuple)) and len(picked) == 2:
                    start, end = picked
                    if (start, end) != (lo, hi):
                        day = df[dcol].dt.date
                        mask &= day.between(start, end)
                        active.append(f"{dcol}: {start} – {end}")
 
        for col in filter_cats:
            options = sorted(df[col].dropna().astype(str).unique())
            with grid[slot % 2]:
                chosen = st.multiselect(
                    str(col), options, placeholder=t("all"),
                    key=f"f_{file_key}_{ver}_cat_{col}",
                )
            slot += 1
            if chosen:
                mask &= df[col].astype(str).isin(chosen)
                shown = "، ".join(chosen[:3]) if st.session_state.lang == "ar" else ", ".join(chosen[:3])
                active.append(f"{col}: {shown}" + (" …" if len(chosen) > 3 else ""))
 
        usable_nums = [c for c in numeric_cols if not is_id_column(c) and df[c].nunique() > 1]
        if usable_nums:
            with grid[slot % 2]:
                num_col = st.selectbox(
                    t("num_filter"), [None] + usable_nums,
                    format_func=lambda c: t("none") if c is None else str(c),
                    key=f"f_{file_key}_{ver}_numcol",
                )
                if num_col is not None:
                    lo, hi = float(df[num_col].min()), float(df[num_col].max())
                    low, high = st.slider(
                        str(num_col), min_value=lo, max_value=hi, value=(lo, hi),
                        key=f"f_{file_key}_{ver}_num_{num_col}",
                    )
                    if (low, high) != (lo, hi):
                        mask &= df[num_col].between(low, high)
                        active.append(f"{num_col}: {fmt(low)} – {fmt(high)}")
 
    return df[mask], active
 
 
def build_chart_key(file_key, chart_type, x_axis, y_axis, agg):
    return f"chart_{file_key}_{st.session_state.chart_ver}_{chart_type}_{x_axis}_{y_axis}_{agg}"
 
 
def expected_chart_key(file_key):
    state = st.session_state
    parts = [state.get(f"cb_{name}_{file_key}") for name in ("type", "x", "y", "agg")]
    if None in parts or parts[0] == "scatter":
        return None
    return build_chart_key(file_key, *parts)
 
 
def get_chart_selection(file_key):
    info = st.session_state.get("active_chart")
    if not info or not info.get("selectable"):
        return None
    if info["key"] != expected_chart_key(file_key):
        return None
    event = st.session_state.get(info["key"])
    if not event:
        return None
    points = (event.get("selection") or {}).get("points") or []
    values = []
    for point in points:
        value = point["label"] if "label" in point else point.get("x")
        if value is not None and value not in OTHER_LABELS and value not in values:
            values.append(value)
    if not values:
        return None
    return {"col": info["x"], "values": values, "is_date": info["is_date"]}
 
 
def apply_chart_selection(df, selection):
    col = selection["col"]
    if col not in df.columns:
        return df
    if selection["is_date"]:
        wanted = pd.to_datetime(pd.Series(selection["values"]), errors="coerce")
        return df[df[col].isin(wanted)]
    wanted = {str(v) for v in selection["values"]}
    return df[df[col].astype(str).isin(wanted)]
 
 
def render_active_filters(active, selection):
    if not active and not selection:
        return
    chips = "".join(f'<span class="chip">{html.escape(a)}</span>' for a in active)
    if selection:
        values = ", ".join(str(v) for v in selection["values"][:3])
        if len(selection["values"]) > 3:
            values += " …"
        chips += (f'<span class="chip chip-chart">{html.escape(t("chart_filter"))} '
                  f'{html.escape(str(selection["col"]))} = {html.escape(values)}</span>')
    st.markdown(
        f'<div class="chips"><span class="chips-label">{html.escape(t("active_filters"))}</span>{chips}</div>',
        unsafe_allow_html=True,
    )
    buttons = st.columns(2)
    if selection and buttons[0].button(t("clear_chart"), key="btn_clear_chart"):
        st.session_state.chart_ver += 1
        st.rerun()
    if buttons[1 if selection else 0].button(t("reset_all"), key="btn_reset_all"):
        st.session_state.filter_ver += 1
        st.session_state.chart_ver += 1
        st.rerun()
 
 
def delta_html(pct, suffix, fallback=""):
    if pct is None:
        return html.escape(fallback)
    cls = "up" if pct > 0 else "down" if pct < 0 else "flat"
    arrow = "▲" if pct > 0 else "▼" if pct < 0 else "■"
    return f'<span class="delta {cls}">{arrow} {abs(pct):.1f}%</span> {html.escape(suffix)}'
 
 
def kpi_grid(cards):
    body = "".join(
        f'<div class="kpi-card"><div class="kpi-title">{html.escape(str(title))}</div>'
        f'<div class="kpi-value">{html.escape(str(value))}</div>'
        f'<div class="kpi-sub">{sub}</div></div>'
        for title, value, sub in cards
    )
    st.markdown(f'<div class="kpi-grid">{body}</div>', unsafe_allow_html=True)
 
 
def share_sub(part, whole, filtered):
    if not filtered or not whole:
        return ""
    return html.escape(t("of_total").format(p=f"{part / whole * 100:.1f}"))
 
 
def render_kpis(view, full, numeric_cols, date_cols, file_key):
    st.subheader(t("kpi_header"))
    filtered = len(view) != len(full)
    metrics = [c for c in numeric_cols if not is_id_column(c)] or numeric_cols
 
    controls = st.columns(2)
    metric = None
    period = None
    if metrics:
        metric = controls[0].selectbox(t("kpi_metric"), metrics, key=f"kpi_metric_{file_key}")
    if date_cols:
        period = controls[1].selectbox(
            t("compare_by"), ["M", "Q", "Y"],
            format_func=lambda p: t(f"period_{p}"), key=f"kpi_period_{file_key}",
        )
 
    cards = [(
        t("rows"), fmt(len(view)),
        share_sub(len(view), len(full), filtered) or html.escape(t("cols_sub").format(n=view.shape[1])),
    )]
 
    if metric is None:
        total_cells = view.size
        cards += [
            (t("missing"), fmt(view.isna().sum().sum()),
             html.escape(t("missing_sub").format(n=fmt(total_cells)))),
            (t("duplicates"), fmt(view.duplicated().sum()),
             html.escape(t("dup_sub").format(n=fmt(len(view))))),
        ]
        kpi_grid(cards)
        return
 
    series = view[metric]
    total = series.sum()
    mean = series.mean()
    overall_mean = full[metric].mean()
 
    cards.append((f"{t('total')} ({metric})", fmt(total),
                  share_sub(total, full[metric].sum(), filtered) or
                  html.escape(t("min_sub").format(v=fmt(series.min())))))
    cards.append((f"{t('mean')} ({metric})", fmt(mean),
                  delta_html(pct_change(mean, overall_mean), t("vs_overall")) if filtered
                  else html.escape(f"{t('max')}: {fmt(series.max())}")))
 
    if period and len(view):
        dates = view[date_cols[0]]
        if getattr(dates.dt, "tz", None) is not None:
            dates = dates.dt.tz_localize(None)
        periods = dates.dt.to_period(period)
        latest = periods.max()
        if pd.notna(latest):
            previous = latest - 1
            elapsed = dates.max() - latest.start_time
            current_value = view.loc[periods == latest, metric].sum()
            prev_mask = (periods == previous) & (dates - previous.start_time <= elapsed)
            prev_value = view.loc[prev_mask, metric].sum() if prev_mask.any() else None
            cards.append((
                t("period_card").format(m=f"{t('total')} {metric}", p=str(latest)),
                fmt(current_value),
                delta_html(pct_change(current_value, prev_value),
                           t("vs_prev").format(p=str(previous)), fallback=t("no_prev")),
            ))
    if len(cards) < 4:
        cards.append((f"{t('max')} ({metric})", fmt(series.max()),
                      html.escape(t("min_sub").format(v=fmt(series.min())))))
 
    kpi_grid(cards)
 
 
def render_tables(view, numeric_cols, file_name):
    tab_preview, tab_stats = st.tabs([t("preview"), t("stats")])
    with tab_preview:
        st.dataframe(view, width="stretch", hide_index=True)
        base = os.path.splitext(file_name)[0] or "data"
        buttons = st.columns(2)
        buttons[0].download_button(
            t("download_csv"),
            data=view.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{base}_filtered.csv",
            mime="text/csv",
            key="dl_csv",
        )
        try:
            buttons[1].download_button(
                t("download_xlsx"),
                data=to_excel_bytes(view),
                file_name=f"{base}_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_xlsx",
            )
        except Exception:
            pass
    with tab_stats:
        if numeric_cols:
            st.dataframe(view[numeric_cols].describe().round(2), width="stretch")
        else:
            st.info(t("no_numeric"))
 
 
def style_figure(fig):
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="top", y=-0.15),
        dragmode=False,
    )
    return fig
 
 
def render_chart_builder(df, numeric_cols, category_cols, date_cols, colors, file_key):
    st.subheader(t("chart_header"))
    numeric_cols = [c for c in numeric_cols if not is_id_column(c)] + \
                   [c for c in numeric_cols if is_id_column(c)]
    controls = st.columns(4)
    chart_type = controls[0].selectbox(
        t("chart_type"), ["bar", "line", "pie", "scatter"], format_func=t, key=f"cb_type_{file_key}",
    )
 
    if chart_type == "scatter":
        st.caption(t("scatter_hint"))
        if len(numeric_cols) < 2:
            st.info(t("need_two_num"))
            st.session_state.active_chart = None
            return
        x_axis = controls[1].selectbox(t("x"), numeric_cols, index=0, key=f"cb_sx_{file_key}")
        y_axis = controls[2].selectbox(t("y"), numeric_cols, index=1, key=f"cb_sy_{file_key}")
        fig = px.scatter(df, x=x_axis, y=y_axis, color_discrete_sequence=[colors[0]])
        fig.update_traces(marker=dict(size=9, opacity=0.75))
        st.session_state.active_chart = None
        st.plotly_chart(style_figure(fig), width="stretch", config={"displaylogo": False})
        return
 
    x_options = date_cols + [c for c in category_cols if c not in date_cols]
    if not x_options or not numeric_cols:
        st.info(t("need_cat"))
        st.session_state.active_chart = None
        return
 
    default_x = len(date_cols) % len(x_options)
    x_axis = controls[1].selectbox(t("x"), x_options, index=default_x, key=f"cb_x_{file_key}")
    y_axis = controls[2].selectbox(t("y"), numeric_cols, key=f"cb_y_{file_key}")
    agg = controls[3].selectbox(
        t("agg"), ["sum", "mean", "count"],
        format_func=lambda k: t({"sum": "sum", "mean": "avg", "count": "count"}[k]),
        key=f"cb_agg_{file_key}",
    )
    st.caption(t("click_hint"))
 
    grouped = df.groupby(x_axis, as_index=False, dropna=True)[y_axis].agg(agg)
    is_date = x_axis in date_cols
 
    if chart_type == "pie":
        limit = 10
        grouped = grouped.sort_values(y_axis, ascending=False)
        if len(grouped) > limit:
            rest = grouped.iloc[limit:][y_axis].sum()
            grouped = grouped.iloc[:limit].copy()
            grouped[x_axis] = grouped[x_axis].astype(str)
            other_row = pd.DataFrame({x_axis: [t("other")], y_axis: [rest]})
            grouped = pd.concat([grouped, other_row], ignore_index=True)
            st.caption(t("pie_note").format(n=limit))
        fig = px.pie(grouped, names=x_axis, values=y_axis, hole=0.45,
                     color_discrete_sequence=list(colors) + px.colors.qualitative.Pastel)
    elif chart_type == "line" or is_date:
        grouped = grouped.sort_values(x_axis)
        if chart_type == "line":
            fig = px.line(grouped, x=x_axis, y=y_axis, markers=True, color_discrete_sequence=[colors[0]])
            fig.update_traces(line=dict(width=3), marker=dict(size=9))
        else:
            fig = px.bar(grouped, x=x_axis, y=y_axis, color_discrete_sequence=[colors[0]])
    else:
        limit = 20
        grouped = grouped.sort_values(y_axis, ascending=False)
        if len(grouped) > limit:
            grouped = grouped.head(limit)
            st.caption(t("top_note").format(n=limit))
        fig = px.bar(grouped, x=x_axis, y=y_axis, color_discrete_sequence=[colors[0]])
 
    chart_key = build_chart_key(file_key, chart_type, x_axis, y_axis, agg)
    st.session_state.active_chart = {"key": chart_key, "x": x_axis, "is_date": is_date, "selectable": True}
    st.plotly_chart(
        style_figure(fig), width="stretch", key=chart_key,
        on_select="rerun", selection_mode="points",
        config={"displaylogo": False},
    )
 
 
def render_recommendations(df, numeric_cols, category_cols, date_cols, domain):
    lang = st.session_state.lang
    st.subheader(t("rec_header"))
    tab_palette, tab_kpi, tab_charts = st.tabs([t("tab_palette"), t("tab_kpi"), t("tab_charts")])
 
    with tab_palette:
        st.info(f"**{t('detected')}** {domain['name'][lang]}\n\n**{t('reason')}** {domain['desc'][lang]}")
        st.markdown(t("palette_intro"))
        swatches = "".join(
            f'<div class="swatch"><span class="color-box" style="background-color:{c};"></span>'
            f"<code>{c}</code></div>"
            for c in domain["colors"]
        )
        st.markdown(f'<div class="palette">{swatches}</div>', unsafe_allow_html=True)
 
    with tab_kpi:
        candidates = [c for c in numeric_cols if not is_id_column(c)][:4]
        if candidates:
            sep = "، " if lang == "ar" else ", "
            st.markdown(t("kpi_suggest") + " " + sep.join(f"`{c}`" for c in candidates))
        st.markdown(t("kpi_tips"))
 
    with tab_charts:
        recs = []
        text_cats = [c for c in category_cols if c not in date_cols]
        if date_cols and numeric_cols:
            recs.append(t("rec_line").format(col=date_cols[0]))
        small = [c for c in text_cats if 2 <= df[c].nunique() <= 6]
        if small and numeric_cols:
            recs.append(t("rec_pie").format(col=small[0], n=df[small[0]].nunique()))
        if text_cats and numeric_cols:
            recs.append(t("rec_bar").format(x=text_cats[0], y=numeric_cols[0]))
        if len(numeric_cols) >= 2:
            recs.append(t("rec_scatter").format(a=numeric_cols[0], b=numeric_cols[1]))
        st.markdown("\n".join(f"- {r}" for r in recs) if recs else t("rec_none"))
 
 
def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")
 
 
@st.cache_resource(show_spinner=False)
def get_client(api_key):
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=60_000))
 
 
def dataset_context(view, full, file_name, active_filters):
    if view is None:
        return "No dataset uploaded yet."
    parts = [
        f"File: {file_name}",
        f"Full dataset: {full.shape[0]} rows x {full.shape[1]} columns",
    ]
    if active_filters:
        parts.append(f"Active filters: {'; '.join(active_filters)} → {len(view)} rows in the current view")
    parts += [
        "Columns and types:\n" + "\n".join(f"- {c}: {d}" for c, d in full.dtypes.astype(str).items()),
        "First rows of the current view:\n" + view.head(5).to_string(max_colwidth=40),
    ]
    numeric = view.select_dtypes(include="number")
    if not numeric.empty:
        parts.append("Numeric summary of the current view:\n" + numeric.describe().round(2).to_string())
    return "\n\n".join(parts)[:6000]
 
 
def stream_gemini(question, history, context):
    api_key = get_api_key()
    if not api_key:
        yield t("no_key")
        return
 
    language = "Arabic" if st.session_state.lang == "ar" else "English"
    past = "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])
    prompt = f"""You are the assistant inside "Dashboard Co-pilot", a data-analysis app.
Reply in {language}, concisely, using Markdown.
When useful, give both the Excel formula and the Pandas code, using the real column names from the dataset.
If something can't be answered from the dataset, say so instead of inventing numbers.
 
Dataset:
{context}
 
Conversation so far:
{past or "(none)"}
 
User question: {question}"""
 
    client = get_client(api_key)
    fast = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="low"))
    models = [GEMINI_MODEL] + [m for m in FALLBACK_MODELS if m != GEMINI_MODEL]
    attempts = [(m, c) for m in models for c in (fast, None)]
    last_error = None
    skip_model = None
    for model, config in attempts:
        if model == skip_model:
            continue
        got_text = False
        try:
            for chunk in client.models.generate_content_stream(model=model, contents=prompt, config=config):
                if chunk.text:
                    got_text = True
                    yield chunk.text
            if got_text:
                return
        except Exception as error:
            last_error = error
            print(f"Gemini error on {model}: {error}")
            if got_text:
                yield "\n\n" + friendly_error(error)
                return
            if is_capacity_error(error):
                skip_model = model
    yield friendly_error(last_error)
 
 
def is_capacity_error(error):
    text = str(error).upper()
    return any(k in text for k in ("503", "UNAVAILABLE", "OVERLOADED", "429", "RESOURCE_EXHAUSTED", "404", "NOT_FOUND"))
 
 
def friendly_error(error):
    text = str(error).upper() if error else ""
    if any(k in text for k in ("429", "RESOURCE_EXHAUSTED", "QUOTA")):
        return t("ai_quota")
    if any(k in text for k in ("503", "UNAVAILABLE", "OVERLOADED", "TIMEOUT", "TIMED OUT", "DEADLINE")):
        return t("ai_busy")
    return t("ai_error")
 
 
SUGGESTIONS = {
    "ar": ["لخّص لي البيانات المرفوعة", "وش أهم المؤشرات اللي أركز عليها؟", "كيف أحسب المتوسط في إكسل وPandas؟"],
    "en": ["Summarize my uploaded data", "Which KPIs should I focus on?", "How do I compute an average in Excel and Pandas?"],
}
 
 
def queue_question(text):
    text = (text or "").strip()
    if text:
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.awaiting_reply = True
 
 
def submit_chat():
    queue_question(st.session_state.get("chat_text", ""))
 
 
def clear_chat():
    st.session_state.messages = []
    st.session_state.awaiting_reply = False
 
 
def render_chat_widget(context):
    messages = st.session_state.messages
    with st.container(key="chat_fab"):
        with st.popover(t("chat_button")):
            head = st.columns([3, 1], vertical_alignment="center")
            head[0].markdown(f"**{t('chat_header')}**")
            if messages:
                head[1].button(t("clear_short"), key="btn_clear_chat", on_click=clear_chat, help=t("clear_chat"))
 
            with st.container(height=280, border=False):
                if not messages:
                    with st.chat_message("assistant"):
                        st.markdown(t("chat_welcome"))
                    with st.container(key="chat_suggestions"):
                        for i, suggestion in enumerate(SUGGESTIONS[st.session_state.lang]):
                            st.button(suggestion, key=f"chat_suggest_{i}",
                                      on_click=queue_question, args=(suggestion,))
                for message in messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                if st.session_state.get("awaiting_reply") and messages:
                    with st.chat_message("assistant"):
                        pieces = stream_gemini(messages[-1]["content"], messages[:-1], context)
                        with st.spinner(t("thinking")):
                            first = next(pieces, "")
                        reply = st.write_stream(itertools.chain([first], pieces))
                    messages.append({"role": "assistant", "content": reply})
                    st.session_state.awaiting_reply = False
 
            with st.form("chat_form", clear_on_submit=True, border=False):
                st.text_input(t("chat_header"), key="chat_text",
                              placeholder=t("chat_placeholder"), label_visibility="collapsed")
                st.form_submit_button(t("send"), on_click=submit_chat)
 
 
LANG_LABELS = {"ar": "ع", "en": "EN"}
 
 
def on_lang_change():
    choice = st.session_state.lang_choice
    if choice is None:
        st.session_state.lang_choice = st.session_state.lang
        return
    if choice != st.session_state.lang:
        st.session_state.lang = choice
        st.session_state.lang_toast = True
 
 
st.session_state.setdefault("started", False)
 
 
def pick_language(code):
    st.session_state.lang = code
    st.session_state.lang_choice = code
 
 
def start_app():
    st.session_state.started = True
 
 
def render_welcome():
    lang = st.session_state.lang
    with st.container(key="welcome_card"):
        st.markdown(
            '<div class="welcome-top">'
            '<span class="welcome-dot"></span>'
            '<span class="welcome-brand">Dashboard Co-pilot Agent</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.container(key="welcome_lang"):
            pills = st.columns(2)
            pills[0].button("English", key="pick_en", on_click=pick_language, args=("en",),
                            type="primary" if lang == "en" else "secondary")
            pills[1].button("العربية", key="pick_ar", on_click=pick_language, args=("ar",),
                            type="primary" if lang == "ar" else "secondary")
 
        features = "".join(
            f'<div class="welcome-feature" style="--i:{i}">'
            f'<span class="welcome-num">{i + 1:02d}</span>'
            f'<span class="welcome-feature-text">{html.escape(point)}</span></div>'
            for i, point in enumerate(t("welcome_points"))
        )
        st.markdown(
            f'<div class="welcome-body">'
            f'<h2 class="welcome-title">{html.escape(t("welcome_title"))}</h2>'
            f'<p class="welcome-desc">{html.escape(t("welcome_desc"))}</p>'
            f'<div class="welcome-features">{features}</div></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="welcome_start"):
            st.button(t("start"), key="btn_start", on_click=start_app, type="primary")
 
 
if st.session_state.started:
    st.session_state.setdefault("lang_choice", st.session_state.lang)
    with st.container(key="lang_switch"):
        st.segmented_control(
            "Language",
            options=["ar", "en"],
            format_func=LANG_LABELS.get,
            key="lang_choice",
            on_change=on_lang_change,
            label_visibility="collapsed",
        )
 
    if st.session_state.pop("lang_toast", False):
        st.toast(t("lang_switched"))
 
is_ar = st.session_state.lang == "ar"
 
CSS = """
<style>
@keyframes slideUpFade {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.stApp { direction: __DIR__; }
[data-testid="stToolbar"], [data-testid="stHeader"], [data-testid="stDecoration"] { display: none !important; }
.stApp .stMarkdown, .stApp h1, .stApp h2, .stApp h3,
.stApp [data-testid="stCaptionContainer"] { text-align: __ALIGN__; }
 
[data-testid="stDataFrame"], .js-plotly-plot, .stApp pre, .stApp code {
    direction: ltr; text-align: left; unicode-bidi: isolate;
}
 
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin: 8px 0 18px;
    animation: slideUpFade .8s cubic-bezier(.16, 1, .3, 1) both;
}
.kpi-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(59, 130, 246, .3);
    border-radius: 14px;
    padding: 18px 14px;
    box-shadow: 0 10px 20px -5px rgba(0, 0, 0, .3);
    text-align: center;
    transition: transform .3s ease, box-shadow .3s ease;
}
.kpi-card:hover { transform: translateY(-6px); box-shadow: 0 15px 30px -5px rgba(59, 130, 246, .4); }
.kpi-title { color: #94a3b8; font-size: .9rem; font-weight: 600; margin-bottom: 6px; overflow-wrap: anywhere; }
.kpi-value { color: #38bdf8; font-size: 1.8rem; font-weight: 700; overflow-wrap: anywhere; }
.kpi-sub { color: #94a3b8; font-size: .8rem; margin-top: 6px; min-height: 1.1em; overflow-wrap: anywhere; }
.delta { font-weight: 700; direction: ltr; unicode-bidi: isolate; white-space: nowrap; }
.delta.up { color: #34d399; }
.delta.down { color: #f87171; }
.delta.flat { color: #cbd5e1; }
 
.chips { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 4px 0 10px; }
.chips-label { color: #94a3b8; font-size: .85rem; font-weight: 600; }
.chip {
    background: rgba(59, 130, 246, .15); color: #bfdbfe;
    border: 1px solid rgba(59, 130, 246, .35);
    border-radius: 999px; padding: 4px 12px; font-size: .82rem;
    overflow-wrap: anywhere;
}
.chip-chart { background: rgba(16, 185, 129, .15); color: #a7f3d0; border-color: rgba(16, 185, 129, .4); }
 
.palette { display: flex; flex-wrap: wrap; gap: 16px; margin: 6px 0 4px; }
.swatch { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.color-box {
    display: inline-block; width: 44px; height: 44px; border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, .2);
    transition: transform .3s cubic-bezier(.175, .885, .32, 1.275), box-shadow .3s ease;
}
.color-box:hover { transform: scale(1.2) rotate(5deg); box-shadow: 0 8px 20px rgba(59, 130, 246, .5); }
 
.footer-box {
    margin-top: 48px; padding: 22px; text-align: center;
    border-top: 1px solid rgba(100, 116, 139, .3); font-size: 1rem;
}
.footer-box a { color: #3b82f6; text-decoration: none; font-weight: 700; }
.footer-box a:hover { color: #60a5fa; text-decoration: underline; }
 
.st-key-chat_fab,
div:has(> .st-key-chat_fab) {
    position: fixed !important; bottom: 22px; __SIDE__: 22px; top: auto !important;
    z-index: 999990; width: auto !important; height: auto !important; margin: 0 !important;
}
.st-key-chat_fab button {
    width: auto !important;
    border-radius: 999px; padding: .7rem 1.25rem; border: none;
    background: linear-gradient(135deg, #2563eb, #3b82f6); color: #fff; font-weight: 700;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, .6);
    transition: transform .2s ease, filter .2s ease;
}
.st-key-chat_fab button:hover { transform: translateY(-2px); filter: brightness(1.1); color: #fff; }
[data-testid="stPopoverBody"] {
    width: min(400px, calc(100vw - 32px)) !important;
    max-width: none !important;
    max-height: min(560px, calc(100vh - 110px));
    overflow-y: auto;
    direction: __DIR__;
}
.st-key-chat_suggestions { gap: 6px; }
.st-key-chat_suggestions button {
    width: 100%; justify-content: flex-start; text-align: __ALIGN__;
    border-radius: 12px; padding: .35rem .8rem; min-height: 0; font-size: .85rem;
    background: rgba(59, 130, 246, .1); border: 1px solid rgba(59, 130, 246, .35);
}
.st-key-chat_suggestions button:hover { background: rgba(59, 130, 246, .22); border-color: #3b82f6; }
[data-testid="stPopoverBody"] [data-testid="stFormSubmitButton"] button { width: 100%; }
 
.st-key-lang_switch { display: flex; align-items: flex-end; }
.st-key-lang_switch [data-testid="stButtonGroup"] {
    background: rgba(30, 41, 59, .85); border: 1px solid rgba(59, 130, 246, .3);
    border-radius: 999px; padding: 4px; gap: 4px; width: fit-content;
    box-shadow: 0 6px 18px -6px rgba(0, 0, 0, .5);
}
.st-key-lang_switch button {
    border: none !important; border-radius: 999px !important;
    padding: .35rem 1rem !important; min-height: 0 !important;
    background: transparent !important; color: #94a3b8 !important; font-weight: 600;
    transition: background .35s ease, color .35s ease, transform .2s ease, box-shadow .35s ease;
}
.st-key-lang_switch button:hover { color: #e2e8f0 !important; transform: translateY(-1px); }
.st-key-lang_switch button[data-testid$="Active"] {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important; color: #fff !important;
    box-shadow: 0 4px 14px -2px rgba(37, 99, 235, .65);
}
@keyframes langFade_ar { from { opacity: .25; } to { opacity: 1; } }
@keyframes langFade_en { from { opacity: .25; } to { opacity: 1; } }
.block-container { animation: langFade___LANG__ .45s ease both; }
 
@keyframes welcomeIn { from { opacity: 0; transform: translateY(28px) scale(.97); } to { opacity: 1; transform: none; } }
@keyframes borderFlow { 0% { background-position: 0 0, 0% 50%; } 100% { background-position: 0 0, 300% 50%; } }
@keyframes textIn___LANG__ { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes featIn___LANG__ { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes pulse { 0%, 100% { box-shadow: 0 8px 22px -6px rgba(37, 99, 235, .7), 0 0 0 0 rgba(59, 130, 246, .45); }
                   50% { box-shadow: 0 8px 22px -6px rgba(37, 99, 235, .7), 0 0 0 10px rgba(59, 130, 246, 0); } }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
 
.st-key-welcome_card {
    max-width: 600px; margin: 6vh auto 0; padding: 28px 28px 26px;
    border: 1px solid transparent; border-radius: 24px;
    background:
        linear-gradient(160deg, #1e293b 0%, #0f172a 100%) padding-box,
        linear-gradient(120deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6) border-box;
    background-size: 100% 100%, 300% 100%;
    animation: welcomeIn .7s cubic-bezier(.16, 1, .3, 1) both, borderFlow 8s linear infinite;
    box-shadow: 0 30px 70px -25px rgba(37, 99, 235, .45);
    color: #e2e8f0;
}
.welcome-top { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 16px; }
.welcome-dot { width: 8px; height: 8px; border-radius: 50%; background: #22d3ee; animation: blink 1.8s ease-in-out infinite; }
.welcome-brand { font-size: .78rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: #93c5fd; }
 
.st-key-welcome_lang {
    width: fit-content; margin: 0 auto; padding: 4px; border-radius: 999px;
    background: rgba(15, 23, 42, .8); border: 1px solid rgba(148, 163, 184, .25);
}
.st-key-welcome_lang [data-testid="stHorizontalBlock"] { gap: 4px !important; flex-wrap: nowrap !important; }
.st-key-welcome_lang [data-testid="stColumn"] { width: auto !important; flex: 0 0 auto !important; min-width: 0 !important; }
.st-key-welcome_lang button {
    border-radius: 999px !important; padding: .4rem 1.3rem !important; min-height: 0 !important;
    border: none !important; background: transparent !important; color: #94a3b8 !important;
    font-weight: 700; transition: background .35s ease, color .35s ease, transform .2s ease;
}
.st-key-welcome_lang button:hover { color: #fff !important; transform: translateY(-1px); }
.st-key-welcome_lang button[kind="primary"],
.st-key-welcome_lang button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important; color: #fff !important;
    box-shadow: 0 4px 14px -2px rgba(37, 99, 235, .65);
}
 
.welcome-body { direction: __DIR__; margin-top: 18px; }
.welcome-title {
    text-align: center; font-size: 2.2rem; font-weight: 800; margin: 0 0 6px;
    background: linear-gradient(90deg, #ffffff, #93c5fd); -webkit-background-clip: text;
    background-clip: text; color: transparent;
    animation: textIn___LANG__ .5s ease both;
}
.welcome-desc {
    text-align: center; color: #cbd5e1; font-size: 1rem; line-height: 1.7; margin: 0 auto 16px; max-width: 470px;
    animation: textIn___LANG__ .5s ease .08s both;
}
.welcome-features { display: grid; gap: 8px; }
.welcome-feature {
    display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 14px;
    background: rgba(15, 23, 42, .55); border: 1px solid rgba(148, 163, 184, .14);
    text-align: __ALIGN__; cursor: default;
    animation: featIn___LANG__ .45s ease both; animation-delay: calc(.15s + var(--i) * 70ms);
    transition: transform .25s ease, border-color .25s ease, background .25s ease;
}
.welcome-feature:hover {
    transform: translateX(__NUDGE__); border-color: rgba(59, 130, 246, .55); background: rgba(37, 99, 235, .12);
}
.welcome-num {
    flex: 0 0 auto; font-size: .75rem; font-weight: 800; color: #60a5fa; direction: ltr;
    padding: 4px 8px; border-radius: 8px; background: rgba(59, 130, 246, .14);
}
.welcome-feature-text { color: #cbd5e1; font-size: .93rem; line-height: 1.5; }
 
.st-key-welcome_start { margin-top: 18px; }
.st-key-welcome_start button {
    width: 100%; border-radius: 14px; padding: .8rem 1rem; font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(135deg, #2563eb, #3b82f6); border: none; color: #fff;
    animation: pulse 2.4s ease-in-out infinite;
    transition: transform .2s ease, filter .2s ease;
}
.st-key-welcome_start button:hover { transform: translateY(-2px); filter: brightness(1.12); color: #fff; }
.st-key-welcome_start button:active { transform: translateY(0) scale(.98); }
 
@media (max-width: 640px) {
    .st-key-welcome_card { margin-top: 2vh; padding: 22px 16px 18px; border-radius: 20px; }
    .welcome-title { font-size: 1.75rem; }
    .welcome-feature { padding: 9px 11px; }
    .welcome-feature-text { font-size: .86rem; }
    .welcome-feature:hover { transform: none; }
}
 
@media (max-width: 900px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
    .block-container { padding: 1.25rem 1rem 6rem !important; }
    .stApp h1 { font-size: 1.45rem !important; }
    .stApp h3 { font-size: 1.1rem !important; }
    .kpi-grid { gap: 10px; }
    .kpi-card { padding: 12px 8px; }
    .kpi-card:hover { transform: none; }
    .kpi-title { font-size: .78rem; }
    .kpi-value { font-size: 1.3rem; }
    .kpi-sub { font-size: .72rem; }
    .chip { font-size: .75rem; padding: 3px 10px; }
    .stDownloadButton button, .stButton button { width: 100%; }
    .color-box { width: 36px; height: 36px; }
    .footer-box { margin-top: 32px; font-size: .9rem; }
    .st-key-chat_fab, div:has(> .st-key-chat_fab) { bottom: 14px; __SIDE__: 14px; }
    .st-key-chat_fab button { padding: .65rem 1rem; }
}
</style>
""".replace("__DIR__", "rtl" if is_ar else "ltr") \
   .replace("__ALIGN__", "right" if is_ar else "left") \
   .replace("__SIDE__", "left") \
   .replace("__LANG__", st.session_state.lang) \
   .replace("__NUDGE__", "-4px" if is_ar else "4px")
 
st.markdown(CSS, unsafe_allow_html=True)
 
if not st.session_state.started:
    render_welcome()
    st.stop()
 
st.title(t("title"))
st.caption(t("subtitle"))
st.divider()
 
uploaded_file = st.file_uploader(t("upload"), type=["csv", "xlsx"], key="uploader")
 
df = None
view = None
file_name = ""
active_filters = []
if uploaded_file is not None:
    file_name = uploaded_file.name
    file_bytes = uploaded_file.getvalue()
    file_key = f"{zlib.crc32(file_bytes):08x}"
    try:
        df = load_data(file_bytes, file_name)
    except Exception as error:
        st.error(f"{t('read_error')} {error}")
 
if df is not None and df.empty:
    st.warning(t("empty"))
    df = None
 
if df is not None:
    st.success(t("loaded").format(rows=f"{len(df):,}", cols=df.shape[1]))
 
    date_cols = detect_date_columns(df)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    category_cols = df.select_dtypes(include=["object", "category", "string", "bool"]).columns.tolist()
    domain = detect_domain(df, file_name)
 
    base, active_filters = render_filters(df, category_cols, date_cols, numeric_cols, file_key)
 
    selection = get_chart_selection(file_key)
    view = apply_chart_selection(base, selection) if selection else base
    render_active_filters(active_filters, selection)
    if selection:
        values = ", ".join(str(v) for v in selection["values"])
        active_filters = active_filters + [f"{selection['col']} = {values} (chart click)"]
 
    if view.empty:
        st.warning(t("no_rows"))
 
    render_kpis(view, df, numeric_cols, date_cols, file_key)
    st.divider()
    render_chart_builder(base, numeric_cols, category_cols, date_cols, domain["colors"], file_key)
    st.divider()
    render_tables(view, numeric_cols, file_name)
    st.divider()
    render_recommendations(df, numeric_cols, category_cols, date_cols, domain)
elif uploaded_file is None:
    st.info(t("awaiting"))
 
chat_context = (dataset_context(view, df, file_name, active_filters) if df is not None
                else "No dataset uploaded yet.")
render_chat_widget(chat_context)
 
st.markdown(
    """
<div class="footer-box">
    Developed by <b>Wajd Al-Luhaibi</b> | Dashboard Co-pilot Agent<br>
    Follow on X: <a href="https://x.com/wajd_cs" target="_blank">@wajd_cs</a>
</div>
""",
    unsafe_allow_html=True,
)
 
