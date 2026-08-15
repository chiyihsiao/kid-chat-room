import streamlit as st
from datetime import datetime, timedelta, timezone
import time

# 1. 網頁基本設定
st.set_page_config(page_title="小朋友秘密聊天室", page_icon="💬", layout="centered")
st.title("💬 小朋友即時聊天室")

# 2. 在最一開始徹底初始化 session_state 變數，防止 Attribute 錯誤
if "my_name_state" not in st.session_state:
    st.session_state.my_name_state = "小朋友"
if "input_clear_trigger" not in st.session_state:
    st.session_state.input_clear_trigger = 0

# 3. 使用 st.cache_resource 建立所有人共享的記憶體空間
@st.cache_resource
def get_shared_data():
    return {
        "messages": [{"name": "系統管理員", "text": "歡迎來到秘密聊天室！", "time": "系統訊息"}],
        "users": {}
    }

shared_data = get_shared_data()
shared_messages = shared_data["messages"]
shared_users = shared_data["users"]

# 4. 初始化「當前客戶端」的訊息計數器
if "last_msg_count" not in st.session_state:
    st.session_state.last_msg_count = len(shared_messages)

# 5. 建立每秒自動更新的聊天與人數區域
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

# 6. 使用 st.form 包裹輸入區域
form_key = f"chat_form_{st.session_state.input_clear_trigger}"

with st.form(key=form_key, clear_on_submit=True):
    # 💡 【終極修正】直接傳入列表 [1, 3]，代表左邊佔 25% 寬度，右邊佔 75% 寬度
    # 這是最嚴謹、不論新舊版本 Streamlit 都百分之百支援的寫法！
    col1, col2 = st.columns([1, 3])
    
    with col1:
        user_name = st.text_input("我的名字", value=st.session_state.my_name_state)
    
    with col2:
        user_input = st.text_input("輸入訊息...", placeholder="說點什麼吧...")
        
    submitted = st.form_submit_button("傳送訊息", use_container_width=True)
    
    if submitted:
        if user_name.strip():
            st.session_state.my_name_state = user_name
            
        if user_input and user_input.strip():
            tz_taiwan = timezone(timedelta(hours=8))
            now = datetime.now(tz_taiwan)
            time_str = now.strftime("%H:%M")
            
            shared_messages.append({
                "name": user_name, 
                "text": user_input,
                "time": time_str
            })
            shared_users[user_name] = time.time()
            
            st.session_state.input_clear_trigger += 1
            st.rerun()

# 7. 隱藏版管理功能
if st.session_state.my_name_state == "管理者":
    st.write("") 
    if st.button("🚨 爸爸專用：一鍵清空所有聊天紀錄", type="primary", use_container_width=True):
        shared_messages.clear()
        shared_messages.append({"name": "系統管理員", "text": "聊天紀錄已被管理者清空！", "time": "系統訊息"})
        st.rerun()
