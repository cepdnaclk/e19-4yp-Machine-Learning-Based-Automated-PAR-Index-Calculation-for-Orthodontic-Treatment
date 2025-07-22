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

        Map<String, Point3d> buccalPointsMap = pointsFromDb.stream()
                .filter(p -> "Buccal Segment".equals(p.getFile_type()))
                .collect(Collectors.toMap(
                        Point::getName,
                        this::parseCoordinatesFromEntity, (e, r) -> e
                ));

        // 2. Calculate the score for each segment separately
        int upperAnteriorScore = calculateAnteriorSegmentScore(upperPointsMap);
        int lowerAnteriorScore = calculateAnteriorSegmentScore(lowerPointsMap);
        int overjetScore = calculateOverjetScore(upperPointsMap, buccalPointsMap);
        int overbiteScore = calculateOverbiteScore(upperPointsMap, lowerPointsMap);
        int centrelineScore = calculateCentrelineScore(upperPointsMap, lowerPointsMap);

        int buccalAnteroPosterior = calculateBuccalAnteroPosterior(upperPointsMap, lowerPointsMap, "R") +
                calculateBuccalAnteroPosterior(upperPointsMap, lowerPointsMap, "L");
        int buccalTransverse = calculateBuccalTransverse(upperPointsMap, lowerPointsMap, "R") +
                calculateBuccalTransverse(upperPointsMap, lowerPointsMap, "L");
        int buccalVertical = calculateBuccalVertical(upperPointsMap, lowerPointsMap, "R") +
                calculateBuccalVertical(upperPointsMap, lowerPointsMap, "L");

        // 3. Sum the component scores for the final PAR score
        int finalScore = upperAnteriorScore +
                lowerAnteriorScore +
                (overjetScore * 6) +
                (overbiteScore * 2) +
                (centrelineScore * 4) +
                buccalAnteroPosterior + // Weighting is x1
                buccalTransverse +      // Weighting is x1
                buccalVertical;

        // 4. Build the detailed response
        return ParScoreResponse.builder()
                .upperAnteriorScore(upperAnteriorScore)
                .lowerAnteriorScore(lowerAnteriorScore)
                .buccalOcclusionAnteroPosteriorScore(buccalAnteroPosterior)
                .buccalOcclusionTransverseScore(buccalTransverse)
                .buccalOcclusionVerticalScore(buccalVertical)
                .overjetScore(overjetScore * 6)
                .overbiteScore(overbiteScore * 2)
                .centrelineScore(centrelineScore * 4)
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

    private int calculateBuccalAnteroPosterior(Map<String, Point3d> upper, Map<String, Point3d> lower, String side) {
        // Measures the position of the upper molar's mesio-buccal cusp relative to the lower molar's buccal groove.
        // Assumes Z-axis is Antero-Posterior.
        Point3d upperCusp = upper.get(side + "6MB"); // Upper Mesio-Buccal cusp
        Point3d lowerGroove = lower.get(side + "6GB"); // Lower Buccal Groove

        if (upperCusp == null || lowerGroove == null) return 0;

        // Ideal occlusion is when the cusp and groove are aligned in the Z-axis.
        double discrepancy = Math.abs(upperCusp.y - lowerGroove.y);

        // This requires a reference for "half unit" width, we'll estimate using mesio-distal width.
        Point3d lowerMesial = lower.get(side + "6M");
        Point3d lowerDistalBuccal = lower.get(side + "6DB"); // Using distal-buccal for width
        if(lowerMesial == null || lowerDistalBuccal == null) return 0;

        double halfUnitWidth = lowerMesial.distance(lowerGroove);

        if (discrepancy < (halfUnitWidth / 2.0)) return 0; // Less than quarter unit discrepancy
        if (discrepancy < halfUnitWidth) return 1; // Less than half unit
        return 2; // Half unit discrepancy or more
    }

    private int calculateBuccalTransverse(Map<String, Point3d> upper, Map<String, Point3d> lower, String side) {
        // Get all the required points for the calculation
        Point3d upper6MB = upper.get(side + "6MB"); // Mesio-Buccal
        Point3d upper6MP = upper.get(side + "6MP"); // Mesio-Palatal
        Point3d upper6DB = upper.get(side + "6DB"); // Disto-Buccal
        Point3d upper6DP = upper.get(side + "6DP"); // Disto-Palatal
        Point3d upper6GB = upper.get(side + "6GB"); // Upper Buccal Groove

        Point3d lower6MB = lower.get(side + "6MB"); // Lower Mesio-Buccal
        Point3d lower6GB = lower.get(side + "6GB"); // Lower Buccal Groove

        // Check if all necessary points exist to avoid errors
        if (upper6MB == null || upper6MP == null || upper6DB == null || upper6DP == null ||
                upper6GB == null || lower6MB == null || lower6GB == null) {
            System.out.println("Warning: Missing points for Buccal Transverse calculation on side: " + side);
            return 0;
        }

        // 1. Calculate the midpoint of the four upper cusp tips (using X-coordinates)
        double upperMidX = (upper6MB.x + upper6MP.x + upper6DB.x + upper6DP.x) / 4.0;

        // 2. Calculate the reference distance 'd'
        double d = 0.25 * Math.abs(upperMidX - upper6GB.x);

        // 3. Define the boundaries for the "No crossbite" zone
        double noCrossbiteLowerBound = upperMidX - (3 * d);
        double noCrossbiteUpperBound = upperMidX + (3 * d);

        // crossbite
        if(side.equals("L")) {
            if (lower6MB.x < noCrossbiteLowerBound) {
                return 2;
            }
        } else {
            if (lower6MB.x > noCrossbiteUpperBound) {
                return 2;
            }
        }

        // 4. Check for "No crossbite" condition
        // We check if the lower buccal cusp falls within this ideal range
        if (lower6MB.x >= noCrossbiteLowerBound && lower6MB.x <= noCrossbiteUpperBound) {
            return 0; // No crossbite, score is 0
        }

        if (side.equals("L")) {
            // 5. Define the boundaries for the "Crossbite tendency" zone
            double tendencyLowerBound = noCrossbiteUpperBound; // The outer edge of the "no crossbite" zone
            double tendencyUpperBound = lower6GB.x + d;

            // 6. Check for "Crossbite tendency" condition
            if (lower6MB.x >= tendencyLowerBound && lower6MB.x <= tendencyUpperBound) {
                return 1; // Crossbite tendency, score is 1
            }
        }else {
            // 5. Define the boundaries for the "Crossbite tendency" zone
            double tendencyLowerBound = noCrossbiteLowerBound; // The outer edge of the "no crossbite" zone
            double tendencyUpperBound = lower6GB.x - d;

            // 6. Check for "Crossbite tendency" condition
            if (lower6MB.x <= tendencyLowerBound && lower6MB.x >= tendencyUpperBound) {
                return 1; // Crossbite tendency, score is 1
            }
        }

        // If neither of the above conditions are met, it's a full scissor bite
        return 4; // Full scissor bite, score is 4
    }

    private int calculateBuccalVertical(Map<String, Point3d> upper, Map<String, Point3d> lower, String side) {
        // Measures posterior open bite by finding the center of the occluding surfaces.

        // 1. Get all four cusp tips for the upper tooth
        Point3d upper6MB = upper.get(side + "6MB");
        Point3d upper6MP = upper.get(side + "6MP");
        Point3d upper6DB = upper.get(side + "6DB");
        Point3d upper6DP = upper.get(side + "6DP");

        // 2. Get all four cusp tips for the lower tooth
        Point3d lower6MB = lower.get(side + "6MB");
        Point3d lower6MP = lower.get(side + "6MP");
        Point3d lower6DB = lower.get(side + "6DB");
        Point3d lower6DP = lower.get(side + "6DP");

        // Check if all necessary points exist to avoid errors
        if (upper6MB == null || upper6MP == null || upper6DB == null || upper6DP == null ||
                lower6MB == null || lower6MP == null || lower6DB == null || lower6DP == null) {
            System.out.println("Warning: Missing one or more cusp tips for Buccal Vertical calculation on side: " + side);
            return 0;
        }

        // 3. Calculate the centroid (average point) of the upper occluding surface
        Point3d upperOcclusalCenter = new Point3d(
                (upper6MB.x + upper6MP.x + upper6DB.x + upper6DP.x) / 4.0,
                (upper6MB.y + upper6MP.y + upper6DB.y + upper6DP.y) / 4.0,
                (upper6MB.z + upper6MP.z + upper6DB.z + upper6DP.z) / 4.0
        );

        // 4. Calculate the centroid of the lower occluding surface
        Point3d lowerOcclusalCenter = new Point3d(
                (lower6MB.x + lower6MP.x + lower6DB.x + lower6DP.x) / 4.0,
                (lower6MB.y + lower6MP.y + lower6DB.y + lower6DP.y) / 4.0,
                (lower6MB.z + lower6MP.z + lower6DB.z + lower6DP.z) / 4.0
        );

        // 5. Measure the vertical distance (Z-axis) between the two centroids
        double openBite = upperOcclusalCenter.z - lowerOcclusalCenter.z;

        // 6. Assign score based on the distance (same as before)
        if (openBite > 2.0) {
            return 1; // Posterior open bite of more than 2mm
        }

        return 0; // No significant open bite
    }

    // Score calculation for overjet
    private int calculateOverjetScore(Map<String, Point3d> upperPointsMap, Map<String, Point3d> buccalPointsMap) {
        Point3d upperIncisor = upperPointsMap.get("R1Mid");
        Point3d lowerIncisor = buccalPointsMap.get("LCover");


        if (upperIncisor == null || lowerIncisor == null) {
            System.out.println("Warning: Missing R1Mid or LCover point for overjet calculation.");
            return 0; // Cannot calculate if points are missing
        }

        // Calculate the distance, then take its absolute value
        double overjetDistance = Math.abs(upperIncisor.y - lowerIncisor.y);
        System.out.println("Overjet distance:"+overjetDistance);

        // Scoring for positive overjet
        if (overjetDistance <= 3.0) return 0;
        if (overjetDistance <= 5.0) return 1;
        if (overjetDistance <= 7.0) return 2;
        if (overjetDistance <= 9.0) return 3;
        return 4; // Greater than 9mm
    }

    private int calculateOverbiteScore(Map<String, Point3d> upperPointsMap, Map<String, Point3d> lowerPointsMap) {
        Point3d upperIncisorMid = upperPointsMap.get("R1Mid");
        Point3d lowerIncisorMid = lowerPointsMap.get("R1Mid");
        Point3d lowerIncisorGingival = lowerPointsMap.get("R1Low");

        if (upperIncisorMid == null || lowerIncisorMid == null || lowerIncisorGingival == null) {
            System.out.println("Warning: Missing points for overbite calculation.");
            return 0;
        }

        // According to the PDF, overbite is the vertical coverage of the lower incisor.
        // We assume the Z-axis is the vertical direction.
        double lowerIncisorHeight = Math.abs(lowerIncisorMid.z - lowerIncisorGingival.z);

        // Vertical distance between the tips of the upper and lower incisors.
        // A positive value means an open bite, a negative value means an overbite.
        double verticalDistance = upperIncisorMid.z - lowerIncisorMid.z;

        // Open Bite Scoring (if upper incisor is above lower)
        if (verticalDistance > 0) {
            double openBite = verticalDistance;
            if (openBite <= 1.0) return 1;
            if (openBite <= 2.0) return 2;
            if (openBite <= 4.0) return 3;
            return 4;
        }

        // Overbite Scoring (if upper incisor covers lower)
        if (lowerIncisorHeight > 0) { // Avoid division by zero
            double coverage = Math.abs(verticalDistance) / lowerIncisorHeight;
            if (coverage < 1.0/3.0) return 0;
            if (coverage < 2.0/3.0) return 1;
            if (coverage < 1.0) return 2;
            return 3; // Full tooth coverage or more
        }

        return 0; // Default case
    }

    private int calculateCentrelineScore(Map<String, Point3d> upperPointsMap, Map<String, Point3d> lowerPointsMap) {
        // Get the mesial points of the central incisors for both arches
        Point3d upperL1M = upperPointsMap.get("L1M");
        Point3d upperR1M = upperPointsMap.get("R1M");
        Point3d lowerL1M = lowerPointsMap.get("L1M");
        Point3d lowerR1M = lowerPointsMap.get("R1M");

        // Get points to measure the width of the lower incisor
        Point3d lowerR1D = lowerPointsMap.get("R1D");

        if (upperL1M == null || upperR1M == null || lowerL1M == null || lowerR1M == null || lowerR1D == null) {
            System.out.println("Warning: Missing points for centreline calculation.");
            return 0;
        }

        // 1. Calculate the midpoint (center) of the upper incisors
        Point3d upperMidpoint = new Point3d();
        upperMidpoint.add(upperL1M, upperR1M);
        upperMidpoint.scale(0.5);

        // 2. Calculate the midpoint (center) of the lower incisors
        Point3d lowerMidpoint = new Point3d();
        lowerMidpoint.add(lowerL1M, lowerR1M);
        lowerMidpoint.scale(0.5);

        // 3. Calculate the transverse (left-right) distance between the midpoints
        // We assume the X-axis is the transverse direction
        double discrepancy = Math.abs(upperMidpoint.x - lowerMidpoint.x);

        // 4. Calculate the width of the lower incisor to use as a reference
        double lowerIncisorWidth = lowerR1M.distance(lowerR1D);
        if (lowerIncisorWidth == 0) return 0; // Avoid division by zero

        // 5. Score based on the discrepancy as a fraction of the incisor width
        if (discrepancy <= (0.25 * lowerIncisorWidth)) {
            return 0;
        } else if (discrepancy <= (0.5 * lowerIncisorWidth)) {
            return 1;
        } else {
            return 2;
        }
    }
}