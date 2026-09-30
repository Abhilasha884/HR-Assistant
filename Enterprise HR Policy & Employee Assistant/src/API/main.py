from fastapi import FastAPI
from src.API.routes import router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(
    title="Enterprise HR Policy & Employee Assistant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000 ','http://127.0.0.1:5500'],
    allow_credentials=True,
    allow_methods=['GET','PUT','POST','DELETE'],
    allow_headers=['*']
)


app.include_router(router)