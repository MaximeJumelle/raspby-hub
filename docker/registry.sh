#!/bin/bash

# Start a custom Docker registry locally.
docker run -d -p 0.0.0.0:8129:5000 --restart=always --name registry registry:2