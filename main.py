import requests
import re
import base64
import time
import socket
from concurrent.futures import ThreadPoolExecutor

# --- 1. 配置你的订阅源 ---
TARGET_URLS = [
    "https://ZmLyZv.mcsslk.xyz/5ad04c339a19e811d3e4729ab609f67b",
    "https://ghfast.top/https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt"
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/list.txt"
    "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v202603232"
    "https://clash.crossxx.com/sub/vmess/1774195203"
]

# --- 2. 节点检测核心逻辑 ---
def check_node_connectivity(node_url):
    """
    通过尝试建立 TCP 连接来检测节点是否在线
    """
    try:
        # 解析不同协议的 IP 和 端口
        # 匹配格式如: @1.2.3.4:443 或 :443?
        pattern = re.compile(r'@([^:/]+):(\d+)')
        match = pattern.search(node_url)
        
        # 针对 vmess:// 这种特殊的 Base64 格式进行处理
        if "vmess://" in node_url:
            try:
                # 尝试解析 vmess 内部的 JSON 拿到地址和端口
                v2_data = node_url.replace("vmess://", "")
                # 自动补全 base64 padding
                v2_data += "=" * (-len(v2_data) % 4)
                import json
                info = json.loads(base64.b64decode(v2_data).decode('utf-8'))
                host, port = info['add'], int(info['port'])
            except:
                return None
        elif match:
            host, port = match.group(1), int(match.group(2))
        else:
            return None

        # 尝试通过 Socket 建立 TCP 连接 (超时时间 3 秒)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((host, port))
        s.close()
        
        # result 为 0 表示端口是通的，连接成功
        return node_url if result == 0 else None
    except:
        return None

# --- 3. 抓取与处理流程 ---
def fetch_and_extract_nodes(urls):
    all_nodes = set()
    node_pattern = re.compile(r'(vmess|vless|ss|ssr|trojan|tuic|hysteria2?)://[^\s<>"\'|]+', re.IGNORECASE)
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in urls:
        print(f"[{time.strftime('%H:%M:%S')}] 抓取中: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            content = res.text
            # 尝试直接找节点
            all_nodes.update([m.group(0) for m in node_pattern.finditer(content)])
            # 尝试 Base64 解码后再找一遍
            try:
                decoded = base64.b64decode(content + "=" * (-len(content) % 4)).decode('utf-8')
                all_nodes.update([m.group(0) for m in node_pattern.finditer(decoded)])
            except: pass
        except: print(f"抓取失败: {url}")
    return list(all_nodes)

def main():
    print("=== 第一步：抓取原始节点 ===")
    raw_nodes = fetch_and_extract_nodes(TARGET_URLS)
    print(f"原始节点总数: {len(raw_nodes)}")

    print("\n=== 第二步：并发检测连通性 (清洗中...) ===")
    valid_nodes = []
    # 使用 50 个线程同时检测，速度极快！
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_node_connectivity, raw_nodes))
        valid_nodes = [r for r in results if r is not None]

    print(f"\n清洗完成！保留可用节点: {len(valid_nodes)} / {len(raw_nodes)}")

    print("\n=== 第三步：保存并加密订阅 ===")
    if valid_nodes:
        final_content = base64.b64encode('\n'.join(valid_nodes).encode('utf-8')).decode('utf-8')
        with open("sub.txt", 'w', encoding='utf-8') as f:
            f.write(final_content)
        print("✅ sub.txt 更新成功！")
    else:
        print("❌ 没抓到可用节点，不更新。")

if __name__ == "__main__":
    main()
