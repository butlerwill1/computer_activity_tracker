#%%
from activity_tracker_class import ActivityTracker
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer
import json

region = 'eu-west-2'
#%%

act_track = ActivityTracker()
# %%
act_track.start_listeners()
# %%

class MSKTokenProvider:
    def token(self):
        token, _ = MSKAuthTokenProvider.generate_auth_token(region)
        return token

#%%
# Create an instance of MSKTokenProvider class
tp = MSKTokenProvider()

#%% Initialize KafkaAdminClient with required configurations
admin_client = KafkaAdminClient(
    bootstrap_servers=[
            'b-3.democluster.aos5us.c4.kafka.eu-west-2.amazonaws.com:9098',
            'b-1.democluster.aos5us.c4.kafka.eu-west-2.amazonaws.com:9098',
            'b-2.democluster.aos5us.c4.kafka.eu-west-2.amazonaws.com:9098'
        ],
    security_protocol='SASL_SSL',
    sasl_mechanism='OAUTHBEARER',
    sasl_oauth_token_provider=MSKTokenProvider(),
    api_version=(3,5,1),
    client_id='client1',
)
#%%
# Create a Kafka topic
topic_name = "activity"
topic_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=2)]
existing_topics = admin_client.list_topics()

if topic_name not in existing_topics:
    admin_client.create_topics(topic_list)
    print(f"Topic '{topic_name}' has been created")
else:
    print(f"Topic '{topic_name}' already exists")
#%%
# Initialize KafkaProducer
# Initialize KafkaProducer with IAM authentication
producer = KafkaProducer(
        bootstrap_servers=[
            'b-3.democluster.aos5us.c4.kafka.eu-west-2.amazonaws.com:9098',
            'b-1.democluster.aos5us.c4.kafka.eu-west-2.amazonaws.com:9098',
            'b-2.democluster.aos5us.c4.kafka.eu-west-2.amazonaws.com:9098'
        ],
        security_protocol='SASL_SSL',
        sasl_mechanism='OAUTHBEARER',
        sasl_oauth_token_provider=MSKTokenProvider(),
        api_version=(3,5,1),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

# %%
# Send a message to Kafka
producer.send('mytopic', value={'key': 'value'})
producer.flush()
# %%
