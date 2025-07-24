package com.orthodontics.filemanagement.dto;

import lombok.Data;

@Data
public class PointDTO {
    private String point_name;
    private String coordinates; // e.g., "x,y,z"
}