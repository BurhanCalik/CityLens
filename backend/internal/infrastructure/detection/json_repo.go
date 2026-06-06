// Package detection provides infrastructure implementations of the detection
// domain repository. The JSON implementation is deliberately datastore-free so
// the public map and the live demo keep working without Postgres.
package detection

import (
	"context"
	_ "embed"
	"encoding/json"
	"fmt"
	"log/slog"
	"os"

	"github.com/google/uuid"

	"github.com/masterfabric-go/masterfabric/internal/domain/detection/model"
	domainErr "github.com/masterfabric-go/masterfabric/internal/shared/errors"
)

// embeddedDetections is the anonymized detections document baked into the binary
// at build time. It guarantees GET /detections always returns data — even with
// no database, no extra files, and a cold Render instance.
//
//go:embed detections.json
var embeddedDetections []byte

// detectionsNamespace is a fixed UUIDv5 namespace, so the same physical
// detection (lat,lng,label) always maps to the same stable ID across restarts.
// Stable IDs make the demo reproducible and give the web a stable React key.
var detectionsNamespace = uuid.MustParse("6f1b3c9e-0b3a-4c2a-9b7e-9c1d2e3f4a5b")

// JSONRepository serves detections parsed from a JSON document.
type JSONRepository struct {
	detections []*model.Detection
}

// NewJSONRepository loads detections from path when it is non-empty and
// readable, otherwise from the embedded document. Any parse failure on an
// external file falls back to the embedded data, so the repository is always
// usable. context-free construction is intentional: data is loaded once.
func NewJSONRepository(path string, log *slog.Logger) (*JSONRepository, error) {
	raw, source := embeddedDetections, "embedded"
	if path != "" {
		if b, err := os.ReadFile(path); err == nil {
			raw, source = b, path
		} else if log != nil {
			log.Warn("DETECTIONS_PATH unreadable, using embedded detections", "path", path, "error", err)
		}
	}

	parsed, err := parseDetections(raw)
	if err != nil {
		if source == "embedded" {
			return nil, fmt.Errorf("parse embedded detections: %w", err)
		}
		// External file was malformed: fall back to the embedded document.
		if log != nil {
			log.Warn("detections file malformed, using embedded detections", "path", path, "error", err)
		}
		if parsed, err = parseDetections(embeddedDetections); err != nil {
			return nil, fmt.Errorf("parse embedded detections: %w", err)
		}
		source = "embedded(fallback)"
	}

	if log != nil {
		log.Info("detections repository ready", "source", source, "count", len(parsed))
	}
	return &JSONRepository{detections: parsed}, nil
}

// List returns all detections. ctx is accepted for interface conformance and
// future datastore-backed implementations.
func (r *JSONRepository) List(_ context.Context) ([]*model.Detection, error) {
	return r.detections, nil
}

// parseDetections unmarshals the document and normalizes each record: it assigns
// a stable ID when missing and defaults the severity to "info".
func parseDetections(raw []byte) ([]*model.Detection, error) {
	var detections []*model.Detection
	if err := json.Unmarshal(raw, &detections); err != nil {
		return nil, domainErr.New(domainErr.ErrInternal, "invalid detections json", err)
	}

	for _, d := range detections {
		if d.ID == uuid.Nil {
			seed := fmt.Sprintf("%.6f|%.6f|%s", d.Lat, d.Lng, d.Label)
			d.ID = uuid.NewSHA1(detectionsNamespace, []byte(seed))
		}
		if d.Severity == "" {
			d.Severity = model.SeverityInfo
		}
	}
	return detections, nil
}
