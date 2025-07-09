package com.orthodontics.filemanagement.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PointListRequest {
    private Long patient_id;
    private String file_type;
    private String measurement_type;
    private List<PointData> points;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PointData {
        private String point_name;
        private String coordinates;
    }
}