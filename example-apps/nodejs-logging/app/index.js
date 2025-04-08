const express = require('express');
const { logger, requestLogger } = require('./logger');

const app = express();
const port = process.env.PORT || 3000;

// Use the request logger middleware
app.use(requestLogger);

// Add basic routes
app.get('/', (req, res) => {
    req.logger.info('Processing home route');
    res.send('{"code":"500","message":"Hello World!"}');
});

app.get('/error', (req, res) => {
    try {
        // Simulate an error - demonstration purpose
        // noinspection ExceptionCaughtLocallyJS
        throw new Error('This is a test error');
    } catch (error) {
        req.logger.error('An error occurred', { error });
        res.status(500).send('{"code":"500","message":"Something went wrong!"}');
    }
});

app.get('/users/:id', (req, res) => {
    const userId = req.params.id;
    req.logger.info('Fetching user data', { userId });

    // Simulate database lookup
    setTimeout(() => {
        if (userId === '999') {
            req.logger.warn('User not found', { userId });
            return res.status(404).send('{"code":"404","message":"User not found"}');
        }

        const user = { id: userId, name: 'Test User', email: 'test@example.com' };
        req.logger.info('User data retrieved successfully', { userId });
        res.json(user);
    }, 100);
});

// Start the server
app.listen(port, () => {
    logger.info(`Server started on port ${port}`, { port });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    logger.error('Uncaught exception', { error });
    process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason) => {
    logger.error('Unhandled promise rejection', { reason });
});
