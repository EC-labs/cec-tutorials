import signal
import click 

from confluent_kafka import Consumer


def signal_handler(sig, frame):
    print('EXITING SAFELY!')
    exit(0)

signal.signal(signal.SIGTERM, signal_handler)

@click.command()
@click.argument('topic')
@click.argument('consumer_group')
def consume(topic: str, consumer_group: str): 
    c = Consumer({
        'bootstrap.servers': 'kafka.cec.dlandau.nl:19092,kafka.cec.dlandau.nl:29092,kafka.cec.dlandau.nl:39092',
        'group.id': consumer_group,
        'auto.offset.reset': 'latest',
        'security.protocol': 'SSL',
        'ssl.ca.location': './auth/ca.crt',
        'ssl.keystore.location': './auth/kafka.keystore.pkcs12',
        'ssl.keystore.password': 'cc2023',
        'enable.auto.commit': 'true',
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

consume()
