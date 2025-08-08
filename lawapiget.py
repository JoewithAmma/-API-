import json, ssl, urllib.request, zipfile, io
import pandas as pd
from datetime import datetime

# 全國法規資料庫API，僅包含最高位階法律
url = "https://law.moj.gov.tw/api/data/chlaw.json.zip"
context = ssl._create_unverified_context()
# 下載 ZIP 並解壓縮特定檔案
with urllib.request.urlopen(url, context=context) as response:
    with zipfile.ZipFile(io.BytesIO(response.read())) as z:
        if "ChLaw.json" in z.namelist():
            with z.open("ChLaw.json") as jsonfile:
                data = json.load(io.TextIOWrapper(jsonfile, encoding='utf-8-sig'))
        else:
            raise FileNotFoundError("ChLaw.json not found in the ZIP archive.")          
# 全國法規資料庫API，包含行政命令等
url2 = "https://law.moj.gov.tw/api/data/chorder.json.zip"
context2 = ssl._create_unverified_context()
# 下載 ZIP 並解壓縮特定檔案
with urllib.request.urlopen(url2, context=context2) as response:
    with zipfile.ZipFile(io.BytesIO(response.read())) as z:
        if "ChOrder.json" in z.namelist():
            with z.open("ChOrder.json") as jsonfile:
                   try: 
                       data2 = json.load(io.TextIOWrapper(jsonfile, encoding='utf-8-sig'))
                   except Exception as e:
                           page=e.partial
                           data2=page.decode('utf-8-sig')
        else:
            raise FileNotFoundError("ChLaw.json not found in the ZIP archive.")
# 將資料讀進dataframe以利後續資料篩選           
new_data=pd.DataFrame.from_dict(data["Laws"])
data_law= pd.DataFrame.from_dict(data2["Laws"])
final_df = pd.concat([new_data,data_law],ignore_index=True)
# 進行日期資料清理，有些日期會是亂碼
def parse_date(x):
    x = str(x).zfill(8)  # 確保長度，像 '101' 會變 '00000101'
    if len(x) == 8:
        try:
            return datetime.strptime(x, '%Y%m%d')
        except ValueError:
            return pd.NaT
    elif len(x) == 4:
        try:
            return datetime.strptime('1900' + x, '%Y%m%d')  # 補上預設年份
        except ValueError:
            return pd.NaT
    else:
        return pd.NaT
final_df['LawModifiedDate'] = pd.to_datetime(final_df['LawModifiedDate'].apply(parse_date))
current_year = datetime.now().year
current_month = datetime.now().month
previous_month = current_month - 1 if current_month > 1 else 12
previous_month_year = current_year if current_month > 1 else current_year - 1
# 篩選當月與上月的資料
filtered_df = final_df[
    ((final_df['LawModifiedDate'].dt.year == current_year) & (final_df['LawModifiedDate'].dt.month == current_month)) |
    ((final_df['LawModifiedDate'].dt.year == previous_month_year) & (final_df['LawModifiedDate'].dt.month == previous_month))
]        

filtered_df.drop(["LawCategory","LawHasEngVersion","EngLawName","LawArticles"
                  ,"LawForeword","LawAttachements"], axis=1, inplace=True)
updatedate=data["UpdateDate"]
date_str = updatedate.replace("上午", "AM").replace("下午", "PM")
# 解析字串為 datetime 物件
dt = datetime.strptime(date_str, "%Y/%m/%d %p %I:%M:%S")
# 格式化為你要的檔名（yyyyMMdd）
filename_date = dt.strftime("%Y%m%d")
# 輸出第一份檔案當月、上月更新法規資料
outputpath=f"{filename_date}當月份更新資料.csv"
filtered_df.to_csv(outputpath,encoding='utf_8_sig',sep=",",index=False,header=True)
#篩選特定法條，可按需求自行新增
filtered_law_df = final_df[(final_df['LawName'] == "醫療器材管理法") |
                       (final_df['LawName'] == "醫療器材品質管理系統準則") |
                       (final_df['LawName'] == "醫療器材管理法施行細則") |
                       (final_df['LawName'] == "醫療器材品質管理系統檢查及製造許可核發辦法") |
                       (final_df['LawName'] == "醫療器材製造業者設置標準") |
                       (final_df['LawName'] == "醫療器材許可證核發與登錄及年度申報準則") |
                       (final_df['LawName'] == "醫療器材分類分級管理辦法") |
                       (final_df['LawName'] == "醫療器材優良臨床試驗管理辦法") |
                       (final_df['LawName'] == "醫療器材安全監視管理辦法") |
                       (final_df['LawName'] == "醫療器材回收處理辦法") |
                       (final_df['LawName'] == "醫療器材嚴重不良事件通報辦法") |
                       (final_df['LawName'] == "人體研究法") |
                       (final_df['LawName'] == "人體試驗管理辦法") |
                       (final_df['LawName'] == "資通安全管理法施行細則") |
                       (final_df['LawName'] == "資通安全管理法") |
                       (final_df['LawName'] == "個人資料保護法施行細則") |
                       (final_df['LawName'] == '個人資料保護法') ]
filtered_law_df.drop(["LawCategory","LawHasEngVersion","EngLawName","LawArticles"
                  ,"LawForeword","LawAttachements"], axis=1, inplace=True)
# 輸出第二份檔案，特定法規更新資料
outlawpath="特定法條更新資料.csv"
filtered_law_df.to_csv(outlawpath,encoding='utf_8_sig',sep=",",index=False,header=True) 
