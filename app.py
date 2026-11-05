import streamlit as st
import math

st.title("ZIPファイル分割アプリ")
st.write("GitHubのアップロード制限（25MB）などを回避するために、重いファイルを分割します。")

# 1. ファイルのアップロード
uploaded_file = st.file_uploader("分割したいファイルを選択してください", type=["zip"])

# 2. 分割サイズの設定
chunk_size_mb = st.number_input("1ファイルあたりの分割サイズ (MB)", min_value=1, max_value=50, value=24)

if uploaded_file is not None:
    # ファイルを読み込み、サイズを計算
    file_bytes = uploaded_file.read()
    total_size = len(file_bytes)
    chunk_size_bytes = int(chunk_size_mb * 1024 * 1024)
    
    num_chunks = math.ceil(total_size / chunk_size_bytes)
    
    st.write(f"**元のファイルサイズ:** {total_size / (1024*1024):.2f} MB")
    st.write(f"**分割数:** {num_chunks} ファイル")
    st.markdown("---")
    
    # 3. 分割処理とダウンロードボタンの生成
    st.write("以下のボタンから分割されたファイルをひとつずつダウンロードしてください。")
    for i in range(num_chunks):
        start = i * chunk_size_bytes
        end = min(start + chunk_size_bytes, total_size)
        chunk_data = file_bytes[start:end]
        
        chunk_name = f"{uploaded_file.name}.{i+1:03d}"
        
        st.download_button(
            label=f"🔽 {chunk_name} をダウンロード ({len(chunk_data)/(1024*1024):.2f} MB)",
            data=chunk_data,
            file_name=chunk_name,
            mime="application/octet-stream"
        )

st.markdown("---")
st.subheader("💡 分割したファイルの結合方法")
st.write("ダウンロードした複数ファイル（`.001`, `.002`...）を元のZIPファイルに戻すには、コマンドラインを使用します。結合したいファイルを同じフォルダに置き、以下を実行してください。")

st.write("**Windowsの場合 (コマンドプロンプト):**")
st.code("copy /B 結合するファイル名.zip.* 結合後のファイル名.zip", language="cmd")

st.write("**Mac/Linuxの場合 (ターミナル):**")
st.code("cat 結合するファイル名.zip.* > 結合後のファイル名.zip", language="bash")
