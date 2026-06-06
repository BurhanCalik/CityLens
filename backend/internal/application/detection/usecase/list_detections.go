// Package usecase contains the detection application use cases.
package usecase

import (
	"context"
	"fmt"

	"github.com/masterfabric-go/masterfabric/internal/application/detection/dto"
	"github.com/masterfabric-go/masterfabric/internal/domain/detection/repository"
)

// ListDetectionsUseCase returns all anonymized detections for the map.
type ListDetectionsUseCase struct {
	repo repository.DetectionRepository
}

// NewListDetectionsUseCase wires the use case with its repository.
func NewListDetectionsUseCase(repo repository.DetectionRepository) *ListDetectionsUseCase {
	return &ListDetectionsUseCase{repo: repo}
}

// Execute loads detections and maps them to the public response shape.
func (uc *ListDetectionsUseCase) Execute(ctx context.Context) ([]dto.DetectionResponse, error) {
	detections, err := uc.repo.List(ctx)
	if err != nil {
		return nil, fmt.Errorf("list detections: %w", err)
	}

	out := make([]dto.DetectionResponse, 0, len(detections))
	for _, d := range detections {
		out = append(out, dto.FromModel(d))
	}
	return out, nil
}
