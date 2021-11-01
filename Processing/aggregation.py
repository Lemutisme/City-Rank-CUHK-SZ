
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

'''
!!!READ ME!!!: 
输入表格： 指数化后数据.xlsx
输出表格： SecondaryAggregation.xlsx, FirstAggregation.xlsx, ZeroAggregation.xlsx
输出的表格有两个标签上的问题：

问题来源于源数据的标签错误，所以也可以直接在源数据上改。
1. 城生态文明建设 --> 手动改成城市生态文明建设
2. 哈尔滨的人均公共图书馆藏书对应的二级指标改成 --> 城市居民精神文生活动情况
'''

def fetchWeightsForAggregations(df):
	# 获得三个指标list
	first_indicator = list(set(df['一级指标']))
	second_indicator = list(set(df['二级指标']))
	third_indicator = list(set(df['三级指标']))

	# 以指标为index聚合
	one_city = df.loc[np.where(df['城市'] == '昆明')]
	grouped = pd.DataFrame(one_city.groupby(['一级指标','二级指标','三级指标']).count())
	third_frame = pd.DataFrame(grouped.groupby(['一级指标', '二级指标']).sum())
	third_frame = 1/third_frame
	second_frame = third_frame.copy()
	for i in third_frame.index:
	    second_frame.loc[i] = 1
	temp = pd.DataFrame(second_frame.groupby(['一级指标']).sum())
	temp = 1/temp
	for i in second_frame.index:
	    second_frame.loc[i] = temp.loc[i[0]]

	# 分别获取权重
	first_ind = []
	second_ind = []
	second_weight = []
	third_ind = []
	third_weight = []

	for index in grouped.index:
	    first_ind.append(index[0])
	    second_ind.append(index[1])
	    second_weight.append(second_frame.loc[index[0], index[1]]['数据源'])
	    third_ind.append(index[2])
	    third_weight.append(third_frame.loc[index[0], index[1]]['数据源'] )


	# 处理成dataframe
	dataset = pd.DataFrame({'一级指标': first_ind, '二级指标': second_ind, 
	                        '二级权重': second_weight, '三级指标': third_ind, 
	                        '三级权重': third_weight}, columns=['一级指标', '二级指标', '二级权重', '三级指标', '三级权重'])
	dataset = dataset.set_index(['一级指标', '二级指标', '三级指标'])
	return dataset







if __name__ == '__main__':
	print('读取数据...')
	df = pd.read_excel(io="指数化后数据.xlsx", engine='openpyxl').fillna(value=0)
	df = df.drop(['Unnamed: 0'], axis = 1)

	print('修改财政支出-节能环保（亿元）...')
	# 修改修改错误的二级指标
	for i in range(len(df)):
	    if (df.loc[i, '三级指标'] == '财政支出-节能环保（亿元）'):
	        df.loc[i, '二级指标'] = '城市生态环境改善情况'
	print('正在计算权重...')
	dataset = fetchWeightsForAggregations(df)
	years = list(range(2009, 2022))
	print('计算加权值...')
	for i in range(len(df)):
	    df.loc[i, years]  = df.loc[i, years] * dataset.loc[df.loc[i]['一级指标'], df.loc[i]['二级指标'], df.loc[i]['三级指标']]['三级权重']


	print('输出二级聚合...')
	df_secondary = pd.DataFrame(df.groupby(['城市','一级指标','二级指标']).sum())
	df_secondary.to_excel('SecondaryAggregation.xlsx')
	df_secondary = df_secondary.reset_index()
	for i in range(len(df_secondary)):
	    df_secondary.loc[i, years]  = df_secondary.loc[i, years] * dataset.loc[df_secondary.loc[i]['一级指标'], 
	                         	                                                  df_secondary.loc[i]['二级指标']]['二级权重'][0]
	print('Success!')

	print('输出一级聚合...')
	df_first = pd.DataFrame(df_secondary.groupby(['城市','一级指标']).sum())
	df_first = df_first.reset_index()
	df_first.to_excel('FirstAggregation.xlsx')
	print('Success!')

	print('输出零级聚合，并乘以100...')
	final = pd.DataFrame(df_first.groupby(['城市']).sum())
	rescaled = final*20
	rescaled.to_excel('ZeroAggregation.xlsx')
	print('Success!')









