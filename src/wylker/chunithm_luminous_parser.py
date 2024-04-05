from bs4 import BeautifulSoup
import pandas as pd
import requests
from xlsxwriter.utility import xl_col_to_name
from tqdm import tqdm

print("Parsing CHUNITHM LUMINOUS song lists...")

def fetch_html_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def parse_specific_tables(html_content, table_indices):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    dfs = []
    headers = ["曲名", "物量", "旧定数","定数"," "]
    for index in table_indices:
        table = tables[index]
        
        data = []
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'], recursive=False)
            row_data = []
            for cell in cells:
                text = cell.get_text(strip=True)
                link = cell.find('a', href=True)
                if link:
                    text += f" (Link: {link['href']})"
                row_data.append(text)
            data.append(row_data)
    
        
        df = pd.DataFrame(data, columns=headers)
        dfs.append(df)
    return dfs

def process_table_data(df):
    check_strings = ["MAS", "ULT", "EXP","ADV", "ORI", "撃舞", "VAR","東方","P&A","nico","イロ"]
    
    for index, row in df.iterrows():
        while row[0] in check_strings:
            row = row.drop(row.index[0])
            df.loc[index] = row.values.tolist() + [None] * (len(df.columns) - len(row))
    df.dropna(axis=1, how='all', inplace=True)
    return df

def remove_links_from_column(df):
    # 假设链接总是出现在第一列，使用iloc[:, 0]来访问第一列
    df.iloc[:, 0] = df.iloc[:, 0].str.replace(r'\(Link: /chunithmwiki/.+?\)', '', regex=True)
    return df

def save_tables_to_excel(dfs, excel_file):
    sheet_names = ['15', '14+', '14', '13+']
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        for df, sheet_name in zip(dfs, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            worksheet = writer.sheets[sheet_name]
            worksheet.set_column(f'{xl_col_to_name(0)}:{xl_col_to_name(0)}', 50)
            worksheet.set_column(f'{xl_col_to_name(1)}:{xl_col_to_name(1)}', 20)


def save_difficulties(df):
    current_value = None  
    rows_to_drop = []  
    for index, row in df.iterrows():
        try:
            # 尝试将第一列的值转换为浮点数
            value = float(row.iloc[0])
            
            if 10.0 <= value <= 15.4 or (row.iloc[0] is None and row.iloc[3] is not None):
                current_value = value  
                rows_to_drop.append(index)  
                continue  
        except ValueError:
            pass
        
        if current_value is not None:
            df.at[index, '定数'] = current_value
    df.drop(rows_to_drop, inplace=True)
    
    return df

#删除第n行
def drop_specific_row(df, n):
    if len(df) > n-1:
        return df.drop(df.index[n-1])
    return df



# url = "https://wikiwiki.jp/chunithmwiki/CHUNITHM%20LUMINOUS%20%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7%28%E5%AE%9A%E6%95%B0%E9%A0%861%29"
# url2= "https://wikiwiki.jp/chunithmwiki/CHUNITHM%20LUMINOUS%20%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7%28%E5%AE%9A%E6%95%B0%E9%A0%862%29"

# html_content = fetch_html_content(url)

# if html_content:
#     # 只提取第4、5、6、7个表格
#     table_indices = [3, 4, 5, 6]  
#     dfs = parse_specific_tables(html_content, table_indices)
#     processed_dfs = [process_table_data(df) for df in dfs]
#     cleaned_dfs = [remove_links_from_column(df) for df in processed_dfs]
#     updated_dfs = [save_difficulties(df) for df in cleaned_dfs]
#     dfs_after_removal = [drop_specific_row(df, 1) for df in updated_dfs]
#     # 保存到Excel
#     save_tables_to_excel(dfs_after_removal, 'CHUNITHM_LMN_SONG_LIST_1.xlsx')
#     print("Level 13+~15 parsed to CHUNITHM_LMN_SONG_LIST_1.xlsx successfully.")
#     input("Press Enter to continue.")
# else:
#     print("Unable to fetch HTML content.")
#     input("Press Enter to continue.")



# html_content2 = fetch_html_content(url2)

# if html_content2:
#     # 只提取第4、5、6、7个表格
#     table_indices = [3,4,5]  
#     dfs = parse_specific_tables(html_content2, table_indices)
#     processed_dfs = [process_table_data(df) for df in dfs]
#     cleaned_dfs = [remove_links_from_column(df) for df in processed_dfs]
#     updated_dfs = [save_difficulties(df) for df in cleaned_dfs]
#     dfs_after_removal = [drop_specific_row(df, 1) for df in updated_dfs]
#     # 保存到Excel
#     save_tables_to_excel(dfs_after_removal, 'CHUNITHM_LMN_SONG_LIST_2.xlsx')
#     print("Level 12~13 parsed to CHUNITHM_LMN_SONG_LIST_2.xlsx successfully.")
#     input("Press Enter to exit.")
# else:
#     print("Unable to fetch HTML content.")
#     input("Press Enter to exit.")

def process_url(url, table_indices, sheet_names):
    html_content = fetch_html_content(url)
    if not html_content:
        print(f"Unable to fetch HTML content from {url}")
        return []
    
    dfs = parse_specific_tables(html_content, table_indices)
    processed_dfs = [process_table_data(df) for df in dfs]
    cleaned_dfs = [remove_links_from_column(df) for df in processed_dfs]
    updated_dfs = [save_difficulties(df) for df in cleaned_dfs]
    dfs_after_removal = [drop_specific_row(df, 1) for df in updated_dfs]
    return dfs_after_removal, sheet_names

def save_all_tables_to_excel(all_dfs, excel_file):
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        for dfs, sheet_names in tqdm(all_dfs, desc='parsing level statistics...'):
            for df, sheet_name in zip(dfs, sheet_names):
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column(f'{xl_col_to_name(0)}:{xl_col_to_name(0)}', 50)
                worksheet.set_column(f'{xl_col_to_name(1)}:{xl_col_to_name(1)}', 20)



urls_and_tables = [
    ("https://wikiwiki.jp/chunithmwiki/CHUNITHM%20LUMINOUS%20%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7%28%E5%AE%9A%E6%95%B0%E9%A0%861%29", [3, 4, 5, 6], ['15', '14+', '14', '13+']),
    ("https://wikiwiki.jp/chunithmwiki/CHUNITHM%20LUMINOUS%20%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7%28%E5%AE%9A%E6%95%B0%E9%A0%862%29", [3, 4, 5], ['13', '12+', '12']),
    ("https://wikiwiki.jp/chunithmwiki/CHUNITHM%20LUMINOUS%20%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7%28%E5%AE%9A%E6%95%B0%E9%A0%863%29",[3, 4, 5], ['11+', '11', '10~10+'])
]

all_dfs = [process_url(url, table_indices, sheet_names) for url, table_indices, sheet_names in urls_and_tables]

save_all_tables_to_excel(all_dfs, 'CHUNITHM_LMN_SONG_LISTS.xlsx')
print("All levels parsed and saved to CHUNITHM_LMN_SONG_LISTS.xlsx successfully.")
input("Press Enter to exit.")