import numpy as np
from scipy.optimize import curve_fit
import statistics
import random
import matplotlib.pyplot as plt
from scipy import stats
import skimage

import cellprofiler.modules.correctilluminationapply
import cellprofiler.modules.correctilluminationcalculate
import cellprofiler_core.workspace 
import cellprofiler_core.image
import cellprofiler_core.object
import cellprofiler_core.pipeline
cellprofiler_core.preferences.set_headless()




class MorphAn:
	
	def __init__(self):
		return	

	############################
	# Background Correction
	############################

	def get_workspace(self,a,b,c):
		pipe = cellprofiler_core.pipeline.Pipeline()
		pipe.add_module(a)
		object_set = cellprofiler_core.object.ObjectSet()
		measurements = cellprofiler_core.measurement.Measurements()
		workspace = cellprofiler_core.workspace.Workspace(
		pipe,
		a,
		b,
		object_set,
		measurements,
		c,
		)
		return workspace

	def cp4_illumination_correction(self,a,b,c,d,e):
		mod_calc = cellprofiler.modules.correctilluminationcalculate.CorrectIlluminationCalculate()

		# configure the workspace
		mod_calc.image_name.value = 'orig'
		mod_calc.illumination_image_name.value = 'illum'
		mod_calc.intensity_choice.value = 'Regular'
		mod_calc.dilate_objects.value = 'No'
		mod_calc.object_dilation_radius.value = 1
		mod_calc.block_size.value = 60
		mod_calc.rescale_option.value = d
		mod_calc.each_or_all.value = 'Each'
		mod_calc.smoothing_method.value = c
		mod_calc.automatic_object_width.value = 'Automatic'
		mod_calc.object_width.value = 10
		mod_calc.size_of_smoothing_filter.value = e
		mod_calc.save_average_image.value = 'No'
		mod_calc.average_image_name.value = 'Avg'
		mod_calc.save_dilated_image.value = 'No'
		mod_calc.dilated_image_name.value = 'Dil'

		img_orig = cellprofiler_core.image.Image(b)
		image_set_list = cellprofiler_core.image.ImageSetList()
		image_set = image_set_list.get_image_set(0)
		image_set.add("orig", img_orig)

		workspace = self.get_workspace(mod_calc,image_set,image_set_list)
		mod_calc.run(workspace)

		illum = workspace.image_set.get_image("illum")

		# apply the module
		mod_apply = cellprofiler.modules.correctilluminationapply.CorrectIlluminationApply()
		img_orig = cellprofiler_core.image.Image(a)
		image_set_list = cellprofiler_core.image.ImageSetList()
		image_set = image_set_list.get_image_set(0)
		image_set.add('orig', img_orig)
		image_set.add('illum', illum)
		settings = mod_apply.settings()
		settings[0].value = 'orig'
		settings[1].value = 'corr'
		settings[2].value = 'illum'
		settings[3].value = 'Divide'
		workspace = self.get_workspace(mod_apply,image_set,image_set_list)
		mod_apply.run(workspace)

		corr = workspace.image_set.get_image("corr")

		return corr, illum



	def correct_background(self,a,b,c,d,e):
		img_corrected,img_function = self.cp4_illumination_correction(a,b,c,d,e)
		img_corrected = skimage.img_as_uint(img_corrected.pixel_data)
		return img_corrected		




	############################
	# Background Generation
	############################

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
		new_res = new_res.astype(np.uint16).squeeze()
		
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
