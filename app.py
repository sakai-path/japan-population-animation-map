import streamlit as st
import plotly.express as px
import pandas as pd
import requests

def get_estat_data_filtered(cat01_filter='001', cat02_filter='000', cat03_filter='001'):
    """フィルタリング機能付きデータ取得"""
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
        
        if 'GET_STATS_DATA' in data and str(data['GET_STATS_DATA']['RESULT']['STATUS']) == '0':
            values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']
            
            # 都道府県マッピング
            prefectures = {
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
            
            # 緯度経度データ
            coordinates = {
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
            
            # フィルタリングしてデータ変換
            map_data = []
            
            for value in values:
                # フィルタ条件をチェック
                if (value.get('@cat01') == cat01_filter and 
                    value.get('@cat02') == cat02_filter and 
                    value.get('@cat03') == cat03_filter):
                    
                    area_code = value.get('@area')
                    if area_code in prefectures:  # 全国(00000)を除く
                        pref_name = prefectures[area_code]
                        if pref_name in coordinates:
                            map_data.append({
                                '都道府県': pref_name,
                                '人数': int(value.get('$', 0)),
                                '緯度': coordinates[pref_name][0],
                                '経度': coordinates[pref_name][1]
                            })
            
            return pd.DataFrame(map_data)
        else:
            st.error("APIからデータを取得できませんでした")
            return None
        
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return None

def main():
    st.set_page_config(
        page_title="日本出入国者数マップ（比較機能付き）",
        page_icon="🗾",
        layout="wide"
    )
    
    st.title('🗾 日本出入国者数マップ（比較機能付き）')
    st.write('e-Statデータを使用した都道府県別出入国者数の可視化（2020年10月～2021年9月）')
    
    # サイドバーでフィルタ設定
    st.sidebar.header('📊 データフィルタ')
    
    # 入国/出国選択
    cat01_options = {
        '入国者数': '001',
        '出国者数': '002'
    }
    cat01_label = st.sidebar.selectbox('入国/出国', list(cat01_options.keys()))
    cat01_value = cat01_options[cat01_label]
    
    # 男女別選択
    cat02_options = {
        '男女計': '000',
        '男性': '001',
        '女性': '002'
    }
    cat02_label = st.sidebar.selectbox('男女別', list(cat02_options.keys()))
    cat02_value = cat02_options[cat02_label]
    
    # 日本人/外国人選択
    cat03_options = {
        '日本人': '001',
        '外国人': '002'
    }
    cat03_label = st.sidebar.selectbox('日本人/外国人', list(cat03_options.keys()))
    cat03_value = cat03_options[cat03_label]
    
    # 比較機能
    st.sidebar.header('🔄 クイック比較')
    if st.sidebar.button('🇯🇵 日本人 vs 🌍 外国人'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('🇯🇵 日本人')
            df_jp = get_estat_data_filtered(cat01_value, cat02_value, '001')
            if df_jp is not None and len(df_jp) > 0:
                st.metric("総人数", f"{df_jp['人数'].sum():,}人")
                top_jp = df_jp.loc[df_jp['人数'].idxmax()]
                st.write(f"最多: {top_jp['都道府県']} ({top_jp['人数']:,}人)")
        
        with col2:
            st.subheader('🌍 外国人')
            df_fg = get_estat_data_filtered(cat01_value, cat02_value, '002')
            if df_fg is not None and len(df_fg) > 0:
                st.metric("総人数", f"{df_fg['人数'].sum():,}人")
                top_fg = df_fg.loc[df_fg['人数'].idxmax()]
                st.write(f"最多: {top_fg['都道府県']} ({top_fg['人数']:,}人)")
    
    if st.sidebar.button('📥 入国 vs 📤 出国'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('📥 入国')
            df_in = get_estat_data_filtered('001', cat02_value, cat03_value)
            if df_in is not None and len(df_in) > 0:
                st.metric("総人数", f"{df_in['人数'].sum():,}人")
                top_in = df_in.loc[df_in['人数'].idxmax()]
                st.write(f"最多: {top_in['都道府県']} ({top_in['人数']:,}人)")
        
        with col2:
            st.subheader('📤 出国')
            df_out = get_estat_data_filtered('002', cat02_value, cat03_value)
            if df_out is not None and len(df_out) > 0:
                st.metric("総人数", f"{df_out['人数'].sum():,}人")
                top_out = df_out.loc[df_out['人数'].idxmax()]
                st.write(f"最多: {top_out['都道府県']} ({top_out['人数']:,}人)")
    
    # データ取得
    with st.spinner('データを取得中...'):
        df = get_estat_data_filtered(cat01_value, cat02_value, cat03_value)
    
    if df is not None and len(df) > 0:
        
        # 現在の設定を表示
        st.info(f"📋 現在の表示: {cat01_label} × {cat02_label} × {cat03_label}")
        
        # 地図表示
        fig = px.scatter_mapbox(
            df,
            lat='緯度',
            lon='経度',
            hover_name='都道府県',
            hover_data=['人数'],
            color='人数',
            size='人数',
            color_continuous_scale='Viridis',
            size_max=50,
            zoom=4.5,
            height=600,
            title=f'{cat01_label}（{cat02_label}・{cat03_label}）'
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            coloraxis_colorbar=dict(
                title="人数"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 統計情報
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("総人数", f"{df['人数'].sum():,}人")
        
        with col2:
            max_pref = df.loc[df['人数'].idxmax()]
            st.metric("最多", f"{max_pref['都道府県']}: {max_pref['人数']:,}人")
        
        with col3:
            st.metric("平均", f"{df['人数'].mean():.0f}人")
        
        # データテーブル
        st.subheader('📊 都道府県別データ')
        
        # ランキング表示
        df_sorted = df.sort_values('人数', ascending=False).reset_index(drop=True)
        df_sorted.index += 1  # 1から始まるランキング
        
        st.dataframe(
            df_sorted[['都道府県', '人数']],
            use_container_width=True
        )
        
        # 上位5都道府県のグラフ
        st.subheader('📈 上位5都道府県')
        top5 = df_sorted.head(5)
        
        fig_bar = px.bar(
            top5,
            x='都道府県',
            y='人数',
            title=f'{cat01_label}（{cat02_label}・{cat03_label}） 上位5都道府県',
            color='人数',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
    else:
        st.error("データの取得に失敗しました。")

if __name__ == "__main__":
    main()
