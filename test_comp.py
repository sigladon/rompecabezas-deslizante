import streamlit as st
import streamlit.components.v1 as components
import os

html = """
<!DOCTYPE html>
<html><body>
<button onclick="sendVal()">Click me</button>
<script>
    function sendVal() {
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:setComponentValue",
            value: [1,2,3]
        }, "*");
    }
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:componentReady",
        apiVersion: 1
    }, "*");
</script>
</body></html>
"""

os.makedirs("test_comp_dir", exist_ok=True)
with open("test_comp_dir/index.html", "w") as f:
    f.write(html)

comp = components.declare_component("test_comp", path="test_comp_dir")
val = comp()
st.write("Value:", val)
