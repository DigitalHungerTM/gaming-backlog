#!/usr/bin/env bash

# requires curl, protoc, protobuf-devel

cd igdb/proto
curl https://api.igdb.com/v4/igdbapi.proto --remote-name
protoc --python_out=. igdbapi.proto
