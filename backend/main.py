# main.py

import logging
import socket

from auth_router import router as auth_router
from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logging_config import configure_logging
from prometheus_fastapi_instrumentator import Instrumentator
from rag.rag_router import router as rag_router

LOGSTASH_HOST = "logstash"  # docker service name
LOGSTASH_PORT = 5000  # matches your logstash udp input
# Configure logging (console + Logstash)
configure_logging()


class UDPLogHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

    def emit(self, record):
        msg = self.format(record)
        self.sock.sendto(msg.encode(), (self.host, self.port))


logger = logging.getLogger()
logger.setLevel(logging.INFO)

udp_handler = UDPLogHandler(LOGSTASH_HOST, LOGSTASH_PORT)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
udp_handler.setFormatter(formatter)

logger.addHandler(udp_handler)
logger.info("✅ FASTAPI CONNECTED TO LOGSTASH")


# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knowledge Assistant API")

# ⭐ Correct CORS setup
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,  # ❗ NOT CORS_MIDDLEWARE :=
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router, prefix="/auth")
app.include_router(rag_router, prefix="/rag")

Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)


@app.get("/")
def root():
    return {"message": "Knowledge Assistant Backend Running 🚀"}
