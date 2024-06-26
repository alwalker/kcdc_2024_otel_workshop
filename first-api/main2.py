from fastapi import FastAPI, Request
from opentelemetry import trace, baggage, metrics
from opentelemetry.sdk.metrics import MeterProvider
from random import randrange
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)

metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter("my.meter.name")
age_result_counter = meter.create_counter(
    "age.counter", unit="1", description="Counts the amount of work done"
)

tracer = trace.get_tracer("random-server.tracer")
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Random"}

@app.get("/healthcheck")
async def root():
    return 1

@app.get("/random")
async def root(request: Request, surname: str = "", firstname: str = ""):
    headers = dict(request.headers)
    print(f"Received headers: {headers}")
    carrier ={'traceparent': headers['traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
    print(f"Received context: {ctx}")

    b2 ={'baggage': headers['baggage']}
    ctx2 = W3CBaggagePropagator().extract(b2, context=ctx)
    print(f"Received context2: {ctx2}")

    span = trace.get_current_span()
    result = randrange(10)
    age_result_counter.add(1, {"age": result})
    print(baggage.get_baggage('hello', ctx2))
    span.set_attribute("random.value", result)
    span.set_attribute("random.og-agent", baggage.get_baggage('og-agent', ctx2))
    return str(result)