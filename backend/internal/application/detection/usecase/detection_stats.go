package usecase

import (
	"context"
	"fmt"

	"github.com/masterfabric-go/masterfabric/internal/application/detection/dto"
	"github.com/masterfabric-go/masterfabric/internal/domain/detection/model"
	"github.com/masterfabric-go/masterfabric/internal/domain/detection/repository"
)

// DetectionStatsUseCase aggregates detections into dashboard counters.
type DetectionStatsUseCase struct {
	repo repository.DetectionRepository
}

// NewDetectionStatsUseCase wires the use case with its repository.
func NewDetectionStatsUseCase(repo repository.DetectionRepository) *DetectionStatsUseCase {
	return &DetectionStatsUseCase{repo: repo}
}

// Execute computes totals, per-severity and per-label breakdowns, and the mean
// confidence score across all detections.
func (uc *DetectionStatsUseCase) Execute(ctx context.Context) (dto.StatsResponse, error) {
	detections, err := uc.repo.List(ctx)
	if err != nil {
		return dto.StatsResponse{}, fmt.Errorf("detection stats: %w", err)
	}

	stats := dto.StatsResponse{
		Total:      len(detections),
		BySeverity: make(map[string]int),
		ByLabel:    make(map[string]int),
	}

	var scoreSum float64
	for _, d := range detections {
		severity := string(d.Severity)
		if severity == "" {
			severity = string(model.SeverityInfo)
		}
		stats.BySeverity[severity]++
		stats.ByLabel[d.Label]++
		scoreSum += d.Score
	}

	if len(detections) > 0 {
		stats.AvgScore = scoreSum / float64(len(detections))
	}

	return stats, nil
}
