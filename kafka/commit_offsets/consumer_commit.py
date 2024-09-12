import time
import signal
import random
import click 

from confluent_kafka import Consumer


def signal_handler(sig, frame):
    print('EXITING SAFELY!')
    exit(0)

signal.signal(signal.SIGTERM, signal_handler)

def store_data(): 
    print("Start Storing")
    time.sleep(10)
    print("End Storing")

@click.command()
@click.argument('topic')
@click.argument('group_id')
def consume(topic: str, group_id: str): 
    c = Consumer({
        'bootstrap.servers': '13.60.146.188:19093,13.60.146.188:29093,13.60.146.188:39093',
        'group.id': f"{group_id}",
        'auto.offset.reset': 'earliest',
        'security.protocol': 'SSL',
        'ssl.ca.location': './auth/ca.crt',
        'ssl.keystore.location': './auth/kafka.keystore.pkcs12',
        'ssl.keystore.password': 'cc2023',
        'enable.auto.commit': 'false',
        'ssl.endpoint.identification.algorithm': 'none',
    })

    c.subscribe(
        [topic], 
        on_assign=lambda _, p_list: print(p_list)
    )

    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        print(msg.value())
        store_data()
        c.commit(message=msg)
        print("Message committed")
        



consume()
