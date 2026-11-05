import streamlit as st
import zipfile
import io

st.title("ZIPファイル分割アプリ")
st.write("アップロードされたZIPの中身を、指定したサイズの複数の独立したZIPファイルに振り分けます。")

# 1. ファイルのアップロード
uploaded_file = st.file_uploader("分割したいファイルを選択してください", type=["zip"])

# 2. 分割サイズの設定
chunk_size_mb = st.number_input("1ファイルあたりの目標サイズ (MB)", min_value=1, max_value=50, value=24)

if uploaded_file is not None:
    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    
    try:
        # ZIPファイルを読み込む
        with zipfile.ZipFile(uploaded_file, 'r') as zf:
            file_list = zf.infolist()
            
            zip_buffers = []
            current_buffer = io.BytesIO()
            current_zip = zipfile.ZipFile(current_buffer, 'w', zipfile.ZIP_DEFLATED)
            current_size = 0
            
            for file_info in file_list:
                # フォルダ自体はスキップ（中身のファイル処理時に自動で構成されます）
                if file_info.is_dir():
                    continue
                
                # もし中に入っているファイル1つだけで指定サイズを超えている場合の警告
                if file_info.file_size > chunk_size_bytes:
                    st.warning(f"⚠️ '{file_info.filename}' は単体で目標サイズを超えています。そのまま格納します。")
                
                # 新しいファイルを追加するとサイズ上限を超える場合、現在のZIPを完成させて次へ
                if current_size + file_info.file_size > chunk_size_bytes and current_size > 0:
                    current_zip.close()
                    zip_buffers.append(current_buffer.getvalue())
                    
                    # 新しいZIPの準備
                    current_buffer = io.BytesIO()
                    current_zip = zipfile.ZipFile(current_buffer, 'w', zipfile.ZIP_DEFLATED)
                    current_size = 0
                
                # ファイルデータを新しいZIPに追加
                file_data = zf.read(file_info.filename)
                current_zip.writestr(file_info, file_data)
                # 圧縮前のサイズで計算（安全マージンのため）
                current_size += file_info.file_size
                
            # 最後のZIPを完成させる
            if current_size > 0:
                current_zip.close()
                zip_buffers.append(current_buffer.getvalue())
                
        st.success(f"中身を {len(zip_buffers)} 個の独立したZIPファイルに振り分けました！")
        st.write("以下のボタンからそれぞれダウンロードしてください。（そのまま単独で解凍できます）")
        st.markdown("---")
        
        # ダウンロードボタンの生成
        # 元のファイル名から拡張子 .zip を取り除く
        base_name = uploaded_file.name[:-4] if uploaded_file.name.lower().endswith('.zip') else uploaded_file.name
        
        for i, buffer_data in enumerate(zip_buffers):
            chunk_name = f"{base_name}_part{i+1}.zip"
            st.download_button(
                label=f"🔽 {chunk_name} をダウンロード ({len(buffer_data)/(1024*1024):.2f} MB)",
                data=buffer_data,
                file_name=chunk_name,
                mime="application/zip"
            )
            
    except zipfile.BadZipFile:
        st.error("有効なZIPファイルではありません。")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
