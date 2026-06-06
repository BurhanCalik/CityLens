// Package repository declares the detection persistence contracts. The
// interface lives in the domain layer; concrete implementations (JSON file,
// Postgres, ...) live in the infrastructure layer.
package repository

import (
	"context"

	"github.com/masterfabric-go/masterfabric/internal/domain/detection/model"
)

// DetectionRepository provides read access to anonymized detections.
//
// It is intentionally read-only for the demo: detections are produced offline
// by the CV pipeline and served as immutable, reproducible results.
type DetectionRepository interface {
	// List returns all available detections.
	List(ctx context.Context) ([]*model.Detection, error)
}
