python -m grpc_tools.protoc \
  -Isrc \
  --python_out=src \
  --grpc_python_out=src \
  src/v1/encrypt_request.proto \
  src/v1/encrypt_response.proto \
  src/v1/cryptor_service.proto

