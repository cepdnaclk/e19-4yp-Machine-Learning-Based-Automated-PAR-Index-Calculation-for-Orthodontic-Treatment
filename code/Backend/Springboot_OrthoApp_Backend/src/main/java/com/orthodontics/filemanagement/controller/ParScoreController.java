package com.orthodontics.filemanagement.controller;

import com.orthodontics.filemanagement.dto.ParCalculationRequest;
import com.orthodontics.filemanagement.dto.ParScoreResponse;
import com.orthodontics.filemanagement.service.ParScoreService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;

@RestController
@RequestMapping("/api/par-score")
@RequiredArgsConstructor
public class ParScoreController {

    private final ParScoreService parScoreService;

    @CrossOrigin
    @PostMapping("/calculate/{patientId}")
    public ResponseEntity<?> calculateParScore(@PathVariable Long patientId) { // Changed to ResponseEntity<?>
        try {
            ParScoreResponse response = parScoreService.calculateParScoreForPatient(patientId);
            return ResponseEntity.ok(response);
        } catch (IllegalStateException e) {
            // If a duplicate key error occurs, catch it and return a clean error message
            String errorMessage = "Calculation failed due to duplicate point names. " + e.getMessage();
            return ResponseEntity
                    .status(HttpStatus.BAD_REQUEST) // Send a 400 Bad Request status
                    .body(errorMessage);
        }
    }
}