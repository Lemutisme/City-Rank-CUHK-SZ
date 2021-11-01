import pandas as pd
import numpy as np

'''
!!!READ ME!!!: 
输入表格： 最终版源数据.xlsx
输出表格： 指数化后数据.xlsx

输出的表格有两个标签上的问题：

问题来源于源数据的标签错误，所以也可以直接在源数据上改。
1. 城生态文明建设 --> 手动改成城市生态文明建设
2. 哈尔滨的人均公共图书馆藏书对应的二级指标改成 --> 城市居民精神文生活动情况
'''




def fetchGdpWeightsAverage(df, another_cities_gdp):
	# 重组index以三级指标和城市为标准
	grouped_new_df = pd.DataFrame(df.groupby(['三级指标','城市']).sum())
	# 计算所有城市根据gdp的加权平均（所有年份）
	cities = np.asarray(grouped_new_df.loc['万人R&D人员全时当量',:].index)
	indices = np.asarray(grouped_new_df.index)
	items = []
	for i in indices:
	    items.append(i[0])
	    
	indicators = set(items)

	for item in indicators:
	    for city in cities:    
	        if grouped_new_df.loc[(item, city), '需要进行倒数处理的'] == 1:
	            for year in years:
	                if grouped_new_df.loc[(item, city), year] != 0:
	                    grouped_new_df.loc[(item, city), year] = np.reciprocal(grouped_new_df.loc[(item, city), year])
	            grouped_new_df.loc[(item, city), '需要进行倒数处理的'] = 0

	print("处理倒数...")

	weighted_average = {}

	for item in indicators:
	    item_year = {}
	    for year in years: 
	        item_sum = sum(np.asarray(grouped_new_df.loc[(item, cities), year]) * np.asarray(another_cities_gdp.loc[cities, year]))
	        item_year[str(year)] = item_sum
	    weighted_average[item] = item_year

	print("获取GDP加权平均...")

	for item in indicators:

		one_indicator = grouped_new_df.loc[(item, cities), 2016]
		averages = one_indicator[one_indicator != 0].mean()


		for city in cities:
			
			if grouped_new_df.loc[(item, city), '需要处理的数据'] == 0:
				grouped_new_df.loc[(item, city), years] = grouped_new_df.loc[(item, city), years]/averages
			else:
				for year in years:    
					weighted_ave = weighted_average[item][str(year)]
					if weighted_ave != 0:
						grouped_new_df.loc[(item, city), year] = (grouped_new_df.loc[(item, city), year]/weighted_ave)

	print("根据加权平均的字典来计算...")
	return grouped_new_df





def fetchGdpWeights(df):
	# 计算GDP权重
	l = np.where(df['三级指标']=='人均GDP（元）')
	cities_gdp = df.iloc[l[0]]
	cities_gdp = cities_gdp.reset_index(drop=True)
	another_cities_gdp = cities_gdp.copy()
	for year in years:
		if (year == 2020 or year == 2021):
			for i in range(39):
				another_cities_gdp.loc[i, year] = another_cities_gdp.loc[i, 2019]
		else:
		    for i in range(39):
		        replace_value = cities_gdp.loc[i, year]/sum(cities_gdp.loc[:, year])
		        another_cities_gdp.loc[i, year] = replace_value

	# 将城市设置为index
	another_cities_gdp.index
	another_cities_gdp.reset_index(drop=True, inplace=True)
	another_cities_gdp = another_cities_gdp.set_index('城市')
	return another_cities_gdp




def fillZeroLabels(df):
	# 补充指标为0的数据 -- 根据其之前最后出现的指标进行复制
	print("补充为0的标签...")
	temp_label1 = ''
	temp_label2 = ''
	temp_label3 = ''
	for i in range(len(df)):
		if (df.loc[i, '一级指标'] != 0):
			temp_label1 = df.loc[i, '一级指标']
		else:
			df.loc[i, '一级指标'] = temp_label1
		if (df.loc[i, '二级指标'] != 0):
			temp_label2 = df.loc[i, '二级指标']
		else:
			df.loc[i, '二级指标'] = temp_label2

		if (df.loc[i, '三级指标'] != 0):

			temp_label3 = df.loc[i, '三级指标']
		else:
			df.loc[i, '三级指标'] = temp_label3		 
	return df


if __name__ == '__main__':

	# 读取源数据
	print('读取数据...')
	df = pd.read_excel(io="最终版源数据.xlsx", engine='openpyxl').fillna(value=0)

	num = int(input("为了删除空白数据，请输入数据的条目数："))
	df = df[:num]
	# 获取2019年到2020年份list
	years = np.asarray(range(2009, 2022))
	# 获取GDP权重
	print('...')
	gdp_weights = fetchGdpWeights(df)

	'''
	# 检查 -- expected output: 0.04994106250766287
	print(another_cities_gdp.loc[np.where(another_cities_gdp['城市']=='深圳')[0][0], 2009])
	'''

	grouped_new_df = fetchGdpWeightsAverage(df, gdp_weights)
	df = fillZeroLabels(df)

	print("表格复制中...")

	# 根据加权平均的字典来计算以GDP占比不变的表格
	for i in range(len(df)):
	    df.loc[i, years] = grouped_new_df.loc[(df.loc[i]['三级指标'], df.loc[i]['城市']), years]
	print("输出表格...Success!")	

	df.to_excel('指数化后数据.xlsx')







