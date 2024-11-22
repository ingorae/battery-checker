import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# 사용자 입력을 통한 변수 설정 (Streamlit UI 사용)
st.title("센서 배터리 수명 예측")

st.sidebar.header("제품 정보 입력")
VOLTAGE = st.sidebar.number_input("배터리 전압을 입력하세요 (V)", min_value=0.0, value=3.3, step=0.1)  # 배터리 전압 (V)
BATTERY_CAPACITY = st.sidebar.number_input("배터리 용량을 입력하세요 (mAh)", min_value=0.0, value=1200.0, step=50.0)  # 배터리 용량 (mAh)
STANDBY_CURRENT = st.sidebar.number_input("대기 전류를 입력하세요 (µA)", min_value=0.0, value=65.0, step=1.0) * 1e-6  # 대기 전류 (A)
PIR_CURRENT = st.sidebar.number_input("PIR 전류를 입력하세요 (µA)", min_value=0.0, value=12.0, step=1.0) * 1e-6  # PIR 전류 (A)
MMWAVE_CURRENT = st.sidebar.number_input("mmWave 전류를 입력하세요 (µA)", min_value=0.0, value=60.0, step=1.0) * 1e-6  # mmWave 전류 (A)
CYCLE_TIME = st.sidebar.number_input("센서의 주기를 입력하세요 (시간)", min_value=0.0, value=24.0, step=0.1)  # 주기 (시간)
DAILY_OPERATIONS = st.sidebar.number_input("하루 동작 횟수를 입력하세요", min_value=1, value=1, step=1)  # 하루 동작 횟수
OPERATION_DURATION = st.sidebar.number_input("각 동작의 지속 시간을 입력하세요 (초)", min_value=1, value=60, step=1)  # 각 동작의 지속 시간 (초)

# 기본값 설정
HLK_LD2410_CURRENT = st.sidebar.number_input("HLK-LD2410 mmWave 센서 전류를 입력하세요 (µA)", min_value=0.0, value=15.0, step=1.0) * 1e-6  # mmWave 센서 전류 (A)
ZIGBEE_CURRENT = st.sidebar.number_input("TLSR8258 Zigbee 칩 전류를 입력하세요 (µA)", min_value=0.0, value=5.0, step=1.0) * 1e-6  # Zigbee 칩 전류 (A)
OTHER_CURRENT = st.sidebar.number_input("기타 전류를 입력하세요 (µA)", min_value=0.0, value=2.0, step=1.0) * 1e-6  # 기타 전류 (A)

# 모드별 소비 전류 계산
def get_consumption_current(mode):
    # 대기 전류 계산에 추가된 요소들 포함
    total_standby_current = STANDBY_CURRENT + HLK_LD2410_CURRENT + ZIGBEE_CURRENT + OTHER_CURRENT
    if mode == "PIR AND RADAR":
        return total_standby_current + PIR_CURRENT + MMWAVE_CURRENT
    elif mode == "PIR OR RADAR":
        return total_standby_current + max(PIR_CURRENT, MMWAVE_CURRENT)
    elif mode == "ONLY RADAR":
        return total_standby_current + MMWAVE_CURRENT
    else:
        return total_standby_current

# 배터리 수명 계산
def calculate_battery_life(mode):
    current_consumption = get_consumption_current(mode)  # 모드에 따른 소비 전류 계산
    effective_current = (current_consumption * (ACTIVE_TIME * 3600) + STANDBY_CURRENT * (CYCLE_TIME * 3600 - (DAILY_OPERATIONS * OPERATION_DURATION))) / (CYCLE_TIME * 3600)  # 효과적인 소비 전류 계산
    battery_life = (BATTERY_CAPACITY * 1000) / (effective_current * 24 * 365)  # 년 단위로 배터리 수명 계산
    return battery_life

# 모드 설정
modes = ["PIR 및 레이더 동시 사용", "PIR 또는 레이더 사용", "레이더만 사용"]
battery_lives = [calculate_battery_life(mode) for mode in ["PIR AND RADAR", "PIR OR RADAR", "ONLY RADAR"]]

# 데이터프레임 생성 및 그래프 표시
data = pd.DataFrame({
    '센서 모드': modes,
    '예상 배터리 수명 (년)': battery_lives
})

# Plotly Express를 사용하여 더 예쁜 그래프 생성
fig = px.bar(data, x='센서 모드', y='예상 배터리 수명 (년)', color='센서 모드',
             title='센서 모드별 배터리 수명 예측',
             labels={'센서 모드': '센서 모드', '예상 배터리 수명 (년)': '예상 배터리 수명 (년)'},
             template='plotly_white')

fig.update_layout(
    xaxis_title='센서 모드',
    yaxis_title='예상 배터리 수명 (년)',
    title_x=0.5
)

# 그래프 표시
st.plotly_chart(fig)

# 배터리 전압, 용량 등의 값 표시
st.sidebar.subheader("입력된 제품 정보")
st.sidebar.text(f"배터리 전압: {VOLTAGE} V")
st.sidebar.text(f"배터리 용량: {BATTERY_CAPACITY} mAh")
st.sidebar.text(f"대기 전류: {STANDBY_CURRENT * 1e6:.2f} µA")
st.sidebar.text(f"PIR 전류: {PIR_CURRENT * 1e6:.2f} µA")
st.sidebar.text(f"mmWave 전류: {MMWAVE_CURRENT * 1e6:.2f} µA")
st.sidebar.text(f"HLK-LD2410 전류: {HLK_LD2410_CURRENT * 1e6:.2f} µA")
st.sidebar.text(f"TLSR8258 Zigbee 칩 전류: {ZIGBEE_CURRENT * 1e6:.2f} µA")
st.sidebar.text(f"기타 전류: {OTHER_CURRENT * 1e6:.2f} µA")
