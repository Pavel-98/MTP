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

messages = [
    {"role": "user",
     "content": """Video. <|video|> Describe this movie scene."""},
    {"role": "assistant",
     "content": ""}
]

MAX_NUM_FRAMES=16

def encode_video(video_path):
    def uniform_sample(l, n):
        gap = len(l) / n
        idxs = [int(i * gap + gap / 2) for i in range(n)]
        return [l[i] for i in idxs]

    vr = VideoReader(video_path, ctx=cpu(0))
    sample_fps = round(vr.get_avg_fps() / 1)  # FPS
    frame_idx = [i for i in range(0, len(vr), sample_fps)]
    if len(frame_idx) > MAX_NUM_FRAMES:
        frame_idx = uniform_sample(frame_idx, MAX_NUM_FRAMES)
    frames = vr.get_batch(frame_idx).asnumpy()
    frames = [Image.fromarray(v.astype('uint8')) for v in frames]
    print('num frames:', len(frames))
    return frames

service = GoogleSpreadsheetsService('token.json')
reporter = TimeReporter()
spreadsheet_id = os.environ.get('SPREADSHEET_ID', '19ywXrqNZciW3kr57fD4_Y7Dey1uLGCYVVoGDbytllj8')
title = os.environ.get('TITLE', 'cleaned_scenes')
column = os.environ.get('COLUMN', 16)
for i in range(1, 253):
    video_file_number = "0" * (3 - len(str(i))) + str(i)
    videos = ['/content/scenedect_videos/segment_3-Scene-' + video_file_number + '.mp4']


    video_frames = [encode_video(_) for _ in videos]

    inputs = processor(messages, images=None, videos=video_frames)
    inputs.to('cuda')
    inputs.update({
    'tokenizer': tokenizer,
    'max_new_tokens':1000,
    'decode_text':True,
})


    g = model.generate(**inputs)
    reporter.report_time('Description for ' + str(1))
    print(g)
    service.update_value(spreadsheet_id, title, i + 1, column, str(g))
    messages = [
    {"role": "user",
     "content": """Video. <|video|> Describe this movie scene."""},
    {"role": "assistant",
     "content": ""}
]
print(reporter.get_report())