import streamlit as st
import sqlite3
import re

st.set_page_config(page_title="法条查询", page_icon="⚖️")
st.title("法条查询")

keyword = st.text_input("输入关键词，比如：民法典")

if keyword:
    conn = sqlite3.connect("laws_all.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table = cursor.fetchall()[0][0]

    cursor.execute(f"SELECT * FROM {table}")
    all_rows = cursor.fetchall()

    matched = []
    for r in all_rows:
        title = str(r[1])
        if keyword in title:
            matched.append(r)
            if len(matched) >= 30:
                break

    if matched:
        for r in matched:
            title = str(r[1])
            content = str(r[2]).strip()

            if not content:
                continue

            content = content.replace("\\n", "\n").replace("\\u3000", "　")

            # 带“解释/规定/细则/办法”等词的，折叠显示
            if any(word in title for word in ["解释", "规定", "细则", "办法", "批复", "答复", "意见", "通知"]):
                st.markdown(f"### **{title}**")
                with st.expander("查看全文"):
                    st.write(content)
            else:
                # 主法律：直接展开分层正文
                st.markdown(f"## {title}")
                lines = content.split("\n")
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue

                    if re.match(r"^第[一二三四五六七八九十]+编", stripped):
                        st.markdown(f"### {stripped}")
                    elif re.match(r"^第[一二三四五六七八九十]+章", stripped):
                        st.markdown(f"#### {stripped}")
                    elif re.match(r"^第[一二三四五六七八九十]+节", stripped):
                        st.markdown(f"##### {stripped}")
                    elif re.match(r"^第[一二三四五六七八九十百]+条", stripped):
                        st.markdown(f"**{stripped}**")
                    else:
                        st.write(stripped)

            st.markdown("---")
    else:
        st.info("没搜到结果")

    conn.close()