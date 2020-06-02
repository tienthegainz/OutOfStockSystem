# Object Detection

Object detection for shop products - Phase 1, Jan-April/2020

## Todo list:
- [x] Traing on 24 classes
- [x] mAP Evaluation
- [x] Code for prediction on single image
- [x] Code for prediction on a images folder
- [x] Code to generate predicted result to pascal voc format (for upload annotation to cvat)
- [ ] Error analysis on validation, new external dataset
- [ ] Improve model to reduce false positive rate

## Install dependencies

```
pip install -r requirements.txt
```

## Training instruction

### 1.Dataset preparation

Download dataset from CVAT in PASCAL VOC format and  split into training and validation subset by a pre-defined ratio.

Organize training and validation subset into 4 folders:

+ train_image: the folder that contains the train images.

+ train_xml: the folder that contains the train annotations in VOC format.

+ val_image:  the folder that contains the validation images.

+ val_xml: the folder that contatins the validation annotations in VOC format

Splited and organized dataset can be download here: https://drive.google.com/open?id=1GBajAY1acVq93SffboL9Wqranv3Ubl7p

### 2. Config for training process

Edit config.json file

### 3. Download pretrained weights

Download pretrained weights here: https://drive.google.com/file/d/14F_5mvXE-5sX4sG5EwThVydukp-lljXm/view?usp=sharing

### 4. Training

Run: 
```
python3 train.py -c config.json
```
## Evaluate on validation set (MAP)

- Edit paths of validation images and annotations folder in config.json file

- Download trained weights here: https://drive.google.com/file/d/1tTrcksW8LuKJ5vxyQ9tlj1O9cl3hNFb5/view?usp=sharing

- Run: 
```
python3 evaluate.py -c config.json
```
## Predict

### 1. Predict on single image

Run: 
```
python3 detect.py -i input_path -o output_path
```
Note: input_path is path to image you want to predict, output_path is path of folder to save result

### 2. Predict on a folder of images

Run:
```
python3 detect.py -i input_path -o output_path
```
Note: input_path is path to images folder you want to predict, output_path is path os folder to save result

### 3. Predict and generate data to pascal voc format (Use for uploading annotation to cvat)

Run:
```
python3 detect.py -i input_path -o output_path -d True
```
Note: input_path is path to images folder you want to predict, output_path is path os folder to save result.

## Statistic Result:

	On validation set, result acquired: 
	balo: 0.9706
	balo_diutre: 0.8207
	bantreem: 0.8707
	binh_sua: 0.8527
	cautruot: 1.0000
	coc_sua: 0.8517
	ghe_an: 0.9794
	ghe_bap_benh: 0.8333
	ghe_ngoi_oto: 0.8977
	ghedualung_treem: 0.8925
	ke: 0.8090
	noi: 0.9598
	person: 0.7243
	phao: 0.9365
	quay_cui: 1.0000
	tham: 0.8921
	thanh_chan_cau_thang: 0.9706
	thanh_chan_giuong: 0.9913
	xe_babanh: 0.9211
	xe_choichan: 0.9530
	xe_day: 0.8852
	xe_tapdi: 0.9091
	xichdu: 0.8462
	yem: 0.7337
	mAP: 0.8959

	On ghe_an_800 datset, result acquired:
	thanh_chan_cau_thang: 1.0000
	ghedualung_treem: 0.9788
	ghe_an: 0.9628
	cautruot: 0.9619
	quay_cui: 0.9500
	xe_choichan: 0.9167
	balo_diutre: 0.8969
	tham: 0.8969
	person: 0.8870
	binh_sua: 0.8708
	xe_day: 0.8698
	xe_tapdi: 0.8619
	ke: 0.8383
	bantreem: 0.8190
	coc_sua: 0.7745
	ghe_ngoi_oto: 0.7414
	xe_babanh: 0.7388
	thanh_chan_giuong: 0.6997
	yem: 0.6905
	balo: 0.6141
	noi: 0.5897
	xichdu: 0.5714
	phao: 0.5412
	ghe_bap_benh: 0.2222
	mAP: 0.7873


