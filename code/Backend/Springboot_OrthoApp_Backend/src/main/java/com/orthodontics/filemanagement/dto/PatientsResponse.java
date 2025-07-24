package com.orthodontics.filemanagement.dto;

import lombok.*;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Getter
public class PatientsResponse {
//    private Long patient_id;
    private String name;
    private String treatment_status;
    private Double pre_PAR_score;
    private Double post_PAR_score;
    private Long preTreatmentPatientId;
    private Long postTreatmentPatientId;
}
