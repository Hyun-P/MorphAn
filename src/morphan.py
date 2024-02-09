import numpy as np
from scipy.optimize import curve_fit
import statistics
import random
import matplotlib.pyplot as plt
from scipy import stats



class MorphAn:

	def __init__(self):
		return	
	
	def bg_wrapper(self,args):
		return self.background_processor(*args)

	def model_function(self,x,a,b,c,d):
		return a * np.sin(b - x) + c * x**2 + d

	def background_processor(self,a,b,c,d,precut=False,display=False):
		if precut:
			med = np.median(b)
			std = np.std(b)
			thres = med + std
			b = np.where(b>thres, thres, b)

		x_data = a
		y_data = b

		# normalization
		xData = x_data/max(x_data)
		yData = y_data/max(y_data)
		new_y_data = yData.copy()

		popt,pcov = curve_fit(self.model_function, xData, yData)

		x = np.linspace(0, len(a), len(a))
		x = x/max(x)
		y = self.model_function(x, *popt)
		mode = statistics.mode(yData)
		t = yData[yData<mode]

		iqr = stats.iqr(t)
		toCut = iqr*c
		upperThres = y + toCut
		lowerThres = y - toCut

		if d:
			target_indexes = np.where((yData>upperThres) | (yData<lowerThres))[0]
		else:
			target_indexes = np.where((yData>upperThres))[0]

		for i in target_indexes:
			mu = y[i]
			rand = random.gauss(mu, toCut/4)
			new_y_data[i] = rand

		new_res = new_y_data*np.max(y_data)
		
		if display:
			plot_up = upperThres * np.max(y_data)
			plot_dn = lowerThres * np.max(y_data)
			plt.figure(figsize=(20,5))
			plt.plot(x_data,y_data,'ro',markersize=5,label='data')
			plt.plot(x_data,new_res,'bo',markersize=2,label='bg')
			plt.plot(x_data,y*np.max(y_data),linewidth=3.0,label='fit')
			plt.plot(x_data,plot_up,label='Upper Threshold')
			plt.plot(x_data,plot_dn,label='Lower Threshold')
			plt.show()
			plt.close()

		return new_res
