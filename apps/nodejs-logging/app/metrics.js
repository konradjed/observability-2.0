const { metrics } = require('@opentelemetry/api');

// Export our custom metrics registration function
function registerMetrics() {
    const meter = metrics.getMeter('express-metrics');

    // Create custom metrics
    const requestCounter = meter.createCounter('http_requests_total', {
        description: 'Total number of HTTP requests',
    });

    const requestDurationHistogram = meter.createHistogram('http_request_duration_ms', {
        description: 'HTTP request duration in milliseconds',
    });

    const activeRequestsUpDown = meter.createUpDownCounter('http_active_requests', {
        description: 'Number of active HTTP requests',
    });

    const memoryUsageObserver = meter.createObservableGauge('nodejs_memory_usage_bytes', {
        description: 'Node.js process memory usage',
    });

    // Register callback for observing memory usage
    memoryUsageObserver.addCallback((result) => {
        const memoryUsage = process.memoryUsage();
        process.cpuUsage()
        result.observe(memoryUsage.rss, { type: 'rss' });
        result.observe(memoryUsage.heapTotal, { type: 'heapTotal' });
        result.observe(memoryUsage.heapUsed, { type: 'heapUsed' });
        result.observe(memoryUsage.external, { type: 'external' });
    });

    // Return metrics for potential direct usage
    return {
        requestCounter,
        requestDurationHistogram,
        activeRequestsUpDown
    };
}

module.exports = { registerMetrics };