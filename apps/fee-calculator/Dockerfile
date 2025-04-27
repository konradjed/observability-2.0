# Build stage
FROM maven:3.9.9-eclipse-temurin-23-alpine AS build

WORKDIR /app

COPY pom.xml .

COPY src ./src

RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:23-alpine
WORKDIR /app

# Copy built jar from the builder image
COPY --from=build /app/target/fee-calculator-0.0.1-SNAPSHOT.jar fee-calculator.jar

# Download the OpenTelemetry Java agent
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v2.15.0/opentelemetry-javaagent.jar /app/opentelemetry-javaagent.jar

# Run with the agent (it will auto‑collect JVM memory, GC, thread, and process CPU metrics)
ENTRYPOINT [ \
  "java", \
  "-javaagent:/app/opentelemetry-javaagent.jar", \
  "-Dotel.metrics.exporter=otlp", \
  "-Dotel.traces.exporter=otlp", \
  "-Dotel.logs.exporter=otlp", \
  "-Dotel.exporter.otlp.protocol=grpc", \
  "-Dotel.exporter.otlp.endpoint=http://host.docker.internal:4317", \
  "-Dotel.service.name=fee-calculator", \
  "-Dotel.resource.attributes=deployment.environment=local", \
  "-jar","/app/fee-calculator.jar" \
]
