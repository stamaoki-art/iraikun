import streamlit as st
import requests
import pandas as pd
import datetime

# ----------------------------------------
# 共通設定：最新のGASのWebアプリURLを入れてください
# ----------------------------------------
GAS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbx2FmcI7BpM8A7XwvoWKuJlJw1peAgBGJxzYJBvQECN1UNqkAmaYMpmO7jYUKGTqK9jeg/exec"

# 🔑 管理画面用のパスワード（自由に変更してください）
ADMIN_PASSWORD = "yjsnpi"

# サイドバーでモードを切り替え
st.sidebar.title("メニュー選択")
mode = st.sidebar.radio("モード切替", ["新規依頼フォーム", "【管理者用】承認パネル"])

# ----------------------------------------
# 1. 新規依頼フォーム モード
# ----------------------------------------
if mode == "新規依頼フォーム":
    st.title("📥 新規依頼フォーム")
    st.write("必要事項を入力して「送信」ボタンを押してください。")

    with st.form(key="request_form", clear_on_submit=True):
        myoji = st.text_input("苗字：", placeholder="例：山田")
        email = st.text_input("メールアドレス：", placeholder="s_tamaoki@e-gate.co.jp")
        content = st.text_area("依頼内容：", placeholder="依頼の詳細をご記入ください。")
        priority = st.selectbox("重要度：", ["低", "中", "高"], index=1)
        
        # 希望日時
        col1, col2 = st.columns(2)
        with col1:
            req_date = st.date_input("希望日：", datetime.date.today())
        with col2:
            req_time = st.time_input("希望時間：", datetime.time(12, 0))
            
        datetime_str = f"{req_date} {req_time.strftime('%H:%M')}"
        submit_button = st.form_submit_button(label="送信！")

    if submit_button:
        if not myoji or not email or not content:
            st.error("❌ 「苗字」「メールアドレス」「依頼内容」は必須入力です。")
        else:
            payload = {
                "action": "new",
                "myoji": myoji,
                "email": email,
                "content": content,
                "priority": priority,
                "datetime": datetime_str
            }
            
            with st.spinner("データを送信中..."):
                try:
                    response = requests.post(GAS_WEBAPP_URL, json=payload)
                    if response.status_code == 200:
                        st.success("🎉 依頼の送信、スプレッドシートへの反映が完了しました！")
                        st.balloons()
                    else:
                        st.error(f"❌ エラーが発生しました (Status Code: {response.status_code})")
                except Exception as e:
                    st.error(f"❌ 通信エラーが発生しました: {e}")

# ----------------------------------------
# 2. 承認パネル モード（パスワード保護付き）
# ----------------------------------------
else:
    st.title("🛡️ 承認・ステータス管理パネル")
    
    # 🔐 パスワード入力欄を設置（入力中は文字が「●」になります）
    password_input = st.text_input("管理者パスワードを入力してください：", type="password")
    
    # パスワードが一致しない場合はここで処理をストップする
    if password_input != ADMIN_PASSWORD:
        if password_input: # 何か入力されていて間違っている場合
            st.error("❌ パスワードが違います。")
        else:
            st.info("🔑 管理画面を表示するにはパスワードが必要です。")
            
    else:
        # パスワードが合っている場合のみ、データを読み込んで表示する
        st.success("🔓 認証されました。")
        
        with st.spinner("最新データを読み込み中..."):
            try:
                res = requests.get(GAS_WEBAPP_URL)
                if res.status_code == 200:
                    all_data = res.json()
                    df = pd.DataFrame(all_data)
                else:
                    df = pd.DataFrame()
                    st.error("データが取得できませんでした。GASのURLを確認してください。")
            except Exception as e:
                df = pd.DataFrame()
                st.error(f"データ通信エラー: {e}")

        if not df.empty and "ID" in df.columns:
            id_list = df["ID"].tolist()
            selected_id = st.selectbox("処理するIDを選択:", id_list)
            
            row = df[df["ID"] == selected_id].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**依頼者:** {row.get('依頼者', 'なし')}")
                st.info(f"**依頼者mail:** {row.get('メールアドレス', 'なし')}")
            with col2:
                st.warning(f"**重要度:** {row.get('重要度', 'なし')}")
                st.write(f"**現在の状態:** {row.get('承認', '未承認')}")
            
            st.text_area("依頼内容:", value=row.get('依頼内容', ''), disabled=True)
            
            with st.form("approval_form"):
                status = st.radio("ステータス変更:", ["承認", "取下", "保留"], horizontal=True)
                comment = st.text_area("コメント：", placeholder="依頼者へのメッセージを入力してください（J列に反映されます）")
                
                submit = st.form_submit_button("送信")
                
                if submit:
                    payload = {
                        "action": "update",
                        "id": selected_id,
                        "status": status,
                        "comment": comment,
                        "myoji": row.get('依頼者', ''),
                        "userEmail": row.get('メールアドレス', '')
                    }
                    
                    with st.spinner("ステータスを更新中..."):
                        try:
                            res_post = requests.post(GAS_WEBAPP_URL, json=payload)
                            if res_post.status_code == 200:
                                st.success(f"🎉 ID:{selected_id} を「{status}」に更新し、メールを送信しました！")
                                st.balloons()
                            else:
                                st.error("更新に失敗しました。")
                        except Exception as e:
                            st.error(f"通信エラー: {e}")
        else:
            st.info("現在、処理待ちの依頼データはありません。")
