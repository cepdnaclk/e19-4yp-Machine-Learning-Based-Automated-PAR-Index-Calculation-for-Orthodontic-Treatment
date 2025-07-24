package com.orthodontics.filemanagement.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class PatientDetailResponse {
    private Long patient_id;
    private String name;
    private String treatment_status;
    private Double par_score;
}