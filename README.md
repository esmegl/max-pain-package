# Max pain calculator

This is a simple project to calculate max pain.

# How to use

Run `pip install -e .`

### Launch elastic:

    `docker run \
        -itd \
        --rm \
        --network=host \
        --mount type=bind,source="$(pwd)"/elastic,target=/usr/share/elasticsearch/data \
        --env "elastic_username=elastic" \
        --env "elastic_password=password" \
        --env "xpack.security.enabled=false" \
        elastic`

### Launch kibana:

    `docker run \
        -itd \
        --rm \
        --network=host \
        --env "ELASTICSEARCH_HOSTS=http://localhost:9200" \
        --env "ELASTICSEARCH_USERNAME=elastic" \
        --env "ELASTICSEARCH_PASSWORD=password" \
        docker.elastic.co/kibana/kibana:7.17.4`

- Kibana UI at: https://localhost:5601