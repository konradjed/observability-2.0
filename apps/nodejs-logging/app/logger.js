const winston = require('winston');
const { v4: uuidv4 } = require('uuid');
const { trace, context, ROOT_CONTEXT, SpanStatusCode } = require('@opentelemetry/api');

// Create a custom format that outputs JSON
const jsonFormat = winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    // Add OpenTelemetry trace context to logs
    winston.format((info) => {
        const activeSpan = trace.getActiveSpan();
        if (activeSpan) {
            const spanContext = activeSpan.spanContext();
            info.traceId = spanContext.traceId;
            info.spanId = spanContext.spanId;
        }
        return info;
    })(),
    winston.format.json()
);

// Create the logger
const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: jsonFormat,
    defaultMeta: {
        "service.name": 'user-service',
        environment: process.env.NODE_ENV || 'development'
    },
    transports: [
        new winston.transports.Console()
    ]
});

// Add request ID and OpenTelemetry context to logs when used with Express
const requestLogger = (req, res, next) => {
    req.requestId = uuidv4();

    // The span should already be created by OpenTelemetry Express instrumentation
    // But we can get it and add custom attributes
    const currentSpan = trace.getActiveSpan();
    if (currentSpan) {
        currentSpan.setAttribute('request.id', req.requestId);
    }

    // Add request context to all logs in this request
    req.logger = logger.child({
        requestId: req.requestId,
        method: req.method,
        url: req.url
    });

    // Log the request
    req.logger.info('Request received');

    // Record start time
    req._startTime = Date.now();

    // Log response
    const originalSend = res.send;
    res.send = function(body) {
        const responseTime = Date.now() - req._startTime;

        if (currentSpan) {
            currentSpan.setAttribute('response.time_ms', responseTime);

            // Set span status based on HTTP status code
            if (res.statusCode >= 400) {
                currentSpan.setStatus({
                    code: SpanStatusCode.ERROR,
                    message: `Error response: ${res.statusCode}`
                });
            }
        }

        req.logger.info('Response sent', {
            statusCode: res.statusCode,
            responseTime
        });

        return originalSend.call(this, body);
    };

    next();
};

// Synchronous sleep function (blocks the event loop)
function sleepSync(ms) {
    const endTime = Date.now() + ms;
    while (Date.now() < endTime) {
        // Busy wait – not recommended for production code!
    }
}

// Synchronous custom span creator
function createCustomSpanSync(spanName, fn) {
    const tracer = trace.getTracer('default');
    const span = tracer.startSpan(spanName);
    try {
        fn(span);
    } catch (err) {
        span.recordException(err);
        throw err;
    } finally {
        span.end();
    }
}

// Helper to create a custom span
const createCustomSpan = (name, fn, parentSpan = null) => {
    const tracer = trace.getTracer('express-otel-example');

    let ctx = ROOT_CONTEXT;
    if (parentSpan) {
        ctx = trace.setSpan(ctx, parentSpan);
    }

    return context.with(ctx, () => {
        return tracer.startActiveSpan(name, async (span) => {
            try {
                const result = await fn(span);
                span.end();
                return result;
            } catch (error) {
                span.setStatus({
                    code: SpanStatusCode.ERROR,
                    message: error.message
                });
                span.recordException(error);
                span.end();
                throw error;
            }
        });
    });
};

module.exports = { logger, requestLogger, createCustomSpan };
