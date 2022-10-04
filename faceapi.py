#!/usr/bin/env python
# coding: utf-8


import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
import tempfile
import csv
import json
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

"""
#csv読み込み（jpgデータ）
with open("data_source.csv", "r", newline="", encoding="utf8") as f:
    reader = csv.reader(f)
    data = [row for row in reader]

data.remove(data[0])
for i in range(len(data)):
    data[i].remove(data[i][0])
    data[i].remove(data[i][0])
"""

# Create an authenticated FaceClient.
face_client = FaceClient("https://avactr-faceapi.cognitiveservices.azure.com/", CognitiveServicesCredentials("a550fdc1428f4468a0b9bc87d315230c"))



#グループ作成

ACTRESS_GROUP_ID = 'my-actress-group'

TARGET_PERSON_GROUP_ID = str(uuid.uuid4())

#print('Actress group:', ACTRESS_GROUP_ID)
#face_client.person_group.create(person_group_id=ACTRESS_GROUP_ID, name=ACTRESS_GROUP_ID)

#スクレイピングした最新のnameをname_listに設定 100件？
name_list=[]


#個人データ作成 名簿をAPIへ登録 
"""
avact_names = []
for name in name_list:
    avact = face_client.person_group_person.create(ACTRESS_GROUP_ID, name)
    avact_names.append(avact)
avact_names
"""


#for文で個人名(avact_names)の顔にそれぞれに６つのファイル（jpg）を割り当てる
"""
for avact in avact_names:
    for i in range(1,2):
        index = avact_names.index(avact)
        with tempfile.TemporaryDirectory() as dname:               
            url = data[index][i]
            response = requests.get(url)
            d_image = response.content
            with open(os.path.join(dname, "file.jpg"), "w+b") as f:
                f.write(d_image)
                image = open(os.path.join(dname, "file.jpg"), 'r+b')
                face_client.person_group_person.add_face_from_stream(ACTRESS_GROUP_ID, avact.person_id, image)
                print("{0}番{1}の{2}枚目の顔を検出しました".format(index, name_list[index], i))
"""

"""
#トレーニング

print('Training the person group...')

face_client.person_group.train(ACTRESS_GROUP_ID)

while (True):
    training_status = face_client.person_group.get_training_status(ACTRESS_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        sys.exit('Training the person group has failed.')
    time.sleep(5)
"""


#判定関数　urlは画像url, file_nameはhogehoge.jpg


def similar_judge(url, file_name):
    with tempfile.TemporaryDirectory() as dname:
        response = requests.get(url)
        d_image = response.content
        with open(os.path.join(dname, file_name), "w+b") as f:
            f.write(d_image)
        image = open(os.path.join(dname, file_name), 'r+b')
        face_ids = []
        faces = face_client.face.detect_with_stream(image)
        for face in faces:
            face_ids.append(face.face_id)
        results = face_client.face.identify(face_ids, ACTRESS_GROUP_ID)
        if not results[0].candidates:
            print("似ている候補はいませんでした。")
        else:
            for person in results:
                conf_list = []
                for person in results:
                    conf_list.append(person.candidates[0].confidence)
                max_conf = max(conf_list)
                for person in results:
                    if person.candidates[0].confidence == max_conf:
                        max_person_id = person.candidates[0].person_id
            
                identified = face_client.person_group_person.get(ACTRESS_GROUP_ID, max_person_id)
                iden_name = identified.name
            
                print('{}の顔を検証しています'.format(os.path.basename(image.name)))
                print('{}の写真を検証した結果、[{}]さんに似ています。一致度は{}％です'.format(os.path.basename(image.name), iden_name ,max_conf))

            
                


#テスト ファイル名はfugafuga.jpg
url = input("anyone's url?")
file_name = "checkface.jpg"  
similar_judge(url,file_name)



