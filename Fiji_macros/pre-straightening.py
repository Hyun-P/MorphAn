# @String(value="<HTML>This script runs Sholl Analysis (Iron) on an entire directory of reconstruction files.<br>Processing log is shown in Console.", visibility="MESSAGE") msg
# @File(label="Input directory:", style="directory", description="Input folder containing reconstruction files (.traces, .swc, json) to be analyzed") top_dir
# @String(label="Filename filter", description="<HTML>Only filenames matching this string (case sensitive) will be considered.<br>Regex patterns accepted. Leave empty to disable fitering.",value="") name_filter
# @String(label="Output (tables and plots):", choices={"Place holder for other parameters","description"}) output_choice
# @ImageJ ij
# @ RoiManager roiManager

import os, sys, csv, math, time
from ij import IJ, ImagePlus
from ij.plugin import Straightener
from ij.plugin.frame import RoiManager
from ij.gui import PointRoi, PolygonRoi
from ij.gui import Overlay
from sc.fiji.snt import (Tree, Path, PathAndFillManager)
from sc.fiji.snt.analysis import (SNTTable, ShollAnalyzer, TreeAnalyzer, RoiConverter)
from sc.fiji.snt.analysis.sholl import (Profile, ShollUtils)
from sc.fiji.snt.analysis.sholl.parsers import (TreeParser)
from sc.fiji.snt.util import (SWCPoint, PointInImage)

# Log function
def log(msg, level = "info"):
	# https://forum.image.sc/t/logservice-issue-with-jython-slim-2-7-2-and-scripting-jython-1-0-0/
	from org.scijava.log import LogLevel
	if "warn" in level:
		ij.log().log(LogLevel.WARN, msg)
	elif "error" in level:
		ij.log().log(LogLevel.ERROR, msg)
	else:
		ij.log().log(LogLevel.INFO, msg)

# a function to get point x,y of a node?
def get_point(pii):
	return pii.getX(), pii.getY()
	
########################################################################
########################################################################
# This is only to:
# 	1. 
########################################################################
########################################################################

def main():

	print('***'*100)

	# get ROI Manager object
	rm = RoiManager.getInstance2()

	# delete any existing rois in the ROI Manager
	rm.reset()
	
	# define a output directory to save straightened swc data; if it doesn't exist, create one; This is where the necessary paths data are saved
	output_dir = os.path.join(os.path.dirname(top_dir.getAbsolutePath()),'swc_paths_data')
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)
	
	# define a output directory to save sholl data; if it doesn't exists, create one; This is where the sholl data are saved
	sholl_out_dir = os.path.join(os.path.dirname(top_dir.getAbsolutePath()),'sholl')
	if not os.path.exists(sholl_out_dir):
		os.mkdir(sholl_out_dir)
		
	tree_out_dir = os.path.join(os.path.dirname(top_dir.getAbsolutePath()),'tree_data')
	if not os.path.exists(tree_out_dir):
		os.mkdir(tree_out_dir)
		
	roi_output_dir = os.path.join(os.path.dirname(top_dir.getAbsolutePath()), 'ROI_to_be_straightened')
	if not os.path.exists(roi_output_dir):
		os.mkdir(roi_output_dir)
	
	total_num_imgs = len(os.listdir(top_dir.getAbsolutePath()))
	ind_num_img = 1

	# top_dir = an input directory where the swc data from Vaa3D/Gcut is stored; iterate through files and get data
	for root,dirs,files in os.walk(top_dir.getAbsolutePath()):

		# skip the first file iteration, which is the input directory itself, or an empty directory
		if root == top_dir.getAbsolutePath() or not files: continue
		
		else:

			# get the name of the image from the subfolders
			img_name = os.path.basename(root)
			
			# print an image name that is being processed
			print('\n'*4)
			print('==='*40)
			print('Image: %s'%img_name)
			print('%s/%s'%(ind_num_img,total_num_imgs))
			print('==='*40)
			ind_num_img = ind_num_img + 1
			
			
			for tfile in files:
				
				if 'swc' not in tfile: continue
				
				order_list = []
					
				trace_path = os.path.join(root,tfile)

				tree = Tree.fromFile(trace_path)
				
				# get a file name of the tree
				filename = tree.getLabel()
				print(filename)
				
				
				################################################################################################################
				# SNT Tree Data
				################################################################################################################
				
				# get paths from the tree
				paths = tree.list()
				#print(paths)
				print(len(paths))
				if len(paths) <= 3:
					continue
					
				# get the position x,y of soma
				centroid = tree.getRoot()
				somax,somay = get_point(centroid)
				
				graph = tree.getGraph()
				
				ta = TreeAnalyzer(tree)
				
				tametrics = ta.getMetrics()
				ta.measure(tametrics, False)
				tatable = ta.getTable()
				tatable.pop(0) # first value seems to be off; not sure what
				
				troot = tree.getRoot()
				
				# get primary paths
				pris = ta.getPrimaryBranches()
				target_pri = pris[-1]
				target_pri_root = target_pri.getNodes()[1]
				root_dist = troot.distanceTo(target_pri_root)
				
				tametrics.append('Root_Distance')
				new_tatable = []
				for tat in tatable:
					new_tatable.append(tat[0])
				new_tatable.append(root_dist)
				
				tametrics.append('X')
				tametrics.append('Y')
				new_tatable.append(somax)
				new_tatable.append(somay)
				
				csv_path = os.path.join(tree_out_dir, filename+".csv")
					
				if os.path.exists(csv_path):
					os.remove(csv_path)
				fields = tametrics
				with open(csv_path, 'w') as csvfile:
					csvwriter = csv.writer(csvfile, lineterminator='\n')
					csvwriter.writerow(fields)
					csvwriter.writerow(new_tatable)
			
#				tmp_inds = []
#				for pi,path in enumerate(paths):
#					
#					nodes = path.getNodes()
#					nlength = len(nodes)
#					if nlength == 1: continue
#					
#					plength = path.getLength()
#					
#					if plength <= 10:
#						path_id = path.getID()
#						print(path,path_id, nlength, plength)
#						tmp_inds.append(path)
#						
#				for ti in tmp_inds:
#					target = tree.get(tree.indexOf(ti))
#					#print(target)
#					tree.remove(target)

				
#				sholl_out_indiv_dir = os.path.join(sholl_out_dir, filename)
#				if not os.path.exists(sholl_out_indiv_dir):
#					os.mkdir(sholl_out_indiv_dir)
	
				
	
				# The following codes are to project a skeletonized image of the tracing on to a blank image
				# blank = IJ.createImage("Blank", "16-bit black", 2048, 2048, 1) # Creates a blank image
				# skeleton = tree.skeletonize(blank, 65535) # this would be a convenient option
				#skeleton = tree.getSkeleton2D()
				# skeleton.show()
				# test = skeleton.resize(2048,2048,1,'skeleton')
				
				if 'ini' in filename: continue
	
				# print the name of the tree being processed
	
				################################################################################################################
				# Traditional Sholl Analysis
				################################################################################################################
				
				print('***'*15)
				print('Traditional Sholl Analysis')
						
				# if the directory is not empty, then the analysis is done; skip.
				
				# initialize a TreeParser object with the tree
				parser = TreeParser(tree)

				# get the coordinate of the cell body
				center_point = tree.getRoot()

				# set the cell boday as the origin of Sholl Analysis
				parser.setCenter(center_point)

				# set the step size of the circles
				parser.setStepSize(1)

				# parse data
				parser.parse()
				if not parser.successful():
					log.error("Could not be parsed!")

				# profile in parser contains the sholl data; ie) the distance and the number of crossings
				profile = parser.getProfile()
				if profile.isEmpty():
					log.error("All intersection counts were zero! Invalid threshold range!?")
				else:

					# get rid of zeros -> from where?
					profile.trimZeroCounts()

				# radii means the circle data; ie) distances from soma
				radii = profile.radii()

				# create an empty list to store the number of intersection data
				inters = []

				# get the number of intersections at each radius and append to the list = inters
				for radius in radii:
					inters.append(profile.getCountAtRadius(radius))

				# create a tmp list to store both radius and intersection data
				tmp = []

				# iterate each radius and intersection data from both lists
				for r,i in zip(radii, inters):
					tmp.append([r,i])
				fields = ['radius', 'intersection']
				csv_name = str('%s__sholl-traditional.csv'%filename)

				csv_path = os.path.expanduser(os.path.join(sholl_out_dir, csv_name))
				with open(csv_path, 'w') as csvfile:
					csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
					csvwriter.writerow(fields)
					for r,i in zip(radii,inters):
						csvwriter.writerow([r,i])
						
				print('Complete!')
					
				################################################################################################################
				################################################################################################################
	
				################################################################################################################
				# New Sholl
				################################################################################################################
						
				print('***'*15)
				print('New Sholl Analysis')
				
				roi_indiv_output_dir = os.path.join(roi_output_dir, img_name)
				if not os.path.exists(roi_indiv_output_dir):
					os.mkdir(roi_indiv_output_dir)
	
				# get paths from the tree
				paths = tree.list()
				#print(paths)
			
				# get the position x,y of soma
				centroid = tree.getRoot()
				somax,somay = get_point(centroid)
				axon_length = paths[0].getLength()
				
				if axon_length == 0:
					tfilename = filename.split('_soma')[0]
					vaa_fpath = os.path.join(os.path.dirname(top_dir.getAbsolutePath()),'vaa3d',img_name,'%s.swc'%tfilename)
					
					vaa_tree = Tree.fromFile(vaa_fpath)
					vaa_paths = vaa_tree.list()
				
				pripaths = paths[0].getChildren()
				vaatogcut_dict = {}
				gcuttovaa_dict = {}
				
				if axon_length == 0:
					print(' ')
					print('---'*15)
					print('=== GCut to Vaa ===')
					for ppath in pripaths:
						
						ppath_name = ppath.getName()
						ppath_id = ppath.getID()
						ppath_length = ppath.getLength()
						ppath_parent = ppath.getStartJoins()
						ppath_start_point = get_point(ppath.getNodes()[0])
						ppath_last_point = get_point(ppath.getNodes()[-1])
						
						for vp in vaa_paths:
							tnodes = vp.getNodes()
							ntnodes = []
							for tn in tnodes:
								ntnodes.append(get_point(tn))
								
							if ppath_start_point in ntnodes:
								
								vp_id = vp.getID()
								vp_name = vp.getName()
								vp_parent = vp.getStartJoins()
								print('%s of %s <===> %s of %s'%(ppath,ppath_parent, vp,vp_parent))
									
								vp_start_point_index = ntnodes.index(ppath_start_point)
								vp_section_omit = vp.getSection(0,vp_start_point_index)
								vp_section_omit_length = vp_section_omit.getLength()
								ppath_new_length = ppath_length + vp_section_omit_length
	
								vp_parent_section_juction_length = 0
								if vp_parent:
									vp_parent_nodes = vp_parent.getNodes()
									vp_junction_nodes = list(vp.getJunctionNodes())
									vp_junction_target_node = vp_junction_nodes[-1]
									vp_junction_target_node_path= vp_junction_target_node.getPath()
									vp_junctions = vp.findJunctions() # index 1 is the root of the path
									vp_junctions_target_point = vp_junctions[0]
									vp_junctions_target_points = get_point(vp_junctions_target_point)
									vp_parent_junction_indices = vp_parent.findJunctionIndices()
									vp_parent_junctions = vp_parent.findJunctions()
									#print(vp_junction_target_node_path)
									#print(vp_junctions_target_points)
									#print(vp_parent_junction_indices)
									for vpji in vp_parent_junction_indices:
										tn = get_point(vp_parent_nodes[vpji])
										if tn == vp_junctions_target_points:
											#print(tn, vpji)
											vp_parent_section_juction = vp_parent.getSection(0,vpji)
											vp_parent_section_juction_length = vp_parent_section_juction.getLength()
										
								print('Junction Dist: %s || Length: %s + Omitted: %s -> %s'%(vp_parent_section_juction_length, ppath_length,vp_section_omit_length, ppath_new_length))
								print(' ')
								gcuttovaa_dict[ppath] = {'vaa_path':vp, 'vaa_parent':vp_parent, 'junction_dist':vp_parent_section_juction_length, 
															'new_length':ppath_new_length, 'omit':vp_section_omit_length}
								vaatogcut_dict[vp] = {'path':ppath}
					print('=== GCut to Vaa End ===')
					print('---'*15)
					print(' ')
				
				path_dic = {}
				for path in paths:
					
					path_name = path.getName()
					path_id = path.getID()
					path_length = path.getLength()
					
					nodes = path.getNodes()
					nodes_coords = []
					for node in nodes:
						node = get_point(node)
						nodes_coords.append(node)
					
					children = path.getChildren()
					new_children = []
					distances = []
					
					parent = path.getStartJoins()
					omit_length = 0
					
					# Path Length Change \wedge PARENT CHANGE <- may not be necessary
					if axon_length == 0 and path in pripaths:
						
						vp = gcuttovaa_dict[path]['vaa_path']
						vpname = vp.getName()
						opath_length = path_length
						path_length = gcuttovaa_dict[path]['new_length']
						omit_length = gcuttovaa_dict[path]['omit']
						'''
						vp_parent = gcuttovaa_dict[path]['vaa_parent']
						if vp_parent:
							oparent = parent
							parent = vaatogcut_dict[vp_parent]['path']
							print('Parent Change %s : %s -> %s'%(path, oparent, parent))
						'''
					
					if children:
						for child in children:
							
							child_start_node = child.getStartJoinsPoint().getX(), child.getStartJoinsPoint().getY()
							target_index = nodes_coords.index(child_start_node)
							distance = path.getSection(0, target_index).getLength() + omit_length
							if child in gcuttovaa_dict.keys():
								odistance = distance
								distance = gcuttovaa_dict[child]['junction_dist']
								print('Distance Change %s : %s -> %s'%(child, odistance, distance))
								print(' ')
							distances.append(distance)
							new_children.append(child.getID())
							
					
					
					order_list.append(path_id)
					
					if not parent:
						parent = None

					#for child,dist,cleng in zip(new_children,distances,tlengths):
						#print('Path %s'%child, cleng, dist)
					#print(' ')
					path_dic[path_id] = {"path_length":path_length,
									"children":new_children,
									"distances":distances,
									"parent":parent}
					
				#ordered_dic = {k: path_dic[k] for k in order_list}

#				for k,v in ordered_dic.items():
#					print(k,v)
				csv_path = os.path.join(output_dir, filename+".csv")
					
				if os.path.exists(csv_path):
					os.remove(csv_path)
				fields = ['path_name', 'path_length', 'children', 'distances', 'parent']
				with open(csv_path, 'w') as csvfile:
					csvwriter = csv.writer(csvfile, lineterminator='\n')
					csvwriter.writerow(fields)
					for o in order_list:
						csvwriter.writerow([o, path_dic[o]['path_length'], path_dic[o]['children'], path_dic[o]['distances'], path_dic[o]['parent']])
#					for k,v in ordered_dic.items():
#						csvwriter.writerow([k, v['path_length'], v['children'], v['distances']])
				print('Analysis Complete!')		
				
	


main()
					