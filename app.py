import streamlit as st
import requests
import datetime

# GASのWebアプリURLを設定
GAS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwX6NFQazHozOKPEoKP7NdANapZ7ZIj3nPJXjEIqm0hL5HEvHyCs856D9qgwPBUbnez1w/exec"

st.title("📥 専用依頼フォーム")
st.write("必要事項を入力して「送信」ボタンを押してください。")

# フォームの構築
with st.form(key="request_form", clear_on_submit=True):
    # 苗字
    myoji = st.text_input("苗字：", placeholder="例：山田")
    
    # 依頼内容
    content = st.text_area("依頼内容：", placeholder="依頼の詳細をご記入ください。")
    
    # 重要度（プルダウン）
    priority = st.selectbox("重要度：", ["低", "中", "高"], index=1)
    
    # 希望日時
    # 日付と時間を分けて入力し、後で結合します
    col1, col2 = st.columns(2)
    with col1:
        req_date = st.date_input("希望日：", datetime.date.today())
    with col2:
        req_time = st.time_input("希望時間：", datetime.time(12, 0))
        
    # 希望日時を文字列に変換
    datetime_str = f"{req_date} {req_time.strftime('%H:%M')}"

    # 送信ボタン
    submit_button = st.form_submit_button(label="送信！")

# ボタンが押された時の処理
if submit_button:
    if not myoji or not content:
        st.error("❌ 「苗字」と「依頼内容」は必須入力です。")
    else:
        # GASへ送るデータ
        payload = {
            "myoji": myoji,
            "content": content,
            "priority": priority,
            "datetime": datetime_str
        }
        
        with st.spinner("データを送信中..."):
            try:
                # GASにPOSTリクエストを送信
                response = requests.post(GAS_WEBAPP_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        st.success("🎉 依頼の送信、スプレッドシートへの反映、通知メールの送信が完了しました！")
                    else:
                        st.error(f"❌ エラーが発生しました: {result.get('message')}")
                else:
                    st.error(f"❌ サーバー側でエラーが発生しました (Status Code: {response.status_code})")
            except Exception as e:
                st.error(f"❌ 通信エラーが発生しました: {e}")
