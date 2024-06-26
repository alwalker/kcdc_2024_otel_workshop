from fastapi import FastAPI, Request
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace, propagators, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

app = FastAPI()

resource = Resource(attributes={
    SERVICE_NAME: "hello-server",
    "VAR1": "one",
    "VAR2": "two"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

tracer = trace.get_tracer(__name__)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter()
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/queries")
async def root(request: Request, surname: str = "", firstname: str = ""):
    with tracer.start_as_current_span("hello-server") as span:
        ctx = baggage.set_baggage("og-agent", request.headers["User-Agent"])
        # baggage.set_baggage("og-agent", request.headers["User-Agent"], ctx)
        headers = {}
        W3CBaggagePropagator().inject(headers, ctx)
        TraceContextTextMapPropagator().inject(headers, ctx)
        print(headers)

        result = requests.get("http://localhost:8082/random", headers=headers).text
        span.set_attribute("firstname", firstname)
        span.set_attribute("surname", surname)
        span.set_attribute("age", result)
        return {"message": "Hello " + firstname + " " + surname + ". You are " + result + " years old"}