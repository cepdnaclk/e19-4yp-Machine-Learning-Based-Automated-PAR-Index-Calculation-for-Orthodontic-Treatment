package com.orthodontics.filemanagement.dto;

import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
public class PARIndexPointsRequest {
    private Long pointId;
    private String pointName;
    private String coordinates;

    public PARIndexPointsRequest(Long pointId, String pointName, String coordinates) {
        this.pointId = pointId;
        this.pointName = pointName;
        this.coordinates = coordinates;
    }
}