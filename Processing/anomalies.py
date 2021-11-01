import pandas as pd
import numpy as np




if __name__ == '__main__':
	# 读取源数据
	print('读取指标..')
	df = pd.read_excel(io="指数化后数据.xlsx", engine='openpyxl').fillna(value=0)
	df = df.drop(['Unnamed: 0'], axis = 1)

	years = list(range(2009, 2022))
	year_data = df[years]
	print('筛选含有绝对值超过10的行列...')
	indices = set(np.where(np.abs(year_data) > 10)[0])
	df.loc[indices].to_excel('absOver10.xlsx')
	print('输出表格！ --- absOver10.xlsx')

	print('... 继续进行指标排查')
	print('读取权重表格...')
	weights = pd.read_excel(io="weights.xlsx", engine='openpyxl', index_col=[0,1,2]).fillna(value=0)


	print('输出可能错误的标签！...')
	df = df.set_index(['城市','一级指标','二级指标','三级指标'])
	for ind in df.index:
		if ((ind[1], ind[2], ind[3]) not in weights.index):
			print(ind)
