import os
import requests
from zipfile import ZipFile
import io
import re
import binascii
import UnityPy
import json
import platform
import subprocess

import threading

MAX_THREADS = 50

ROOT = os.path.dirname(os.path.realpath(__file__))
RAW = os.path.join(ROOT, "raw")
EXT = os.path.join(ROOT, "extracted")
VERSION = os.path.join(ROOT, "version.txt")

# アプリの内部リソースバージョンID
# versionId = "r70_47_v8g5eikyrqgs6zuiohj9"
# versionId = "r75_52_49ajrpwcziy395uuk0jq"
versionId = "r76_53_aga2h1wd8vmub5kljnqh"

# リソースのMAP URL
resource_path = f"https://yostar-serverinfo.bluearchiveyostar.com/{versionId}.json"
# resource_path2 = "https://prod-noticeindex.bluearchiveyostar.com/prod/index.json"

option = {
    "skipExistingDownloadedResource": True,
    "skipExistingAssets": True
}

def asset_download(file_info):
    file_url, path, crc = file_info
    filename = file_url.split("/")[-1]
    
    if filename.endswith('.bundle'):
        dest_path = os.path.join(RAW, filename)
    elif 'TableBundles' in file_url:
        dest_path = os.path.join(EXT, 'TableBundles', filename)
    elif 'MediaResources' in file_url:
        dest_path = os.path.join(EXT, 'MediaResources', path)
    else:
        dest_path = os.path.join(EXT, filename)
    
    if option["skipExistingDownloadedResource"] and os.path.isfile(dest_path):
        print(f"{filename} - Already downloaded. Skipping.")
        return
    while True:
        print("Dwonload to: " + file_url)
        downloadFile(file_url, dest_path)
        calculated_crc = calculate_crc32(dest_path)
        if calculated_crc == crc:
            print(f"{filename} - Download successful.")
            break
        else:
            print(f"WARNING: CRC32 checksum for {dest_path} does not match expected value! Retrying...")
            break


def main():
    path = ROOT
    app_id = "com.YostarJP.BlueArchive"
    # 獲取版本
    print("Fetching version")
    if os.path.exists(VERSION):
        with open(VERSION, "rt") as f:
            version = f.read()
    else:
        print("No local version found")
        version = update_apk_version(app_id, path)
    print(version)

    game_files_list = getAllGameFiles()

    active_threads = []
    for file_info in game_files_list:
        # 新しいスレッドを起動し、リストに追加
        while len(active_threads) >= MAX_THREADS:
            # すべてのアクティブスレッドの終了を待つ
            for download_thread in active_threads:
                download_thread.join(timeout=1)
            active_threads = [download_thread for download_thread in active_threads if download_thread.is_alive()]

        download_thread = threading.Thread(target=asset_download, args=(file_info,))
        download_thread.daemon = True
        download_thread.start()
        active_threads.append(download_thread)
    
    # 最後のスレッドが終了するのを待つ
    for download_thread in active_threads:
        download_thread.join()

# 計算文件的CRC32校驗和的函數
def calculate_crc32(file_path):
    buf = open(file_path, 'rb').read()
    crc32 = binascii.crc32(buf) & 0xFFFFFFFF
    return crc32
def getBaseResourceURL():
    data = requests.get(resource_path).json()
    print(data)
    return data["ConnectionGroups"][0]['OverrideConnectionGroups'][-1]['AddressablesCatalogUrlRoot']
# 獲取所有遊戲文件的函數
def getAllGameFiles():
    data = []
    base_url = getBaseResourceURL()

    # BundleFiles
    bundle_url = base_url + '/Android/bundleDownloadInfo.json'
    resB = requests.get(bundle_url).json()
    for asset in resB["BundleFiles"]:
        data.append((base_url + '/Android/' + asset["Name"], "", asset.get("Crc", 0)))
    
    # TableBundles
    # 最新版のみなぜか TableCatalog.json がないため、一時的に過去バージョンから持ってくる
    # TableCatalog.bytes というファイルがあるのでそれを解析して利用するのもあり
    TableBundles_url = "https://prod-clientpatch.bluearchiveyostar.com/r67_jjjg51ngucokd90cuk4l_3" + '/TableBundles/TableCatalog.json'
    # TableBundles_url = base_url + '/TableBundles/TableCatalog.json'
    print(TableBundles_url)
    resT = requests.get(TableBundles_url).json()
    for key, asset in resT["Table"].items():  #
        data.append((base_url + '/TableBundles/' + asset["Name"], "", asset.get("Crc", 0)))  

    # MediaResource
    if (int(versionId[1:3]) < 76): # バージョンでindexのパスが違うようになった
        # r76_53 以前の MediaCatalog indexのURLパス
        MediaResources_url = base_url + '/MediaResources/MediaCatalog.bytes'
    else:
        # r76_53 以降の MediaCatalog indexのURLパス
        MediaResources_url = base_url + '/MediaResources/Catalog/MediaCatalog.bytes'
    if not os.path.exists(RAW):
        os.makedirs(RAW)
    input_file_path = os.path.join(RAW, 'MediaCatalog.bytes')
    response = requests.get(MediaResources_url)
    response.raise_for_status()
    with open(input_file_path, 'wb') as file:
        file.write(response.content)
        
    # 出力ディレクトリが存在しない場合作成
    if not os.path.exists(os.path.join(EXT, 'MediaResources')):
        os.makedirs(os.path.join(EXT, 'MediaResources'))

    output_file_path = os.path.join(EXT, 'MediaResources', 'MediaCatalog.json')
    if platform.system() == 'Windows':
        exe_path = os.path.abspath("MemoryPackDeserializer/MemoryPackDeserializer.exe")
    else:
        exe_path = os.path.abspath("MemoryPackDeserializer/MemoryPackDeserializer")
    subprocess.run([exe_path, input_file_path, output_file_path])
    with open(output_file_path, 'r') as f:
        resM = json.load(f)
    for key, value in resM["Table"].items():
        media_url = base_url + '/MediaResources/' + value["Path"]
        data.append((media_url, value["Path"], value.get("Crc", 0)))  
    return data

# ファイルのダウンロード
def downloadFile(url, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    src = requests.get(url).content
    with open(filename, 'wb') as f:
        f.write(src)

    # 計算CRC32校驗和
    crc32 = calculate_crc32(filename)
    print(f"CRC32 checksum for {filename}: {crc32}")
# 更新APK版本的函數
def update_apk_version(app_id, path):
    print("Downloading the latest APK from QooApp")
    apk_data = download_QooApp_apk(app_id)
    with open(os.path.join(path, "current.apk"), "wb") as f:
        f.write(apk_data)
    print("Extracting app version and API version")
    version = extract_apk_version(apk_data)
    with open(VERSION, "wt") as f:
        f.write(version)
    return version
# 提取APK版本的函數
def extract_apk_version(apk_data):
    with io.BytesIO(apk_data) as stream:
        with ZipFile(stream) as zip:
            # devs are dumb shit and keep moving the app version around
            with zip.open("assets/bin/Data/globalgamemanagers", "r") as f:
                env = UnityPy.load(f)
                for obj in env.objects:
                    if obj.type.name == "PlayerSettings":
                        build_version = re.search(
                            b"\d+?\.\d+?\.\d+", obj.get_raw_data()
                        )[0].decode()
                        return build_version
# 從QooApp下載APK的函數
def download_QooApp_apk(apk_id):
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
    query = urlencode(
        {
            "supported_abis": "x86,armeabi-v7a,armeabi",
            "sdk_version": "22",
        }
    )
    res = urlopen(
        Request(
            url=f"https://d1.qoo-apk.com/12252/apk/com.YostarJP.BlueArchive-275921-131992259-1713925384.apk",
            headers={
                "accept-encoding": "gzip",
                "user-agent": "QooApp 8.1.7",
                "device-id": "80e65e35094bedcc",
            },
            method="GET",
        )
    )
    data = urlopen(res.url).read()
    return data

if __name__ == "__main__":
    main()