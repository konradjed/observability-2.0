const winston = require('winston');
const { v4: uuidv4 } = require('uuid');

// Create a custom format that outputs JSON
const jsonFormat = winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
);

// Create the logger
const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: jsonFormat,
    defaultMeta: {
        service: 'user-service',
        environment: process.env.NODE_ENV || 'development'
    },
    transports: [
        new winston.transports.Console()
    ]
});

// Add request ID to logs when used with Express
const requestLogger = (req, res, next) => {
    req.requestId = uuidv4();

    // Add request context to all logs in this request
    req.logger = logger.child({
        requestId: req.requestId,
        method: req.method,
        url: req.url
    });

    // Log the request
    req.logger.info('Request received');

    // Log response
    const originalSend = res.send;
    res.send = function(body) {
        req.logger.info('Response sent', {
            statusCode: res.statusCode,
            responseTime: Date.now() - req._startTime
        });
        return originalSend.call(this, body);
    };

    // Record start time
    req._startTime = Date.now();

    next();
};

module.exports = { logger, requestLogger };
