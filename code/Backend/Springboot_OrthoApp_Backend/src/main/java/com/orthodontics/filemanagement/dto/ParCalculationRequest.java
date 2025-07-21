package com.orthodontics.filemanagement.dto;

import lombok.Data;
import java.util.List;

@Data
public class ParCalculationRequest {
    private List<PointDTO> points;
}