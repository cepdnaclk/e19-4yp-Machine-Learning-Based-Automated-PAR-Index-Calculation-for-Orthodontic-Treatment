package com.orthodontics.filemanagement.service;

import com.orthodontics.filemanagement.dto.PatientRegisterRequest;
import com.orthodontics.filemanagement.dto.PatientsResponse;
import com.orthodontics.filemanagement.dto.PatientDetailResponse;
import com.orthodontics.filemanagement.model.Patient;
import java.util.Optional;
import com.orthodontics.filemanagement.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.persistence.EntityNotFoundException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class PatientService {

    private final PatientRepository patientRepository;

    public Long createPatient(PatientRegisterRequest patientRegisterRequest) {
        Patient patient = Patient.builder()
                .name(patientRegisterRequest.getName())
                .treatment_status(patientRegisterRequest.getTreatment_status())
                .build();

        patientRepository.save(patient);
        return patient.getPatient_id();
    }

//    public List<PatientsResponse> getAllPatients() {
//        // 1. Fetch all patient records from the database
//        List<Patient> allPatients =  patientRepository.findAll();
//        List<PatientsResponse> patients = new java.util.ArrayList<>(List.of());
//
//        for (Patient patient : allPatients) {
//            PatientsResponse finalPatient= PatientsResponse.builder()
//                    .patient_id(patient.getPatient_id())
//                    .name(patient.getName())
//                    .treatment_status(patient.getTreatment_status())
//                    .build();
//
//            if(Objects.equals(patient.getTreatment_status(), "Pre Treatment")) {
//                finalPatient.setPre_PAR_score(10.0);
//                for (Patient patient1 : allPatients) {
//                    if(patient.getName().equals(patient1.getName()) && Objects.equals(patient1.getTreatment_status(), "Post Treatment")) {
//                        finalPatient.setPost_PAR_score(20.0);
//                        allPatients.remove(patient1);
//                    }
//                }
//            }
//            else if(Objects.equals(patient.getTreatment_status(), "Post Treatment")) {
//                finalPatient.setPost_PAR_score(20.0);
//                for (Patient patient1 : allPatients) {
//                    if(patient.getName().equals(patient1.getName()) && Objects.equals(patient1.getTreatment_status(), "Pre Treatment")) {
//                        finalPatient.setPre_PAR_score(10.0);
//                        allPatients.remove(patient1);
//                    }
//                }
//            }
//
//            patients.add(finalPatient);
//        }
//        return patients;
//    }
    public List<PatientsResponse> getAllPatients() {
        // ... (your existing code to fetch and group patients by name) ...
        Map<String, List<Patient>> groupedByName = patientRepository.findAll().stream()
                .collect(Collectors.groupingBy(Patient::getName));

        List<PatientsResponse> patientsResponseList = new ArrayList<>();

        for (Map.Entry<String, List<Patient>> entry : groupedByName.entrySet()) {
            List<Patient> patientRecords = entry.getValue();

            Optional<Patient> preTreatmentRecord = patientRecords.stream()
                    .filter(p -> "Pre".equals(p.getTreatment_status()))
                    .findFirst();

            Optional<Patient> postTreatmentRecord = patientRecords.stream()
                    .filter(p -> "Post".equals(p.getTreatment_status()))
                    .findFirst();

            // Build the response with the two separate IDs
            PatientsResponse response = PatientsResponse.builder()
                    .name(entry.getKey())
                    .pre_PAR_score(preTreatmentRecord.map(Patient::getPar_score).orElse(null))
                    .post_PAR_score(postTreatmentRecord.map(Patient::getPar_score).orElse(null))
                    .preTreatmentPatientId(preTreatmentRecord.map(Patient::getPatient_id).orElse(null))
                    .postTreatmentPatientId(postTreatmentRecord.map(Patient::getPatient_id).orElse(null))
                    .build();

            patientsResponseList.add(response);
        }

        return patientsResponseList;
    }

    // TODO: Use to select one from list
//    public PatientsResponse getPatientById(Long patientId) {
//        Patient patient = patientRepository.findById(patientId).orElseThrow();
//        return PatientsResponse.builder()
//                .patient_id(patient.getPatient_id())
//                .name(patient.getName())
//                .treatment_status(patient.getTreatment_status())
//                .pre_PAR_score(10.0)
//                .post_PAR_score(20.0)
//                .build();
//    }
    public PatientDetailResponse getPatientById(Long patientId) {
        // 1. Fetch the single patient record from the database
        Patient patient = patientRepository.findById(patientId)
                .orElseThrow(() -> new EntityNotFoundException("Patient not found with id: " + patientId));

        // 2. Build the detailed response using the new DTO
        return PatientDetailResponse.builder()
                .patient_id(patient.getPatient_id())
                .name(patient.getName())
                .treatment_status(patient.getTreatment_status())
                .par_score(patient.getPar_score())
                .build();
    }
}
