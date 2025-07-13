python -m grpc_tools.protoc \
  -Iv1 \
  --python_out=v1 \
  --grpc_python_out=v1 \
  v1/encrypt_request.proto \
  v1/encrypt_response.proto \
  v1/cryptor_service.proto
