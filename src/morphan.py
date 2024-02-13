import numpy as np
from scipy.optimize import curve_fit
import statistics
import random
import matplotlib.pyplot as plt
from scipy import stats
import skimage
import os
import csv
import pandas as pd

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

	def iron_sholl(self, a):
		intersections = []
		lengths = []

		for i,r in enumerate(a):
			intersection = np.count_nonzero(r)
			intersections.append(intersection)
			lengths.append(i)

		df = pd.DataFrame({'Intersection':intersections, 'Length':lengths})

		return df

	def reconstruct_neuron(self, v):
		used = []
		cix = 0
		blank = np.zeros((v[list(v.keys())[0]]['length'] + 10,len(v) * 2 + 2))

		for kk,vv in v.items():
			if kk in used: continue

			length = vv['length']
			children = vv['children']
			soma = vv['soma']
			a,cix,used = self.checkchildren(blank,v,kk,children,used,cix,2)
		
		return a

	def drawaline(self, aa,ll,ss,cc,val):
		aa[ss : ss+ll , cc] = val
		return aa

	def checkchildren(self, a,d,s,c,u,cx,i):
		ii = i+4
		cx = cx + 2

		sl = int(float(d[s]['length']))
		ss = int(float(d[s]['soma']))
		a = self.drawaline(a,sl,ss,cx,s)
		#print(' '*ii, s, sl, ss, cx)
		if c:
			#nc = sorted(c, reverse=False)
			nc = [x for _, x in sorted(zip(d[s]['distances'],c), reverse=True)]
			for cc in nc:
				if cc in u: continue
				#print(' '*ii,cc, d[cc])
				ccc = d[cc]['children']

				u.append(cc)
				a,cx,u = self.checkchildren(a,d,cc,ccc,u,cx,ii)

		return a,cx,u

	def gdfs(self, v,c,p,l=0):
		pda = v[p]
		ti = pda['children'].index(c)
		pl = v[p]['distances'][ti] + l
		gp = v[p]['parent']
		if gp:
			return self.gdfs(v,p,gp,pl)
		else:
			return pl

	def rearrange_tree(self,a):

		for kk,vv in a.items():
			parent = vv['parent']
			if parent:
				pl = self.gdfs(a,kk,parent)
			else:
				pl = 0
			a[kk]['soma'] = pl
		
		return a

	def adoption_agency(self,a):

		for k,v in a.items():
			todelete = []
			try:
				for kk,vv in v.items():
					children = vv['children']
					parent = vv['parent']
					length = vv['length']
					soma = vv['soma']
					if length == 0:
						if kk == 1:continue
						for child in children:
						    print('Parent %s adopts child %s from %s'%(parent, child, kk))
						    a[k][child]['parent'] = parent

						    a[k][parent]['children'].append(child)
						    a[k][parent]['distances'].append(soma)
						    inddel = v[parent]['children'].index(kk)
						    v[parent]['distances'].pop(inddel)
						    v[parent]['children'].pop(inddel)

						    todelete.append(kk)

				for td in todelete:
				    v.pop(td)
			except:
				print(k)
		return a

	def iron_preprocess(self,a):
		"""
		a: data path
		"""

		tmp={}
		fname = os.path.basename(a)
		neuron_name = fname.split('.csv')[0]

		with open(a, 'r') as data:
			for i, line in enumerate(csv.reader(data)):
				if i == 0: continue
				path_name = int(line[0])
				path_length = int(float(line[1]))		        

				if len(line[2]) == 2:
					children = []
				else:
					children = list(map(int, line[2].strip("[]").replace(" ","").split(",")))

				if len(line[3]) == 2:
					distances = []
				else:
					distances = line[3].strip("[]").replace(" ","").split(",")
					distances = list(map(float, distances))

				par = line[4]
				if len(par) == 0:
					par = None
				else:
					par = int(par.split(' ')[1])

				tmp[path_name] = {'length':path_length, 'children':children, 'distances':distances, 'parent':par}

				# rearrange the tree structure
				tmp = self.rearrange_tree(tmp)

		return tmp

	def siamese(self, a,b,c):
		"""
		a: path_dic[image]
		b: data_dic[image]
		c: path with an issue
		"""
		rootx = var3[var5]['x']
		rooty = var3[var5]['y']
		for k,v in var1.items():
			x = v['x']
			y = v['y']
		if rootx == x and rooty == y:
			return k

	def gcut_process(self,a,b,c):
		cmd = '%s %s %s %s' %('python3', a, b, c)
		os.system(cmd)

	def read_swc(self,a):
		tmp = self.read_file(a)
		tmp = [x for x in tmp if '#' not in x]
		return tmp

	def read_file(self,a):
		f = open(a,'r')
		tmp = f.read().splitlines()
		f.close()
		return tmp

	def check_directory(self,a,b):
		parent = os.path.join(a,b)
		if not os.path.exists(parent):
			os.mkdir(parent)
		return parent

	def vaa3d_process(self,a,b,c,
				vaa3d_software_path,p):

		os.chdir(vaa3d_software_path)
		vaaPath = './vaa3d '
		cmd = str(vaaPath + 
			"-x " + "vn2 " + 
			"-f " + "app2 " + 
			"-i " + a + " " +
			"-o " + c + " " +
			"-p " + b + " " + 
			      str(p['channel']) + " " + 
			      str(p['bg_thres']) + " " + 
			      str(p['auto_downsample']) + " " + 
			      str(p['radius_from_2d']) + " " + 
			      str(p['gray_distance']) + " " + 
			      str(p['allow_gap']) + " " + 
			      str(p['length_thres']) + " " + 
			      str(p['allow_resample']) + " " + 
			      str(p['brightfield']) + " " + 
			      str(p['sr_ratio']) + " " +
			      str(p['cnn_type']) + " " + 
			      str(p['high_intensity'])) 

		os.system(cmd)

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
