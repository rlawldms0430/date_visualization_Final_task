#C190010 김지은

import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.features import GeoJsonTooltip

# ---- 제목과 설명 ----
st.title("Graduate School Enrollment Visualization 🎓")
st.write("This dashboard visualizes graduate school enrollment trends by region.")

# ---- 데이터 로드 ----
data_path = '다년도_대학원개황.csv'
geojson_path = 'TL_SCCO_CTPRVN.json'

# 데이터 로드 및 전처리
try:
    # CSV 데이터 로드
    df = pd.read_csv(data_path, encoding='UTF-8')

    # 각 연도별로 필요한 열 순서대로 지정
    columns_mapping = {
        '2018.9': 'Total_Students_2018',
        '2018.10': 'Female_Students_2018',
        '2018.11': 'Master_Students_2018',
        '2018.12': 'Master_Female_Students_2018',
        '2018.13': 'PhD_Students_2018',
        '2018.14': 'PhD_Female_Students_2018',

        '2019.9': 'Total_Students_2019',
        '2019.10': 'Female_Students_2019',
        '2019.11': 'Master_Students_2019',
        '2019.12': 'Master_Female_Students_2019',
        '2019.13': 'PhD_Students_2019',
        '2019.14': 'PhD_Female_Students_2019',

        '2020.9': 'Total_Students_2020',
        '2020.10': 'Female_Students_2020',
        '2020.11': 'Master_Students_2020',
        '2020.12': 'Master_Female_Students_2020',
        '2020.13': 'PhD_Students_2020',
        '2020.14': 'PhD_Female_Students_2020',

        '2021.13': 'Total_Students_2021',
        '2021.14': 'Female_Students_2021',
        '2021.15': 'Master_Students_2021',
        '2021.16': 'Master_Female_Students_2021',
        '2021.17': 'PhD_Students_2021',
        '2021.18': 'PhD_Female_Students_2021',

        '2022.13': 'Total_Students_2022',
        '2022.14': 'Female_Students_2022',
        '2022.15': 'Master_Students_2022',
        '2022.16': 'Master_Female_Students_2022',
        '2022.17': 'PhD_Students_2022',
        '2022.18': 'PhD_Female_Students_2022',

        '2023.13': 'Total_Students_2023',
        '2023.14': 'Female_Students_2023',
        '2023.15': 'Master_Students_2023',
        '2023.16': 'Master_Female_Students_2023',
        '2023.17': 'PhD_Students_2023',
        '2023.18': 'PhD_Female_Students_2023'
    }

    # 열 이름 매핑
    df.rename(columns=columns_mapping, inplace=True)

    # 'Region'과 학생 수 데이터를 포함한 새로운 데이터프레임 만들기
    df_cleaned = df[['시도별(1)', 'Total_Students_2018', 'Female_Students_2018', 'Master_Students_2018', 'PhD_Students_2018', 'PhD_Female_Students_2018',
                     'Total_Students_2019', 'Female_Students_2019', 'Master_Students_2019', 'PhD_Students_2019', 'PhD_Female_Students_2019',
                     'Total_Students_2020', 'Female_Students_2020', 'Master_Students_2020', 'PhD_Students_2020', 'PhD_Female_Students_2020',
                     'Total_Students_2021', 'Female_Students_2021', 'Master_Students_2021', 'PhD_Students_2021', 'PhD_Female_Students_2021',
                     'Total_Students_2022', 'Female_Students_2022', 'Master_Students_2022', 'PhD_Students_2022', 'PhD_Female_Students_2022',
                     'Total_Students_2023', 'Female_Students_2023', 'Master_Students_2023', 'PhD_Students_2023', 'PhD_Female_Students_2023']]

    # 지역 이름을 'Region'으로 설정
    df_cleaned.rename(columns={'시도별(1)': 'Region'}, inplace=True)

    # 불필요한 행 삭제 (예: 첫 번째와 세 번째 행)
    df_cleaned = df_cleaned.drop([0, 3])

    # 행 번호 리셋
    df_cleaned.reset_index(drop=True, inplace=True)

    # 강원특별자치도를 강원도로 수정
    df_cleaned['Region'] = df_cleaned['Region'].replace('강원특별자치도', '강원도')

    # 특정 지역의 첫 번째 행만 남기기
    df_cleaned = df_cleaned[df_cleaned['Region'].duplicated(keep='first') == False]

    st.write("### Cleaned Data Preview:")
    st.dataframe(df_cleaned)

except Exception as e:
    st.error(f"❌ Error loading or processing data: {e}")

# ---- GeoJSON 데이터 로드 ----
try:
    # GeoJSON 데이터 로드
    korea_geo = gpd.read_file(geojson_path)
    st.write("### GeoJSON Data Preview:")
    st.write(korea_geo.head())

    # 좌표계 변환 (Folium은 EPSG:4326만 지원)
    if korea_geo.crs != "EPSG:4326":
        korea_geo = korea_geo.to_crs(epsg=4326)
        st.write("✅ GeoJSON CRS converted to EPSG:4326 (WGS84)")

except Exception as e:
    st.error(f"❌ Error loading GeoJSON data: {e}")
# ---- 사이드바: 연도 선택 ----
year = st.sidebar.selectbox("Select Year", ["2018", "2019", "2020", "2021", "2022", "2023"], key="year_selectbox")

# 연도별 학생 수 열 리스트
columns_to_select = [
    'Region', 
    f'Total_Students_{year}', 
    f'Female_Students_{year}', 
    f'Master_Students_{year}', 
    f'PhD_Students_{year}', 
    f'PhD_Female_Students_{year}'
]

# 해당 연도에 맞는 데이터만 선택
df_year = df_cleaned[columns_to_select]

# 각 연도에 대해 학생 수 열들을 숫자 타입으로 변환
columns_for_conversion = [
    f'Total_Students_{year}', 
    f'Female_Students_{year}', 
    f'Master_Students_{year}', 
    f'PhD_Students_{year}', 
    f'PhD_Female_Students_{year}'
]

# 숫자 타입으로 변환 (NaN 값은 자동으로 처리)
for col in columns_for_conversion:
    df_year[col] = pd.to_numeric(df_year[col], errors='coerce')

# ---- 데이터 병합 ----
try:
    # GeoJSON 데이터 이름 통일 (강원특별자치도 -> 강원도)
    korea_geo['CTP_KOR_NM'] = korea_geo['CTP_KOR_NM'].replace({'강원특별자치도': '강원도'})

    # 데이터 병합
    merged_data = korea_geo.merge(
        df_year,  # 연도별로 필터링된 데이터 사용
        left_on='CTP_KOR_NM',
        right_on='Region',
        how='left'
    )

    st.write(f"### Merged Data Preview for {year}:")
    st.dataframe(merged_data)

except Exception as e:
    st.error(f"❌ Error merging data: {e}")

# ---- 지도 시각화 ----
st.write(f"## {year} Map Visualization of Graduate Enrollment")

try:
    # Folium 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    # 총학생수 Choropleth 지도 추가
    folium.Choropleth(
        geo_data=merged_data.to_json(),
        data=merged_data,
        columns=['CTP_KOR_NM', f'Total_Students_{year}'],
        key_on='feature.properties.CTP_KOR_NM',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Total Students in {year}'
    ).add_to(m)

    # 석사 학생수 Choropleth 지도 추가
    folium.Choropleth(
        geo_data=merged_data.to_json(),
        data=merged_data,
        columns=['CTP_KOR_NM', f'Master_Students_{year}'],
        key_on='feature.properties.CTP_KOR_NM',
        fill_color='BuPu',  # 색상을 다르게 설정
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Master Students in {year}'
    ).add_to(m)

    # 박사 학생수 Choropleth 지도 추가
    folium.Choropleth(
        geo_data=merged_data.to_json(),
        data=merged_data,
        columns=['CTP_KOR_NM', f'PhD_Students_{year}'],
        key_on='feature.properties.CTP_KOR_NM',
        fill_color='OrRd',  # 색상을 다르게 설정
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'PhD Students in {year}'
    ).add_to(m)

    # 툴팁 추가 (지역, 총학생수, 석사, 박사)
    folium.GeoJson(
        merged_data,
        tooltip=GeoJsonTooltip(
            fields=['CTP_KOR_NM', f'Total_Students_{year}', f'Master_Students_{year}', f'PhD_Students_{year}'],
            aliases=['Region', 'Total Students', 'Master Students', 'PhD Students'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 1px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800
        )
    ).add_to(m)

    # 레이어 컨트롤 추가 (각각의 학생 수를 선택할 수 있게)
    folium.LayerControl().add_to(m)

    # Streamlit에서 Folium 지도 출력
    st_folium(m, width=800, height=600)

except Exception as e:
    st.error(f"❌ Error displaying map: {e}")


