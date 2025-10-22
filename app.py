import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time
import requests

def test_specific_stats(stats_id):
    try:
        app_id = st.secrets["e_stat"]["app_id"]
        
        url = 'https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData'
        params = {
            'appId': app_id,
            'statsDataId': stats_id,
            'lang': 'J'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'GET_STATS_DATA' in data:
            result = data['GET_STATS_DATA']['RESULT']
            status = result['STATUS']
            
            if status == '0':
                st.success(f"✅ 統計表ID {stats_id} のデータ取得成功！")
                
                statistical_data = data['GET_STATS_DATA']['STATISTICAL_DATA']
                
                table_inf = statistical_data['TABLE_INF']
                st.write(f"**統計表名**: {table_inf['TITLE']}")
                st.write(f"**統計名**: {table_inf['STATISTICS_NAME']}")
                
                if 'CLASS_INF' in statistical_data:
                    st.write("### 分類情報:")
                    class_inf = statistical_data['CLASS_INF']['CLASS_OBJ']
                    for cls in class_inf:
                        st.write(f"- {cls['@name']}: {cls['@id']}")
                
                if 'DATA_INF' in statistical_data:
                    values = statistical_data['DATA_INF']['VALUE']
                    st.write(f"### データ件数: {len(values)}")
                    if len(values) > 0:
                        st.write("### データサンプル（最初の5件）:")
                        for i, value in enumerate(values[:5]):
                            st.write(f"{i+1}. {value}")
                    else:
                        st.warning("データが0件です")
                
                return data
            else:
                error_msg = result.get('ERROR_MSG', '不明なエラー')
                st.error(f"❌ 統計表ID {stats_id} - APIエラー: {error_msg}")
        else:
            st.error(f"❌ 統計表ID {stats_id} - 予期しないレスポンス形式")
            
    except Exception as e:
        st.error(f"❌ 統計表ID {stats_id} - エラー: {e}")
    
    return None

def create_sample_data():
    prefectures = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', 
                   '茨城', '栃木', '群馬', '埼玉', '千葉', '東京', '神奈川']
    
    coords = {
        '北海道': [43.06, 141.35], '青森': [40.82, 140.74], '岩手': [39.70, 141.15],
        '宮城': [38.27, 140.87], '秋田': [39.72, 140.10], '山形': [38.24, 140.36],
        '福島': [37.75, 140.47], '茨城': [36.34, 140.45], '栃木': [36.57, 139.88],
        '群馬': [36.39, 139.06], '埼玉': [35.86, 139.65], '千葉': [35.61, 140.12],
        '東京': [35.68, 139.76], '神奈川': [35.45, 139.64]
    }
    
    data = []
    for year in range(2000, 2021):
        for pref in prefectures:
            base_pop = np.random.randint(500, 1400)
            if pref in ['東京', '神奈川', '埼玉', '千葉']:
                pop_change = (year - 2000) * 0.5 + np.random.normal(0, 2)
            else:
                pop_change = -(year - 2000) * 0.3 + np.random.normal(0, 1.5)
            
            data.append({
                '年': year,
                '都道府県': pref,
                '人口': base_pop + pop_change,
                '緯度': coords[pref][0],
                '経度': coords[pref][1],
                '人口変化率': pop_change
            })
    
    return pd.DataFrame(data)

def main():
    st.set_page_config(
        page_title="日本人口変化アニメーション地図",
        page_icon="🗾",
        layout="wide"
    )
    
    st.title('🗾 日本人口変化アニメーション地図')
    st.write('2000年〜2020年の人口変化を時系列で可視化')
    
    st.sidebar.header('API設定')
    
    # 有名な統計表ID候補
    candidate_ids = [
        '0003448238',  # 令和2年国勢調査
        '0003448239',  # 令和2年国勢調査 都道府県別
        '0003312212',  # 平成27年国勢調査
        '0003109687',  # 平成22年国勢調査
        '0000030001',  # 人口推計
        '0000020201'   # 住民基本台帳
    ]
    
    st.sidebar.write("### 国勢調査・人口統計ID:")
    for stats_id in candidate_ids:
        if st.sidebar.button(f'🔍 {stats_id}'):
            test_specific_stats(stats_id)
    
    # 手動入力
    st.sidebar.write("### 手動入力:")
    manual_id = st.sidebar.text_input('統計表ID', '')
    if st.sidebar.button('🔍 手動テスト'):
        if manual_id:
            test_specific_stats(manual_id)
    
    df = create_sample_data()
    
    st.sidebar.header('表示設定')
    
    selected_year = st.sidebar.slider(
        '表示年', 
        min_value=2000, 
        max_value=2020, 
        value=2000,
        step=1
    )
    
    if st.sidebar.button('▶️ アニメーション再生'):
        placeholder = st.empty()
        
        for year in range(2000, 2021):
            year_data = df[df['年'] == year]
            
            fig = px.scatter_mapbox(
                year_data,
                lat='緯度',
                lon='経度',
                hover_name='都道府県',
                hover_data=['人口', '人口変化率'],
                color='人口変化率',
                size='人口',
                color_continuous_scale='RdYlBu_r',
                size_max=30,
                zoom=4.5,
                height=600,
                title=f'{year}年の人口分布'
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                coloraxis_colorbar=dict(
                    title="人口変化率",
                    ticksuffix="%"
                )
            )
            
            placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(0.5)
    
    year_data = df[df['年'] == selected_year]
    
    fig = px.scatter_mapbox(
        year_data,
        lat='緯度',
        lon='経度',
        hover_name='都道府県',
        hover_data=['人口', '人口変化率'],
        color='人口変化率',
        size='人口',
        color_continuous_scale='RdYlBu_r',
        size_max=30,
        zoom=4.5,
        height=600,
        title=f'{selected_year}年の人口分布'
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        coloraxis_colorbar=dict(
            title="人口変化率",
            ticksuffix="%"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader(f'{selected_year}年のデータ')
    st.dataframe(year_data[['都道府県', '人口', '人口変化率']].sort_values('人口変化率', ascending=False))

if __name__ == "__main__":
    main()
