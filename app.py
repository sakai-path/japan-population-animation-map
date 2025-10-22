import streamlit as st
import plotly.express as px
import pandas as pd
import requests

def get_estat_data_safe():
    """安全なデータ取得（段階的エラーチェック付き）"""
    try:
        st.write("### ステップ1: APIキー取得")
        app_id = st.secrets["e_stat"]["app_id"]
        st.success(f"✅ APIキー取得成功")
        
        st.write("### ステップ2: API呼び出し")
        url = 'https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData'
        params = {
            'appId': app_id,
            'statsDataId': '0003448239',
            'lang': 'J'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'GET_STATS_DATA' in data and data['GET_STATS_DATA']['RESULT']['STATUS'] == '0':
            st.success("✅ API呼び出し成功")
            
            st.write("### ステップ3: データ構造確認")
            values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']
            st.write(f"データ件数: {len(values)}")
            st.write("サンプルデータ:")
            st.json(values[0])  # 最初の1件を表示
            
            st.write("### ステップ4: データ変換")
            
            # 都道府県マッピング（一部のみテスト）
            prefectures = {
                '01000': '北海道', '13000': '東京都', '27000': '大阪府'
            }
            
            # 緯度経度（一部のみテスト）
            coordinates = {
                '北海道': [43.06, 141.35], 
                '東京都': [35.68, 139.76], 
                '大阪府': [34.69, 135.50]
            }
            
            # データ変換（最初の10件のみ）
            map_data = []
            for i, value in enumerate(values[:10]):
                area_code = value.get('@area')
                st.write(f"処理中 {i+1}: area_code={area_code}")
                
                if area_code in prefectures:
                    pref_name = prefectures[area_code]
                    if pref_name in coordinates:
                        map_data.append({
                            '都道府県': pref_name,
                            '出入国者数': int(value.get('$', 0)),
                            '緯度': coordinates[pref_name][0],
                            '経度': coordinates[pref_name][1]
                        })
                        st.write(f"✅ {pref_name}: {value.get('$', 0)}人")
            
            st.write("### ステップ5: DataFrame作成")
            df = pd.DataFrame(map_data)
            st.write(f"DataFrame作成成功: {len(df)}行")
            st.dataframe(df)
            
            return df
        else:
            st.error("❌ API呼び出し失敗")
            return None
            
    except Exception as e:
        st.error(f"❌ エラー発生: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

def main():
    st.set_page_config(
        page_title="日本出入国者数マップ（デバッグ版）",
        page_icon="🗾",
        layout="wide"
    )
    
    st.title('🗾 日本出入国者数マップ（デバッグ版）')
    
    if st.button('📊 安全なデータ取得テスト'):
        df = get_estat_data_safe()
        
        if df is not None and len(df) > 0:
            st.write("### 🎉 成功！簡単な地図表示")
            
            fig = px.scatter_mapbox(
                df,
                lat='緯度',
                lon='経度',
                hover_name='都道府県',
                hover_data=['出入国者数'],
                color='出入国者数',
                size='出入国者数',
                zoom=4.5,
                height=400
            )
            
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
