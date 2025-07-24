package com.orthodontics.filemanagement.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ParScoreResponse {
    // We'll have separate scores for each component
    private int upperAnteriorScore;
    private int lowerAnteriorScore;
    private int buccalOcclusionAnteroPosteriorScore;
    private int buccalOcclusionTransverseScore;
    private int buccalOcclusionVerticalScore;
    private int overjetScore;
    private int overbiteScore;
    private int centrelineScore;
    private int finalParScore;
}