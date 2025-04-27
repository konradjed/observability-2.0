package com.example.feecalculator.controller;

import com.example.feecalculator.model.PaymentFeeCalculationRequest;
import com.example.feecalculator.model.PaymentFeeResponse;
import com.example.feecalculator.service.FeeService;
import lombok.AllArgsConstructor;
import lombok.extern.java.Log;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/fee-calculator")
@AllArgsConstructor
@Slf4j
public class FeeCalculatorController {
    private final FeeService feeService;

    @PostMapping("/fee")
    public ResponseEntity<PaymentFeeResponse> getFee(@RequestBody PaymentFeeCalculationRequest request) {
        log.info("Received fee request: {}", request);
        if (request.getAmount() < 0) {
            log.warn("Rejecting negative amount: {}", request.getAmount());
            return ResponseEntity.badRequest().build();
        }
        PaymentFeeResponse resp = feeService.calculateFee(request);
        log.info("Responding with fee: {}", resp);
        return ResponseEntity.ok(resp);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handleError(Exception ex) {
        log.error("Unhandled error", ex);
        return ResponseEntity.status(500).body("Internal server error");
    }
}
