// Package model holds the CityLens detection domain entities. It is pure Go and
// must not import application or infrastructure packages.
package model

import (
	"time"

	"github.com/google/uuid"
)

// Severity classifies how urgent a detected urban issue is, so a municipality
// can triage field work (e.g. show only "urgent" items on the map).
type Severity string

const (
	// SeverityInfo is a routine, non-blocking observation.
	SeverityInfo Severity = "info"
	// SeverityWarning needs attention but is not an emergency.
	SeverityWarning Severity = "warning"
	// SeverityUrgent should be acted on quickly.
	SeverityUrgent Severity = "urgent"
)

// Detection is a single anonymized urban-object detection produced by the
// CityLens computer-vision pipeline.
//
// KVKK note: a Detection only ever describes an inanimate urban object and the
// public location where it was seen. It never contains faces, license-plate
// text, identities or any personal data — those are irreversibly blurred before
// detection runs.
type Detection struct {
	ID         uuid.UUID `json:"id"`
	Lat        float64   `json:"lat"`
	Lng        float64   `json:"lng"`
	Label      string    `json:"label"`
	Score      float64   `json:"score"`
	ImageURL   string    `json:"image_url"`
	Address    string    `json:"address,omitempty"`
	Severity   Severity  `json:"severity,omitempty"`
	CapturedAt time.Time `json:"captured_at,omitempty"`
}
