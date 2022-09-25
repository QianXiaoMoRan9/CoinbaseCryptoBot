from email import message
import websocket
import rel
import json
from multiprocessing import Process, Queue

QUEUE = Queue()

def on_message(ws, message):
    global QUEUE
    if message:
        QUEUE.put(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    ws.send(json.dumps({
        "type": "unsubscribe",
        "channels": [
            "matches",
            "level2_batch"
        ]
    }))
    print("### closed ###")


def on_open(ws):
    print("Opened connection")
    ws.send(
        json.dumps(
            {
                "type": "subscribe",
                "product_ids": ['BTC-USD', 'ETH-USD', 'MATIC-USD'],
                "channels": ["matches"],
            }
        )
    )

def message_consumer(queue):
    result = []
    cur = 1
    while(True):
        message = queue.get()
        if message:
            result.append(message)
            if (len(result) == 50):
                with open("./raw/{cur}.json", "w") as f:
                    f.write(json.dumps(result))
                    cur += 1
                    result = []

def start_websocket():

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws-feed.exchange.coinbase.com",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

def start_job():
    global QUEUE
    p1 = Process(target=message_consumer, args=(QUEUE,))
    p1.start()
    start_websocket()
    p1.join()

