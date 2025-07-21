package com.orthodontics.filemanagement.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ParScoreResponse {
    // We'll have separate scores for each component
    private int upperAnteriorScore;
    private int lowerAnteriorScore;
    // ... we can add overjet, overbite, etc. here later ...
    private int finalParScore;
}