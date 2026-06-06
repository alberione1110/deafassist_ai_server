import asyncio
import queue
import threading

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.audio_worker import audio_worker

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    await websocket.send_json({
        "type": "status",
        "message": "connected",
    })

    result_queue = queue.Queue()
    stop_event = threading.Event()
    worker_thread = None

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=0.05,
                )

                if data.get("type") == "start":
                    if worker_thread is None or not worker_thread.is_alive():
                        stop_event.clear()
                        worker_thread = threading.Thread(
                            target=audio_worker,
                            args=(result_queue, stop_event),
                            daemon=True,
                        )
                        worker_thread.start()

                    await websocket.send_json({
                        "type": "status",
                        "message": "started",
                    })

                elif data.get("type") == "stop":
                    stop_event.set()

                    await websocket.send_json({
                        "type": "status",
                        "message": "stopped",
                    })

            except asyncio.TimeoutError:
                pass

            while not result_queue.empty():
                await websocket.send_json(result_queue.get())

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        pass

    finally:
        stop_event.set()
