require('./opentelemetry-instrumentation');
const express = require('express');
const { logger, requestLogger } = require('./logger');

const app = express();
const port = process.env.PORT || 3000;
const router = express.Router();

const { Pool } = require('pg');

// Set up the PostgreSQL connection pool
const pool = new Pool({
    host: process.env.PGHOST || 'postgres',
    port: process.env.PGPORT || 5432,
    user: process.env.PGUSER || 'postgres',
    password: process.env.PGPASSWORD || 'postgres',
    database: process.env.PGDATABASE || 'testdb'
});

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

router.get('/users/:id', async (req, res) => {
    const userId = req.params.id;
    req.logger.info('Fetching user data', { userId });

    try {
        const { rows } = await pool.query(
            'SELECT id, name, email FROM users WHERE id = $1',
            [userId]
        );

        if (rows.length === 0) {
            req.logger.warn('User not found', { userId });
            return res.status(404).send('{"code":"404","message":"User not found"}');
        }

        req.logger.info('User data retrieved successfully', { userId });
        res.json(rows[0]);
    } catch (error) {
        req.logger.error('Database query failed', { error });
        res.status(500).send('{"code":"500","message":"Database error"}');
    }
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