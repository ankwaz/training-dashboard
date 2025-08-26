# Required libraries: streamlit, pandas, numpy, plotly, kaleido

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="자격증 대시보드", layout="wide", page_icon="📊")

# ----- 글로벌 스타일 및 헤더 구성 -----
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        background:#f8fafc;
        color:#64748b;
    }
    .stApp {background:#f8fafc;}
    .header {
        position: sticky; top:0; z-index:100;
        display:flex; justify-content:space-between; align-items:center;
        background:#ffffff; padding:12px 24px; border-bottom:1px solid #e2e8f0;
    }
    .header-left .title{font-size:20px;font-weight:700;color:#1e293b;}
    .header-left .breadcrumb{font-size:14px;color:#64748b;}
    .header-buttons button{
        background:#2563eb; color:#fff; border:none; border-radius:8px;
        padding:8px; margin-left:8px; cursor:pointer;
    }
    .header-buttons button:hover{background:#3b82f6;}
    div[data-testid="stSidebar"]{background:#ffffff;}
    .metric-card{
        border-radius:12px;
        box-shadow:0 4px 6px -1px rgb(0 0 0 / 0.1),0 2px 4px -2px rgb(0 0 0 / 0.1);
        padding:24px; margin-bottom:16px; background:#ffffff; color:#1e293b;
        transition:box-shadow .2s ease;
    }
    .metric-card.primary{background:#2563eb;color:#ffffff;}
    .metric-card h3{margin:0 0 8px 0; font-size:1rem; font-weight:600; color:#1e293b;}
    .metric-card.primary h3{color:#ffffff;}
    .metric-card p{margin:0; font-size:1.5rem; font-weight:700;}
    .metric-card.primary p{color:#ffffff;}
    .metric-card:hover{
        box-shadow:0 10px 15px -3px rgb(0 0 0 / 0.1),0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    .stButton>button{background:#2563eb;color:#fff;border:none;border-radius:8px;padding:10px 16px;}
    .stButton>button:hover{background:#3b82f6;}
    .stButton.secondary>button{background:#e2e8f0;color:#475569;}
    .stDownloadButton>button{background:#2563eb;color:#fff;border:none;border-radius:8px;padding:10px 16px;}
    .stDownloadButton>button:hover{background:#3b82f6;}
    @media (max-width:480px){
        .metric-container .metric-card{width:100%;}
    }
    </style>
    <div class="header">
        <div class="header-left">
            <div class="title">자격증 취득자 분석 대시보드</div>
            <div class="breadcrumb">홈 / 대시보드</div>
        </div>
        <div class="header-buttons">
            <button>🔔</button>
            <button>⚙️</button>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 자격증 설명 사전
CERT_DESC = {
    "정보처리기사": "IT 시스템 개발 및 운영 능력 인증",
    "전기기사": "전기 설계 및 시공 전문가",
    "건축기사": "건축 설계·감리 기술자",
    "토목기사": "토목 구조물 설계 및 관리",
    "기계기사": "기계 설계·제작 능력 인증",
    "산업안전기사": "산업현장 안전관리 전문가",
    "화공기사": "화학공정 운영·관리 능력",
    "환경기사": "환경오염 방지 기술자",
    "통신기사": "통신 시스템 설계·운영",
    "소방설비기사": "소방 설비 설계·시공 전문가",
}

# 필터 상태 초기화
for _k, _v in [
    ("year_sel", []),
    ("gender_sel", []),
    ("region_sel", []),
    ("cert_sel", []),
    ("search_q", ""),
]:
    st.session_state.setdefault(_k, _v)

@st.cache_data
def generate_sample_data(n: int = 500) -> pd.DataFrame:
    np.random.seed(42)
    years = np.arange(1993, 2026)
    genders = ["남성", "여성"]
    regions = [
        "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
        "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    ]
    certificate_types = list(CERT_DESC.keys())
    data = []
    for _ in range(n):
        year = np.random.choice(years)
        gender = np.random.choice(genders)
        region = np.random.choice(regions)
        age = np.random.randint(20, 61)
        birth_year = year - age
        cert = np.random.choice(certificate_types)
        start = datetime(year, 1, 1)
        day_offset = int(np.random.randint(0, 365))
        acquired_at = start + pd.Timedelta(days=day_offset)
        data.append(
            {
                "year": year,
                "gender": gender,
                "age": age,
                "birth_year": birth_year,
                "region": region,
                "certificate_type": cert,
                "acquired_at": acquired_at,
            }
        )
    return pd.DataFrame(data)

def load_data(file: BytesIO | None = None) -> pd.DataFrame:
    """엑셀을 불러오거나 샘플 데이터를 생성"""
    if file is not None:
        df = pd.read_excel(file)
    elif os.path.exists("certifications.xlsx"):
        df = pd.read_excel("certifications.xlsx")
    else:
        df = generate_sample_data(500)
    if "acquired_at" in df.columns:
        df["acquired_at"] = pd.to_datetime(df["acquired_at"])
    return df

uploaded_file = st.sidebar.file_uploader("엑셀 데이터 업로드", type=["xlsx"])
df = load_data(uploaded_file)

ALL_REGIONS = sorted(df["region"].unique())
ALL_GENDERS = sorted(df["gender"].unique())
ALL_CERTS = sorted(df["certificate_type"].unique())


def parse_search(query: str):
    tokens = query.strip().split()
    filters = {"year": [], "gender": [], "region": [], "certificate_type": []}
    for tok in tokens:
        if tok.isdigit() and int(tok) in df["year"].unique():
            filters["year"].append(int(tok))
        if tok in ALL_GENDERS:
            filters["gender"].append(tok)
        if tok in ALL_REGIONS:
            filters["region"].append(tok)
        if tok in ALL_CERTS:
            filters["certificate_type"].append(tok)
    return filters

# 안내 문구
st.info("현재는 500건의 샘플 데이터만 표시됩니다. 72,000건 데이터로 곧 업데이트될 예정입니다!")

# 사이드바 필터
st.sidebar.header("필터")
year_sel = st.sidebar.multiselect(
    "📅 연도", sorted(df["year"].unique()), key="year_sel"
)
gender_sel = st.sidebar.multiselect("🚻 성별", ALL_GENDERS, key="gender_sel")
region_sel = st.sidebar.multiselect("📍 지역", ALL_REGIONS, key="region_sel")
cert_sel = st.sidebar.multiselect("📝 자격증 종류", ALL_CERTS, key="cert_sel")
search_q = st.sidebar.text_input(
    "텍스트 검색", placeholder="예: 서울 2020 여성", key="search_q"
)
parsed = parse_search(search_q)
if parsed["year"]:
    st.session_state.year_sel = parsed["year"]
if parsed["gender"]:
    st.session_state.gender_sel = parsed["gender"]
if parsed["region"]:
    st.session_state.region_sel = parsed["region"]
if parsed["certificate_type"]:
    st.session_state.cert_sel = parsed["certificate_type"]

col_reset, col_save, col_load = st.sidebar.columns(3)
with col_reset:
    if st.button("모두 선택 초기화", key="reset"):
        for k in ["year_sel", "gender_sel", "region_sel", "cert_sel", "search_q"]:
            st.session_state[k] = [] if k != "search_q" else ""
        st.experimental_rerun()
with col_save:
    if st.button("저장", key="save"):
        st.session_state.saved_filters = {
            "year_sel": st.session_state.year_sel,
            "gender_sel": st.session_state.gender_sel,
            "region_sel": st.session_state.region_sel,
            "cert_sel": st.session_state.cert_sel,
            "search_q": st.session_state.search_q,
        }
        st.sidebar.success("저장되었습니다")
with col_load:
    if st.button("불러오기", key="load"):
        saved = st.session_state.get("saved_filters")
        if saved:
            for k, v in saved.items():
                st.session_state[k] = v
            st.experimental_rerun()

year_sel = st.session_state.year_sel
gender_sel = st.session_state.gender_sel
region_sel = st.session_state.region_sel
cert_sel = st.session_state.cert_sel
search_q = st.session_state.search_q

filtered = df.copy()
if year_sel:
    filtered = filtered[filtered["year"].isin(year_sel)]
if gender_sel:
    filtered = filtered[filtered["gender"].isin(gender_sel)]
if region_sel:
    filtered = filtered[filtered["region"].isin(region_sel)]
if cert_sel:
    filtered = filtered[filtered["certificate_type"].isin(cert_sel)]

# 상단 주요 지표
_gender_counts = filtered["gender"].value_counts()
_male = int(_gender_counts.get("남성", 0))
_female = int(_gender_counts.get("여성", 0))
_region_counts = filtered["region"].value_counts()
_top_region = _region_counts.index[0] if not _region_counts.empty else "-"

def metric_html(title: str, value: str, primary: bool = False) -> str:
    cls = "metric-card primary" if primary else "metric-card"
    return f"<div class='{cls}'><h3>{title}</h3><p>{value}</p></div>"

m1, m2, m3 = st.columns(3)
m1.markdown(metric_html("전체 취득자", f"{len(filtered):,}명", True), unsafe_allow_html=True)
m2.markdown(metric_html("남 / 여 취득자", f"{_male:,} / {_female:,}"), unsafe_allow_html=True)
m3.markdown(metric_html("최다 지역", _top_region), unsafe_allow_html=True)


def add_download_button(fig, filename: str):
    buf = BytesIO()
    fig.write_image(buf, format="png")
    st.download_button(
        "PNG로 다운로드", data=buf.getvalue(), file_name=filename, mime="image/png"
    )

# 연도별 자격증 취득자 수
st.subheader("연도별 자격증 취득자 수")
year_counts = filtered.groupby("year").size().reset_index(name="count")
fig_year = px.line(
    year_counts,
    x="year",
    y="count",
    markers=True,
    color_discrete_sequence=["#2563eb"],
)
fig_year.update_traces(line=dict(width=2))
fig_year.update_xaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
fig_year.update_yaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
st.plotly_chart(fig_year, use_container_width=True)
if not year_counts.empty:
    max_row = year_counts.loc[year_counts["count"].idxmax()]
    st.caption(
        f"{int(max_row['year'])}년에 {int(max_row['count'])}명이 취득했습니다."
    )
add_download_button(fig_year, "yearly_trend.png")

# 성별 비율
st.subheader("성별 비율")
gender_counts = _gender_counts.reset_index()
gender_counts.columns = ["gender", "count"]
fig_gender = px.pie(
    gender_counts,
    names="gender",
    values="count",
    color_discrete_sequence=["#2563eb", "#3b82f6"],
)
st.plotly_chart(fig_gender, use_container_width=True)
if not gender_counts.empty:
    total = gender_counts["count"].sum()
    female = gender_counts.loc[gender_counts["gender"] == "여성", "count"]
    female_pct = float(female) / total * 100 if not female.empty else 0
    st.caption(f"여성 비율은 {female_pct:.1f}% 입니다.")
add_download_button(fig_gender, "gender_ratio.png")

# 지역별 분포
st.subheader("지역별 분포")
region_counts = _region_counts.reset_index()
region_counts.columns = ["region", "count"]
fig_region_bar = px.bar(
    region_counts,
    x="region",
    y="count",
    color_discrete_sequence=["#2563eb"],
)
fig_region_bar.update_xaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
fig_region_bar.update_yaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
st.plotly_chart(fig_region_bar, use_container_width=True)
region_coords = {
    "서울": (37.5665, 126.9780),
    "부산": (35.1796, 129.0756),
    "대구": (35.8714, 128.6014),
    "인천": (37.4563, 126.7052),
    "광주": (35.1595, 126.8526),
    "대전": (36.3504, 127.3845),
    "울산": (35.5384, 129.3114),
    "세종": (36.4800, 127.2890),
    "경기": (37.2636, 127.0286),
    "강원": (37.8228, 128.1555),
    "충북": (36.6357, 127.4912),
    "충남": (36.6588, 126.6728),
    "전북": (35.8174, 127.1530),
    "전남": (34.8161, 126.4630),
    "경북": (36.4919, 128.8889),
    "경남": (35.2383, 128.6917),
    "제주": (33.4996, 126.5312),
}
region_geo = region_counts.copy()
region_geo["lat"] = region_geo["region"].map(lambda r: region_coords[r][0])
region_geo["lon"] = region_geo["region"].map(lambda r: region_coords[r][1])
fig_geo = px.scatter_geo(
    region_geo,
    lat="lat",
    lon="lon",
    size="count",
    color="count",
    hover_name="region",
    scope="asia",
    color_continuous_scale="Blues",
)
fig_geo.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig_geo, use_container_width=True)
if not region_counts.empty:
    top_region = region_counts.iloc[0]["region"]
    st.caption(f"가장 많은 취득 지역은 {top_region}입니다.")
add_download_button(fig_region_bar, "region_bar.png")
add_download_button(fig_geo, "region_map.png")

# 연령대별 분포
st.subheader("연령대별 분포")

def age_group(age: int) -> str:
    if age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    else:
        return "40대 이상"

filtered["age_group"] = filtered["age"].apply(age_group)
age_counts = filtered["age_group"].value_counts().reset_index()
age_counts.columns = ["age_group", "count"]
fig_age = px.bar(
    age_counts,
    x="age_group",
    y="count",
    color_discrete_sequence=["#2563eb"],
)
fig_age.update_xaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
fig_age.update_yaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
st.plotly_chart(fig_age, use_container_width=True)
if not age_counts.empty:
    top_age = age_counts.iloc[0]["age_group"]
    st.caption(f"가장 많은 연령대는 {top_age}입니다.")
add_download_button(fig_age, "age_distribution.png")

# 자격증 인기 순위
st.subheader("자격증 인기 순위")
if year_sel and len(year_sel) == 1:
    cert_df = filtered[filtered["year"] == year_sel[0]]
else:
    cert_df = filtered
cert_counts = cert_df["certificate_type"].value_counts().head(5).reset_index()
cert_counts.columns = ["certificate_type", "count"]
cert_counts["description"] = cert_counts["certificate_type"].map(
    lambda x: CERT_DESC.get(x, "설명 없음")
)
fig_cert = px.bar(
    cert_counts,
    x="certificate_type",
    y="count",
    hover_data=["description"],
    color_discrete_sequence=["#2563eb"],
)
fig_cert.update_xaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
fig_cert.update_yaxes(showgrid=True, gridcolor="#e2e8f0", griddash="dot")
st.plotly_chart(fig_cert, use_container_width=True)
if not cert_counts.empty:
    top_cert = cert_counts.iloc[0]["certificate_type"]
    st.caption(f"가장 인기 있는 자격증은 {top_cert}입니다.")
add_download_button(fig_cert, "top_certificates.png")

