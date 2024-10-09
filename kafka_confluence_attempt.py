#%%
from activity_tracker_class import ActivityTracker
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
import boto3


#%% Define your AWS MSK cluster bootstrap servers
bootstrap_servers = 'b-1.democluster.t44ymf.c4.kafka.eu-west-2.amazonaws.com:9096,b-2.democluster.t44ymf.c4.kafka.eu-west-2.amazonaws.com:9096,b-3.democluster.t44ymf.c4.kafka.eu-west-2.amazonaws.com:9096'

#%% Token provider for IAM authentication
class MSKTokenProvider:
    def token(self):
        token, _ = MSKAuthTokenProvider.generate_auth_token('eu-west-2')
        return token

# Fetch SASL/SCRAM credentials from AWS Secrets Manager
def get_sasl_scram_credentials(secret_name, region_name):
    client = boto3.client('secretsmanager', region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    secrets = eval(response['SecretString'])  # Assumes the secret is stored as a dict
    return secrets['username'], secrets['password']

#%% Configuration for both the AdminClient and Producer using SASL/SCRAM
def get_kafka_conf():
    # Retrieve username and password from Secrets Manager
    username, password = get_sasl_scram_credentials('AmazonMSK_attempt2', 'eu-west-2')
    
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'SCRAM-SHA-512',  # or 'SCRAM-SHA-256'
        'sasl.username': username,
        'sasl.password': password,
    }
    
    return conf

#%% Create a topic using AdminClient
def create_topic(topic_name):
    conf = get_kafka_conf()
    admin_client = AdminClient(conf)

    new_topic = NewTopic(
        topic=topic_name,
        num_partitions=1,  # Number of partitions
        replication_factor=2  # Replication factor (must be <= number of brokers)
    )

    # Attempt to create the topic
    try:
        admin_client.create_topics([new_topic])
        print(f"Topic '{topic_name}' created successfully")
    except Exception as e:
        print(f"Failed to create topic: {e}")

#%% Send a message to a topic using Producer
def send_message(topic_name, key, value):
    conf = get_kafka_conf()
    producer = Producer(conf)

    # Produce a message to the topic
    producer.produce(topic=topic_name, key=key, value=value)
    producer.flush()  # Ensure message is sent

    print(f"Message sent to topic '{topic_name}'")

# Example usage
if __name__ == "__main__":
    topic_name = "my_new_topic"

    # Create a topic
    create_topic(topic_name)

    # Send a sample message to the newly created topic
    send_message(topic_name, key="test_key", value="Hello, Kafka!")
#%%
