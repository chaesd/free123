import requests
import re
import base64
import time

# 在这里填入你找到的 GitHub 公开订阅源 (建议使用 Raw 链接)
# 比如搜索 github "免费节点"、"free v2ray" 等找到的 txt 文件链接
TARGET_URLS = [
    "https://ZmLyZv.mcsslk.xyz/5ad04c339a19e811d3e4729ab609f67b",
    "https://ghfast.top/https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt"
    # 替换为真实的 Github Raw 链接或包含节点的普通网页 URL
]

def fetch_and_extract_nodes(urls):
    """
    抓取网页并使用正则表达式提取所有节点链接
    """
    all_nodes = set() # 使用 set 自动去重
    
    # 正则表达式：匹配常见的代理协议链接
    # 匹配 vmess://, vless://, ss://, ssr://, trojan://, tuic://, hysteria:// 等等
    # [^\s<>"\'|]+ 表示匹配直到遇到空格、引号等非链接字符为止
    node_pattern = re.compile(r'(vmess|vless|ss|ssr|trojan|tuic|hysteria2?)://[^\s<>"\'|]+', re.IGNORECASE)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for url in urls:
        print(f"[{time.strftime('%H:%M:%S')}] 正在抓取: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                text_content = response.text
                
                # 1. 尝试直接从网页文本中提取明文节点
                matches = node_pattern.finditer(text_content)
                for match in matches:
                    all_nodes.add(match.group(0))
                
                # 2. 处理该网页本身就是一个 Base64 订阅链接的情况
                try:
                    # 尝试将整个网页内容进行 Base64 解码
                    # 去除可能存在的空格和换行
                    clean_b64 = text_content.replace('\n', '').replace('\r', '').strip()
                    # 补齐 '='
                    missing_padding = len(clean_b64) % 4
                    if missing_padding:
                        clean_b64 += '=' * (4 - missing_padding)
                        
                    decoded_text = base64.b64decode(clean_b64).decode('utf-8')
                    
                    # 再次在解码后的文本中寻找节点
                    decoded_matches = node_pattern.finditer(decoded_text)
                    for match in decoded_matches:
                        all_nodes.add(match.group(0))
                except Exception:
                    # 如果不是 Base64 格式，解码会报错，直接忽略即可
                    pass
                
        except requests.exceptions.RequestException as e:
            print(f"抓取失败 {url}: {e}")

    return list(all_nodes)

def generate_subscription(nodes, output_file="sub.txt"):
    """
    将抓取到的节点打包成标准的 Base64 订阅文件
    """
    if not nodes:
        print("没有抓取到任何节点，不生成文件。")
        return

    # 将所有节点用换行符连接成一个长字符串
    raw_content = '\n'.join(nodes)
    
    # 绝大多数代理客户端（v2rayN, Clash 等）识别的订阅格式是 Base64 编码后的字符串
    encoded_content = base64.b64encode(raw_content.encode('utf-8')).decode('utf-8')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(encoded_content)
        
    print(f"\n✅ 成功抓取并去重，共获得 {len(nodes)} 个有效节点！")
    print(f"✅ 订阅文件已生成：{output_file}")
    print("你可以将此文件放到公网服务器上，通过 http 链接导入你的代理软件。")

if __name__ == "__main__":
    print("开始执行节点聚合爬虫...")
    nodes = fetch_and_extract_nodes(TARGET_URLS)
    generate_subscription(nodes)
