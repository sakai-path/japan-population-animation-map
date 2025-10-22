import streamlit as st
import plotly.express as px
import pandas as pd
import requests

def test_specific_stats(stats_id):
    """さっき成功したテスト関数（そのまま）"""
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
                return data
            else:
                st.error(f"❌ APIエラー (STATUS={status}): {msg}")
                return None
        else:
            st.error("❌ 予期しないレスポンス形式")
            
    except Exception as e:
        st.error(f"❌ エラー: {e}")
    
    return None

def get_simple_data():
    """シンプルなデータ取得（エラー詳細表示付き）"""
    try:
        st.write("### データ取得開始...")
        
        app_id = st.secrets["e_stat"]["app_id"]
        st.write(f"✅ APIキー取得成功: {app_id[:10]}...")
        
        url = 'https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData'
        params = {
            'appId': app_id,
            'statsDataId': '0003448239',
            'lang': 'J'
        }
        
        st.write("### API呼び出し中...")
        response = requests.get(url, params=params)
        st.write(f"レスポンスステータス: {response.status_code}")
        
        data = response.json()
        
        if 'GET_STATS_DATA' in data:
            result = data['GET_STATS_DATA']['RESULT']
            status = str(result.get('STATUS'))
            msg = result.get('ERROR_MSG', '')
            
            st.write(f"API STATUS: {status} / MESSAGE: {msg}")
            
            if status == '0':
                st.success("✅ データ取得成功！")
                
                # データ件数確認
                values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']
                st.write(f"データ件数: {len(values)}")
                
                return data
            else:
                st.error(f"❌ APIエラー: {msg}")
                return None
        else:
            st.error("❌ 予期しないレスポンス")
            st.json(data)
            return None
            
    except Exception as e:
        st.error(f"❌ 例外エラー: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

def main():
    st.set_page_config(
        page_title="日本出入国者数マップ",
        page_icon="🗾",
        layout="wide"
    )
    
    st.title('🗾 日本出入国者数マップ')
    
    # さっき成功したテスト機能
    st.sidebar.header('テスト機能')
    if st.sidebar.button('🔍 0003448239 テスト'):
        test_specific_stats('0003448239')
    
    # 新しいデータ取得機能
    st.sidebar.header('データ取得')
    if st.sidebar.button('📊 データ取得実行'):
        data = get_simple_data()
        if data:
            st.write("### 取得データ確認")
            st.json(data)

if __name__ == "__main__":
    main()
