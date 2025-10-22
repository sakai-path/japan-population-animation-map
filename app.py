import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time
import requests

def _as_list(x):
    return x if isinstance(x, list) else ([] if x is None else [x])

def get_real_data():
    """実際のe-Statデータを取得して地図用に変換"""
    try:
        app_id = st.secrets["e_stat"]["app_id"]
        
        url = 'https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData'
        params = {
            'appId': app_id,
            'statsDataId': '0003448239',
            'lang': 'J'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'GET_STATS_DATA' in data:
            result = data['GET_STATS_DATA']['RESULT']
            status = str(result.get('STATUS'))
            
            if status == '0':
                statistical_data = data['GET_STATS_DATA']['STATISTICAL_DATA']
                values = _as_list(statistical_data.get('DATA_INF', {}).get('VALUE'))
                
                # 都道府県コードと名前のマッピング
                area_mapping = {
                    '01000': '北海道', '02000': '青森県', '03000': '岩手県', '04000': '宮城県',
                    '05000': '秋田県', '06000': '山形県', '07000': '福島県', '08000': '茨城県',
                    '09000': '栃木県', '10000': '群馬県', '11000': '埼玉県', '12000': '千葉県',
                    '13000': '東京都', '14000': '神奈川県', '15000': '新潟県', '16000': '富山県',
                    '17000': '石川県', '18000': '福井県', '19000': '山梨県', '20000': '長野県',
                    '21000': '岐阜県', '22000': '静岡県', '23000': '愛知県', '24000': '三重県',
                    '25000': '滋賀県', '26000': '京都府', '27000': '大阪府', '28000': '兵庫県',
                    '29000': '奈良県', '30000': '和歌山県', '31000': '鳥取県', '32000': '島根県',
                    '33000': '岡山県', '34000': '広島県', '35000': '山口県', '36000': '徳島県',
                    '37000': '香川県', '38000': '愛媛県', '39000': '高知県', '40000': '福岡県',
                    '41000': '佐賀県', '42000': '長崎県', '43000': '熊本県', '44000': '大分県',
                    '45000': '宮崎県', '46000': '鹿児島県', '47000': '沖縄県'
                }
                
                # 都道府県の緯度経度
                coords = {
                    '北海道': [43.06, 141.35], '青森県': [40.82, 140.74], '岩手県': [39.70, 141.15],
                    '宮城県': [38.27, 140.87], '秋田県': [39.72, 140.10], '山形県': [38.24, 140.36],
                    '福島県': [37.75, 140.47], '茨城県': [36.34, 140.45], '栃木県': [36.57, 139.88],
                    '群馬県': [36.39, 139.06], '埼玉県': [35.86, 139.65], '千葉県': [35.61, 140.12],
                    '東京都': [35.68, 139.76], '神奈川県': [35.45, 139.64], '新潟県': [37.90, 139.02],
                    '富山県': [36.70, 137.21], '石川県': [36.59, 136.63], '福井県': [36.06, 136.22],
                    '山梨県': [35.66, 138.57], '長野県': [36.65, 138.18], '岐阜県': [35.39, 136.72],
                    '静岡県': [34.98, 138.38], '愛知県': [35.18, 136.91], '三重県': [34.73, 136.51],
                    '滋賀県': [35.00, 135.87], '京都府': [35.02, 135.75], '大阪府': [34.69, 135.50],
                    '兵庫県': [34.69, 135.18], '奈良県': [34.69, 135.83], '和歌山県': [34.23, 135.17],
                    '鳥取県': [35.50, 134.23], '島根県': [35.47, 133.05], '岡山県': [34.66, 133.92],
                    '広島県': [34.40, 132.46], '山口県': [34.19, 131.47], '徳島県': [34.07, 134.56],
                    '香川県': [34.34, 134.04], '愛媛県': [33.84, 132.77], '高知県': [33.56, 133.53],
                    '福岡県': [33.61, 130.42], '佐賀県': [33.25, 130.30], '長崎県': [32.74, 129.87],
                    '熊本県': [32.79, 130.74], '大分県': [33.24, 131.61], '宮崎県': [31.91, 131.42],
                    '鹿児島県': [31.56, 130.56], '沖縄県': [26.21, 127.68]
                }
                
                # データを変換
                map_data = []
                for value in values:
                    area_code = value.get('@area')
                    if area_code in area_mapping and area_code != '00000':  # 全国除く
                        pref_name = area_mapping[area_code]
                        if pref_name in coords:
                            map_data.append({
                                '都道府県': pref_name,
                                '出入国者数': int(value.get('$', 0)),
                                '緯度': coords[pref_name][0],
                                '経度': coords[pref_name][1]
                            })
                
                return pd.DataFrame(map_data)
            
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
    
    return None

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
            status = str(result.get('STATUS'))
            msg = result.get('ERROR_MSG', '')
            
            st.write(f"RESULT: STATUS={status} / MESSAGE={msg}")
            
            if status == '0':
                st.success(f"✅ 統計表ID {stats_id} のデータ取得成功！")
                
                statistical_data = data['GET_STATS_DATA']['STATISTICAL_DATA']
                
                table_inf = statistical_data['TABLE_INF']
                st.write(f"**統計表名**: {table_inf['TITLE']}")
                st.write(f"**統計名**: {table_inf['STATISTICS_NAME']}")
                
                if 'CLASS_INF' in statistical_data:
                    st.write("### 分類情報:")
                    class_objs = _as_list(statistical_data['CLASS_INF'].get('CLASS_OBJ', []))
                    for cls in class_objs:
                        st.write(f"- {cls['@name']}: {cls['@id']}")
                
                if 'DATA_INF' in statistical_data:
                    values = _as_list(statistical_data.get('DATA_INF', {}).get('VALUE'))
                    st.write(f"### データ件数: {len(values)}")
                    
                    if len(values) > 0:
                        st.write("### データサンプル（最初の5件）:")
                        for i, value in enumerate(values[:5]):
                            st.write(f"{i+1}. {value}")
                    else:
                        st.warning("データが0件でした")
                
                return data
            else:
                st.error(f"❌ APIエラー (STATUS={status}): {msg or '不明なエラー'}")
                return None
        else:
            st.error(f"❌ 統計表ID {stats_id} - 予期しないレスポンス形式")
            
    except Exception as e:
        st.error(f"❌ 統計表ID {stats_id} - エラー: {e}")
    
    return None

def create_sample_data():
    prefectures = ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', 
                   '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県']
    
    coords = {
        '北海道': [43.06, 141.35], '青森県': [40.82, 140.74], '岩手県': [39.70, 141.15],
        '宮城県': [38.27, 140.87], '秋田県': [39.72, 140.10], '山形県': [38.24, 140.36],
        '福島県': [37.75, 140.47], '茨城県': [36.34, 140.45], '栃木県': [36.57, 139.88],
        '群馬県': [36.39, 139.06], '埼玉県': [35.86, 139.65], '千葉県': [35.61, 140.12],
        '東京都': [35.68, 139.76], '神奈川県': [35.45, 139.64]
    }
    
    data = []
    for year in range(2000, 2021):
        for pref in prefectures:
            base_pop = np.random.randint(500, 1400)
            if pref in ['東京都', '神奈川県', '埼玉県', '千葉県']:
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
    
    # 成功した統計表ID
    candidate_ids = [
        '0000020201',  # 住民基本台帳人口移動報告
        '0003448239',  # 令和2年国勢調査 都道府県別
        '0000030001'   # 人口推計
    ]
    
    st.sidebar.write("### 統計表IDテスト:")
    for stats_id in candidate_ids:
        if st.sidebar.button(f'🔍 {stats_id}'):
            test_specific_stats(stats_id)
    
    # 手動入力
    st.sidebar.write("### 手動入力:")
    manual_id = st.sidebar.text_input('統計表ID', '')
    if st.sidebar.button('🔍 手動テスト'):
        if manual_id:
            test_specific_stats(manual_id)
    
    st.sidebar.header('データ表示')
    
    # 実データ表示オプション
    use_real_data = st.sidebar.checkbox('実際のe-Statデータを使用')
    
    if use_real_data:
        df = get_real_data()
        if df is not None and len(df) > 0:
            st.write("### 実際のe-Statデータ（出入国者数）")
            
            # 地図表示
            fig = px.scatter_mapbox(
                df,
                lat='緯度',
                lon='経度',
                hover_name='都道府県',
                hover_data=['出入国者数'],
                color='出入国者数',
                size='出入国者数',
                color_continuous_scale='Viridis',
                size_max=30,
                zoom=4.5,
                height=600,
                title='都道府県別出入国者数（2020年）'
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                coloraxis_colorbar=dict(
                    title="出入国者数",
                    ticksuffix="人"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # データテーブル
            st.subheader('都道府県別データ')
            st.dataframe(df.sort_values('出入国者数', ascending=False))
        else:
            st.error("実データの取得に失敗しました")
            df = create_sample_data()
    else:
        df = create_sample_data()
    
    if not use_real_data:
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
