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
            info.parentSpanId = activeSpan ? activeSpan.parentSpanId : 'unknown-parent-span-id';
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

module.exports = { logger, requestLogger };
