// Package detection exposes the detection HTTP endpoints. These are public
// (no JWT/tenant required) and registered outside the /api/v1 group, like the
// health probes, so the web map can read them directly.
package detection

import (
	"net/http"

	"github.com/masterfabric-go/masterfabric/internal/application/detection/usecase"
	"github.com/masterfabric-go/masterfabric/internal/shared/response"
)

// Handler serves anonymized detections and their aggregate stats.
type Handler struct {
	listUC  *usecase.ListDetectionsUseCase
	statsUC *usecase.DetectionStatsUseCase
}

// NewHandler creates a detection handler.
func NewHandler(listUC *usecase.ListDetectionsUseCase, statsUC *usecase.DetectionStatsUseCase) *Handler {
	return &Handler{listUC: listUC, statsUC: statsUC}
}

// List handles GET /detections and returns the full detection array.
func (h *Handler) List(w http.ResponseWriter, r *http.Request) {
	items, err := h.listUC.Execute(r.Context())
	if err != nil {
		response.Error(w, err)
		return
	}
	response.JSON(w, http.StatusOK, items)
}

// Stats handles GET /detections/stats and returns dashboard counters.
func (h *Handler) Stats(w http.ResponseWriter, r *http.Request) {
	stats, err := h.statsUC.Execute(r.Context())
	if err != nil {
		response.Error(w, err)
		return
	}
	response.JSON(w, http.StatusOK, stats)
}
