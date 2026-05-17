#!/bin/bash
aws ecs update-service \
    --cluster wuduh-cluster \
    --service wuduh-service \
    --desired-count 0 \
    --region us-east-1 > /dev/null

echo "Wuduh stopped — no longer charging"