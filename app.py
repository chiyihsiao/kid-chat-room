import streamlit as st
from datetime import datetime, timedelta, timezone
import time

# 1. 網頁基本設定（抬頭與小圖示）
st.set_page_config(page_title="小朋友秘密聊天室", page_icon="💬", layout="centered")
st.title("💬 小朋友即時聊天室")

# 2. 核心修正：在程式最一開始徹底初始化 session_state 變數，防止網頁報錯
if "my_name_state" not in st.session_state:
    st.session_state.my_name_state = "小朋友"
if "input_clear_trigger" not in st.session_state:
    st.session_state.input_clear_trigger = 0

# 3. 使用 st.cache_resource 建立所有人共享的記憶體空間（跨裝置同步關鍵）
@st.cache_resource
def get_shared_data():
    return {
        "messages": [{"name": "系統管理員", "text": "歡迎來到秘密聊天室！", "time": "系統訊息"}],
        "users": {}
    }

shared_data = get_shared_data()
shared_messages = shared_data["messages"]
shared_users = shared_data["users"]

# 4. 初始化「當前裝置」的訊息計數器（用來判斷是否有新訊息傳入以播放音效）
if "last_msg_count" not in st.session_state:
    st.session_state.last_msg_count = len(shared_messages)

# 5. 建立每秒自動更新的聊天區域與在線人數（Fragment 局部更新機制）
@st.fragment(run_every=1.0)
def show_chat_and_users():
    current_time = time.time()
    current_user_name = st.session_state.my_name_state
    
    # 刷新自己當前的在線時間
    if current_user_name.strip():
        shared_users[current_user_name] = current_time
        
    # 檢查所有人，如果超過 5 秒沒動靜，判定為離開並從名單刪除
    expired_users = [name for name, last_seen in shared_users.items() if current_time - last_seen > 5.0]
    for name in expired_users:
        if name in shared_users:
            del shared_users[name]
            
    # 取得當前所有在線上的名字清單
    online_list = list(shared_users.keys())
    online_count = len(online_list)
    
    # 顯示目前在線人數綠色小標籤
    st.markdown(f"🟢 **目前在線人數：{online_count} 人** ({', '.join(online_list)})")
    
    # 判斷是否有人傳新訊息
    has_new_message = len(shared_messages) > st.session_state.last_msg_count
    
    # 組合 HTML 聊天室內容外框與歷史訊息
    chat_html = '<div id="my-chat-container" style="height:350px; border:1px solid #ddd; border-radius:5px; padding:15px; overflow-y:auto; background-color:#f9f9f9; margin-bottom:10px;">'
    for msg in shared_messages:
        chat_html += f'<div style="margin-bottom:8px;"><strong>{msg["name"]}</strong> <span style="color:gray; font-size:0.8rem;">({msg["time"]})</span>： {msg["text"]}</div>'
    chat_html += '</div>'
    
    # JavaScript 控制：網頁置底滾動與線上音效播放
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
    
    # 渲染前端 HTML/JS 元件
    st.components.v1.html(chat_html + js_code, height=370)

# 顯示在線人數與聊天視窗
show_chat_and_users()

st.divider()

# 6. 使用 st.form 打包輸入區域，解決重複發送兩次訊息的 BUG
form_key = f"chat_form_{st.session_state.input_clear_trigger}"

with st.form(key=form_key, clear_on_submit=True):
    # 加上 參數切分比例，避免舊版 Streamlit 雲端報錯
    col1, col2 = st.columns()
    
    with col1:
        user_name = st.text_input("我的名字", value=st.session_state.my_name_state)
    
    with col2:
        user_input = st.text_input("輸入訊息...", placeholder="說點什麼吧...")
        
    # 表單提交按鈕
    submitted = st.form_submit_button("傳送訊息", use_container_width=True)
    
    if submitted:
        # 更新目前使用者的名字狀態
        if user_name.strip():
            st.session_state.my_name_state = user_name
            
        # 檢查並加入新訊息
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
            
            # 改變計算機，強制下一次表單完全重置為空白
            st.session_state.input_clear_trigger += 1
            st.rerun()

# 7. 隱藏版管理功能（名字輸入「管理者」才會顯現）
if st.session_state.my_name_state == "管理者":
    st.write("") 
    if st.button("🚨 爸爸專用：一鍵清空所有聊天紀錄", type="primary", use_container_width=True):
        shared_messages.clear() # 擦除所有歷史訊息
        shared_messages.append({"name": "系統管理員", "text": "聊天紀錄已被管理者清空！", "time": "系統訊息"})
        st.rerun()
