package com.orthodontics.filemanagement.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PointRequest {
    private Long point_ID;
    private Long patient_id;
    private String point_name;
    private String coordinates;
    private String file_type;
    private String measurement_type;
}