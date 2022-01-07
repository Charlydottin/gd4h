from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from argostranslate import package, translate
AVAILABLE_LANG = ["fr","en"]
SWITCH_LANGS = dict(zip(AVAILABLE_LANG,AVAILABLE_LANG[::-1]))
installed_languages = translate.get_installed_languages()
fr_en = installed_languages[1].get_translation(installed_languages[0])
en_fr = installed_languages[0].get_translation(installed_languages[1])


router = APIRouter()

def translate(text, _from="fr"):
    if _from == "fr":
        return fr_en.translate(text)
    else:
        return en_fr.translate(text)

@router.post('/from={lang}',response_class=Response)
async def translation(data: Request, lang):
    data_b = await data.body()
    result = translate(data_b, lang)
    return JSONResponse(result)

# @router.post("/{lang}")
# async def translate_text_from(request: Request, lang, text: str = Body(...)):
#     return jsonable_encoder(text)
#     # return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder({lang:text}))
    