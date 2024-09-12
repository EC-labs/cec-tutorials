import click

from confluent_kafka import Producer


p = Producer({
    'bootstrap.servers': '13.60.146.188:19093,13.60.146.188:29093,13.60.146.188:39093',
    'security.protocol': 'SSL',
    'ssl.ca.location': './auth/ca.crt',
    'ssl.keystore.location': './auth/kafka.keystore.pkcs12',
    'ssl.keystore.password': 'cc2023',
    'ssl.endpoint.identification.algorithm': 'none',
})

@click.command()
@click.argument('topic')
def produce(topic: str): 
    i = 0
    while True: 
        message = input()
        p.produce(topic, key=f"{i}", value=message.encode('utf-8'))
        p.flush()
        i+=1

produce()
