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


### 2. Config for training process

Edit config.json file

### 3. Training

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

	chai: 1.0000
	gói: 0.9998
	mAP: 0.9999

