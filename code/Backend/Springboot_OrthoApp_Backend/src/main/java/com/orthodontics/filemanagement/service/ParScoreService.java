package com.orthodontics.filemanagement.service;
import com.orthodontics.filemanagement.dto.ParScoreResponse;
import com.orthodontics.filemanagement.model.Point;
import com.orthodontics.filemanagement.repository.PointRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import javax.vecmath.Point3d;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ParScoreService {

    private final PointRepository pointRepository;

    public ParScoreResponse calculateParScoreForPatient(Long patientId) {
        List<Point> pointsFromDb = pointRepository.findAllByStlFiles_id(patientId);

        // 1. Filter the points from the DB into two separate maps.
        // This solves the duplicate key problem.
        Map<String, Point3d> upperPointsMap = pointsFromDb.stream()
                .filter(p -> "Upper Arch Segment".equals(p.getFile_type()))
                .collect(Collectors.toMap(
                        Point::getName,
                        this::parseCoordinatesFromEntity,
                        (existing, replacement) -> existing // Keep first on duplicates within the same arch
                ));

        Map<String, Point3d> lowerPointsMap = pointsFromDb.stream()
                .filter(p -> "Lower Arch Segment".equals(p.getFile_type()))
                .collect(Collectors.toMap(
                        Point::getName,
                        this::parseCoordinatesFromEntity,
                        (existing, replacement) -> existing // Keep first on duplicates within the same arch
                ));

        // 2. Calculate the score for each segment separately
        int upperAnteriorScore = calculateAnteriorSegmentScore(upperPointsMap);
        int lowerAnteriorScore = calculateAnteriorSegmentScore(lowerPointsMap);

        // 3. Sum the component scores for the final PAR score
        int finalScore = upperAnteriorScore + lowerAnteriorScore; // Add other scores here in the future

        // 4. Build the detailed response
        return ParScoreResponse.builder()
                .upperAnteriorScore(upperAnteriorScore)
                .lowerAnteriorScore(lowerAnteriorScore)
                .finalParScore(finalScore)
                .build();
    }

    // This method can now be reused for both upper and lower arches
    private int calculateAnteriorSegmentScore(Map<String, Point3d> pointsMap) {
        String[][] contactPointPairs = {
                {"R3M", "R2D"},
                {"R2M", "R1D"},
                {"R1M", "L1M"},
                {"L1D", "L2M"},
                {"L2D", "L3M"}
        };
        int totalScore = 0;
        for (String[] pair : contactPointPairs) {
            Point3d p1 = pointsMap.get(pair[0]);
            Point3d p2 = pointsMap.get(pair[1]);
            if (p1 != null && p2 != null) {
                totalScore += getScoreForDistance(p1.distance(p2));
            }
        }
        return totalScore;
    }

    // Helper methods (parseCoordinatesFromEntity and getScoreForDistance) remain the same
    private Point3d parseCoordinatesFromEntity(Point point) {
        String[] coords = point.getCoordinates().split(",");
        return new Point3d(Double.parseDouble(coords[0]), Double.parseDouble(coords[1]), Double.parseDouble(coords[2]));
    }

    private int getScoreForDistance(double distance) {
        if (distance <= 1.0) return 0;
        if (distance <= 2.0) return 1;
        if (distance <= 4.0) return 2;
        if (distance <= 8.0) return 3;
        return 4;
    }
}