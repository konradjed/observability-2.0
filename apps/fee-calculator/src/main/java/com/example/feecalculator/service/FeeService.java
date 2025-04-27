// src/main/java/com/example/feecalculator/service/FeeService.java
package com.example.feecalculator.service;

import com.example.feecalculator.model.PaymentFeeCalculationRequest;
import com.example.feecalculator.model.PaymentFeeResponse;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.LongHistogram;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class FeeService {
    private final Tracer tracer;
    private final Meter meter;
    private final LongCounter requestCounter;
    private final LongHistogram processingTime;

    public FeeService(OpenTelemetry openTelemetry) {
        this.tracer = openTelemetry.getTracer("fee-calculator");
        this.meter = openTelemetry.getMeter("fee-calculator");
        this.requestCounter = meter.counterBuilder("fee_calculation_requests_total")
                .setDescription("Total number of fee calculation requests")
                .build();
        this.processingTime = meter.histogramBuilder("payment_processing_time_ms")
                .setDescription("Processing time in ms")
                .ofLongs()
                .build();
    }

    public PaymentFeeResponse calculateFee(PaymentFeeCalculationRequest request) {
        log.info("Starting fee calculation for {}", request);
        Span span = tracer.spanBuilder("calculateFee").startSpan();
        try (Scope scope = span.makeCurrent()) {
            requestCounter.add(1);
            long start = System.currentTimeMillis();
            double fee = request.getAmount() * 0.10;
            long duration = System.currentTimeMillis() - start;
            processingTime.record(duration);
            span.setAttribute("payment.amount", request.getAmount());
            span.setAttribute("payment.fee", fee);
            PaymentFeeResponse resp = new PaymentFeeResponse(fee);
            log.debug("Fee details: amount={} fee={} durationMs={}", request.getAmount(), fee, duration);
            log.info("Completed fee calculation: {}", resp);
            return resp;
        } finally {
            span.end();
        }
    }
}
