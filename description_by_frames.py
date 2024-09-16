import os

from PIL import Image

from transformers import AutoTokenizer, AutoProcessor, AutoModel, AutoConfig
from decord import VideoReader, cpu    # pip install decord
import torch

from time_reporter import TimeReporter
from google_spreadsheet import GoogleSpreadsheetsService

model_path = 'mPLUG/mPLUG-Owl3-7B-240728'
config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
print(config)
# model = mPLUGOwl3Model(config).cuda().half()
model =  AutoModel.from_pretrained(model_path, attn_implementation='sdpa', torch_dtype=torch.half, trust_remote_code=True)
model.eval().cuda().half()
tokenizer = AutoTokenizer.from_pretrained(model_path)
processor = model.init_processor(tokenizer)

path_of_images = 'scenedetect_jpgs/segment_3-Scene-'
service = GoogleSpreadsheetsService('')
reporter = TimeReporter()
spreadsheet_id = os.environ.get('SPREADSHEET_ID', '19ywXrqNZciW3kr57fD4_Y7Dey1uLGCYVVoGDbytllj8')
title = os.environ.get('TITLE', 'cleaned_scenes')
column = os.environ.get('COLUMN', 17)

for i in range(1, 253):
    messages = [
    {"role": "user",
     "content": """<|image|> <|image|> <|image|> Describe this movie scene based on these three images (beginning, middle, and end of the scene)."""},
    {"role": "assistant",
     "content": ""}
]
    number_of_scene = '0' * (3 - len(str(i))) + str(i) + '-'
    image1 = Image.open(path_of_images + number_of_scene + '01.jpg')
    image2 = Image.open(path_of_images + number_of_scene + '02.jpg')
    image3 = Image.open(path_of_images + number_of_scene + '03.jpg')
    inputs = processor(messages, images=[image1, image2, image3], videos=None)

    inputs.to('cuda')
    inputs.update({
    'tokenizer': tokenizer,
    'max_new_tokens':100,
    'decode_text':True,
})


    g = model.generate(**inputs)
    reporter.report_time('Description for ' + str(i))
    service.update_value(spreadsheet_id, title, i + 1, column, str(g))
    print(g)
 print(reporter.get_report())