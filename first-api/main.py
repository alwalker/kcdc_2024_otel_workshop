from fastapi import FastAPI, Request
from opentelemetry import trace, propagators, baggage, metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
import requests

tracer = trace.get_tracer("hello-server.tracer")
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/queries")
async def root(request: Request, surname: str = "", firstname: str = ""):
    # with tracer.start_as_current_span("hello-server") as span:
    span = trace.get_current_span()
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