import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = '/Users/jskim/Library/Fonts/RIDIBatang.otf'  # 폰트 경로
font_prop = fm.FontProperties(fname=font_path, size=12)
plt.rc('font', family=font_prop.get_name())

# 사이드바에 사용자 입력 받기
st.sidebar.title('설정')
battery_capacity = st.sidebar.number_input('AAA 건전지 용량 (mAh)', min_value=0.0, value=1200.0, key='capacity')  # 기본값 1200 mAh
mode = st.sidebar.selectbox('감지 모드 선택', ['PIR', 'HLK-LD2410', 'TLSR8258'])  # 모드 선택 변경

# 소모 전류 설정
current_options = {
    # 'PIR AND RADAR': 80.0,  # HLK-LD2410
    # 'PIR OR RADAR': 80.0 + 12e-3,  # HLK-LD2410 + PIR
    # 'ONLY RADAR': 80.0,  # HLK-LD2410
    'PIR': 12e-3,  # 12µA
    'HLK-LD2410': 80.0,  # 80mAç
    'TLSR8258': 5.3,  # 5.3mA
    '기타': 1.0  # 1mA
}

# 사이드바에 각 모듈별 소비 전류 값 입력
st.sidebar.header('모듈별 소비 전류 설정')
for module in current_options.keys():
    current_options[module] = st.sidebar.number_input(f'{module} 소비 전류 (mA)', value=current_options[module], key=module)

# 모드에 따라 전류 선택
current_draw_value = current_options[mode]  # 선택된 모드에 따른 전류 값

# AAA 건전지 2개 직렬 연결 시 총 전압 계산
total_battery_voltage = 1.5 * 2  # 직렬 연결로 전압 두 배

# 배터리 지속 시간 계산
usable_capacity = battery_capacity  # 용량은 그대로 유지
battery_life = usable_capacity / current_draw_value

# 방전 곡선 계산
time_points = np.linspace(0, battery_life, 100)
voltage = np.piecewise(time_points,
                       [time_points < battery_life * 0.7, time_points >= battery_life * 0.7],
                       [lambda t: total_battery_voltage - (0.5 / (battery_life * 0.7)) * t,  # 완만한 감소 구간
                        lambda t: 1.0 - (0.5 / (battery_life * 0.3)) * (t - battery_life * 0.7)])  # 급격한 감소 구간

# 남은 배터리 용량 계산
remaining_capacity = usable_capacity - (current_draw_value * time_points)

# 새로운 탭 추가
tab1, tab2 = st.tabs(["배터리 수명 예측", "전체 소비 전류"])
tab2.subheader("총 소비 전류")

with tab1:
    # 그래프 수정: 가로축은 시간, 세로축은 전압
    plt.figure(figsize=(10, 5))

    # 시간 단위 변환: 24시간 이상일 경우 일로 환산
    if battery_life > 24:
        time_points_display = time_points / 24  # 일로 환산
        x_label = '시간(Day)'
    else:
        time_points_display = time_points  # 시간 단위 유지
        x_label = '시간(Hour)'

    plt.plot(time_points_display, voltage, label='전압 (V)', color='blue')
    plt.scatter(battery_life / 24 if battery_life > 24 else battery_life, 0, color='red', label='현재 설정')
    plt.xlabel(x_label)
    plt.ylabel('전압 (V)')
    plt.title(f'시간에 따른 배터리 전압 변화 - 모드: {mode}')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

with tab2:
    # 소비 전류 비율 계산
    total_current = sum(current_options.values())
    current_ratios = {key: value / total_current for key, value in current_options.items()}

    # 원형 그래프 그리기
    plt.figure(figsize=(8, 8))
    plt.pie(current_ratios.values(), labels=current_ratios.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('모듈별 소비 전류 비율')
    plt.axis('equal')  # 원형 그래프를 원으로 유지
    st.pyplot(plt)
