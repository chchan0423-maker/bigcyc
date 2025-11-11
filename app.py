# app.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
import os
import matplotlib.font_manager as fm
import platform
from matplotlib import rc

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 깃허브 리눅스 기준
if platform.system() == 'Linux':
    fontname = './NanumGothic.ttf'
    font_files = fm.findSystemFonts(fontpaths=fontname)
    fm.fontManager.addfont(fontname)
    fm._load_fontmanager(try_read_cache=False)
    rc('font', family='NanumGothic')


# ====== Streamlit 기본 설정 ======
st.set_page_config(page_title="AI Job Market Trends Dashboard", layout="wide")
st.title("🤖 AI Job Market Trends 데이터 분석 대시보드")
st.markdown("이 앱은 **AI 일자리 시장 동향 CSV 파일을 자동으로 불러와 분석 및 시각화**합니다.")

# ====== 1️⃣ CSV 파일 자동 불러오기 ======
file_name = "AI_Job_Market_Trends.csv"

if not os.path.exists(file_name):
    st.error(f"❌ `{file_name}` 파일을 찾을 수 없습니다. 같은 폴더에 CSV 파일을 넣어주세요.")
    st.stop()

df = pd.read_csv(file_name)
st.success("✅ CSV 파일 로드 완료!")

# ====== 2️⃣ 데이터 기본 정보 ======
st.header("📊 데이터 기본 정보")
st.write("**데이터 샘플 (상위 5개)**")
st.dataframe(df.head())

st.write("**기초 통계 요약**")
st.dataframe(df.describe(include='all'))

st.write("**결측치 현황**")
st.dataframe(df.isnull().sum())

# ====== 3️⃣ 필터 설정 (사이드바) ======
st.sidebar.header("🎯 데이터 필터")
selected_job = st.sidebar.multiselect("직무(Job Title)", df['Job Title'].unique())
selected_industry = st.sidebar.multiselect("산업(Industry)", df['Industry'].unique())
selected_location = st.sidebar.multiselect("지역(Location)", df['Location'].unique())

filtered_df = df.copy()
if selected_job:
    filtered_df = filtered_df[filtered_df['Job Title'].isin(selected_job)]
if selected_industry:
    filtered_df = filtered_df[filtered_df['Industry'].isin(selected_industry)]
if selected_location:
    filtered_df = filtered_df[filtered_df['Location'].isin(selected_location)]

st.write(f"📄 현재 데이터 개수: {len(filtered_df)}개")
st.dataframe(filtered_df.head())

# ====== 4️⃣ 직무별 평균 연봉 ======
st.header("💰 직무별 평균 연봉")
avg_salary_by_job = filtered_df.groupby('Job Title')['Salary'].mean().sort_values(ascending=False)
fig1 = px.bar(avg_salary_by_job, x=avg_salary_by_job.index, y=avg_salary_by_job.values,
              title="직무별 평균 연봉", labels={'x': '직무', 'y': '평균 연봉(USD)'})
st.plotly_chart(fig1, use_container_width=True)

# ====== 5️⃣ 산업별 연봉 분포 ======
st.header("🏭 산업별 연봉 분포")
fig2 = px.box(filtered_df, x='Industry', y='Salary', color='Industry',
              title="산업별 연봉 분포", points="all")
st.plotly_chart(fig2, use_container_width=True)

# ====== 6️⃣ 지역별 일자리 수 ======
st.header("🌍 지역별 일자리 수")
loc_count = filtered_df['Location'].value_counts().reset_index()
loc_count.columns = ['Location', 'Count']
fig3 = px.bar(loc_count, x='Location', y='Count', title="지역별 일자리 수")
st.plotly_chart(fig3, use_container_width=True)

# ====== 7️⃣ 기술(스킬) 분석 ======
st.header("🧠 가장 많이 요구되는 기술 Top 10")
skills_series = filtered_df['Skills'].dropna().apply(lambda x: [s.strip() for s in x.split(',')])
all_skills = [skill for sublist in skills_series for skill in sublist]
top_skills = pd.DataFrame(Counter(all_skills).most_common(10), columns=['Skill', 'Count'])

fig4 = px.bar(top_skills, x='Count', y='Skill', orientation='h',
              title="가장 많이 요구되는 기술 Top 10")
st.plotly_chart(fig4, use_container_width=True)

# ====== 8️⃣ 연봉 분포 ======
st.header("📈 연봉 분포 히스토그램")
fig5, ax = plt.subplots(figsize=(8, 4))
sns.histplot(filtered_df['Salary'], bins=20, kde=True, ax=ax)
ax.set_title("연봉 분포")
st.pyplot(fig5)

# ====== 9️⃣ 시간별 평균 연봉 추이 ======
if 'Date' in filtered_df.columns:
    st.header("⏱️ 시간에 따른 평균 연봉 추이")
    df_time = filtered_df.copy()
    df_time['Date'] = pd.to_datetime(df_time['Date'], errors='coerce')
    df_time = df_time.dropna(subset=['Date'])
    df_time = df_time.groupby(pd.Grouper(key='Date', freq='M'))['Salary'].mean().reset_index()

    fig6 = px.line(df_time, x='Date', y='Salary', title="월별 평균 연봉 추이")
    st.plotly_chart(fig6, use_container_width=True)

# ====== 🔟 데이터 다운로드 ======
st.header("📥 필터링된 데이터 다운로드")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📄 CSV로 다운로드", csv, "filtered_data.csv", "text/csv")
