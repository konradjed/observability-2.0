require('./opentelemetry-instrumentation');
const express = require('express');
const { logger, requestLogger, createCustomSpan } = require('./logger');

const app = express();
const port = process.env.PORT || 3000;
const router = express.Router();

app.use(requestLogger);

router.get('/error', (req, res) => {
    req.logger.info('Processing error route');
    try {
        // Simulated error for demonstration
        throw new Error('This is a test error');
    } catch (error) {
        req.logger.error('An error occurred', { error });
        res.status(500).send('{"code":"500","message":"Something went wrong!"}');
    }
});

router.get('/users/:id', (req, res) => {
    const userId = req.params.id;
    req.logger.info('Fetching user data', { userId });

    // Create a custom span for a simulated database query operation
    createCustomSpan('database.query', async (span) => {
        span.setAttribute('db.operation', 'findUser');
        span.setAttribute('db.user_id', userId);
        await new Promise(resolve => setTimeout(resolve, 150));

        if (userId === '999') {
            req.logger.warn('User not found', { userId });
            return res.status(404).send('{"code":"404","message":"User not found"}');
        }

        const user = { id: userId, name: 'Test User', email: 'test@example.com' };
        req.logger.info('User data retrieved successfully', { userId });
        res.json(user);
    });
});

app.use(router)

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