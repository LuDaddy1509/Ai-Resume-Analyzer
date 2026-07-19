import streamlit as st
import requests
import json

# ====================== TAILWIND CDN ======================
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');

    .main {
        background-color: #0f172a;
        color: white;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
    }
    .card {
        background-color: #1e2937;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Resume Analyzer")
st.markdown("<p class='text-gray-400 text-lg'>Tối ưu CV - Vượt qua ATS - Tăng cơ hội trúng tuyển</p>",
            unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

uploaded_file = st.file_uploader("📤 Tải CV của bạn lên (PDF)", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    with st.spinner("🔍 Đang phân tích CV..."):
        try:
            response = requests.post(f"{API_URL}/parse-resume", files={"file": uploaded_file})

            if response.status_code == 200:
                data = response.json()

                st.success("✅ Phân tích hoàn tất!", icon="🎉")

                # Main Content với Tailwind
                col1, col2 = st.columns([3, 2])

                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <h2 class="text-2xl font-bold mb-4 text-blue-400">👤 Thông tin cá nhân</h2>
                        <div class="grid grid-cols-2 gap-4">
                            <p><strong>Họ tên:</strong> {data.get('full_name', 'N/A')}</p>
                            <p><strong>Email:</strong> {data.get('email', 'N/A')}</p>
                            <p><strong>Phone:</strong> {data.get('phone', 'N/A')}</p>
                            <p><strong>LinkedIn:</strong> {data.get('linkedin', 'N/A')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    skills = data.get("skills", [])
                    st.markdown(f"""
                    <div class="card">
                        <h2 class="text-2xl font-bold mb-4 text-green-400">🛠️ Kỹ năng</h2>
                        <div class="flex flex-wrap gap-2">
                            {"".join([f'<span class="bg-green-600 text-white px-3 py-1 rounded-full text-sm">{skill}</span>' for skill in skills])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Kinh nghiệm
                st.markdown("<h2 class='text-2xl font-bold mt-8 mb-4 text-purple-400'>💼 Kinh nghiệm làm việc</h2>",
                            unsafe_allow_html=True)
                for exp in data.get("experiences", []):
                    st.markdown(f"""
                    <div class="card mb-4">
                        <h3 class="font-semibold text-lg">{exp.get('position')} • {exp.get('company')}</h3>
                        <p class="text-gray-400">{exp.get('dates')} {exp.get('location', '')}</p>
                        <ul class="list-disc ml-5 mt-2">
                            {"".join([f'<li>{bullet}</li>' for bullet in exp.get('bullets', [])])}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                # Full JSON
                with st.expander("📋 Xem Full JSON"):
                    st.json(data)

                st.download_button(
                    "📥 Tải JSON",
                    data=json.dumps(data, ensure_ascii=False, indent=2),
                    file_name="parsed_resume.json",
                    mime="application/json"
                )

            else:
                st.error(f"Lỗi server: {response.text}")
        except Exception as e:
            st.error(f"Không kết nối được backend. Kiểm tra backend đang chạy chưa?\n\nLỗi: {e}")

st.markdown("---")
st.markdown("<p class='text-center text-gray-500'>Made with ❤️ using FastAPI + Streamlit + Tailwind</p>",
            unsafe_allow_html=True)