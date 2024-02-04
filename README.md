# Blue Archive JP downloader
# "Blue Archive" is a registered trademark of NAT GAMES Co., Ltd. and Yostar Co., Ltd. This repository is not affiliated with NEXON Korea Corp., NEXON GAMES Co., Ltd., and Yostar Co., Ltd. All game resources are copyrighted to their respective owners.


A small project that downloads all assets of the global version of Blue Archive and extracts them while it's at it.
The script updates the assets and even its own parameters on its own,
so all you have to do is execute the download_assets.py script after every update to get the latest files.

## Requirements

- Python 3.9.13+
- UnityPy 1.7.21
- requests
- xxhash
- pycryptodome
- flatbuffers

# Scripts

- ``download_assets.py``
  - This script downloads and extracts the latest assets.
  - "Switched to JP Server."
- ``extract_tables.py``
  - Extracts and decrypts the tables from the zip files in ``TableBundles``
  - due to the way it works, this script can take ages, around 15 minutes.
- ``flatbuf_schema_generator.py``
- Cannot use.
  

## TODO

- fix the decoding of some tables (flatbuf_schema_generator, FlatData/dump.py)
  - AnimationBlendTable (decoder missing)
  - AnimatorDataTable   (str decoding)
  - FurnitureExcelTable ('Location' not found)
  - GachaElementExcelTable ('EventContentId' not found)
  - ItemExcelTable ('EventContentId' not found)
  - MissionExcelTable ('EventContentId' not found)
  - OperatorExceTable ('Key' not found)
  - ShopExcel ('EventContentId' not found)
  - ShopInfoExcel ('EventContentId' not found)
  - ShopRefreshExcel ('EventContentId' not found)
# Reference & Thank
https://github.com/lwd-temp/blue-archive-spine-production
Report from Pscgylotti.
https://github.com/K0lb3/Blue-Archive---Asset-Downloader/issues/5
