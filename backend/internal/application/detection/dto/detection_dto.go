// Package dto holds the request/response shapes for the detection use cases.
package dto

import (
	"time"

	"github.com/masterfabric-go/masterfabric/internal/domain/detection/model"
)

// DetectionResponse is the public JSON contract served by GET /detections.
// It follows the agreed output contract:
//
//	{ "lat", "lng", "label", "score", "image_url" }
//
// plus a few optional fields the web UI uses for richer display.
type DetectionResponse struct {
	ID         string  `json:"id"`
	Lat        float64 `json:"lat"`
	Lng        float64 `json:"lng"`
	Label      string  `json:"label"`
	Category   string  `json:"category,omitempty"`
	Score      float64 `json:"score"`
	ImageURL   string  `json:"image_url"`
	Address    string  `json:"address,omitempty"`
	Severity   string  `json:"severity,omitempty"`
	CapturedAt string  `json:"captured_at,omitempty"`
}

// StatsResponse is the aggregate served by GET /detections/stats, used to power
// the counters and filters on the map dashboard.
type StatsResponse struct {
	Total      int            `json:"total"`
	BySeverity map[string]int `json:"by_severity"`
	ByLabel    map[string]int `json:"by_label"`
	AvgScore   float64        `json:"avg_score"`
}

// FromModel maps a domain Detection to its public response shape.
func FromModel(d *model.Detection) DetectionResponse {
	captured := ""
	if !d.CapturedAt.IsZero() {
		captured = d.CapturedAt.UTC().Format(time.RFC3339)
	}
	return DetectionResponse{
		ID:         d.ID.String(),
		Lat:        d.Lat,
		Lng:        d.Lng,
		Label:      d.Label,
		Category:   d.Category,
		Score:      d.Score,
		ImageURL:   d.ImageURL,
		Address:    d.Address,
		Severity:   string(d.Severity),
		CapturedAt: captured,
	}
}
