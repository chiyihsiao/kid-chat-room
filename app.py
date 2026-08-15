import streamlit as st
from datetime import datetime, timedelta, timezone
import time

# 1. 網頁基本設定
st.set_page_config(page_title="小朋友秘密聊天室", page_icon="💬", layout="centered")
st.title("💬 小朋友即時聊天室")

# 2. 使用 st.cache_resource 建立所有人共享的記憶體空間
@st.cache_resource
def get_shared_data():
    return {
        "messages": [{"name": "系統管理員", "text": "歡迎來到秘密聊天室！", "time": "系統訊息"}],
        "users": {}
    }

shared_data = get_shared_data()
shared_messages = shared_data["messages"]
shared_users = shared_data["users"]

# 3. 初始化「當前客戶端」的訊息計算機（用來判斷有沒有新訊息進來以播放音效）
if "last_msg_count" not in st.session_state:
    st.session_state.last_msg_count = len(shared_messages)

# 4. 初始化目前使用者的預設名字
if "my_name_state" not in st.session_state:
    st.session_state.my_name_state = "小朋友"

# 5. 定義「傳送訊息」的動作
def send_message():
    # 💡 檢查 session_state 中是否有輸入框的值
    user_input = st.session_state.get("chat_user_input", "")
    user_name = st.session_state.get("my_name_state", "小朋友")
    
    # 核心防重複機制：如果輸入框已經是空的（可能被另一個事件清空了），就直接跳出不執行
    if not user_input or not user_input.strip():
        return
        
    if user_name.strip():
        tz_taiwan = timezone(timedelta(hours=8))
        now = datetime.now(tz_taiwan)
        time_str = now.strftime("%H:%M")
        
        shared_messages.append({
            "name": user_name, 
            "text": user_input,
            "time": time_str
        })
        shared_users[user_name] = time.time()
        
    # 【關鍵】立刻清空 session_state 中的字，防止第二次重複觸發
    st.session_state.chat_user_input = ""
    # 強制網頁立刻刷新，中斷按鈕的二次連動
    st.rerun()

# 6. 建立每秒自動更新的聊天與人數區域
@st.fragment(run_every=1.0)
def show_chat_and_users():
    current_time = time.time()
    current_user_name = st.session_state.my_name_state
    
    if current_user_name.strip():
        shared_users[current_user_name] = current_time
        
    expired_users = [name for name, last_seen in shared_users.items() if current_time - last_seen > 5.0]
    for name in expired_users:
        if name in shared_users:
            del shared_users[name]
            
    online_list = list(shared_users.keys())
    online_count = len(online_list)
    
    st.markdown(f"🟢 **目前在線人數：{online_count} 人** ({', '.join(online_list)})")
    
    has_new_message = len(shared_messages) > st.session_state.last_msg_count
    
    chat_html = '<div id="my-chat-container" style="height:350px; border:1px solid #ddd; border-radius:5px; padding:15px; overflow-y:auto; background-color:#f9f9f9; margin-bottom:10px;">'
    for msg in shared_messages:
        chat_html += f'<div style="margin-bottom:8px;"><strong>{msg["name"]}</strong> <span style="color:gray; font-size:0.8rem;">({msg["time"]})</span>： {msg["text"]}</div>'
    chat_html += '</div>'
    
    js_code = """
    <script>
        var container = document.getElementById("my-chat-container");
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    """
    
    if has_new_message:
        js_code += """
        var audio = new Audio("https://google.com");
        audio.volume = 0.5;
        audio.play().catch(function(error) { console.log("音效播放被瀏覽器阻擋"); });
        """
        st.session_state.last_msg_count = len(shared_messages)
        
    js_code += "</script>"
    
    st.components.v1.html(chat_html + js_code, height=370)

show_chat_and_users()

st.divider()

# 7. 輸入區域
col1, col2 = st.columns([1, 3]) # 調整比例

with col1:
    st.text_input("我的名字", value="小朋友", key="my_name_state")

with col2:
    st.text_input(
        "輸入訊息...", 
        placeholder="說點什麼吧...", 
        key="chat_user_input",
        on_change=send_message
    )

# 傳送按鈕
st.button("傳送訊息", use_container_width=True, on_click=send_message)
