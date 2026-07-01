
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 기본 설정 및 데이터 로드 (.xlsx 연동)
# ==========================================
st.set_page_config(page_title="개인 맞춤형 건강 식단 추천(채소류)", page_icon="🥦", layout="wide")

@st.cache_data
def load_data():
    # 업로드하신 2개의 엑셀 파일을 읽어옵니다. (파일명이 다르다면 수정해주세요)
    efficacy_df = pd.read_excel("flavonoid_efficacy_sources.xlsx")
    veg_df = pd.read_excel("flavonoid_grouped_by_class.xlsx")
    
    # 두 데이터를 연결하기 위해 efficacy_df의 '성분'에서 영문명 추출 (예: "Apigenin (아피제닌)" -> "Apigenin")
    efficacy_df['Eng_Name'] = efficacy_df['성분'].apply(lambda x: str(x).split(" (")[0].strip())
    
    return efficacy_df, veg_df

try:
    efficacy_df, veg_df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다. 파일명과 확장자(.xlsx)를 확인해주세요.\n오류 내용: {e}")
    st.stop()

# ==========================================
# 2. 상태 관리 (메뉴 간 데이터 공유)
# ==========================================
if 'recommended_veggies' not in st.session_state:
    st.session_state.recommended_veggies = []

# ==========================================
# 3. 사이드바 메뉴 설정
# ==========================================
st.sidebar.title("📱 개인 맞춤형 건강 식단 추천(채소류)")
menu = st.sidebar.radio(
    "메뉴를 선택하세요",
    ("🩺 건강 고민 진단", "🥗 맞춤형 식단 플래너", "📖 플라보노이드 도감", "📊 나의 섭취량 기록")
)

st.title("📱 개인 맞춤형 건강 식단 추천(채소류)")
st.write("---")

# ==========================================
# 🩺 기능 1: 건강 고민 진단 및 큐레이션
# ==========================================
if menu == "🩺 건강 고민 진단":
    st.header("나의 건강 고민은 무엇인가요?")
    
    # 사용자가 이해하기 쉬운 건강 고민 키워드 매핑
    health_keywords = {
        "관절 및 염증 완화": "염증",
        "혈당 조절 (당뇨)": "당뇨",
        "심혈관 건강 (고혈압 등)": "심혈관",
        "장 건강 및 면역력 증진": "장 건강",
        "간 보호 및 피로 회복": "간",
        "호흡기 및 알레르기 (천식 등)": "알레르기",
        "세포 보호 및 항산화 (노화방지)": "항산화",
        "항암 및 종양 억제": "항암"
    }
    
    selected_issue = st.selectbox("현재 가장 고민되는 증상을 선택해주세요.", list(health_keywords.keys()))
    search_keyword = health_keywords[selected_issue]
    
    # 해당 효능(키워드)을 가진 성분 찾기
    matched_components = efficacy_df[efficacy_df['효능'].str.contains(search_keyword, na=False)]
    
    if not matched_components.empty:
        # 가장 첫 번째 매칭된 성분을 타겟으로 설정
        target_row = matched_components.iloc[0]
        target_kor_name = target_row['성분']
        target_eng_name = target_row['Eng_Name']
        
        st.success(f"**{selected_issue}**에는 **{target_kor_name}** 성분이 효과적입니다.\n\n*(효능: {target_row['효능']})*")
        
        # 함량 데이터(veg_df)에서 해당 성분이 가장 많은 채소 TOP 3 추출
        if target_eng_name in veg_df.columns:
            st.subheader(f"🏆 '{target_kor_name}' 함유량 TOP 3 채소")
            
            top_veggies = veg_df[['채소류', target_eng_name]].sort_values(by=target_eng_name, ascending=False).head(3)
            
            # 다음 메뉴(식단 플래너)를 위해 세션 상태에 저장
            st.session_state.recommended_veggies = top_veggies['채소류'].tolist()
            
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            for idx, row in enumerate(top_veggies.iterrows()):
                with cols[idx]:
                    st.metric(label=f"{idx+1}위: {row[1]['채소류']}", value=f"{row[1][target_eng_name]:.1f} mg/100g")
        else:
            st.warning(f"함량 데이터에 '{target_eng_name}' 컬럼이 존재하지 않습니다.")
    else:
        st.info("해당 고민에 직접적으로 매칭되는 성분을 찾지 못했습니다. 다른 고민을 선택해보세요.")

# ==========================================
# 🥗 기능 2: 맞춤형 하루 식단 설계 플래너
# ==========================================
elif menu == "🥗 맞춤형 식단 플래너":
    st.header("오늘의 맞춤형 식단 제안")
    
    recom_veggies = st.session_state.recommended_veggies
    
    if recom_veggies and len(recom_veggies) >= 3:
        st.info("💡 '건강 고민 진단'에서 추천받은 핵심 채소들을 활용한 하루 레시피입니다.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("🌅 아침")
            st.write(f"**{recom_veggies[0]} 클렌즈 쥬스**")
            st.write(f"가장 성분이 풍부한 **{recom_veggies[0]}**을(를) 활용하여 사과나 물과 함께 부드럽게 갈아 마십니다. 아침 공복 흡수율을 높여줍니다.")
        with col2:
            st.subheader("☀️ 점심")
            st.write(f"**{recom_veggies[1]} 닭가슴살 샐러드**")
            st.write(f"**{recom_veggies[1]}**을(를) 베이스로 가벼운 단백질을 곁들여 포만감과 활력을 챙기는 든든한 점심입니다.")
        with col3:
            st.subheader("🌙 저녁")
            st.write(f"**{recom_veggies[2]} 올리브유 가벼운 볶음**")
            st.write(f"소화가 잘 되도록 **{recom_veggies[2]}**을(를) 올리브유에 살짝 볶아 지용성 플라보노이드의 체내 흡수를 극대화합니다.")
    else:
        st.warning("👈 먼저 **'건강 고민 진단'** 메뉴에서 증상을 선택하여 채소를 추천받아주세요!")

# ==========================================
# 📖 기능 3: 플라보노이드 도감 (데이터베이스)
# ==========================================
elif menu == "📖 플라보노이드 도감":
    st.header("플라보노이드 백과사전")
    st.write("각 성분별 효능과 입증된 과학적 출처(PMC)를 확인하세요.")
    
    # 보여주기용 데이터프레임 정리 (Eng_Name 등 내부용 컬럼 제외)
    display_df = efficacy_df[['성분', '효능', '출처', '출처사이트']]
    st.dataframe(display_df, use_container_width=True)

# ==========================================
# 📊 기능 4: 나의 섭취량 기록 (트래커)
# ==========================================
elif menu == "📊 나의 섭취량 기록":
    st.header("오늘 하루 섭취량 트래커")
    st.write("오늘 먹은 채소와 양(g)을 입력하면 섭취한 플라보노이드 계열 밸런스를 분석해 드립니다.")
    
    veggie_list = veg_df['채소류'].unique()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("섭취량 입력")
        selected_veggies = st.multiselect("오늘 먹은 채소를 선택하세요:", veggie_list)
        
        intake_data = {}
        for v in selected_veggies:
            amount = st.number_input(f"{v} 섭취량 (g)", min_value=0, value=100, step=10)
            intake_data[v] = amount
            
    with col2:
        st.subheader("섭취 밸런스 분석")
        if intake_data:
            # 개별 성분 컬럼만 추출 (총합계 성격의 컬럼은 차트에서 제외하여 시각적 혼동 방지)
            exclude_cols = ['채소류', 'Total Flavonoids', 'Flavanones', 'Flavones', 'Flavonols', 'Chalcones/Dihydrochalcones']
            target_cols = [c for c in veg_df.columns if c not in exclude_cols]
            
            consumed = {col: 0.0 for col in target_cols}
            
            # 섭취량 비례 계산
            for v, amount in intake_data.items():
                v_row = veg_df[veg_df['채소류'] == v].iloc[0]
                for col in target_cols:
                    consumed[col] += (amount / 100.0) * v_row[col]
            
            # 섭취량이 0보다 큰 성분 중 상위 6개만 방사형 차트로 표시
            tracker_df = pd.DataFrame(list(consumed.items()), columns=['성분', '섭취량(mg)'])
            tracker_df = tracker_df[tracker_df['섭취량(mg)'] > 0].sort_values(by='섭취량(mg)', ascending=False).head(6)
            
            if not tracker_df.empty:
                fig = px.line_polar(tracker_df, r='섭취량(mg)', theta='성분', line_close=True, markers=True)
                fig.update_traces(fill='toself', fillcolor='rgba(46, 204, 113, 0.5)', line_color='green')
                st.plotly_chart(fig, use_container_width=True)
                st.success("✅ 오늘 섭취한 주요 플라보노이드 성분 밸런스입니다.")
            else:
                st.warning("선택한 채소에 기록된 플라보노이드 성분이 없습니다.")
        else:
            st.info("👈 좌측에서 오늘 먹은 채소를 1개 이상 선택해주세요.")
