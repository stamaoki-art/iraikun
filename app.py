import streamlit as st
import requests
import datetime

GAS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycby3wk7m01-yOqJ7KUU2z17zNNCb5-nPzOdi6lAb52YCucQWJ5RItdDbdlrg1PJ6j9OgiA/exec"

st.title("📥 依頼フォーム（メールアドレス対応版）")

with st.form(key="request_form", clear_on_submit=True):
    myoji = st.text_input("苗字：", placeholder="山田")
    email = st.text_input("メールアドレス：", placeholder="s_tamaoki@e-gate.co.jp") # 追加
    content = st.text_area("依頼内容：")
    priority = st.selectbox("重要度：", ["低", "中", "高"], index=1)
    
    col1, col2 = st.columns(2)
    with col1:
        req_date = st.date_input("希望日：", datetime.date.today())
    with col2:
        req_time = st.time_input("希望時間：", datetime.time(12, 0))
    datetime_str = f"{req_date} {req_time.strftime('%H:%M')}"

    submit_button = st.form_submit_button(label="送信！")

if submit_button:
    if not myoji or not email or not content:
        st.error("❌ 苗字、メールアドレス、依頼内容は必須です。")
    else:
        payload = {
            "myoji": myoji,
            "email": email, # 追加
            "content": content,
            "priority": priority,
            "datetime": datetime_str
        }
        # ...（以下送信処理は前と同じ）
        
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
