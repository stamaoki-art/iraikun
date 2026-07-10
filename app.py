import streamlit as st
import requests
import pandas as pd

GAS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbx2FmcI7BpM8A7XwvoWKuJlJw1peAgBGJxzYJBvQECN1UNqkAmaYMpmO7jYUKGTqK9jeg/exec"

st.sidebar.title("メニュー選択")
mode = st.sidebar.radio("モード切替", ["新規依頼フォーム", "【管理者用】承認パネル"])

if mode == "新規依頼フォーム":
    # （以前作成した新規作成用コードをここに）
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
    # ... 省略 ...

else:
    st.title("🛡️ 承認・ステータス管理パネル")
    
    # スプレッドシートから現在のデータを取得
    with st.spinner("データを読み込み中..."):
        res = requests.get(GAS_WEBAPP_URL)
        all_data = res.json()
        df = pd.DataFrame(all_data)

    if not df.empty:
        # ID選択
        id_list = df["ID"].tolist()
        selected_id = st.selectbox("処理するIDを選択:", id_list)
        
        # 選択されたIDの詳細を自動表示
        row = df[df["ID"] == selected_id].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**依頼者:** {row['依頼者']}")
            st.info(f"**メール:** {row['メールアドレス']}")
        with col2:
            st.warning(f"**重要度:** {row['重要度']}")
        
        st.text_area("依頼内容:", value=row['依頼内容'], disabled=True)
        
        # 承認フォーム
        with st.form("approval_form"):
            status = st.radio("ステータス変更:", ["承認", "取下", "保留"], horizontal=True)
            comment = st.text_area("担当者コメント:", placeholder="依頼者へのメッセージを入力してください")
            
            submit = st.form_submit_button("回答を送信（メール通知実行）")
            
            if submit:
                payload = {
                    "action": "update",
                    "id": selected_id,
                    "status": status,
                    "comment": comment,
                    "myoji": row['依頼者'],
                    "userEmail": row['メールアドレス']
                }
                res = requests.post(GAS_WEBAPP_URL, json=payload)
                if res.status_code == 200:
                    st.success(f"ID:{selected_id} のステータスを「{status}」に更新し、通知を送信しました。")
                    st.balloons()
    else:
        st.write("現在、処理待ちの依頼はありません。")
