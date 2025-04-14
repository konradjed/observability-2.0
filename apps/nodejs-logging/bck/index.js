'use strict';

const express = require('express');
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { OTLPTraceExporter, OTLPMetricExporter } = require('@opentelemetry/exporter-otlp-http');
// Auto instrumentation for Node.js – this includes Express instrumentation among others.
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

// -----------------------------------------------------------------------------
// Configure OTLP Exporters (Traces & Metrics)
// -----------------------------------------------------------------------------
// Replace these URLs with the endpoints exposed by your OpenTelemetry Collector or
// Elastic APM Server’s OTLP receiver.
const traceExporter = new OTLPTraceExporter({
    url: 'http://host.docker.internal:8200/v1/traces',
    headers: {'Authorization': 'ApiKey Z2hsNUpKWUJQT1VmUnR0OF9BeHU6bDBlWElkOTNRNWEzQmZHclRwbG9ndw=='},
});

const metricExporter = new OTLPMetricExporter({
    url: 'http://host.docker.internal:8200/v1/metrics',
    headers: {'Authorization': 'ApiKey Z2hsNUpKWUJQT1VmUnR0OF9BeHU6bDBlWElkOTNRNWEzQmZHclRwbG9ndw=='},
});

// -----------------------------------------------------------------------------
// Initialize OpenTelemetry SDK with auto instrumentation and OTLP exporters
// -----------------------------------------------------------------------------
const sdk = new NodeSDK({
    traceExporter,
    metricReader: new PeriodicExportingMetricReader({
        exporter: metricExporter,
        exportIntervalMillis: 10000, // Export metrics every 10 seconds
    }),
    instrumentations: [getNodeAutoInstrumentations()],
});

// Start the OpenTelemetry SDK.
sdk.start();

// -----------------------------------------------------------------------------
// Setup Express Application
// -----------------------------------------------------------------------------
const app = express();

app.get('/', (req, res) => {
    res.send('Hello, OpenTelemetry with Express!');
});

app.get('/users/:id', (req, res) => {
    const userId = req.params.id;
    console.log('Fetching user data', { userId });

    if (userId === '999') {
        console.log('User not found', { userId });
        return res.status(404).send('{"code":"404","message":"User not found"}');
    }

    const user = { id: userId, name: 'Test User', email: 'test@example.com' };
    console.log('User data retrieved successfully', { userId });
    res.json(user);
});

// Start the Express server.
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Express server listening on port ${PORT}`);
});

// -----------------------------------------------------------------------------
// Graceful Shutdown: Ensure the SDK flushes before exit
// -----------------------------------------------------------------------------
process.on('SIGTERM', () => {
    sdk.shutdown()
        .then(() => {
            console.log('OpenTelemetry SDK shut down');
            process.exit(0);
        })
        .catch((error) => {
            console.error('Error shutting down SDK', error);
            process.exit(1);
        });
});