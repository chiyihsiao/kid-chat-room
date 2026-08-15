import streamlit as st
from datetime import datetime, timedelta, timezone

# 1. 網頁基本設定
st.set_page_config(page_title="小朋友秘密聊天室", page_icon="💬", layout="centered")
st.title("💬 小朋友即時聊天室")

# =================【核心修正】=================
# 使用 st.cache_resource 建立一個「所有人共享」的記憶體空間
@st.cache_resource
def get_shared_messages():
    # 當第一個連線進來時初始化，之後所有人都共用這個 list
    return [{"name": "系統管理員", "text": "歡迎來到多人在線秘密聊天室！", "time": "系統訊息"}]

# 取得共享的聊天紀錄列表
shared_messages = get_shared_messages()
# =============================================

# 2. 定義「傳送訊息」的動作
def send_message():
    user_input = st.session_state.chat_user_input
    user_name = st.session_state.chat_user_name
    
    if user_input.strip():
        # 取得目前的台灣時間 (UTC+8)
        tz_taiwan = timezone(timedelta(hours=8))
        now = datetime.now(tz_taiwan)
        time_str = now.strftime("%H:%M")
        
        # 💡 重點：把訊息加進「共享列表」，這樣所有人都能立刻看到！
        shared_messages.append({
            "name": user_name, 
            "text": user_input,
            "time": time_str
        })
        
    # 清空輸入框
    st.session_state.chat_user_input = ""

# 3. 建立每秒自動更新的聊天區域
@st.fragment(run_every=1.0)
def show_chat_box():
    with st.container(height=350, border=True):
        # 💡 讀取共享的訊息
        for msg in shared_messages:
            st.markdown(
                f"**{msg['name']}** <span style='color: gray; font-size: 0.8rem;'>({msg['time']})</span>： {msg['text']}", 
                unsafe_allow_html=True
            )

# 顯示聊天視窗
show_chat_box()

st.divider()

# 4. 輸入區域
col1, col2 = st.columns([1, 3])

with col1:
    st.text_input("我的名字", value="小朋友", key="chat_user_name")

with col2:
    st.text_input(
        "輸入訊息...", 
        placeholder="說點什麼吧...", 
        key="chat_user_input",
        on_change=send_message
    )

# 傳送按鈕
st.button("傳送訊息", use_container_width=True, on_click=send_message)
