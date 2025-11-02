import streamlit as st
import pandas as pd
import numpy as np
import streamlit_authenticator as stauth # 認証ライブラリ
import yaml # 設定ファイル読み込み用

# --- 1. アプリ専用の記憶場所 (session_state) にデータを保存する ---
if 'df' not in st.session_state:
    
    total_lockers = 200
    locker_numbers = [f"{i:03d}" for i in range(1, total_lockers + 1)]
    
    student_ids = [np.nan] * total_lockers
    names = [np.nan] * total_lockers
    
    student_ids[0] = 'S1001' # 001番
    names[0] = '田中 太郎'
    student_ids[1] = 'S1002' # 002番
    names[1] = '鈴木 花子'
    student_ids[3] = 'S1003' # 004番
    names[3] = '佐藤 次郎'
    
    initial_data = {
        'Locker No.': locker_numbers,
        'Student ID': student_ids,
        'Name': names
    }
    st.session_state.df = pd.DataFrame(initial_data)

# --- ここからが認証機能 ---

# 2. Streamlit SecretsからGoogleのキーを読み込む
google_client_id = st.secrets["GOOGLE_CLIENT_ID"]
google_client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
cookie_name = st.secrets["COOKIE_NAME"]
cookie_key = st.secrets["COOKIE_KEY"]

# 3. 認証オブジェクトを作成
# ★★★ 修正点 ★★★
# 'usernames' と 'social_logins' を *1つの* 辞書にまとめる
credentials = {
    'usernames': {}, # 従来のパスワードログイン用（空でも必須）
    'social_logins': { # ソーシャルログイン用
        'google': {
            'client_id': google_client_id,
            'client_secret': google_client_secret
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,      # 1. 結合した辞書
    cookie_name,      # 2. クッキー名 (string)
    cookie_key,       # 3. クッキーキー (string)
    3600              # 4. 有効期限 (int)
)

st.title('ロッカー管理システム')

# 4. ログイン・ログアウトボタンを表示
login_placeholder = st.empty()
with login_placeholder:
    # この部分は正しかったので変更なし
    authenticator.login(
        location='main'
    )

# --- 認証ステータスの確認 ---
if st.session_state["authentication_status"]:
    login_placeholder.empty() # ログインフォームを消す
    
    with st.container():
        st.write(f'Welcome *{st.session_state["name"]}*')
        authenticator.logout('Logout', 'main')

    # --- 5. タブの作成（ログイン成功時のみ表示） ---
    tab1, tab2 = st.tabs(["🗂️ 閲覧・登録用", "🔒 管理者用"])
    
    # ( ... ここから下のロッカー管理のコードは変更ありません ...)
    
    # ---------------------------------
    # --- tab1 (閲覧・登録用) の中身 ---
    # ---------------------------------
    with tab1:
        st.header('ロッカー空き状況')
        
        df_lockers = st.session_state.df 
        available_lockers = df_lockers[df_lockers['Student ID'].isnull()]
        
        if available_lockers.empty:
            st.warning('現在、空きロッカーはありません。')
        else:
            st.dataframe(available_lockers[['Locker No.']], use_container_width=True, height=300)

        st.divider() 

        st.header('ロッカー新規登録')
        
        available_list_tab1 = available_lockers['Locker No.'].tolist()
        
        if not available_list_tab1:
            st.info('現在、登録できる空きロッカーがありません。')
        else:
            locker_no_reg_tab1 = st.selectbox('空いているロッカーを選択してください:', available_list_tab1, key='reg_locker_select_tab1')
            student_id_reg_tab1 = st.text_input('学籍番号 (例: 2403036)', key='reg_sid_tab1')
            name_reg_tab1 = st.text_input('氏名 (例: 埼玉太郎)', key='reg_name_tab1')
            
            if st.button('この内容で登録する', key='reg_button_tab1'):
                if not student_id_reg_tab1 or not name_reg_tab1:
                    st.error('学籍番号と氏名の両方を入力してください。')
                else:
                    df_lockers.loc[df_lockers['Locker No.'] == locker_no_reg_tab1, ['Student ID', 'Name']] = [student_id_reg_tab1, name_reg_tab1]
                    st.session_state.df = df_lockers 
                    st.success(f"【登録完了】ロッカー '{locker_no_reg_tab1}' に '{name_reg_tab1}' さんを登録しました。")
                    st.rerun()

    # ---------------------------------
    # --- tab2 (管理者用) の中身 ---
    # ---------------------------------
    with tab2:
        st.header('管理者パネル')
        
        df_lockers = st.session_state.df

        st.subheader('📝 ロッカー新規登録')
        
        available_lockers_tab2 = df_lockers[df_lockers['Student ID'].isnull()]
        available_list_tab2 = available_lockers_tab2['Locker No.'].tolist()

        if not available_list_tab2:
            st.info('現在、登録できる空きロッカーがありません。')
        else:
            locker_no_reg_tab2 = st.selectbox('空いているロッカーを選択してください:', available_list_tab2, key='reg_locker_select_tab2')
            student_id_reg_tab2 = st.text_input('学籍番号 (例: 2403036)', key='reg_sid_tab2')
            name_reg_tab2 = st.text_input('氏名 (例: 埼玉太郎)', key='reg_name_tab2')
            
            if st.button('この内容で登録する', key='reg_button_tab2'):
                if not student_id_reg_tab2 or not name_reg_tab2:
                    st.error('学籍番号と氏名の両方を入力してください。')
                else:
                    df_lockers.loc[df_lockers['Locker No.'] == locker_no_reg_tab2, ['Student ID', 'Name']] = [student_id_reg_tab2, name_reg_tab2]
                    st.session_state.df = df_lockers 
                    st.success(f"【登録完了】ロッカー '{locker_no_reg_tab2}' に '{name_reg_tab2}' さんを登録しました。")
                    st.rerun()

        st.divider()

        st.subheader('🗑️ 使用者の削除 (プルダウン)')
        
        used_lockers = df_lockers.dropna(subset=['Student ID'])
        used_locker_list = used_lockers['Locker No.'].tolist()
        
        if not used_locker_list:
            st.info('現在、使用中のロッカーはありません。')
        else:
            locker_no_del = st.selectbox('削除するロッカーを選択してください:', used_locker_list, key='del_locker_select')
            
            if st.button('このロッカーの使用者を削除する', type="primary", key='del_button_pulldown'):
                df_lockers.loc[df_lockERS['Locker No.'] == locker_no_del, ['Student ID', 'Name']] = [np.nan, np.nan]
                st.session_state.df = df_lockers 
                st.success(f"【削除完了】ロッカー '{locker_no_del}' の使用者情報を削除しました。")
                st.rerun()
                
        st.divider() 

        st.subheader('🗂️ 全ロッカー一覧 (削除ボタン付き)')

        col_header = st.columns([1, 2, 2, 1]) 
        col_header[0].markdown('**Locker No.**')
        col_header[1].markdown('**Student ID**')
        col_header[2].markdown('**Name**')
        col_header[3].markdown('**操作**')
        st.divider()

        for index in st.session_state.df.index:
            row = st.session_state.df.loc[index]
            
            cols = st.columns([1, 2, 2, 1])
            
            cols[0].text(row['Locker No.'])
            cols[1].text(row.fillna('--- 空き ---')['Student ID'])
            cols[2].text(row.fillna('--- 空き ---')['Name'])
            
            if not pd.isnull(row['Student ID']):
                if cols[3].button('削除', key=f"del_{index}", type="primary"):
                    st.session_state.df.loc[index, ['Student ID', 'Name']] = [np.nan, np.nan]
                    st.success(f"ロッカー '{row['Locker No.']}' の使用者を削除しました。")
                    st.rerun()
            else:
                cols[3].text("")

elif st.session_state["authentication_status"] is False:
    st.error('Login failed.') # ログイン失敗
elif st.session_state["authentication_status"] is None:
    st.info('Please login to access the app') # 初期画面
