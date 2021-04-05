docker pull tensorflow/serving
MODEL_NAME=use_model
MODEL_PATH=serving_models/
DOCKER_PATH=/models/use_model
# docker run -p 8038:8501 — mount type=bind,source=${MODEL_PATH},target=${MODEL_PATH} -e MODEL_NAME=${MODEL_NAME} -t tensorflow/serving
docker run -t -d --rm -p  8510:8501 -p 8511:8500 \
    -v "$(pwd)/$MODEL_PATH:/models/" \
    --name tf_custom_serving \
    tensorflow/serving \
    --model_config_file=/models/models.config \
    --model_config_file_poll_wait_seconds=60 \
    --tensorflow_intra_op_parallelism=4 \
    --tensorflow_inter_op_parallelism=4
