import streamlit as st
import plotly.express as px
import pandas as pd
import requests

def debug_api_call():
    """API呼び出しの詳細デバッグ"""
    try:
        st.write("### ステップ1: APIキー取得")
        app_id = st.secrets["e_stat"]["app_id"]
        st.success(f"✅ APIキー取得成功")
        
        st.write("### ステップ2: API呼び出し詳細")
        url = 'https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData'
        params = {
            'appId': app_id,
            'statsDataId': '0003448239',
            'lang': 'J'
        }
        
        st.write("**リクエスト情報:**")
        st.write(f"URL: {url}")
        st.write(f"パラメータ: {params}")
        
        response = requests.get(url, params=params)
        
        st.write("**レスポンス情報:**")
        st.write(f"ステータスコード: {response.status_code}")
        st.write(f"レスポンスヘッダー: {dict(response.headers)}")
        
        if response.status_code == 200:
            st.success("✅ HTTP通信成功")
            
            try:
                data = response.json()
                st.write("**JSONパース成功**")
                
                # レスポンス構造確認
                st.write("**レスポンス構造:**")
                st.write(f"トップレベルキー: {list(data.keys())}")
                
                if 'GET_STATS_DATA' in data:
                    result = data['GET_STATS_DATA']['RESULT']
                    status = result.get('STATUS')
                    message = result.get('ERROR_MSG', '')
                    
                    st.write(f"**API結果:**")
                    st.write(f"STATUS: {status}")
                    st.write(f"MESSAGE: {message}")
                    
                    if status == '0':
                        st.success("✅ API呼び出し成功！")
                        
                        # データ構造確認
                        if 'STATISTICAL_DATA' in data['GET_STATS_DATA']:
                            stat_data = data['GET_STATS_DATA']['STATISTICAL_DATA']
                            st.write("**統計データ構造:**")
                            st.write(f"キー: {list(stat_data.keys())}")
                            
                            if 'DATA_INF' in stat_data:
                                data_inf = stat_data['DATA_INF']
                                if 'VALUE' in data_inf:
                                    values = data_inf['VALUE']
                                    st.write(f"データ件数: {len(values)}")
                                    st.write("最初のデータ:")
                                    st.json(values[0])
                                else:
                                    st.error("❌ VALUE キーが見つかりません")
                            else:
                                st.error("❌ DATA_INF キーが見つかりません")
                        else:
                            st.error("❌ STATISTICAL_DATA キーが見つかりません")
                    else:
                        st.error(f"❌ APIエラー: STATUS={status}, MESSAGE={message}")
                else:
                    st.error("❌ GET_STATS_DATA キーが見つかりません")
                    st.write("実際のレスポンス:")
                    st.json(data)
                    
            except Exception as json_error:
                st.error(f"❌ JSONパースエラー: {json_error}")
                st.write("生レスポンス:")
                st.text(response.text[:1000])  # 最初の1000文字
                
        else:
            st.error(f"❌ HTTP通信失敗: {response.status_code}")
            st.write("エラーレスポンス:")
            st.text(response.text[:1000])
            
    except Exception as e:
        st.error(f"❌ 予期しないエラー: {e}")
        import traceback
        st.code(traceback.format_exc())

def main():
    st.set_page_config(
        page_title="API詳細デバッグ",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title('🔍 API詳細デバッグ')
    
    if st.button('🔍 詳細デバッグ実行'):
        debug_api_call()

if __name__ == "__main__":
    main()
