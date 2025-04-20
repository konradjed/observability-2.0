//logger for OTEL
const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO);
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const {ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION} = require('@opentelemetry/semantic-conventions');
const { trace } = require('@opentelemetry/api');
const { PeriodicExportingMetricReader , MeterProvider} = require('@opentelemetry/sdk-metrics');
const { AlwaysOnSampler } = require('@opentelemetry/sdk-trace-base');
const { HostMetrics } = require('@opentelemetry/host-metrics');


// Create a resource that identifies your service
const resource = new Resource({
    [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'user-service',
    [ATTR_SERVICE_VERSION]: '1.0.0',
});

const traceExporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT || 'http://host.docker.internal:4318/v1/traces',
    protocol: 'http/protobuf'
});

const metricExporter = new OTLPMetricExporter({
    url: process.env.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT || 'http://host.docker.internal:4318/v1/metrics',
    protocol: 'http/protobuf'
});

const metricReader = new PeriodicExportingMetricReader({
    exporter: metricExporter,
    intervalMillis: 15000,
})

const meterProvider = new MeterProvider({
    resource: resource,
    readers: [metricReader],
});

const hostMetrics = new HostMetrics({ meterProvider: meterProvider , name: "user-service"});
hostMetrics.start();

// Configure the OpenTelemetry SDK
const sdk = new NodeSDK({
    sampler: new AlwaysOnSampler(),
    resource,
    traceExporter,
    metricReader: new PeriodicExportingMetricReader({
        exporter: metricExporter,
        intervalMillis: 15000,
    }),
    instrumentations: [
        getNodeAutoInstrumentations(),
    ],
});

// Start the SDK
sdk.start();

// Export the trace API for use in application code
module.exports = { trace };

// Ensure proper shutdown on SIGTERM
process.on('SIGTERM', () => {
    sdk.shutdown()
        .then(() => console.log('OpenTelemetry SDK shut down successfully'))
        .catch((error) => console.log('Error shutting down OpenTelemetry SDK', error))
        .finally(() => process.exit(0));
});