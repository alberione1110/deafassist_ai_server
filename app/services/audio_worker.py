import queue
import threading

from kws_doa.mic_stream import MicStream
from kws_doa.KwsDoa import AudioPipeline
from app.services.result_formatter import (
    build_error_message,
    build_inference_message,
)

def audio_worker(result_queue: queue.Queue, stop_event: threading.Event):
    pipeline = AudioPipeline()
    mic = MicStream()

    try:
        for chunk in mic.stream():
            if stop_event.is_set():
                break

            try:
                result = pipeline.process_chunk(chunk)
                if result is not None:
                    result_queue.put(build_inference_message(result))
            except Exception as e:
                result_queue.put(build_error_message(f"pipeline error: {e}"))

    except Exception as e:
        result_queue.put(build_error_message(f"mic stream error: {e}"))
