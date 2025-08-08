import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication 
import ssl

# Gmail 登入資訊
sender_email = "XXXX"  # 換成你自己的 Gmail
receiver_emails = [
    "XXXX",
    "XXXX"
]  # 收件者（Outlook 或其他）
#要在檔案裡面放入email的應用程式密碼
with open("XXX", "r", encoding="utf-8") as f:
    password = f.read().strip()
# 要比對的法條清單
target_laws = [
    "醫療器材管理法", "醫療器材品質管理系統準則", "醫療器材管理法施行細則",
    "醫療器材品質管理系統檢查及製造許可核發辦法", "醫療器材製造業者設置標準",
    "醫療器材許可證核發與登錄及年度申報準則", "醫療器材分類分級管理辦法",
    "醫療器材優良臨床試驗管理辦法", "醫療器材安全監視管理辦法", "醫療器材回收處理辦法",
    "醫療器材嚴重不良事件通報辦法", "人體研究法", "人體試驗管理辦法",
    "資通安全管理法施行細則", "資通安全管理法", "個人資料保護法施行細則", "個人資料保護法"
]
total_updates = filtered_df[filtered_df["LawName"].isin(target_laws)].shape[0]
# 信件內容標頭 + 更新數量
message_body = f"📌 區塊一[本月與上月關注法條更新檢查結果]（共 {total_updates} 條更新）\n\n"
for law in target_laws:
    matched = filtered_df[filtered_df["LawName"] == law]
    if not matched.empty:
        message_body += f"⚠️ {law} 有更新，共 {len(matched)} 筆。\n"
        message_body += matched[["LawID", "LawName", "LawModifiedDate"]].to_string(index=False)
        message_body += "\n\n"
    else:
        message_body += f"✅ {law} 無更新。\n"
message_body += "\n" + "="*60+"我是分隔線" + "\n\n"
total_keyword_updates = 0
keyword_section = ""
keywords = ["醫療器材", "人體", "個人資料", "資通安全", "數位醫療", "智慧醫療"]
for keyword in keywords:
    matched_keywords = filtered_df[filtered_df["LawName"].str.contains(keyword, na=False)]
    if not matched_keywords.empty:
        count = len(matched_keywords)
        total_keyword_updates += count
        keyword_section += f"⚠️ 關鍵字「{keyword}」有相關法規更新，共 {count} 筆。\n"
        keyword_section += matched_keywords[["LawName", "LawModifiedDate","LawURL"]].to_string(index=False, header=False)
        keyword_section += "\n\n"
    else:
        keyword_section += f"✅ 關鍵字「{keyword}」無相關法規更新。\n"
# 加上標題與統計總筆數
message_body += f"🔍 區塊二[關鍵字搜尋結果]（共 {total_keyword_updates} 筆更新）\n\n"
message_body += keyword_section
# 建立信件
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = ", ".join(receiver_emails)
msg['Subject'] = f"法規更新通知 - {filename_date}"
msg.attach(MIMEText(message_body, 'plain'))
fileName = '特定法條更新資料.csv'
pdfload = MIMEApplication(open(fileName,'rb').read()) 
pdfload.add_header('Content-Disposition', # 內容配置
                   'attachment', # 附件
                   filename=fileName) 
msg.attach(pdfload)
fileName = f"{filename_date}當月份更新資料.csv"
pdfload2= MIMEApplication(open(fileName,'rb').read()) 
pdfload2.add_header('Content-Disposition', # 內容配置
                   'attachment', # 附件
                   filename=fileName) 
msg.attach(pdfload2)
# 傳送 Email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_emails, msg.as_string())
# 如果要寄送outlook可以替換成以下程式碼
# context = ssl.create_default_context()
# with smtplib.SMTP("smtp.office365.com", 587) as server:
#     server.starttls(context=context)  # Outlook 需要 STARTTLS
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_emails, msg.as_string())
keywords = ["醫療器材", "人體", "個人資料", "資通安全", "數位醫療", "智慧醫療"]
print("📧 郵件已成功發送！")
