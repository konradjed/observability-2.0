# Observability 2.0 with ELK Stack Logging

This project demonstrates how to set up a Observability 2.0 with structured logging that gets collected by Filebeat and sent to Elasticsearch for analysis in Kibana.

## Features

- Node.js Express application with structured JSON logging
  - Winston logger with request context tracking
- Docker Compose setup with ELK stack
- fluent-bit configured to collect Docker logs
  - Log parsing to extract structured data

## Getting Started

1. Clone this repository
2. Run the stack with Docker Compose:
    ```shell
    docker-compose up -d
    ```
3. Access the application at http://localhost:3000
4. View logs in Kibana at http://localhost:5601

## Available Routes on Node.js example Application

- `GET /` - Simple hello world response
- `GET /error` - Triggers an error to demonstrate error logging
- `GET /users/:id` - Simulates a user lookup (use ID 999 to see a 404 response)

## Log Exploration in Kibana

1. Open Kibana at http://localhost:5601
2. Go to Stack Management > Index Patterns
3. Create an index pattern for `docker-*`
4. Go to Discover to explore your logs
5. Create visualizations based on log data

## Notes

- The security for Elasticsearch is disabled for demonstration
- fluent-bit is configured to parse JSON logs from any application
- Winston is configured to output structured JSON logs

# TODO

- [ ] OpenTelemetry on Node.js APP
- [ ] Python App Example
- [ ] Java App Example
- [ ] Trace Exploration
- [ ] Example of event storage and correlation with OpenTelemetry
- [ ] Export metrics
- [ ] Create example dashboard for metrics
