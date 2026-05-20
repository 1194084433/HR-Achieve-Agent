import streamlit as st

st.set_page_config(page_title="HR Archive Agent", layout="wide")
st.title("📁 员工档案批量标准化智能体")

st.write("欢迎使用！系统正在运行中...")

if st.button("测试连接"):
    st.success("连接成功！")
