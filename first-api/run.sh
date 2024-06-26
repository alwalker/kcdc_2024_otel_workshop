opentelemetry-instrument \
    --traces_exporter otlp \
    --metrics_exporter otlp \
    --logs_exporter otlp \
    --service_name hello-server \
    --resource_attributes "var1=one,var2=two" \
    fastapi run --port 8080 main.py