# 蔚藍檔案（Blue Archive）日服下載器

**免責聲明：** "Blue Archive"是NAT GAMES Co., Ltd.和Yostar Co., Ltd.的註冊商標。 本儲存庫與NEXON Korea Corp.、NEXON GAMES Co., Ltd.及Yostar Co., Ltd.無關。 所有遊戲資源的版權屬於其各自的所有者。

這是一個小型項目，旨在下載全球版本的藍檔案的所有資源並同時進行提取。 該腳本自主更新資源及其參數，您只需在每次更新後執行`download_assets.py`腳本即可取得最新檔案。

## 要求

- Python 3.9.13+
- UnityPy 1.7.21
- requests
- xxhash
- Pythoncryptodome
- flatbuffers

# 腳本

- ``download_assets.py``
   - 下載並提取最新的資源。
   - "已切換至JP伺服器。"
- ``extract_tables.py``
   - 從「TableBundles」中的zip檔案中提取並解密表格。 由於其性質，此腳本可能需要大約15分鐘的時間來完成。
- ``flatbuf_schema_generator.py``
   - 目前無法使用。



# 參考和致謝
  https://github.com/lwd-temp/blue-archive-spine-production
- 提供我的想法。
- Pscgylotti的回報。 [問題連結](https://github.com/K0lb3/Blue-Archive---Asset-Downloader/issues/5)
