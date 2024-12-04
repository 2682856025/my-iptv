import requests
import subprocess
import re

CHECK_URL = [
    "https://bbbk.asia/final_streams.txt",
]


def verify_url(url):
    try:
        res = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"},
                           timeout=(3, 3))
        return True
    except requests.exceptions.Timeout:
        # 处理超时异常
        return False
    except requests.exceptions.RequestException as e:
        # 处理其他请求异常
        return False


def get_url_content(url):
    try:
        res = subprocess.check_output('curl -s -L "' + url + '"', shell=True)
        return res.decode('utf-8')
    except Exception as e:
        return ""


def convert_to_m3u(txt):
    lines = txt.split("\n")
    m3u_output = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"\n'
    current_group = None
    for line in lines:
        trimmed_line = line.strip()
        if trimmed_line != "":
            if "#genre#" in trimmed_line:
                current_group = trimmed_line.replace(",#genre#", "").strip()
            else:
                original_channel_name, channel_link = map(str.strip, trimmed_line.split(","))
                processed_channel_name = re.sub(r'(CCTV|CETV)-(\d+).*', r'\1\2', original_channel_name)
                m3u_output += f'#EXTINF:-1 tvg-name="{processed_channel_name}" tvg-logo="https://live.fanmingming.com/tv/{processed_channel_name}.png"'
                if current_group:
                    m3u_output += f' group-title="{current_group}"'
                m3u_output += f',{original_channel_name}\n{channel_link}\n'
    return m3u_output


def check_all_url(data):
    ret = ""
    for ise in data.split("\n"):
        print(ise)
        if not ise or ise == "":
            continue
        isesplit = ise.strip().split(",")
        if len(isesplit) >= 2:
            if isesplit[1].strip().startswith("http"):
                if verify_url(isesplit[1].strip()):
                    print("append:", ise)
                    ret += "\n" + ise
                else:
                    print("过滤无法访问的源:", ise)
                continue
        ret += "\n" + ise
    return ret


def load_ext_url():
    ret = ""
    for url in CHECK_URL:
        if not url or url == "":
            continue
        content = get_url_content(url)
        if content:
            ret += check_all_url(content)

    for line in ret.split("\n"):
        with open("latest_streams.txt", "a") as f:
            f.write("\n" + line)

    m3u_txt = convert_to_m3u(ret)
    with open("latest_streams.m3u", "w") as f:
        f.write(m3u_txt)

    print("状态: over")


print("开始测试live地址并保存")
load_ext_url()
