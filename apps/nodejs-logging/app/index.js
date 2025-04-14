const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');

// For troubleshooting, set the log level to DiagLogLevel.DEBUG
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);

// Initialize OpenTelemetry (EDOT style) – must come first!
require('./opentelemetry-instrumentation');

const express = require('express');
const { logger, requestLogger, createCustomSpan } = require('./logger');
// const { registerMetrics } = require('./metrics');

const app = express();
const port = process.env.PORT || 3000;

// Register custom metrics (instrumentation for EDOT observability)
// const metrics = registerMetrics();

// Use the request logger middleware (logs now include trace identifiers)
app.use(requestLogger);

// Basic routes to demonstrate distributed tracing
app.get('/', (req, res) => {
    req.logger.info('Processing home route');
    res.send('{"code":"200","message":"Hello World!"}');
});

app.get('/slow', async (req, res) => {
    req.logger.info('Processing slow route');

    // Create a custom span to simulate a slow operation
    await createCustomSpan('slow.operation', async (span) => {
        span.setAttribute('operation.type', 'delay');
        req.logger.debug('Starting slow operation');
        await new Promise(resolve => setTimeout(resolve, 500));
        req.logger.debug('Finished slow operation');
    });

    res.send('{"code":"200","message":"This was a slow response"}');
});

app.get('/error', (req, res) => {
    req.logger.info('Processing error route');
    try {
        // Simulated error for demonstration
        throw new Error('This is a test error');
    } catch (error) {
        req.logger.error('An error occurred', { error });
        res.status(500).send('{"code":"500","message":"Something went wrong!"}');
    }
});

app.get('/users/:id', (req, res) => {
    const userId = req.params.id;
    req.logger.info('Fetching user data', { userId });

    // Create a custom span for a simulated database query operation
    createCustomSpan('database.query', async (span) => {
        span.setAttribute('db.operation', 'findUser');
        span.setAttribute('db.user_id', userId);
        await new Promise(resolve => setTimeout(resolve, 1000));

        if (userId === '999') {
            req.logger.warn('User not found', { userId });
            return res.status(404).send('{"code":"404","message":"User not found"}');
        }

        const user = { id: userId, name: 'Test User', email: 'test@example.com' };
        req.logger.info('User data retrieved successfully', { userId });
        res.json(user);
    });
});

// Start the server
app.listen(port, () => {
    logger.info(`Server started on port ${port}`, { port });
});

// Global error handlers for uncaught exceptions or unhandled promise rejections
process.on('uncaughtException', (error) => {
    logger.error('Uncaught exception', { error });
    process.exit(1);
});
process.on('unhandledRejection', (reason) => {
    logger.error('Unhandled promise rejection', { reason });
});