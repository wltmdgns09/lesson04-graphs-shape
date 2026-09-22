import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "1년간 박스오피스 10위권에 든 영화 가운데, 그 기간에 개봉한 216편의 데이터를 "
    "여러 그래프로 살펴봅니다."
)


# ------------------------------------------------------------
# 데이터 불러오기
# ------------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # genre 열에 세로막대(|) 기호로 여러 장르가 적힌 경우 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # openDt(개봉일, 여덟 자리 숫자)를 날짜 형식으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    return df


with st.spinner("데이터를 불러오는 중입니다..."):
    movies = load_data(DATA_URL)

with st.expander("📄 원본 데이터 미리보기"):
    st.dataframe(movies, use_container_width=True)


# ==============================================================
# 그래프 1. 장르별 영화 편수 (도넛 그래프)
# ==============================================================
st.markdown("---")
st.header("1. 장르별 영화 편수")

genre_counts = (
    movies["genre"]
    .value_counts()
    .rename_axis("genre")
    .reset_index(name="count")
)

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_genre.update_traces(
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
    textinfo="percent+label",
)
fig_genre.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_genre, use_container_width=True)

top_genre_row = genre_counts.iloc[0]
top_genre_name = top_genre_row["genre"]
top_genre_ratio = top_genre_row["count"] / genre_counts["count"].sum() * 100

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"박스오피스 10위권에 든 216편 가운데 '{top_genre_name}' 장르가 "
    f"{top_genre_row['count']}편({top_genre_ratio:.1f}%)으로 가장 많이 관객의 선택을 받았다."
)
