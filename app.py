import streamlit as st
import plotly.express as px
import pandas as pd
import requests
import time

def get_estat_data_filtered(cat01_filter='001', cat02_filter='000', cat03_filter='001', area_filter=None):
    """フィルタリング機能付きデータ取得（都道府県フィルタ対応）"""
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
            
            # 都道府県コードの逆引き
            pref_to_code = {v: k for k, v in prefectures.items()}
            
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
                        
                        # 都道府県フィルタのチェック
                        if area_filter and area_filter != '全都道府県':
                            if pref_name != area_filter:
                                continue
                        
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

def create_animated_comparison():
    """アニメーション比較機能"""
    st.subheader('🎬 アニメーション比較')
    
    animation_type = st.selectbox(
        'アニメーション種類',
        ['日本人→外国人', '入国→出国', '男性→女性→男女計']
    )
    
    if st.button('▶️ アニメーション開始'):
        placeholder = st.empty()
        
        if animation_type == '日本人→外国人':
            patterns = [
                ('🇯🇵 日本人（入国・男女計）', '001', '000', '001'),
                ('🌍 外国人（入国・男女計）', '001', '000', '002')
            ]
        elif animation_type == '入国→出国':
            patterns = [
                ('📥 入国（日本人・男女計）', '001', '000', '001'),
                ('📤 出国（日本人・男女計）', '002', '000', '001')
            ]
        else:  # 男性→女性→男女計
            patterns = [
                ('👨 男性（入国・日本人）', '001', '001', '001'),
                ('👩 女性（入国・日本人）', '001', '002', '001'),
                ('👥 男女計（入国・日本人）', '001', '000', '001')
            ]
        
        for title, cat01, cat02, cat03 in patterns:
            df = get_estat_data_filtered(cat01, cat02, cat03)
            if df is not None and len(df) > 0:
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
                    height=500,
                    title=title
                )
                fig.update_layout(mapbox_style="open-street-map")
                placeholder.plotly_chart(fig, use_container_width=True)
                time.sleep(2)

def main():
    st.set_page_config(
        page_title="日本出入国者数マップ",
        page_icon="🗾",
        layout="wide"
    )
    
    st.title('🗾 日本出入国者数マップ')
    st.write('e-Statデータを使用した都道府県別出入国者数の可視化（2020年10月～2021年9月）')
    
    # サイドバー設定
    st.sidebar.header('🎛️ 表示設定')
    
    # 表示モード選択
    display_mode = st.sidebar.radio(
        '表示モード',
        ['🗺️ 単一地図表示', '⚖️ 左右比較表示', '📊 数値比較表', '🎬 アニメーション']
    )
    
    if display_mode == '🗺️ 単一地図表示':
        # 単一表示モード
        st.sidebar.subheader('フィルタ設定')
        
        # 都道府県選択
        prefecture_list = ['全都道府県', '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
                          '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県',
                          '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県',
                          '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県', '鳥取県',
                          '島根県', '岡山県', '広島県', '山口県', '徳島県', '香川県', '愛媛県', '高知県',
                          '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']
        
        selected_prefecture = st.sidebar.selectbox('都道府県', prefecture_list)
        
        cat01_options = {'入国者数': '001', '出国者数': '002'}
        cat01_label = st.sidebar.selectbox('入国/出国', list(cat01_options.keys()))
        cat01_value = cat01_options[cat01_label]
        
        cat02_options = {'男女計': '000', '男性': '001', '女性': '002'}
        cat02_label = st.sidebar.selectbox('男女別', list(cat02_options.keys()))
        cat02_value = cat02_options[cat02_label]
        
        cat03_options = {'日本人': '001', '外国人': '002'}
        cat03_label = st.sidebar.selectbox('日本人/外国人', list(cat03_options.keys()))
        cat03_value = cat03_options[cat03_label]
        
        # データ取得
        df = get_estat_data_filtered(cat01_value, cat02_value, cat03_value, selected_prefecture)
        
        if df is not None and len(df) > 0:
            # 現在の設定表示
            filter_text = f"{cat01_label} × {cat02_label} × {cat03_label}"
            if selected_prefecture != '全都道府県':
                filter_text += f" × {selected_prefecture}"
            st.info(f"📋 表示中: {filter_text}")
            
            # 地図表示
            zoom_level = 8 if selected_prefecture != '全都道府県' else 4.5
            
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
                zoom=zoom_level,
                height=600,
                title=filter_text
            )
            
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
            
            # 統計情報
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("総人数", f"{df['人数'].sum():,}人")
            
            with col2:
                if len(df) > 0:
                    max_pref = df.loc[df['人数'].idxmax()]
                    st.metric("最多", f"{max_pref['都道府県']}: {max_pref['人数']:,}人")
            
            with col3:
                st.metric("平均", f"{df['人数'].mean():.0f}人")
            
            # データテーブル
            if selected_prefecture == '全都道府県':
                st.subheader('📊 都道府県別ランキング')
                df_sorted = df.sort_values('人数', ascending=False).reset_index(drop=True)
                df_sorted.index += 1
                st.dataframe(df_sorted[['都道府県', '人数']], use_container_width=True)
                
                # 上位10都道府県のグラフ
                st.subheader('📈 上位10都道府県')
                top10 = df_sorted.head(10)
                
                fig_bar = px.bar(
                    top10,
                    x='都道府県',
                    y='人数',
                    title=f'{filter_text} 上位10都道府県',
                    color='人数',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.subheader(f'📊 {selected_prefecture}の詳細')
                st.dataframe(df[['都道府県', '人数']], use_container_width=True)
        else:
            st.warning("選択した条件のデータがありません")
    
    elif display_mode == '⚖️ 左右比較表示':
        # 左右比較表示
        st.sidebar.subheader('比較設定')
        
        comparison_type = st.sidebar.selectbox(
            '比較項目',
            ['日本人 vs 外国人', '入国 vs 出国', '男性 vs 女性']
        )
        
        if comparison_type == '日本人 vs 外国人':
            df1 = get_estat_data_filtered('001', '000', '001')
            df2 = get_estat_data_filtered('001', '000', '002')
            title1, title2 = '🇯🇵 日本人（入国・男女計）', '🌍 外国人（入国・男女計）'
            
        elif comparison_type == '入国 vs 出国':
            df1 = get_estat_data_filtered('001', '000', '001')
            df2 = get_estat_data_filtered('002', '000', '001')
            title1, title2 = '📥 入国（日本人・男女計）', '📤 出国（日本人・男女計）'
            
        else:  # 男性 vs 女性
            df1 = get_estat_data_filtered('001', '001', '001')
            df2 = get_estat_data_filtered('001', '002', '001')
            title1, title2 = '👨 男性（入国・日本人）', '👩 女性（入国・日本人）'
        
        col1, col2 = st.columns(2)
        
        # スケール統一のための最大値計算
        max_val = 0
        if df1 is not None and len(df1) > 0:
            max_val = max(max_val, df1['人数'].max())
        if df2 is not None and len(df2) > 0:
            max_val = max(max_val, df2['人数'].max())
        
        with col1:
            st.subheader(title1)
            if df1 is not None and len(df1) > 0:
                fig1 = px.scatter_mapbox(
                    df1,
                    lat='緯度',
                    lon='経度',
                    hover_name='都道府県',
                    hover_data=['人数'],
                    color='人数',
                    size='人数',
                    color_continuous_scale='Reds',
                    size_max=40,
                    zoom=4.5,
                    height=500,
                    range_color=[0, max_val]
                )
                fig1.update_layout(mapbox_style="open-street-map")
                st.plotly_chart(fig1, use_container_width=True)
                
                st.metric("総人数", f"{df1['人数'].sum():,}人")
                
                # 上位5都道府県
                top5_1 = df1.nlargest(5, '人数')
                st.write("**上位5都道府県:**")
                for i, row in top5_1.iterrows():
                    st.write(f"{row['都道府県']}: {row['人数']:,}人")
        
        with col2:
            st.subheader(title2)
            if df2 is not None and len(df2) > 0:
                fig2 = px.scatter_mapbox(
                    df2,
                    lat='緯度',
                    lon='経度',
                    hover_name='都道府県',
                    hover_data=['人数'],
                    color='人数',
                    size='人数',
                    color_continuous_scale='Blues',
                    size_max=40,
                    zoom=4.5,
                    height=500,
                    range_color=[0, max_val]
                )
                fig2.update_layout(mapbox_style="open-street-map")
                st.plotly_chart(fig2, use_container_width=True)
                
                st.metric("総人数", f"{df2['人数'].sum():,}人")
                
                # 上位5都道府県
                top5_2 = df2.nlargest(5, '人数')
                st.write("**上位5都道府県:**")
                for i, row in top5_2.iterrows():
                    st.write(f"{row['都道府県']}: {row['人数']:,}人")
    
    elif display_mode == '📊 数値比較表':
        # 数値比較表
        st.subheader('📊 全パターン数値比較')
        
        patterns = [
            ('入国・日本人・男女計', '001', '000', '001'),
            ('入国・外国人・男女計', '001', '000', '002'),
            ('出国・日本人・男女計', '002', '000', '001'),
            ('出国・外国人・男女計', '002', '000', '002'),
            ('入国・日本人・男性', '001', '001', '001'),
            ('入国・日本人・女性', '001', '002', '001'),
            ('入国・外国人・男性', '001', '001', '002'),
            ('入国・外国人・女性', '001', '002', '002')
        ]
        
        comparison_data = []
        for name, cat01, cat02, cat03 in patterns:
            df = get_estat_data_filtered(cat01, cat02, cat03)
            if df is not None and len(df) > 0:
                total = df['人数'].sum()
                max_pref = df.loc[df['人数'].idxmax()]
                min_pref = df.loc[df['人数'].idxmin()]
                comparison_data.append({
                    'パターン': name,
                    '総人数': f"{total:,}人",
                    '最多都道府県': f"{max_pref['都道府県']} ({max_pref['人数']:,}人)",
                    '最少都道府県': f"{min_pref['都道府県']} ({min_pref['人数']:,}人)",
                    '平均': f"{df['人数'].mean():.0f}人"
                })
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
            
            # 総人数の比較グラフ
            st.subheader('📈 総人数比較')
            
            # 数値のみ抽出してグラフ用データ作成
            graph_data = []
            for item in comparison_data:
                total_num = int(item['総人数'].replace(',', '').replace('人', ''))
                graph_data.append({
                    'パターン': item['パターン'],
                    '総人数': total_num
                })
            
            df_graph = pd.DataFrame(graph_data)
            fig_comparison = px.bar(
                df_graph,
                x='パターン',
                y='総人数',
                title='パターン別総人数比較',
                color='総人数',
                color_continuous_scale='Viridis'
            )
            fig_comparison.update_xaxes(tickangle=45)
            st.plotly_chart(fig_comparison, use_container_width=True)
    
    else:  # アニメーション
        create_animated_comparison()
    
    # フッター
    st.markdown("---")
    st.markdown("**データソース**: e-Stat（政府統計の総合窓口）| **対象期間**: 2020年10月～2021年9月")

if __name__ == "__main__":
    main()
