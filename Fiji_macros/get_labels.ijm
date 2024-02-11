for (i=1;i<=nSlices;i++) {
	setSlice(i);
	print(i, getInfo("slice.label"));
}