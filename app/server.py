from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO

from os import listdir
import uuid
import shutil

from fastai import *
from fastai.vision import *


export_file_url = 'https://www.dropbox.com/s/tmzpoo5pz7fwa0b/export.pkl?raw=1'
export_file_name = 'export.pkl'

classes = ['janusz', 'mitia', 'niekot', 'zbychu']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner():
    await download_file(export_file_url, path/export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    file_name = data['name'].replace('_', '')
    img = open_image(BytesIO(img_bytes))

    prediction = learn.predict(img)

    label = str(prediction[0])

    print(prediction)
    # print(file_name)

    randname = str(uuid.uuid4())

    # randext = '.jpg'

    fn = label + '_' + randname + file_name

    image_path = path/'images'/fn
    
    print(image_path)

    img.save(image_path)

    # print(listdir(path/'images'))

    

    return JSONResponse({'result': label,
                         'confidences': str(prediction[2])})


@app.route('/uploads')
def uploads(request):
    archive_path = shutil.make_archive(path/'uploads', 'zip', path/'images')
    print(archive_path)

    response = FileResponse(archive_path, media_type='application/zip')
    return response




if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042)
