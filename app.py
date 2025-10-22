import streamlit as st
import plotly.express as px
import pandas as pd
import requests

def debug_data_structure():
    """データ構造の詳細確認"""
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
            
            # 分類情報の確認
            st.subheader("📋 分類情報")
            class_objs = data['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']
            
            for cls in class_objs:
                st.write(f"**{cls['@name']} ({cls['@id']})**")
                if 'CLASS' in cls:
                    classes = cls['CLASS'] if isinstance(cls['CLASS'], list) else [cls['CLASS']]
                    for c in classes[:10]:  # 最初の10件のみ表示
                        st.write(f"  - {c.get('@name', 'N/A')}: {c.get('@code', 'N/A')}")
                    if len(classes) > 10:
                        st.write(f"  ... 他 {len(classes)-10} 件")
                st.write("---")
            
            # 実際のデータサンプル
            st.subheader("📊 データサンプル")
            values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']
            
            st.write(f"総データ件数: {len(values)}")
            
            # 最初の20件を表示
            st.write("**最初の20件:**")
            sample_data = []
            for i, value in enumerate(values[:20]):
                sample_data.append({
                    'No': i+1,
                    'area': value.get('@area'),
                    'time': value.get('@time'),
                    'tab': value.get('@tab'),
                    'cat01': value.get('@cat01'),
                    'cat02': value.get('@cat02'),
                    'cat03': value.get('@cat03'),
                    'value': value.get('$'),
                    'unit': value.get('@unit')
                })
            
            st.dataframe(pd.DataFrame(sample_data))
            
            # ユニークな値の確認
            st.subheader("🔍 ユニークな値の確認")
            
            areas = set()
            times = set()
            tabs = set()
            cat01s = set()
            cat02s = set()
            cat03s = set()
            
            for value in values:
                areas.add(value.get('@area'))
                times.add(value.get('@time'))
                tabs.add(value.get('@tab'))
                cat01s.add(value.get('@cat01'))
                cat02s.add(value.get('@cat02'))
                cat03s.add(value.get('@cat03'))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**地域コード数**: {len(areas)}")
                st.write(f"地域コード例: {sorted(list(areas))[:10]}")
                
                st.write(f"**時間コード数**: {len(times)}")
                st.write(f"時間コード: {sorted(list(times))}")
                
                st.write(f"**表章項目数**: {len(tabs)}")
                st.write(f"表章項目: {sorted(list(tabs))}")
            
            with col2:
                st.write(f"**cat01数**: {len(cat01s)}")
                st.write(f"cat01: {sorted(list(cat01s))}")
                
                st.write(f"**cat02数**: {len(cat02s)}")
                st.write(f"cat02: {sorted(list(cat02s))}")
                
                st.write(f"**cat03数**: {len(cat03s)}")
                st.write(f"cat03: {sorted(list(cat03s))}")
            
            return data
        else:
            st.error("データ取得失敗")
            return None
            
    except Exception as e:
        st.error(f"エラー: {e}")
        return None

def main():
    st.set_page_config(
        page_title="データ構造デバッグ",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title('🔍 データ構造デバッグ')
    st.write('実際のデータ構造を詳しく確認します')
    
    if st.button('📊 データ構造確認'):
        debug_data_structure()

if __name__ == "__main__":
    main()
