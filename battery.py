import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = '/Users/jskim/Library/Fonts/RIDIBatang.otf'  # 폰트 경로
font_prop = fm.FontProperties(fname=font_path, size=12)
plt.rc('font', family=font_prop.get_name())

# 사용자 입력 받기
st.title('배터리 수명 예측 도구')
battery_capacity = st.number_input('AAA 건전지 용량 (mAh)', min_value=0.0, value=1200.0, key='capacity')  # 기본값 1200 mAh

# 소모 전류 선택
current_options = {
    'PIR': 12e-3,  # 12µA
    'HLK-LD2410': 80.0,  # 80mA
    'TLSR8258': 5.3,  # 5.3mA
    '기타': 1.0  # 1mA
}
current_draw = st.selectbox('소비 전류 선택', list(current_options.keys()), index=1)  # 기본값 HLK-LD2410
current_draw_value = current_options[current_draw]

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

# 그래프 수정: 가로축은 시간, 세로축은 전압
plt.figure(figsize=(10, 5))

# 시간 단위 변환: 24시간 이상일 경우 일로 환산
if battery_life > 24:
    time_points_display = time_points / 24  # 일로 환산
    x_label = '시간(일)'
else:
    time_points_display = time_points  # 시간 단위 유지
    x_label = '시간(Hour)'

plt.plot(time_points_display, voltage, label='전압 (V)', color='blue')
plt.scatter(battery_life / 24 if battery_life > 24 else battery_life, 0, color='red', label='현재 설정')
plt.xlabel(x_label)
plt.ylabel('전압 (V)')
plt.title('시간에 따른 배터리 전압 변화')
plt.legend()
plt.grid(True)
st.pyplot(plt)
