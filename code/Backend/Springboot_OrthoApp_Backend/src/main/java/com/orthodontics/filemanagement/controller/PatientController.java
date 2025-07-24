package com.orthodontics.filemanagement.controller;

import com.orthodontics.filemanagement.dto.PatientRegisterRequest;
import com.orthodontics.filemanagement.dto.PatientRegisterResponse;
import com.orthodontics.filemanagement.dto.PatientsResponse;
import com.orthodontics.filemanagement.dto.StlFileResponse;
import com.orthodontics.filemanagement.dto.PatientDetailResponse;
import com.orthodontics.filemanagement.service.PatientService;
import com.orthodontics.filemanagement.service.STLFileService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/patient")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService patientService;
    private final STLFileService STLFileService;

    @CrossOrigin
    @PostMapping(value = "/register", consumes = {"multipart/form-data"})
    public ResponseEntity<PatientRegisterResponse> registerPatient(@ModelAttribute PatientRegisterRequest patientRegisterRequest) throws IOException {
        Long patient_id = patientService.createPatient(patientRegisterRequest);

        STLFileService.createSTLFile(patientRegisterRequest, patient_id);

        PatientRegisterResponse response = PatientRegisterResponse.builder()
                .patient_id(patient_id)
                .build();

        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    @CrossOrigin
    @GetMapping(value = "/patients")
    public ResponseEntity<List<PatientsResponse>> getAllPatients() {
        List<PatientsResponse> patients = patientService.getAllPatients();
        return new ResponseEntity<>(patients, HttpStatus.OK);
    }

    @CrossOrigin
    @GetMapping(value = "/{patientId}")
    public ResponseEntity<PatientDetailResponse> getPatientById(@PathVariable Long patientId) {
        PatientDetailResponse patient = patientService.getPatientById(patientId);
        return ResponseEntity.ok(patient);
    }

    @CrossOrigin
    @GetMapping(value = "/{patientId}/{fileType}")
    public ResponseEntity<StlFileResponse> getPatientStlFile(
            @PathVariable Long patientId,
            @PathVariable String fileType) throws IOException {

        StlFileResponse response = STLFileService.getStlFileAsBase64(patientId, fileType);
        return ResponseEntity.ok(response);
    }
}
