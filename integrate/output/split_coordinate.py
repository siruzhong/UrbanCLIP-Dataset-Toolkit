import pandas as pd

# 读取CSV文件
df = pd.read_csv('integrated_satellite_data.csv', header=None, names=['satellite_img_name', 'BD09 coordinate', 'WGS84 coordinate', 'carbon_emissions (ton)', 'population (unit)', 'gdp (million yuan)'])

# 使用正则表达式提取经度和纬度
df[['lat', 'lon']] = df['WGS84 coordinate'].str.extract(r'\(([^,]+), ([^)]+)\)')

# 将字符串转换为浮点数
df['lat'] = df['lat'].astype(float)
df['lon'] = df['lon'].astype(float)

# 删除原始coordinates列
df.drop(columns=['WGS84 coordinate'], inplace=True)

df.to_csv('integrated_satellite_data_coordinate_split.csv', index=False)

# 打印处理后的DataFrame
print(df)
