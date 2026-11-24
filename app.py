import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Titanic 대시보드", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("titanic.csv")

df = load_data()

# [수정] filter_data 함수에 ports(항구) 조건 추가
def filter_data(df, sexes, classes, age_range, ports):
    f = df[df["sex"].isin(sexes) & df["pclass"].isin(classes) & df["embarked"].isin(ports)]
    if age_range != (0, 80):
        f = f[f["age"].between(*age_range)]
    return f

def kpi(df):
    if len(df) == 0:
        return 0, 0, 0
    n = len(df)
    rate = round(df["survived"].mean() * 100, 1)
    age = round(df["age"].mean(), 1)
    return n, rate, age

def class_rate_bar(df):
    r = df.groupby("pclass")["survived"].mean().mul(100).round(1).reset_index()
    fig = px.bar(r, x="pclass", y="survived", text="survived", title="객실 등급별 생존율(%)")
    return fig

def age_hist(df):
    fig = px.histogram(df, x="age", color="survived", barmode="overlay", opacity=0.6, title="생존 여부별 나이 분포")
    return fig

st.title("타이타닉, 누가 살아남았나?")

sexes = st.sidebar.multiselect("성별", ["male", "female"], ["male", "female"])
classes = st.sidebar.multiselect("객실 등급", [1, 2, 3], [1, 2, 3])
ages = st.sidebar.slider("나이", 0, 80, (0, 80))

# [추가] 사이드바에 승선 항구 multiselect 추가[cite: 52]
ports = st.sidebar.multiselect("승선 항구", ["S", "C", "Q"], ["S", "C", "Q"])[cite: 52]

if not sexes or not classes or not ports:
    st.warning("성별, 객실 등급, 승선 항구를 하나 이상 선택하세요.")
    st.stop()

# [수정] filter_data 호출 시 ports 전달
f = filter_data(df, sexes, classes, ages, ports)

if len(f) == 0:
    st.warning("조건에 맞는 승객이 없습니다.")
    st.stop()

n, rate, age = kpi(f)
c1, c2, c3 = st.columns(3)
c1.metric("승객 수", f"{n}명")
# [수정] 생존율 KPI에 전체 평균(38.4%) 대비 증감치(delta) 표시[cite: 52]
c2.metric("생존율", f"{rate}%", f"{rate - 38.4:+.1f}%p")[cite: 52]
c3.metric("평균 나이", f"{age}세")

left, right = st.columns(2)
left.plotly_chart(class_rate_bar(f), use_container_width=True)
right.plotly_chart(age_hist(f), use_container_width=True)

with st.expander("데이터 보기"):
    st.dataframe(f)
