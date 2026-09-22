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


# ==============================================================
# 그래프 2. 장르 안에 영화 - 트리맵 (칸 크기 = 총 관객)
# ==============================================================
st.markdown("---")
st.header("2. 장르별 영화의 총 관객 수 (트리맵)")

fig_treemap = px.treemap(
    movies,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객: %{value:,.0f}명<extra></extra>",
)
fig_treemap.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_treemap, use_container_width=True)

top_movie_row = movies.loc[movies["total_audi"].idxmax()]

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"'{top_movie_row['genre']}' 장르의 '{top_movie_row['movieNm']}'가 "
    f"총 관객 {top_movie_row['total_audi']:,.0f}명으로 가장 큰 칸을 차지하며, "
    "장르 내에서도 영화별 흥행 편차가 크게 나타난다."
)


# ==============================================================
# 그래프 3. 총 관객 수 히스토그램
# ==============================================================
st.markdown("---")
st.header("3. 총 관객 수 분포 (히스토그램)")

fig_hist = px.histogram(
    movies,
    x="total_audi",
)
fig_hist.update_traces(
    hovertemplate="관객 구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    margin=dict(t=30, b=30, l=10, r=10),
    bargap=0.05,
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 몰려 있는 구간 계산 (히스토그램과 동일한 개수의 구간으로 분할)
bin_series = pd.cut(movies["total_audi"], bins=20)
mode_bin = bin_series.value_counts().idxmax()
mode_bin_count = bin_series.value_counts().max()

top_audi_movie = movies.loc[movies["total_audi"].idxmax()]

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"대부분의 영화는 총 관객 {mode_bin.left:,.0f}명 ~ {mode_bin.right:,.0f}명 구간에 "
    f"{mode_bin_count}편으로 가장 많이 몰려 있으며, 총 관객이 가장 많은 영화는 "
    f"'{top_audi_movie['movieNm']}'({top_audi_movie['total_audi']:,.0f}명)이다."
)


# ==============================================================
# 그래프 4. 개봉일 스크린수 vs 총 관객 - 산점도 (장르별 색)
# ==============================================================
st.markdown("---")
st.header("4. 개봉일 스크린수와 총 관객의 관계 (산점도)")

fig_scatter = px.scatter(
    movies,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)
fig_scatter.update_traces(
    hovertemplate="영화명: %{hovertext}<br>개봉일 스크린수: %{x:,.0f}관<br>총 관객: %{y:,.0f}명<extra></extra>",
)
fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_scatter, use_container_width=True)

scrn_audi_corr = movies["first_scrn"].corr(movies["total_audi"])

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"개봉일 스크린수와 총 관객 수의 상관계수는 {scrn_audi_corr:.2f}로, "
    + (
        "스크린수가 많을수록 총 관객도 함께 늘어나는 경향이 뚜렷하다."
        if scrn_audi_corr >= 0.5
        else "스크린수가 많다고 해서 총 관객이 반드시 많은 것은 아니며, 장르별로 흥행 패턴이 갈린다."
    )
)


# ==============================================================
# 그래프 5. 장르별 총 관객 분포 - 박스플롯 (10편 이상 장르만)
# ==============================================================
st.markdown("---")
st.header("5. 장르별 총 관객 분포 (박스플롯)")

genre_movie_counts = movies["genre"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index.tolist()
movies_major = movies[movies["genre"].isin(major_genres)]

fig_box = px.box(
    movies_major,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
)
fig_box.update_traces(
    hovertemplate="영화명: %{hovertext}<br>총 관객: %{y:,.0f}명<extra></extra>",
)
fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False,
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_box, use_container_width=True)

box_median = movies_major.groupby("genre")["total_audi"].median().sort_values(ascending=False)
top_median_genre = box_median.index[0]

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"영화가 10편 이상인 장르 가운데 '{top_median_genre}' 장르의 총 관객 중앙값이 "
    f"{box_median.iloc[0]:,.0f}명으로 가장 높으며, 상자 밖 이상치들은 해당 장르 안에서도 "
    "유난히 흥행했거나 부진했던 영화들을 보여준다."
)


# ==============================================================
# 그래프 6. 개봉일 스크린수 vs 총 관객 - 버블 차트
#            (점 크기 = 첫 주 관객, 장르별 색)
# ==============================================================
st.markdown("---")
st.header("6. 개봉일 스크린수와 총 관객의 관계 (버블 차트)")

fig_bubble = px.scatter(
    movies,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
)
fig_bubble.update_traces(
    hovertemplate=(
        "영화명: %{hovertext}<br>"
        "개봉일 스크린수: %{x:,.0f}관<br>"
        "총 관객: %{y:,.0f}명<br>"
        "첫 주 관객: %{marker.size:,.0f}명<extra></extra>"
    ),
)
fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_bubble, use_container_width=True)

top_week_movie = movies.loc[movies["first_week_audi"].idxmax()]

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"버블 크기(첫 주 관객)가 큰 영화일수록 총 관객도 함께 큰 편이며, "
    f"첫 주 관객이 가장 많았던 영화는 '{top_week_movie['movieNm']}'"
    f"({top_week_movie['first_week_audi']:,.0f}명)로 초반 흥행이 전체 흥행으로 이어지는 경향을 보여준다."
)


# ==============================================================
# 그래프 7. 제작 국가 - 장르 - 선버스트 (칸 크기 = 영화 편수)
# ==============================================================
st.markdown("---")
st.header("7. 제작 국가별 장르 구성 (선버스트)")

fig_sunburst = px.sunburst(
    movies,
    path=["nation", "genre"],
)
fig_sunburst.update_traces(
    hovertemplate="%{label}<br>편수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_sunburst, use_container_width=True)

top_nation_row = movies["nation"].value_counts().reset_index(name="count").iloc[0]
top_nation_genre = (
    movies[movies["nation"] == top_nation_row["nation"]]["genre"]
    .value_counts()
    .idxmax()
)

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"'{top_nation_row['nation']}'이(가) {top_nation_row['count']}편으로 가장 많은 제작 국가이며, "
    f"그중에서도 '{top_nation_genre}' 장르가 가장 큰 비중을 차지한다."
)


# ==============================================================
# 그래프 8. 첫 주 관객이 총 관객에서 차지하는 비중은 장르마다 다른가 - 박스플롯
# ==============================================================
st.markdown("---")
st.header("8. 첫 주 관객이 총 관객에서 차지하는 비중은 장르마다 다른가")

movies["first_week_ratio"] = movies["first_week_audi"] / movies["total_audi"]

fig_ratio = px.box(
    movies,
    x="genre",
    y="first_week_ratio",
    color="genre",
    points="outliers",
    hover_name="movieNm",
    title="첫 주 관객이 총 관객에서 차지하는 비중은 장르마다 다른가",
)
fig_ratio.update_traces(
    hovertemplate="영화명: %{hovertext}<br>첫 주 관객 비중: %{y:.1%}<extra></extra>",
)
fig_ratio.update_layout(
    xaxis_title="장르",
    yaxis_title="첫 주 관객 비중",
    yaxis_tickformat=".0%",
    showlegend=False,
    margin=dict(t=60, b=30, l=10, r=10),
)

st.plotly_chart(fig_ratio, use_container_width=True)

ratio_median = movies.groupby("genre")["first_week_ratio"].median().sort_values(ascending=False)
top_ratio_genre = ratio_median.index[0]
bottom_ratio_genre = ratio_median.index[-1]

st.markdown("**🔎 이 그래프로 알 수 있는 것**")
st.info(
    f"'{top_ratio_genre}' 장르는 첫 주 관객 비중 중앙값이 {ratio_median.iloc[0]:.1%}로 "
    f"개봉 초반에 관객이 몰리는 경향이 가장 강하고, '{bottom_ratio_genre}' 장르는 "
    f"{ratio_median.iloc[-1]:.1%}로 상대적으로 뒷심(입소문)으로 관객을 모으는 편이다."
)
