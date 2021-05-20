from jaeger_client import Config
import opentracing


def start_jaeger():
    config = Config(
        config={
            "sampler": {
                "type": "ratelimiting",
                "param": 5,
            },
        },
        service_name="hotel-v1",
        validate=True,
    )
    tracer = config.initialize_tracer()

    return {"tracer": tracer, "root": None}


def set_root_span(context, name, req):
    tracer = context["tracer"]
    span = tracer.start_span(name)
    span.set_tag(opentracing.tags.HTTP_METHOD, req.method)
    span.set_tag(opentracing.tags.HTTP_URL, req.path)

    return {"tracer": tracer, "root": span}


def start_span(name, context, parent):
    tracer = context["tracer"]
    if parent is None:
        parent = context["root"]
    span = tracer.start_span(name, child_of=parent)
    tracer.inject(span, opentracing.propagation.Format.TEXT_MAP, {})
    return span


def stop_span(span):
    span.finish()


def finish_tracer(context, status_code):
    span = context["root"]
    span.set_tag(opentracing.tags.HTTP_STATUS_CODE, status_code)
    stop_span(span)


class Jaeger:
    def __init__(self):
        self.context = start_jaeger()
        self.history = []

    def start(self, name, req=None):
        if req:
            self.context = set_root_span(self.context, name, req)
        else:
            span = start_span(
                name, self.context, self.history[-1] if len(self.history) > 0 else None
            )
            self.history.append(span)

    def stop(self, status_code=None):
        if status_code:
            finish_tracer(self.context, status_code)
        else:
            span = self.history.pop()
            stop_span(span)
