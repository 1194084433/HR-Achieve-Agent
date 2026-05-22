import streamlit as st
import requests
import json
import time
from datetime import datetime

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="员工档案批量标准化智能体",
    page_icon="📁",
    layout="wide"
)

# ==================== 标题区 ====================
st.title("📁 员工档案批量标准化智能体")
st.markdown("上传入职材料，自动识别提取信息，智能补全缺失字段，一键导出标准化档案。")

# ==================== 侧边栏：操作日志 ====================
with st.sidebar:
    st.header("📋 操作日志")
    log_container = st.container(height=300)
    
    # 模拟后端地址配置（后续改真实地址）
    backend_url = "http://localhost:8000"

# ==================== 主区域 ====================
# 选项卡布局
tab1, tab2 = st.tabs(["📤 上传识别", "📊 批量处理"])

# ==================== 选项卡1：上传识别 ====================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    # ----- 左列：上传区 -----
    with col1:
        st.subheader("1️⃣ 上传入职材料")
        
        uploaded_file = st.file_uploader(
            "支持身份证、学历证书等图片或PDF文件",
            type=["jpg", "jpeg", "png", "pdf"],
            accept_multiple_files=False,
            help="单次上传一个文件，批量处理请切换到「批量处理」选项卡"
        )
        
        if uploaded_file:
            # 显示上传的图片预览
            if uploaded_file.type.startswith("image"):
                st.image(uploaded_file, caption="上传的文件预览", use_column_width=True)
            else:
                st.info(f"已上传文件：{uploaded_file.name}（PDF 暂不支持预览）")
        
        # 识别按钮
        recognize_btn = st.button(
            "🔍 开始识别",
            type="primary",
            use_container_width=True,
            disabled=(uploaded_file is None)
        )
    
    # ----- 右列：结果展示区 -----
    with col2:
        st.subheader("2️⃣ 识别结果")
        
        # 用 session_state 保存识别结果，避免页面刷新丢失
        if "recognition_result" not in st.session_state:
            st.session_state.recognition_result = None
        if "missing_fields" not in st.session_state:
            st.session_state.missing_fields = []
        
        # 占位符：结果会动态更新到这里
        result_placeholder = st.empty()
        missing_placeholder = st.empty()
        export_placeholder = st.empty()
        
        # ========== 识别逻辑 ==========
        if recognize_btn and uploaded_file:
            with st.spinner("正在识别中，请稍候..."):
                # 模拟进度条
                progress_bar = st.progress(0)
                for percent in range(0, 101, 20):
                    time.sleep(0.3)
                    progress_bar.progress(percent, text=f"处理中 {percent}%")
                progress_bar.empty()
                
                # ---------- 调用后端 API ----------
                # 实际使用时取消注释下面代码，并确保后端已启动
                """
                files = {"file": uploaded_file.getvalue()}
                try:
                    response = requests.post(
                        f"{backend_url}/recognize/idcard",
                        files=files,
                        timeout=30
                    )
                    if response.status_code == 200:
                        result = response.json()
                    else:
                        st.error(f"后端返回错误：{response.text}")
                        result = None
                except requests.exceptions.ConnectionError:
                    st.error("无法连接到后端服务，请确认 FastAPI 已启动")
                    result = None
                """
                
                # ---------- 模拟数据（后端没写好时先用这个） ----------
                # TODO: 等后端接口就绪后，删除下面这段模拟数据
                result = {
                    "姓名": "张三",
                    "性别": "男",
                    "民族": "汉",
                    "出生日期": "1990-05-15",
                    "住址": "北京市海淀区中关村南大街5号",
                    "身份证号": "110101199005152345",
                    "签发机关": "",
                    "有效期限": "2020-01-01-2040-01-01"
                }
                # ---------- 模拟数据结束 ----------
                
                if result:
                    st.session_state.recognition_result = result
                    
                    # 检查缺失字段
                    missing = [k for k, v in result.items() if not v or v.strip() == ""]
                    st.session_state.missing_fields = missing
                    
                    # 写日志
                    with log_container:
                        st.success(f"[{datetime.now().strftime('%H:%M:%S')}] 识别完成，发现 {len(missing)} 个缺失字段")
                else:
                    st.session_state.recognition_result = None
                    with log_container:
                        st.error(f"[{datetime.now().strftime('%H:%M:%S')}] 识别失败")
            
            st.rerun()
        
        # ========== 展示识别结果 ==========
        if st.session_state.recognition_result:
            result = st.session_state.recognition_result
            
            with result_placeholder.container():
                st.markdown("#### 📋 提取的信息")
                
                # 用表格展示字段
                display_data = []
                for field, value in result.items():
                    is_missing = (not value or value.strip() == "")
                    display_data.append({
                        "字段": field,
                        "值": value if not is_missing else "⚠️ 缺失",
                        "状态": "✅" if not is_missing else "❌"
                    })
                
                st.dataframe(
                    display_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "字段": st.column_config.TextColumn("字段", width="small"),
                        "值": st.column_config.TextColumn("识别结果", width="large"),
                        "状态": st.column_config.TextColumn("状态", width="small")
                    }
                )
            
            # 缺失字段提示 + 手动补全
            if st.session_state.missing_fields:
                with missing_placeholder.container():
                    st.warning(f"⚠️ 发现 {len(st.session_state.missing_fields)} 个缺失字段，请手动填写：")
                    
                    manual_inputs = {}
                    for field in st.session_state.missing_fields:
                        manual_inputs[field] = st.text_input(
                            f"请输入 {field}",
                            key=f"manual_{field}"
                        )
                    
                    if st.button("💾 确认补全"):
                        for field, value in manual_inputs.items():
                            if value:
                                st.session_state.recognition_result[field] = value
                        st.session_state.missing_fields = [
                            k for k, v in st.session_state.recognition_result.items()
                            if not v or v.strip() == ""
                        ]
                        with log_container:
                            st.info(f"[{datetime.now().strftime('%H:%M:%S')}] 已手动补全字段")
                        st.rerun()
            
            # 导出按钮
            with export_placeholder.container():
                if st.button("📥 导出标准档案（Word）", type="primary", use_container_width=True):
                    with st.spinner("正在生成档案..."):
                        # ---------- 调用后端导出接口 ----------
                        # 实际使用时取消注释
                        """
                        try:
                            response = requests.post(
                                f"{backend_url}/export/word",
                                json=st.session_state.recognition_result,
                                timeout=30
                            )
                            if response.status_code == 200:
                                st.download_button(
                                    label="⬇️ 下载档案文件",
                                    data=response.content,
                                    file_name=f"员工档案_{st.session_state.recognition_result.get('姓名', '未知')}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                        except Exception as e:
                            st.error(f"导出失败：{e}")
                        """
                        
                        # 模拟导出
                        st.success(f"✅ 档案已生成：员工档案_{st.session_state.recognition_result.get('姓名', '未知')}.docx")
                        st.info("（模拟模式，连接后端后可实际下载文件）")
                        with log_container:
                            st.success(f"[{datetime.now().strftime('%H:%M:%S')}] 档案导出成功")

# ==================== 选项卡2：批量处理 ====================
with tab2:
    st.subheader("📊 批量上传与处理")
    
    uploaded_files = st.file_uploader(
        "可同时上传多个文件",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True,
        help="支持批量选择多个文件同时处理"
    )
    
    if uploaded_files:
        st.info(f"已选择 {len(uploaded_files)} 个文件")
        
        if st.button("🚀 批量处理全部文件", type="primary"):
            st.info("批量处理功能将在后续版本中实现")
            # TODO: 遍历文件列表，逐个调用后端接口
            with log_container:
                st.info(f"[{datetime.now().strftime('%H:%M:%S')}] 批量处理 {len(uploaded_files)} 个文件（功能开发中）")
    else:
        st.info("请先上传文件，或切换到「上传识别」选项卡进行单文件处理")
